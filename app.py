import streamlit as st
import pandas as pd

# =========================
# CONFIG PAGINA
# =========================
st.set_page_config(
    page_title="Ricerca SAP ↔ K1",
    layout="wide",
    page_icon="🔎"
)

st.title("🔎 Ricerca Conti SAP ↔ K1")
st.markdown("Trova rapidamente la relazione tra conti SAP e K1")

# =========================
# CARICAMENTO DATI
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("XBRALLASA.XLSX", engine="openpyxl")

    # Pulizia colonne
    df.columns = df.columns.str.strip()

    # Conversione data
    if "Inizio validità" in df.columns:
        df["Inizio validità"] = pd.to_datetime(df["Inizio validità"], errors='coerce')

        # ✅ REGOLA: tieni SOLO la più recente per ogni Conto SAP
        df = (
            df.sort_values("Inizio validità", ascending=False)
              .drop_duplicates(subset=["Conto Sap"], keep="first")
        )

    return df

df = load_data()

# =========================
# SIDEBAR INFO
# =========================
with st.sidebar:
    st.header("ℹ️ Info")
    st.write(f"Totale conti unici: **{len(df)}**")
    st.markdown("""
    **Come usare il tool:**
    - Puoi compilare uno o più campi
    - Le ricerche sono parziali
    - È sempre mostrata la versione più recente
    """)

# =========================
# FILTRI (UI MIGLIORATA)
# =========================
st.subheader("🔧 Filtri di ricerca")

col1, col2 = st.columns([2, 1])  # SAP più grande

with col1:
    conto_sap = st.text_input("Conto SAP", placeholder="Es. 6260")

with col2:
    k1 = st.text_input("Voce K1", placeholder="Es. 00335")

col3, col4 = st.columns(2)

with col3:
    desc_sap = st.text_input("Descrizione conto SAP")

with col4:
    desc_k1 = st.text_input("Descrizione conto NCG")

# =========================
# FILTRAGGIO
# =========================
filtered_df = df.copy()

if conto_sap:
    filtered_df = filtered_df[
        filtered_df["Conto Sap"].astype(str).str.contains(conto_sap, case=False, na=False)
    ]

if desc_sap:
    filtered_df = filtered_df[
        filtered_df["Descrizione conto Sap"].astype(str).str.contains(desc_sap, case=False, na=False)
    ]

if k1:
    filtered_df = filtered_df[
        filtered_df["Voce K1"].astype(str).str.contains(k1, case=False, na=False)
    ]

if desc_k1:
    filtered_df = filtered_df[
        filtered_df["Descrizione conto NCG"].astype(str).str.contains(desc_k1, case=False, na=False)
    ]

# =========================
# ORDINAMENTO (UX MIGLIORE)
# =========================
if "Conto Sap" in filtered_df.columns:
    filtered_df = filtered_df.sort_values("Conto Sap")

# =========================
# OUTPUT
# =========================
st.subheader(f"📊 Risultati trovati: {len(filtered_df)}")

# Evidenzia colonne chiave
def highlight_cols(df):
    return df.style.set_properties(**{
        'font-weight': 'bold'
    }, subset=["Conto Sap"]) \
    .set_properties(**{
        'color': '#0b5394'
    }, subset=["Voce K1"])

if len(filtered_df) > 0:
    st.dataframe(
        highlight_cols(filtered_df),
        use_container_width=True,
        height=600
    )
else:
    st.warning("⚠️ Nessun risultato trovato")

# =========================
# DOWNLOAD
# =========================
def convert_xlsx(df):
    return df.to_excel(index=False, engine='openpyxl')

st.download_button(
    label="⬇️ Scarica risultati Excel",
    data=convert_xlsx(filtered_df),
    file_name="risultati_ricerca.xlsx"
)

# =========================
# EXTRA: VISTA PER K1
# =========================
st.markdown("---")
st.subheader("🔍 Vista per K1")

k1_sel = st.text_input("Inserisci K1 per vedere tutti i conti SAP collegati")

if k1_sel:
    df_k1 = df[df["Voce K1"].astype(str).str.contains(k1_sel, case=False, na=False)]

    st.write(f"Conti SAP collegati: {len(df_k1)}")

    st.dataframe(
        df_k1.sort_values("Conto Sap"),
        use_container_width=True
    )