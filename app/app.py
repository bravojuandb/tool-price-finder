from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "clean_data" / "makita_offer_2026.xlsx"


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)

    df["Modelo"] = df["Modelo"].astype(str).str.upper().str.strip()
    df["Descripción"] = df["Descripción"].astype(str)

    return df

def search_products(df: pd.DataFrame, query: str) -> pd.DataFrame:
    query = query.upper().strip()

    if not query:
        return pd.DataFrame()

    exact = df[df["Modelo"] == query]

    if not exact.empty:
        return exact

    partial = df[
        df["Modelo"].str.contains(query, na=False)
        | df["Descripción"].str.upper().str.contains(query, na=False)
    ]

    return partial


st.set_page_config(
    page_title="Buscador de precios Makita",
    layout="wide",
)

st.title("Herramientas Makita (PVPs 2026)")

st.write("Búsqueda por modelo, nombre o descripción")

df = load_data(DATA_FILE)

query = st.text_input(
    "Escriba aquí:",
    placeholder="Ejemplo: DHP492, GA9020, lijadora, aspirador",
)

result = search_products(df, query)

if query:
    if result.empty:
        st.warning("No se ha encontrado nada")
    else:
        st.success(f"{len(result)} resultado(s)")

        st.dataframe(
            result[["Modelo", "Descripción", "PVP-2026"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "PVP-2026": st.column_config.NumberColumn(
                    "PVP-2026",
                    format="€ %.2f",
                )
            },
        )

else:
    st.info("Escriba modelo, nombre o descripción")

st.markdown(
    '<div class="footer-text">Creado por Juan D. Bravo · 2026</div>',
    unsafe_allow_html=True,
)