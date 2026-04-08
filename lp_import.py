#!/usr/bin/env python3
"""
thermo-check.de — Landing Page Import Script v2.3
==================================================
Dual Import: Legt jede Landing Page automatisch in zwei Welten an.
  1. Extern (17xx) — SEO-Master, rankende Seite, mit Header/Footer
  2. Intern (13xx) — Schatten-Seite, Canonical auf Extern

Parent-IDs:
  K intern: 1392 (/schimmel-wohnung-test/)
  P intern: 1394 (/schimmel-risiko-rechner/)
  K extern: 1731 (/schimmel-ratgeber/)
  P extern: 1739 (/schimmel-profi/)

Render Environment Variables:
  WP_URL      = https://test.thermo-check.de
  WP_USER     = wordpress-benutzername
  WP_APP_PASS = application-password

Verwendung:
  python lp_import.py              # alle JSONs im /faq_content Ordner
  python lp_import.py datei.json   # einzelne Datei
  python lp_import.py --dry-run    # test ohne echte Requests

JSON-Struktur Ebene 1 (vier Felder):
  title            — Seitentitel / Frage (Standard-WP-Feld)
  vertiefung       — Druckaufbau, warum das wirklich ein Problem ist
  mangeldefinition — Die offene Frage, die den Impuls erzeugt
  cta_text         — Individualisierter Satz, der den Button einleitet

  Das Script schreibt vertiefung/mangeldefinition/cta_text als separate
  Custom Meta Fields (für Saims Template-Zonen) UND baut daraus das
  WordPress content-Feld als HTML-Fallback zusammen.

JSON-Struktur Ebene 2 (klassisch):
  content          — HTML, Antwort + Thermo-Check Integration

v2.2 Änderungen:
  - Vier-Felder-Struktur für Ebene-1-Seiten (title/vertiefung/mangeldefinition/cta_text)
  - Script baut content automatisch aus den drei Textfeldern zusammen
  - vertiefung, mangeldefinition, cta_text werden als Custom Meta Fields geschrieben
  - Ebene-2-Seiten: content-Feld wie bisher unterstützt
  - REQUIRED_FIELDS je nach ebene unterschiedlich validiert
  - parent-Feld im JSON wird ignoriert (Warnung ausgegeben)
  - Parent wird ausschließlich vom Script aus zielgruppe gesetzt
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

WP_URL      = os.getenv("WP_URL",      "https://test.thermo-check.de")
WP_USER     = os.getenv("WP_USER",     "")
WP_APP_PASS = os.getenv("WP_APP_PASS", "")

# Interne Welt (13xx) — ohne Header/Footer, Canonical auf Extern
PARENT_K_INTERN = 1392   # /schimmel-wohnung-test/
PARENT_P_INTERN = 1394   # /schimmel-risiko-rechner/

# Externe Welt (17xx) — SEO-Master, mit Header/Footer
PARENT_K_EXTERN = 1731   # /schimmel-ratgeber/
PARENT_P_EXTERN = 1739   # /schimmel-profi/

# Externe URL-Basis für Canonical-Konstruktion
BASE_URL_K_EXTERN = "https://thermo-check.de/schimmel-ratgeber"
BASE_URL_P_EXTERN = "https://thermo-check.de/schimmel-profi"

CONTENT_DIR = Path(__file__).parent / "faq_content"

# Pflichtfelder — je nach ebene unterschiedlich
REQUIRED_FIELDS_EBENE1 = ["title", "slug", "zielgruppe", "vertiefung", "mangeldefinition", "cta_text", "excerpt"]
REQUIRED_FIELDS_EBENE2 = ["title", "slug", "zielgruppe", "content", "excerpt"]

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
# JSON VALIDIERUNG
# ============================================================

def validate_json(data, filepath):
    """Prüft Pflichtfelder und Wertebereich vor dem Import."""
    errors = []

    ebene = data.get("ebene", "")
    if ebene == "1":
        required = REQUIRED_FIELDS_EBENE1
    else:
        required = REQUIRED_FIELDS_EBENE2

    for field in required:
        if not data.get(field):
            errors.append(f"Pflichtfeld fehlt oder leer: '{field}'")

    # Warnung wenn parent-Feld im JSON steht — wird ignoriert, Script setzt Parent selbst
    if "parent" in data:
        log("⚠", f"JSON enthält 'parent'-Feld — wird ignoriert. Parent wird ausschließlich aus zielgruppe + Importmodus gesetzt.")

    zielgruppe = data.get("zielgruppe", "")
    if zielgruppe not in ["K", "P"]:
        errors.append(f"zielgruppe muss 'K' oder 'P' sein, nicht '{zielgruppe}'")

    slug = data.get("slug", "")
    if "/" in slug or "\\" in slug:
        errors.append(f"slug enthält Slash — nur den reinen Slug angeben, keinen Pfad: '{slug}'")
    if re.search(r"[^a-z0-9\-äöü]", slug):
        errors.append(f"slug enthält unerlaubte Zeichen: '{slug}'")

    status = data.get("status", "draft")
    if status not in ["draft", "publish"]:
        errors.append(f"status muss 'draft' oder 'publish' sein, nicht '{status}'")

    if errors:
        log("✗", f"Validierungsfehler in {filepath.name}:")
        for e in errors:
            log("  →", e)
        return False

    return True

# ============================================================
# FAQ SCHEMA GENERATOR
# ============================================================

def build_faq_schema(faq_items):
    """
    Generiert JSON-LD FAQ-Schema aus strukturierten Daten.
    Das JSON enthält nur question/answer — das Script baut das Schema.
    Einmal hier ändern = alle Seiten aktualisiert beim nächsten Import.
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"]
                }
            }
            for item in faq_items
        ]
    }
    return f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'

