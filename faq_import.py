#!/usr/bin/env python3
"""
thermo-check.de — FAQ Import Script
====================================
Importiert faq_item Eintraege via WordPress REST API.
Credentials kommen aus Render Environment Variables — kein Passwort im Code.

Render Environment Variables (einmalig setzen):
  WP_URL      = https://test.thermo-check.de
  WP_USER     = dein-wordpress-benutzername
  WP_APP_PASS = xxxx xxxx xxxx xxxx xxxx xxxx

Verwendung:
  python faq_import.py              # importiert alle JSONs im /faq_content Ordner
  python faq_import.py frage1.json  # einzelne Datei
  python faq_import.py --dry-run    # Test ohne echten Request
"""

import json
import os
import sys
import argparse
import requests
from pathlib import Path
from base64 import b64encode

# ============================================================
# KONFIGURATION — nur aus Umgebungsvariablen, kein Hardcoding
# ============================================================

WP_URL      = os.getenv("WP_URL",      "https://test.thermo-check.de")
WP_USER     = os.getenv("WP_USER",     "")
WP_APP_PASS = os.getenv("WP_APP_PASS", "")

CONTENT_DIR = Path(__file__).parent / "faq_content"

# ============================================================
# AUTH
# ============================================================

def get_auth_header():
    credentials = f"{WP_USER}:{WP_APP_PASS}"
    token = b64encode(credentials.encode()).decode("utf-8")
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

def test_connection():
    url = f"{WP_URL}/wp-json/wp/v2/users/me"
    try:
        r = requests.get(url, headers=get_auth_header(), timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"✓ Verbunden als: {data.get('name', 'Unbekannt')}")
            return True
        else:
            print(f"✗ Auth-Fehler: {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Verbindungsfehler: {e}")
        return False

# ============================================================
# IMPORT
# ============================================================

def get_existing(slug):
    url = f"{WP_URL}/wp-json/wp/v2/faq_item"
    try:
        r = requests.get(url, headers=get_auth_header(),
                        params={"slug": slug, "status": "any"}, timeout=10)
        if r.status_code == 200:
            items = r.json()
            if items:
                return items[0]["id"]
    except Exception:
        pass
    return None

def import_faq(data, dry_run=False):
    slug = data.get("slug", data["acf"]["faq_id"])
    question = data["acf"].get("faq_question", "")

    print(f"\n→ {question[:60]}...")
    print(f"  ID: {data['acf'].get('faq_id')}  |  Zielgruppe: {data['acf'].get('faq_zielgruppe')}")

    if dry_run:
        print("  [DRY RUN] Würde importiert — kein echter Request")
        return True

    payload = {
        "title":  question,
        "slug":   slug,
        "status": data.get("status", "draft"),
        "acf": {
            "faq_id":          data["acf"].get("faq_id", ""),
            "faq_zielgruppe":  data["acf"].get("faq_zielgruppe", ""),
            "faq_question":    data["acf"].get("faq_question", ""),
            "faq_answer":      data["acf"].get("faq_answer", ""),
            "faq_snippet":     data["acf"].get("faq_snippet", ""),
        }
    }

    existing_id = get_existing(slug)

    try:
        if existing_id:
            url = f"{WP_URL}/wp-json/wp/v2/faq_item/{existing_id}"
            r = requests.post(url, headers=get_auth_header(),
                            json=payload, timeout=30)
            action = "Aktualisiert"
        else:
            url = f"{WP_URL}/wp-json/wp/v2/faq_item"
            r = requests.post(url, headers=get_auth_header(),
                            json=payload, timeout=30)
            action = "Angelegt"

        if r.status_code in [200, 201]:
            item = r.json()
            print(f"  ✓ {action}: ID {item['id']}")
            return True
        else:
            print(f"  ✗ Fehler {r.status_code}: {r.text[:200]}")
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
    parser = argparse.ArgumentParser(description="thermo-check.de FAQ Import")
    parser.add_argument("files", nargs="*", help="Einzelne JSON-Datei(en)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 50)
    print("thermo-check.de — FAQ Import")
    print("=" * 50)

    if not args.dry_run:
        if not WP_USER or not WP_APP_PASS:
            print("✗ WP_USER und WP_APP_PASS fehlen.")
            print("  In Render unter Environment Variables setzen.")
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

        if import_faq(data, dry_run=args.dry_run):
            success += 1
        else:
            errors += 1

    print("\n" + "=" * 50)
    print(f"Fertig: {success} erfolgreich, {errors} Fehler")
    print("=" * 50)

if __name__ == "__main__":
    main()
