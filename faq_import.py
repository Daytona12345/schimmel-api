import os
import requests

# ==========================================
# CONFIG
# ==========================================
WP_URL = "https://test.thermo-check.de"
API_POST = f"{WP_URL}/wp-json/wp/v2/faq_item"
TOKEN_URL = f"{WP_URL}/wp-json/jwt-auth/v1/token"

WP_USER = os.getenv("WP_USER")
WP_APP_PASS = os.getenv("WP_APP_PASS")

# ==========================================
# CHECK ENV
# ==========================================
print("==================================================")
print("thermo-check.de — FAQ Import")
print("==================================================")

if not WP_USER or not WP_APP_PASS:
    print("✗ WP_USER und WP_APP_PASS fehlen.")
    exit(1)

# ==========================================
# STEP 1: TOKEN HOLEN
# ==========================================
print("🔐 Hole JWT Token...")

token_res = requests.post(TOKEN_URL, json={
    "username": WP_USER,
    "password": WP_APP_PASS
})

if token_res.status_code != 200:
    print("✗ Token Fehler:", token_res.text)
    exit(1)

token = token_res.json().get("token")

if not token:
    print("✗ Kein Token erhalten")
    exit(1)

print("✔ Token OK")

# ==========================================
# STEP 2: FAQ DATEN (TEST)
# ==========================================
faq_data = {
    "title": "Automatischer FAQ Test",
    "status": "publish",
    "acf": {
        "faq_id": "faq_999",
        "faq_zielgruppe": "test",
        "faq_question": "Funktioniert der Import jetzt?",
        "faq_answer": "Ja – jetzt läuft alles über JWT 🚀",
        "faq_snippet": "Test erfolgreich"
    }
}

# ==========================================
# STEP 3: POSTEN
# ==========================================
print("📤 Sende FAQ...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

res = requests.post(API_POST, json=faq_data, headers=headers)

if res.status_code in [200, 201]:
    print("✔ FAQ erfolgreich erstellt!")
else:
    print("✗ Fehler beim Erstellen:", res.status_code)
    print(res.text)
    exit(1)
