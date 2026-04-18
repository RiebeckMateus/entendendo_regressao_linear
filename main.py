import streamlit as st
import pandas as pd
import requests

# =========================
# CONFIG
# =========================
URL = 'https://testezin-a804e-default-rtdb.firebaseio.com/doramas/.json'
PAGE_SIZE = 10

st.set_page_config(layout='centered')

# =========================
# STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = 0

if "selected_item" not in st.session_state:
    st.session_state.selected_item = None

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
# FILTRO - LANGUAGE
# =========================
linguagens = sorted(df["language"].dropna().unique())

linguagem_selecionada = st.selectbox(
    "Filtrar por idioma",
    options=["Todos"] + linguagens
)

# =========================
# BUSCA
# =========================
busca = st.text_input("Buscar por nome")

# =========================
# CONTROLE DE ESTADO DOS FILTROS
# =========================
if "last_busca" not in st.session_state:
    st.session_state.last_busca = ""

if "last_language" not in st.session_state:
    st.session_state.last_language = "Todos"

# =========================
# APLICA FILTROS
# =========================
if busca:
    df = df[df["title"].str.contains(busca, case=False, na=False)]

if linguagem_selecionada != "Todos":
    df = df[df['language'] == linguagem_selecionada]

# =========================
# RESET DE PÁGINA (CORRETO)
# =========================
filtro_alterado = (
    busca != st.session_state.last_busca
    or linguagem_selecionada != st.session_state.last_language
)

if filtro_alterado:
    st.session_state.page = 0

st.session_state.last_busca = busca
st.session_state.last_language = linguagem_selecionada

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
@st.dialog("Detalhes", width='medium')
def abrir_dialog(item):
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(item.get("cover_url"))

    with col2:
        st.subheader(item.get("title"))
        st.caption(f"Idioma: {item.get('language')}")
        st.write(item.get("description"))

        st.link_button("Assistir", item.get("bunny_url"))

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
                <img src="{imagem}" style="
                    width:100%;
                    aspect-ratio:2/3;
                    object-fit:cover;
                    border-radius:8px;
                ">
            </a>
            <h4>{titulo}</h4>
            <p style="font-size:12px;">{descricao}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # botão separado (fora do HTML)
    if st.button("Ver detalhes", key=item.get("slug")):
        abrir_dialog(item.to_dict() if hasattr(item, "to_dict") else item)

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
    if st.button("⬅️ Primeira página") and st.session_state.page > 0:
        st.session_state.page = 0
        st.rerun()

with col2:
    st.write(f"Página {st.session_state.page + 1} de {total_paginas}")

with col3:
    if st.button("Próxima ➡️") and st.session_state.page < total_paginas - 1:
        st.session_state.page += 1
        st.rerun()
    if st.button("última ➡️") and st.session_state.page < total_paginas - 1:
        st.session_state.page = total_paginas
        st.rerun()