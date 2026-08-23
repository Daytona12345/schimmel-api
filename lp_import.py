#!/usr/bin/env python3
"""
thermo-check.de — Landing Page Import Script v3.1
==================================================
Eine Welt. Eine Seite pro Landingpage, im Bereich /wissen.
Kein Dual Import, kein HTML-Zusammenbau, keine HTML-Bereinigung.

Architektur (verbindlich, M0 18.06.):
  Eine fuehrende Datenquelle pro Wert — keine Doppelhaltung.
    - Inhaltsbausteine + Steuerung  -> ACF-Felder (tc_...)
    - URL-Slug                      -> WordPress-Post-Slug (post_name)
    - SEO-Title / Meta-Description  -> RankMath (meta_input)
  HTML wird UNVERAENDERT gespeichert. Das Script baut, bereinigt
  und ergaenzt nichts am gelieferten HTML.

Ablageort:
  Die /wissen-Installation ist eine eigenstaendige WordPress-Installation.
  Das "/wissen/" im Pfad kommt aus deren Permalink-Struktur (Beitragsname),
  NICHT aus einer Eltern-Seite. Daher: kein Parent.

Render Environment Variables:
  WP_URL      = https://thermo-check.de/wissen
  WP_USER     = wordpress-benutzername
  WP_APP_PASS = application-password

Verwendung:
  python lp_import_v3.py              # alle JSONs im /faq_content Ordner
  python lp_import_v3.py datei.json   # einzelne Datei
  python lp_import_v3.py --dry-run    # Test ohne echte Requests

Idempotenz (v3):
  Eindeutige Identifikation ueber tc_site_id (ein ACF-Feld).
  Gefunden  -> aktualisieren (POST auf bestehende Page-ID).
  Nicht da  -> neu anlegen.
  Kein tc_variant mehr (Dual Import entfaellt).

v3.1 (24.6):
  Neues Pflichtfeld tc_intro_question (Eingangs-/Leserfrage, Kernstueck
  der Seite). In ACF_FIELDS und REQUIRED_FIELDS aufgenommen. Position
  vor tc_situation_user.
"""

import json
import os
import re
import sys
import argparse
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path

# ============================================================
# KONFIGURATION
# ============================================================

WP_URL      = os.getenv("WP_URL",      "https://thermo-check.de/wissen")
WP_USER     = os.getenv("WP_USER",     "")
WP_APP_PASS = os.getenv("WP_APP_PASS", "")

CONTENT_DIR = Path(__file__).parent / "faq_content"

# Default-Status, falls das JSON keinen 'status' liefert
DEFAULT_STATUS = "draft"

# Alle inhaltlichen + steuernden ACF-Felder (tc_-Praefix).
# Reihenfolge wie in M0. tc_site_id und tc_page_type sind Steuerfelder,
# der Rest sind Inhaltsbausteine. Alle gehen ueber 'acf' in den Payload.
ACF_FIELDS = [
    "tc_site_id",
    "tc_page_type",
    "tc_intro_question",
    "tc_situation_user",
    "tc_issue_classification",
    "tc_key_question",
    "tc_alternative",
    "tc_cta",
    "tc_legal_advice",
    "tc_excerpt",
]

# Pflichtfelder im JSON. tc_legal_advice ist NICHT pflicht (bei
# Nicht-Konflikt leer), wird aber immer mitgeschrieben (siehe build_acf).
REQUIRED_FIELDS = [
    "title",
    "tc_site_id",
    "tc_page_type",
    "slug",
    "seo_title",
    "meta_description",
    "tc_intro_question",
    "tc_excerpt",
    "tc_situation_user",
    "tc_issue_classification",
    "tc_key_question",
    "tc_alternative",
    "tc_cta",
]

# ============================================================
# LOGGING
# ============================================================

def log(symbol, msg):
    print(f"  {symbol} {msg}")

def log_section(title):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")

# ============================================================
# AUTH
# ============================================================

def auth():
    return HTTPBasicAuth(WP_USER, WP_APP_PASS)

def test_connection():
    url = f"{WP_URL}/wp-json/wp/v2/users/me"
    try:
        r = requests.get(url, auth=auth(), timeout=10)
        if r.status_code == 200:
            data = r.json()
            log("✓", f"Verbunden als: {data.get('name', 'Unbekannt')}")
            return True
        else:
            log("✗", f"Auth-Fehler: {r.status_code} — {r.text[:200]}")
            return False
    except Exception as e:
        log("✗", f"Verbindungsfehler: {e}")
        return False

# ============================================================
# JSON VALIDIERUNG (neues Schema)
# ============================================================

