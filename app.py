import streamlit as st
import pandas as pd

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="SAP ↔ K1",
    layout="wide",
    page_icon="💼"
)

# =========================
# STILE CUSTOM
# =========================
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .block-container {
        padding-top: 2rem;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #ddd;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
# 💼 Mappatura Conti SAP ↔ K1
### Ricerca veloce e dinamica
""")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("XBRALLASA.XLSX", engine="openpyxl")
    df.columns = df.columns.str.strip()

    for col in df.columns:
        df[col] = df[col].astype(str)

    if "Inizio validità" in df.columns:
        df["Inizio validità"] = pd.to_datetime(df["Inizio validità"], errors='coerce')

        df = (
            df.sort_values("Inizio validità", ascending=False)
              .drop_duplicates(subset=["Conto Sap"], keep="first")
        )
    return df

df = load_data()

# =========================
# FILTRI (CARD STYLE)
# =========================
st.markdown("## 🔎 Filtri di ricerca")

with st.container():
    col1, col2, col3, col4 = st.columns([2, 1, 2, 2])

    with col1:
        conto_sap = st.text_input("Conto SAP", placeholder="Es. 6260105001")

    with col2:
        k1 = st.text_input("K1")

    with col3:
        desc_sap = st.text_input("Descrizione SAP")

    with col4:
        desc_k1 = st.text_input("Descrizione K1")

# =========================
# FILTRAGGIO
# =========================
filtered_df = df.copy()

if conto_sap:
    filtered_df = filtered_df[
        filtered_df["Conto Sap"].str.contains(conto_sap, case=False, na=False)
    ]

if desc_sap:
    filtered_df = filtered_df[
        filtered_df["Descrizione conto Sap"].str.contains(desc_sap, case=False, na=False)
    ]

if k1:
    filtered_df = filtered_df[
        filtered_df["Voce K1"].str.contains(k1, case=False, na=False)
    ]

if desc_k1:
    filtered_df = filtered_df[
        filtered_df["Descrizione conto NCG"].str.contains(desc_k1, case=False, na=False)
    ]

# =========================
# KPI (molto più moderno)
# =========================
colA, colB = st.columns(2)

with colA:
    st.metric("Conti trovati", len(filtered_df))

with colB:
    st.metric("Totale conti unici", len(df))

# =========================
# RISULTATI
# =========================
st.markdown("## 📊 Risultati")

if len(filtered_df) > 0:
    st.dataframe(
        filtered_df.sort_values("Conto Sap"),
        use_container_width=True,
        height=550
    )
else:
    st.info("Nessun risultato trovato")

# =========================
# VISTA PER K1
# =========================
st.markdown("---")
st.markdown("## 🔁 Ricerca inversa (K1 → SAP)")

k1_sel = st.text_input("Inserisci K1")

if k1_sel:
    df_k1 = df[df["Voce K1"].str.contains(k1_sel, case=False, na=False)]

    st.write(f"Conti SAP collegati: {len(df_k1)}")

    st.dataframe(
        df_k1.sort_values("Conto Sap"),
        use_container_width=True
    )

# =========================
# DOWNLOAD
# =========================
st.markdown("---")

st.download_button(
    "⬇️ Scarica risultati",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="risultati.csv"
)
