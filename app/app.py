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

st.set_page_config(
    page_title="Buscador de precios Makita",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #f7f7f5;
    }

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #666;
        margin-top: 4px;
        margin-bottom: 28px;
    }

    .creator-box {
        text-align: center;
        background: white;
        padding: 14px 18px;
        border-radius: 14px;
        border: 1px solid #e5e5e5;
        max-width: 650px;
        margin: 0 auto 28px auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .creator-box strong {
        color: #111;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h1 style="text-align: center; margin-bottom: 0;">
        Herramientas Makita
    </h1>
    <p style="text-align: center; font-size: 18px; color: gray;">
        Buscador de precios · PVPs 2026
    </p>
    """,
    unsafe_allow_html=True,
)


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