def validate_json(data, filepath):
    """Prueft Pflichtfelder, Slug und tc_site_id vor dem Import."""
    errors = []

    for field in REQUIRED_FIELDS:
        # tc_legal_advice ist bewusst nicht pflicht; leerer String erlaubt.
        if data.get(field) in (None, ""):
            errors.append(f"Pflichtfeld fehlt oder leer: '{field}'")

    # tc_site_id: Kleinbuchstaben, Ziffern, Unterstriche, Bindestriche
    site_id = data.get("tc_site_id", "")
    if site_id and re.search(r"[^a-z0-9_\-]", site_id):
        errors.append(f"tc_site_id enthaelt unerlaubte Zeichen: '{site_id}'")

    # slug: reines ASCII a-z 0-9 -, kein Slash
    slug = data.get("slug", "")
    if "/" in slug or "\\" in slug:
        errors.append(f"slug enthaelt Slash: '{slug}'")
    if slug and re.search(r"[^a-z0-9\-]", slug):
        errors.append(f"slug enthaelt unerlaubte Zeichen (nur a-z 0-9 - erlaubt): '{slug}'")

    # status (optional, Default draft)
    status = data.get("status", DEFAULT_STATUS)
    if status not in ["draft", "publish"]:
        errors.append(f"status muss 'draft' oder 'publish' sein, nicht '{status}'")

    # categories (optional): muss Liste von Strings sein, falls vorhanden
    cats = data.get("categories")
    if cats is not None:
        if not isinstance(cats, list) or any(not isinstance(c, str) for c in cats):
            errors.append("categories muss eine Liste von Klarnamen (Strings) sein")

    if errors:
        log("✗", f"Validierungsfehler in {filepath.name}:")
        for e in errors:
            log("  →", e)
        return False

    return True

# ============================================================
# KATEGORIEN  (Klarnamen -> WP-IDs)
# ============================================================

def get_category_ids(names):
    """Schlaegt WP-Kategorie-IDs zu Klarnamen nach. Unbekannte werden gewarnt."""
    if not names:
        return []
    url = f"{WP_URL}/wp-json/wp/v2/categories"
    try:
        r = requests.get(url, auth=auth(), params={"per_page": 100}, timeout=10)
        if r.status_code == 200:
            all_cats = r.json()
            id_map = {c["name"].lower(): c["id"] for c in all_cats}
            ids = []
            for name in names:
                cat_id = id_map.get(name.lower())
                if cat_id:
                    ids.append(cat_id)
                else:
                    log("⚠", f"Kategorie nicht gefunden: {name}")
            return ids
        else:
            log("✗", f"Kategorie-Lookup HTTP {r.status_code}")
    except Exception as e:
        log("✗", f"Kategorie-Lookup Fehler: {e}")
    return []

# ============================================================
# IDEMPOTENZ-LOOKUP ueber tc_site_id
# ============================================================

def find_page_by_site_id(site_id):
    """
    Sucht eine Seite anhand von tc_site_id.
    Laedt alle Seiten paginiert und filtert in Python nach ACF.
    Nur ein Filter (tc_site_id) — kein tc_variant mehr.
    """
    url = f"{WP_URL}/wp-json/wp/v2/pages"
    page_num = 1
    per_page = 100

    try:
        while True:
            r = requests.get(url, auth=auth(), params={
                "per_page": per_page,
                "page":     page_num,
                "status":   "any",
                "_fields":  "id,acf"
            }, timeout=15)

            if r.status_code == 200:
                pages = r.json()
                if not pages:
                    break

                for page in pages:
                    acf = page.get("acf", {})
                    if not isinstance(acf, dict):
                        # ACF liefert bei leeren/fehlenden Werten teils ein
                        # leeres Array [] statt eines Objekts {} - solche
                        # Seiten koennen kein tc_site_id tragen, ueberspringen.
                        continue
                    if acf.get("tc_site_id") == site_id:
                        return page["id"]

                total_pages = int(r.headers.get("X-WP-TotalPages", 1))
                if page_num >= total_pages:
                    break
                page_num += 1

            elif r.status_code == 400:
                break
            else:
                log("✗", f"Lookup HTTP {r.status_code}")
                break

    except Exception as e:
        log("✗", f"Lookup-Fehler: {e}")

    return None

# ============================================================
# PAYLOAD-BAUSTEINE
# ============================================================

def build_acf(data):
    """
    Baut das ACF-Dict. Alle tc_-Felder werden geschrieben.
    tc_legal_advice wird IMMER gesetzt (leerer String bei Nicht-Konflikt),
    damit das Feld auf jeder Seite existiert und das Template sich
    darauf verlassen kann.
    HTML wird unveraendert uebernommen.
    """
    acf = {}
    for field in ACF_FIELDS:
        acf[field] = data.get(field, "")
    return acf