# ============================================================
# CONTENT BEREINIGUNG
# ============================================================

def strip_cta_links(content):
    """Entfernt Inline-CTA-Links aus dem Content."""
    cleaned = re.sub(r'<a\s+href=["\'][^"\']*["\'][^>]*>.*?</a>', '', content, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)
    cleaned = re.sub(r'\s+</p>', '</p>', cleaned)
    return cleaned.strip()

# ============================================================
# KATEGORIEN
# ============================================================

def get_category_ids(names):
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
    except Exception as e:
        log("✗", f"Kategorie-Lookup Fehler: {e}")
    return []

def get_category_ids_for_page(zielgruppe, ebene):
    """
    Kategorien werden automatisch aus zielgruppe + ebene abgeleitet.
    JSON braucht kein categories-Feld mehr.
    K/P + Ebene 1/2 werden in WordPress-Kategorie-IDs übersetzt.
    """
    names = []
    if zielgruppe == "P":
        names.append("P")
    else:
        names.append("K")
    if ebene == "1":
        names.append("Ebene 1")
    elif ebene == "2":
        names.append("Ebene 2")
    return get_category_ids(names)
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
    except Exception as e:
        log("✗", f"Kategorie-Lookup Fehler: {e}")
    return []

# ============================================================
# SEITEN-LOOKUP (Idempotenz)
# ============================================================

def get_existing_page(slug, parent_id):
    """
    Sucht nach einer Seite mit diesem Slug unter einem bestimmten Parent.
    Verhindert Duplikate wenn intern und extern denselben Slug haben.
    """
    url = f"{WP_URL}/wp-json/wp/v2/pages"
    try:
        r = requests.get(url, auth=auth(),
                        params={"slug": slug, "status": "any", "per_page": 100}, timeout=10)
        if r.status_code == 200:
            pages = r.json()
            for page in pages:
                if page.get("parent") == parent_id:
                    return page["id"]
    except Exception:
        pass
    return None

def build_ebene1_content(data):
    """
    Baut das WordPress content-Feld aus den vier Ebene-1-Feldern zusammen.
    Reihenfolge: vertiefung → mangeldefinition → cta_text
    title ist Standard-WP-Feld, wird separat geschrieben.
    """
    v = data.get("vertiefung", "").strip()
    m = data.get("mangeldefinition", "").strip()
    c = data.get("cta_text", "").strip()
    parts = [f"<p>{x}</p>" for x in [v, m, c] if x]
    return "\n".join(parts)

# ============================================================
# SEITE ANLEGEN / AKTUALISIEREN
# ============================================================

