#!/usr/bin/env python3
"""
thermo-check.de — Landing Page Import Script v2.5
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

Idempotenz-Logik (v2.5):
  Eindeutige Identifikation über tc_id + tc_variant.
  tc_id kommt aus dem JSON (z.B. "K1_0001").
  tc_variant wird vom Script gesetzt: "extern" oder "intern".
  Kein Slug-Lookup, kein Parent-Lookup — deterministisch und duplikatfrei.

v2.5 Änderungen:
  - Idempotenz über tc_id + tc_variant statt slug + parent
  - tc_id ist Pflichtfeld im JSON
  - tc_variant wird automatisch gesetzt, steht nicht im JSON
  - Beide Felder werden als ACF-Felder geschrieben
  - Slug wird nicht mehr zur Identifikation verwendet
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
REQUIRED_FIELDS_EBENE1 = ["title", "slug", "zielgruppe", "tc_id", "vertiefung", "mangeldefinition", "cta_text", "excerpt"]
REQUIRED_FIELDS_EBENE2 = ["title", "slug", "zielgruppe", "tc_id", "content", "excerpt"]

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

    if "parent" in data:
        log("⚠", "JSON enthält 'parent'-Feld — wird ignoriert.")

    zielgruppe = data.get("zielgruppe", "")
    if zielgruppe not in ["K", "P"]:
        errors.append(f"zielgruppe muss 'K' oder 'P' sein, nicht '{zielgruppe}'")

    slug = data.get("slug", "")
    if "/" in slug or "\\" in slug:
        errors.append(f"slug enthält Slash: '{slug}'")
    if re.search(r"[^a-z0-9\-äöü]", slug):
        errors.append(f"slug enthält unerlaubte Zeichen: '{slug}'")

    status = data.get("status", "draft")
    if status not in ["draft", "publish"]:
        errors.append(f"status muss 'draft' oder 'publish' sein, nicht '{status}'")

    # tc_id Format prüfen: nur Kleinbuchstaben, Ziffern, Unterstriche, Bindestriche
    tc_id = data.get("tc_id", "")
    if tc_id and re.search(r"[^a-z0-9A-Z_\-]", tc_id):
        errors.append(f"tc_id enthält unerlaubte Zeichen: '{tc_id}'")

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
    names = []
    names.append("P" if zielgruppe == "P" else "K")
    names.append("Ebene 1" if ebene == "1" else "Ebene 2")
    return get_category_ids(names)

# ============================================================
# IDEMPOTENZ-LOOKUP über tc_id + tc_variant
# ============================================================

def find_page_by_tc_id(tc_id, tc_variant):
    """
    Sucht eine Seite anhand von tc_id + tc_variant.
    Kein Slug-Lookup, kein Parent-Lookup.
    Gibt die WordPress-Seiten-ID zurück oder None.
    """
    url = f"{WP_URL}/wp-json/wp/v2/pages"
    try:
        # Alle Seiten mit dieser tc_id laden (ACF-Feld)
        r = requests.get(url, auth=auth(), params={
            "meta_key":   "tc_id",
            "meta_value": tc_id,
            "per_page":   100,
            "status":     "any"
        }, timeout=15)

        if r.status_code == 200:
            pages = r.json()
            for page in pages:
                # tc_variant aus ACF-Feldern prüfen
                acf = page.get("acf", {})
                if acf.get("tc_variant") == tc_variant:
                    return page["id"]
    except Exception as e:
        log("✗", f"Lookup-Fehler: {e}")
    return None

# ============================================================
# CONTENT AUFBAU EBENE 1
# ============================================================

def build_ebene1_content(data):
    v = data.get("vertiefung", "").strip()
    m = data.get("mangeldefinition", "").strip()
    c = data.get("cta_text", "").strip()
    parts = [f"<p>{x}</p>" for x in [v, m, c] if x]
    return "\n".join(parts)

# ============================================================
# SEITE ANLEGEN / AKTUALISIEREN
# ============================================================

def push_page(data, parent_id, tc_variant, canonical_url=None, dry_run=False):
    """
    Legt eine WordPress-Seite an oder aktualisiert sie.
    Identifikation über tc_id + tc_variant — deterministisch, duplikatfrei.
    """
    title   = data.get("title", "")
    slug    = data.get("slug", "")
    status  = data.get("status", "draft")
    ebene   = data.get("ebene", "2")
    tc_id   = data.get("tc_id", "")

    # Content aufbauen
    if ebene == "1":
        raw_content = build_ebene1_content(data)
    else:
        raw_content = data.get("content", "")

    clean_content = strip_cta_links(raw_content)

    # FAQ-Schema
    faq_items  = data.get("faq", [])
    faq_schema = build_faq_schema(faq_items) if faq_items else ""

    if dry_run:
        log("→", f"[DRY RUN] {tc_variant.upper()} — {title[:60]}")
        log(" ", f"tc_id: {tc_id} | Slug: {slug} | Parent: {parent_id}")
        if canonical_url:
            log(" ", f"Canonical: {canonical_url}")
        return "dry-run"

    cat_ids = get_category_ids_for_page(data.get("zielgruppe", "K"), ebene)

    # RankMath via meta_input
    meta = {
        "rank_math_title":         data.get("meta", {}).get("rank_math_title", ""),
        "rank_math_description":   data.get("meta", {}).get("rank_math_description", ""),
        "rank_math_focus_keyword": data.get("meta", {}).get("rank_math_focus_keyword", ""),
        "faq_schema":              faq_schema,
    }
    if canonical_url:
        meta["rank_math_canonical_url"] = canonical_url

    # ACF-Felder — tc_id und tc_variant immer, E1-Felder nur bei Ebene 1
    acf_fields = {
        "tc_id":      tc_id,
        "tc_variant": tc_variant,
    }
    if ebene == "1":
        acf_fields["tc_vertiefung"]       = data.get("vertiefung", "")
        acf_fields["tc_mangeldefinition"] = data.get("mangeldefinition", "")
        acf_fields["tc_cta_text"]         = data.get("cta_text", "")

    payload = {
        "title":      title,
        "slug":       slug,
        "status":     status,
        "parent":     parent_id,
        "excerpt":    data.get("excerpt", ""),
        "content":    clean_content,
        "categories": cat_ids,
        "meta_input": meta,
        "acf":        acf_fields,
    }

    # Lookup über tc_id + tc_variant
    existing_id = find_page_by_tc_id(tc_id, tc_variant)

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
# DUAL IMPORT
# ============================================================

def dual_import(data, dry_run=False):
    """
    Dual Import — Reihenfolge ist zwingend:
    1. Extern anlegen (17xx) → externe URL zurückbekommen
    2. Intern anlegen (13xx) → Canonical auf externe URL setzen
    Identifikation: tc_id + tc_variant (extern/intern)
    """
    zielgruppe = data.get("zielgruppe", "K")
    slug       = data.get("slug", "")
    tc_id      = data.get("tc_id", "")
    title      = data.get("title", "")[:60]
    ebene      = data.get("ebene", "nicht gesetzt")

    if zielgruppe == "P":
        parent_extern  = PARENT_P_EXTERN
        parent_intern  = PARENT_P_INTERN
        canonical_base = BASE_URL_P_EXTERN
    else:
        parent_extern  = PARENT_K_EXTERN
        parent_intern  = PARENT_K_INTERN
        canonical_base = BASE_URL_K_EXTERN

    canonical_url = f"{canonical_base}/{slug}/"

    log_section(f"{title}")
    print(f"  tc_id: {tc_id} | Slug: {slug} | Zielgruppe: {zielgruppe} | Ebene: {ebene}")

    # Schritt 1 — Extern
    print(f"\n  [1/2] Extern → Parent {parent_extern} | tc_variant: extern")
    extern_id = push_page(data, parent_extern, tc_variant="extern",
                          canonical_url=None, dry_run=dry_run)

    if not extern_id and not dry_run:
        log("✗", "Extern fehlgeschlagen — Intern wird übersprungen")
        return False

    # Schritt 2 — Intern
    print(f"\n  [2/2] Intern → Parent {parent_intern} | tc_variant: intern | Canonical: {canonical_url}")
    intern_id = push_page(data, parent_intern, tc_variant="intern",
                          canonical_url=canonical_url, dry_run=dry_run)

    if not intern_id and not dry_run:
        log("⚠", "Intern fehlgeschlagen — Extern wurde angelegt, Canonical fehlt noch")
        return False

    return True

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="thermo-check.de Landing Page Dual Import v2.5")
    parser.add_argument("files", nargs="*")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 50)
    print("  thermo-check.de — Landing Page Dual Import v2.5")
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
