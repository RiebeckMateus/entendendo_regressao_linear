from firebase_admin import credentials, db
import firebase_admin
import pandas as pd
import requests

# =========================
# CONFIG
# =========================
DATABASE_URL = 'https://testezin-a804e-default-rtdb.firebaseio.com/'
CAMINHO_CREDENCIAL = 'firebase-credentials.json'
URL_API = 'https://fbngdxhkaueaolnyswgn.supabase.co/rest/v1/doramas?select=*'

api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZibmdkeGhrYXVlYW9sbnlzd2duIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM4MjQ5MTcsImV4cCI6MjA3OTQwMDkxN30.fm9MKpmmNadMpbPVekIpwyTuyW9cLO9KRyCbJIOQWSM'

HEADERS = {
    "apikey": api_key,
    "authorization": f"Bearer {api_key}",
    "accept": "application/json"
}

# =========================
# INIT FIREBASE (TRAVA)
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(CAMINHO_CREDENCIAL)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DATABASE_URL
    })

ref = db.reference('doramas')

# =========================
# EXTRAÇÃO (API)
# =========================
response = requests.get(URL_API, headers=HEADERS)
dados = response.json()

df = pd.DataFrame(dados)[['slug', 'title', 'description', 'cover_url', 'language', 'bunny_url']]

# =========================
# LIMPEZA (NaN -> None)
# =========================
df = df.astype(object).where(pd.notnull(df), None)

# =========================
# TRANSFORMAÇÃO
# =========================
dados = df.to_dict(orient='records')

# =========================
# RESET BASE
# =========================
ref.delete()

# =========================
# CARGA (USANDO SLUG)
# =========================
updates = {}

for item in dados:
    slug = item.get("slug")

    if not slug:
        continue  # ignora registros sem chave

    updates[slug] = item

# sobe tudo de uma vez
ref.update(updates)

print(f"{len(updates)} registros enviados com sucesso.")