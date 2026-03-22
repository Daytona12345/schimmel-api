#!/usr/bin/env python3
"""
thermo-check.de — Landing Page Import Script
=============================================
Importiert Landing Pages als WordPress Pages via REST API.
Parent-Seiten: K=1392, P=1394

Render Environment Variables:
  WP_URL      = https://test.thermo-check.de
  WP_USER     = wordpress-benutzername
  WP_APP_PASS = application-password

Verwendung:
  python lp_import.py              # alle JSONs im /faq_content Ordner
  python lp_import.py datei.json   # einzelne Datei
  python lp_import.py --dry-run    # test ohne request
"""

import json
import os
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

PARENT_K = 1392  # schimmel-wohnung-test
PARENT_P = 1394  # schimmel-risiko-rechner

CONTENT_DIR = Path(__file__).parent / "faq_content"

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
            print(f"✓ Verbunden als: {data.get('name', 'Unbekannt')}")
            return True
        else:
            print(f"✗ Auth-Fehler: {r.status_code}")
            print(f"  Antwort: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ Verbindungsfehler: {e}")
        return False

# ============================================================
# KATEGORIEN
# ============================================================

def get_category_ids(names):
    url = f"{WP_URL}/wp-json/wp/v2/categories"
    try:
        r = requests.get(url, auth=auth(),
                        params={"per_page": 100}, timeout=10)
        if r.status_code == 200:
            all_cats = r.json()
            id_map = {c["name"].lower(): c["id"] for c in all_cats}
            ids = []
            for name in names:
                cat_id = id_map.get(name.lower())
                if cat_id:
                    ids.append(cat_id)
                else:
                    print(f"  ⚠ Kategorie nicht gefunden: {name}")
            return ids
    except Exception as e:
        print(f"  ✗ Kategorie-Lookup Fehler: {e}")
    return []

# ============================================================
# IMPORT
# ============================================================

def get_existing_page(slug):
    url = f"{WP_URL}/wp-json/wp/v2/pages"
    try:
        r = requests.get(url, auth=auth(),
                        params={"slug": slug, "status": "any"}, timeout=10)
        if r.status_code == 200:
            pages = r.json()
            if pages:
                return pages[0]["id"]
    except Exception:
        pass
    return None

def import_page(data, dry_run=False):
    title      = data.get("title", "")
    slug       = data.get("slug", "")
    zielgruppe = data.get("zielgruppe", "K")
    parent     = PARENT_K if zielgruppe == "K" else PARENT_P

    print(f"\n→ {title[:60]}")
    print(f"  Slug: /{slug}/  |  Zielgruppe: {zielgruppe}  |  Parent: {parent}")

    if dry_run:
        print("  [DRY RUN] Würde importiert — kein echter Request")
        return True

    cat_names = data.get("categories", [])
    cat_ids   = get_category_ids(cat_names) if cat_names else []

    payload = {
        "title":      title,
        "slug":       slug,
        "status":     data.get("status", "draft"),
        "parent":     parent,
        "excerpt":    data.get("excerpt", ""),
        "content":    data.get("content", ""),
        "categories": cat_ids,
        "meta": {
            "rank_math_title":         data.get("meta", {}).get("rank_math_title", ""),
            "rank_math_description":   data.get("meta", {}).get("rank_math_description", ""),
            "rank_math_focus_keyword": data.get("meta", {}).get("rank_math_focus_keyword", ""),
            "faq_schema":              data.get("meta", {}).get("faq_schema", ""),
        }
    }

    existing_id = get_existing_page(slug)

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
            print(f"  ✓ {action}: ID {page['id']} — {WP_URL}/?page_id={page['id']}")
            return True
        else:
            print(f"  ✗ Fehler {r.status_code}: {r.text[:300]}")
            return False

    except requests.exceptions.Timeout:
        print("  ✗ Timeout — nochmal versuchen")
        return False
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        return False

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="thermo-check.de Landing Page Import")
    parser.add_argument("files", nargs="*")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 50)
    print("thermo-check.de — Landing Page Import")
    print("=" * 50)

    if not args.dry_run:
        if not WP_USER or not WP_APP_PASS:
            print("✗ WP_USER und WP_APP_PASS fehlen.")
            sys.exit(1)
        if not test_connection():
            sys.exit(1)
    else:
        print("[DRY RUN — keine echten Requests]")

    if args.files:
        files = [Path(f) for f in args.files]
    else:
        if not CONTENT_DIR.exists():
            print(f"✗ Ordner nicht gefunden: {CONTENT_DIR}")
            sys.exit(1)
        files = sorted(CONTENT_DIR.glob("*.json"))
        if not files:
            print(f"✗ Keine JSON-Dateien in {CONTENT_DIR}")
            sys.exit(1)

    print(f"\n{len(files)} Datei(en) gefunden\n")

    success, errors = 0, 0
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"\n✗ JSON-Fehler in {filepath.name}: {e}")
            errors += 1
            continue

        if import_page(data, dry_run=args.dry_run):
            success += 1
        else:
            errors += 1

    print("\n" + "=" * 50)
    print(f"Fertig: {success} erfolgreich, {errors} Fehler")
    if not args.dry_run and success > 0:
        print(f"→ Drafts prüfen: {WP_URL}/wp-admin/edit.php?post_type=page")
    print("=" * 50)

if __name__ == "__main__":
    main()