def build_meta(data):
    """RankMath-Meta ueber meta_input. Keys aus v2.5 bestaetigt."""
    meta = {
        "rank_math_title":       data.get("seo_title", ""),
        "rank_math_description": data.get("meta_description", ""),
    }
    # Focus-Keyword optional: nur setzen, wenn geliefert.
    fk = data.get("focus_keyword")
    if fk:
        meta["rank_math_focus_keyword"] = fk
    return meta

# ============================================================
# SEITE ANLEGEN / AKTUALISIEREN
# ============================================================

def push_page(data, dry_run=False):
    """
    Legt eine WordPress-Seite an oder aktualisiert sie.
    Identifikation ueber tc_site_id. Kein Parent.
    content-Feld wird NICHT befuellt — Inhalt lebt in ACF.
    """
    site_id = data.get("tc_site_id", "")
    title   = data.get("title", "")   # Pflichtfeld (Validierung stellt sicher, dass gesetzt)
    slug    = data.get("slug", "")
    status  = data.get("status", DEFAULT_STATUS)

    acf  = build_acf(data)
    meta = build_meta(data)
    cat_ids = get_category_ids(data.get("categories", [])) if not dry_run else []

    if dry_run:
        log("→", f"[DRY RUN] {title[:60]}")
        log(" ", f"tc_site_id: {site_id} | slug: {slug} | status: {status}")
        log(" ", f"page_type: {data.get('tc_page_type','')} | "
                 f"legal_advice: {'gefuellt' if data.get('tc_legal_advice') else 'leer'}")
        log(" ", f"categories: {data.get('categories', [])}")
        log(" ", f"seo_title: {meta['rank_math_title'][:50]}")
        log(" ", f"ACF-Felder: {', '.join(acf.keys())}")
        return "dry-run"

    payload = {
        "title":      title,
        "slug":       slug,
        "status":     status,
        "excerpt":    "",          # WP-Standard-Excerpt bleibt leer; tc_excerpt ist ACF
        # 'content' wird bewusst NICHT gesetzt (Inhalt liegt in ACF)
        "categories": cat_ids,
        "meta_input": meta,
        "acf":        acf,
    }

    existing_id = find_page_by_site_id(site_id)

    try:
        if existing_id:
            url = f"{WP_URL}/wp-json/wp/v2/pages/{existing_id}"
            action = "Aktualisiert"
        else:
            url = f"{WP_URL}/wp-json/wp/v2/pages"
            action = "Angelegt"

        r = requests.post(url, auth=auth(), json=payload, timeout=30)

        if r.status_code in [200, 201]:
            page     = r.json()
            page_id  = page["id"]
            page_url = page.get("link", f"{WP_URL}/?page_id={page_id}")
            log("✓", f"{action}: ID {page_id} — {page_url}")
            return page_id
        else:
            log("✗", f"Fehler {r.status_code}: {r.text[:300]}")
            return None

    except requests.exceptions.Timeout:
        log("✗", "Timeout — nochmal versuchen")
        return None
    except Exception as e:
        log("✗", f"Fehler: {e}")
        return None

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="thermo-check.de Landing Page Import v3.1")
    parser.add_argument("files", nargs="*")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 50)
    print("  thermo-check.de — Landing Page Import v3.1")
    print("=" * 50)

    if not args.dry_run:
        if not WP_USER or not WP_APP_PASS:
            log("✗", "WP_USER und WP_APP_PASS fehlen.")
            sys.exit(1)
        if not test_connection():
            sys.exit(1)
    else:
        print("  [DRY RUN — keine echten Requests]")

    if args.files:
        files = [Path(f) for f in args.files]
    else:
        if not CONTENT_DIR.exists():
            log("✗", f"Ordner nicht gefunden: {CONTENT_DIR}")
            sys.exit(1)
        files = sorted(CONTENT_DIR.glob("*.json"))
        if not files:
            log("✗", f"Keine JSON-Dateien in {CONTENT_DIR}")
            sys.exit(1)

    print(f"\n  {len(files)} Datei(en) gefunden")

    success, errors, skipped = 0, 0, 0

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            log("✗", f"JSON-Fehler in {filepath.name}: {e}")
            errors += 1
            continue

        if not validate_json(data, filepath):
            skipped += 1
            continue

        log_section(data.get("tc_site_id", filepath.name))
        if push_page(data, dry_run=args.dry_run):
            success += 1
        else:
            errors += 1

    print(f"\n{'=' * 50}")
    print(f"  Fertig: {success} erfolgreich | {errors} Fehler | {skipped} uebersprungen")
    if not args.dry_run and success > 0:
        print(f"  → Drafts pruefen: {WP_URL}/wp-admin/edit.php?post_type=page")
    print("=" * 50)

if __name__ == "__main__":
    main()
