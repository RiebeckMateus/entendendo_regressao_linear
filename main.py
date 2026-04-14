import streamlit as st
import pandas as pd
import requests

# =========================
# CONFIG
# =========================
URL = 'https://testezin-a804e-default-rtdb.firebaseio.com/doramas/.json'
PAGE_SIZE = 10

# =========================
# STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = 0

# =========================
# LOAD DATA
# =========================
@st.cache_data
def carregar_dados():
    dados = requests.get(URL).json()

    if isinstance(dados, dict):
        return list(dados.values())
    elif isinstance(dados, list):
        return dados
    return []

dados = carregar_dados()
df = pd.DataFrame(dados)

# =========================
# BUSCA
# =========================
busca = st.text_input("Buscar por nome")

if busca:
    df = df[df["title"].str.contains(busca, case=False, na=False)]
    st.session_state.page = 0  # reset página ao filtrar

# =========================
# PAGINAÇÃO
# =========================
total_paginas = max(1, (len(df) - 1) // PAGE_SIZE + 1)

st.session_state.page = max(
    0,
    min(st.session_state.page, total_paginas - 1)
)

inicio = st.session_state.page * PAGE_SIZE
fim = inicio + PAGE_SIZE

df_pagina = df.iloc[inicio:fim]

# =========================
# CARDS
# =========================
def render_card(item):
    titulo = item.get("title", "Sem título")
    imagem = item.get("cover_url", "")  # ajusta conforme seu campo
    descricao = item.get("description", "")
    link = item.get("bunny_url", "#")

    if not imagem:
        imagem = "https://via.placeholder.com/300x400"

    descricao = (descricao[:100] + "...") if descricao else ""

    st.markdown(f"""
        <div style="
            border:1px solid #ddd;
            border-radius:10px;
            padding:10px;
            height:100%;
        ">
            <a href="{link}" target="_blank">
                <img src="{imagem}" style="width:100%; border-radius:8px;">
            </a>
            <h4>{titulo}</h4>
            <p style="font-size:12px;">{descricao}</p>
        </div>
    """, unsafe_allow_html=True)

# grid (2 colunas → 5 linhas = 10 cards)
cols = st.columns(2)

for i, (_, row) in enumerate(df_pagina.iterrows()):
    with cols[i % 2]:
        render_card(row)

# =========================
# CONTROLES
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Anterior") and st.session_state.page > 0:
        st.session_state.page -= 1
        st.rerun()

with col2:
    st.write(f"Página {st.session_state.page + 1} de {total_paginas}")

with col3:
    if st.button("Próxima ➡️") and st.session_state.page < total_paginas - 1:
        st.session_state.page += 1
        st.rerun()