def push_page(data, parent_id, canonical_url=None, dry_run=False):
    """
    Legt eine WordPress-Seite an oder aktualisiert sie.
    Gemeinsamer Schlüssel intern↔extern: slug (eindeutig, unveränderlich).
    """
    title  = data.get("title", "")
    slug   = data.get("slug", "")
    status = data.get("status", "draft")
    ebene  = data.get("ebene", "2")

    # Content-Logik: Ebene 1 = aus V/M/C zusammenbauen, Ebene 2 = content-Feld direkt
    if ebene == "1":
        raw_content = build_ebene1_content(data)
    else:
        raw_content = data.get("content", "")

    clean_content = strip_cta_links(raw_content)
    if raw_content != clean_content:
        log("✓", "CTA-Links aus Content entfernt")

    # FAQ-Schema generieren
    faq_items  = data.get("faq", [])
    faq_schema = build_faq_schema(faq_items) if faq_items else ""

    if dry_run:
        action = "Extern" if not canonical_url else "Intern"
        log("→", f"[DRY RUN] {action} — {title[:60]}")
        log(" ", f"Slug: {slug} | Parent: {parent_id}")
        if canonical_url:
            log(" ", f"Canonical: {canonical_url}")
        return "dry-run"

    cat_ids = get_category_ids_for_page(data.get("zielgruppe", "K"), ebene)

    meta = {
        "rank_math_title":         data.get("meta", {}).get("rank_math_title", ""),
        "rank_math_description":   data.get("meta", {}).get("rank_math_description", ""),
        "rank_math_focus_keyword": data.get("meta", {}).get("rank_math_focus_keyword", ""),
        "faq_schema":              faq_schema,
    }

    # Ebene-1-Felder als Custom Meta Fields — für Saims Template-Zonen
    if ebene == "1":
        meta["tc_vertiefung"]       = data.get("vertiefung", "")
        meta["tc_mangeldefinition"] = data.get("mangeldefinition", "")
        meta["tc_cta_text"]         = data.get("cta_text", "")

    # Canonical für interne Seite setzen
    if canonical_url:
        meta["rank_math_canonical_url"] = canonical_url

    payload = {
        "title":      title,
        "slug":       slug,
        "status":     status,
        "parent":     parent_id,
        "excerpt":    data.get("excerpt", ""),
        "content":    clean_content,
        "categories": cat_ids,
        "meta_input": meta,
    }

    existing_id = get_existing_page(slug, parent_id)

    try:
        if existing_id:
            url = f"{WP_URL}/wp-json/wp/v2/pages/{existing_id}"
            r = requests.post(url, auth=auth(), json=payload, timeout=30)
            action = "Aktualisiert"
        else:
            url = f"{WP_URL}/wp-json/wp/v2/pages"
            r = requests.post(url, auth=auth(), json=payload, timeout=30)
            action = "Angelegt"

        if r.status_code in [200, 201]:
            page = r.json()
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
# DUAL IMPORT
# ============================================================

def dual_import(data, dry_run=False):
    """
    Dual Import — Reihenfolge ist zwingend:
    1. Extern anlegen (17xx) → URL zurückbekommen
    2. Intern anlegen (13xx) → Canonical auf externe URL setzen

    Gemeinsamer Schlüssel: slug (eindeutig für beide Welten)
    """
    zielgruppe = data.get("zielgruppe", "K")
    slug       = data.get("slug", "")
    title      = data.get("title", "")[:60]

    # Parent-IDs bestimmen
    if zielgruppe == "P":
        parent_extern = PARENT_P_EXTERN
        parent_intern = PARENT_P_INTERN
        canonical_base = BASE_URL_P_EXTERN
    else:
        parent_extern = PARENT_K_EXTERN
        parent_intern = PARENT_K_INTERN
        canonical_base = BASE_URL_K_EXTERN

    canonical_url = f"{canonical_base}/{slug}/"

    ebene = data.get("ebene", "nicht gesetzt")
    log_section(f"{title}")
    print(f"  Slug: {slug} | Zielgruppe: {zielgruppe} | Ebene: {ebene}")

    # Schritt 1 — Extern (Master)
    print(f"\n  [1/2] Extern → Parent {parent_extern}")
    extern_id = push_page(data, parent_extern, canonical_url=None, dry_run=dry_run)

    if not extern_id and not dry_run:
        log("✗", "Extern fehlgeschlagen — Intern wird übersprungen (kein Canonical möglich)")
        return False

    # Schritt 2 — Intern (Schatten mit Canonical)
    print(f"\n  [2/2] Intern → Parent {parent_intern} | Canonical: {canonical_url}")
    intern_id = push_page(data, parent_intern, canonical_url=canonical_url, dry_run=dry_run)

    if not intern_id and not dry_run:
        log("⚠", "Intern fehlgeschlagen — Extern wurde angelegt, Canonical fehlt noch")
        return False

    return True

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="thermo-check.de Landing Page Dual Import v2.0")
    parser.add_argument("files", nargs="*")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 50)
    print("  thermo-check.de — Landing Page Dual Import v2.0")
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

        if dual_import(data, dry_run=args.dry_run):
            success += 1
        else:
            errors += 1

    print(f"\n{'=' * 50}")
    print(f"  Fertig: {success} erfolgreich | {errors} Fehler | {skipped} übersprungen")
    if not args.dry_run and success > 0:
        print(f"  → Drafts prüfen: {WP_URL}/wp-admin/edit.php?post_type=page")
    print("=" * 50)

if __name__ == "__main__":
    main()
