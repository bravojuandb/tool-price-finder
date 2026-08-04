from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent

HERRAMIENTAS_MAKITA_FILE = BASE_DIR / "clean_data" / "makita_offer_2026.xlsx"
ACCESORIOS_MAKITA_FILE = BASE_DIR / "clean_data" / "makita_accesorios.xlsx"
ARTICULOS_CV_TOOLS_FILE = BASE_DIR / "clean_data" / "cv_tools_2026_clean.xlsx"


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)

    # Clean possible hidden spaces in column names
    df.columns = df.columns.str.strip()

    # Normalize searchable text
    df["Modelo"] = df["Modelo"].astype(str).str.upper().str.strip()
    df["Descripción"] = df["Descripción"].astype(str).str.strip()

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


def render_search(
    df: pd.DataFrame,
    placeholder: str,
    key: str,
    price_col: str,
) -> None:
    query = st.text_input(
        "Escriba aquí:",
        placeholder=placeholder,
        key=key,
    )

    result = search_products(df, query)

    if query:
        if result.empty:
            st.warning("No se ha encontrado nada")
        else:
            st.success(f"{len(result)} resultado(s)")

            st.dataframe(
                result[["Modelo", "Descripción", price_col]],
                hide_index=True,
                use_container_width=True,
                column_config={
                    price_col: st.column_config.NumberColumn(
                        price_col,
                        format="€ %.2f",
                    )
                },
            )
    else:
        st.info("Escriba modelo, nombre o descripción")


st.set_page_config(
    page_title="Buscador de precios Makita y CV Tools",
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
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h1 style="text-align: center; margin-bottom: 0;">
        BUSCADOR DE PRECIOS
    </h1>
    <p style="text-align: center; font-size: 18px; color: gray;">
        · Sólo PVPs 2026 ·
    </p>
    """,
    unsafe_allow_html=True,
)

makita_herr_df = load_data(HERRAMIENTAS_MAKITA_FILE)
makita_acc_df = load_data(ACCESORIOS_MAKITA_FILE)
cv_tools_df = load_data(ARTICULOS_CV_TOOLS_FILE)

tab_1, tab_2, tab_3 = st.tabs(
    ["MAKITA·Máquinas", "MAKITA·Accesorios", "CV TOOLS·Todo"]
)

with tab_1:
    st.subheader("MAKITA Máquinas")
    render_search(
        makita_herr_df,
        placeholder="Ejemplo: DHP492, GA9020, lijadora, aspirador",
        key="herramientas_search",
        price_col="PVP-2026",
    )

with tab_2:
    st.subheader("MAKITA Accesorios")
    render_search(
        makita_acc_df,
        placeholder="Ejemplo: broca, disco, batería, cargador",
        key="accesorios_search",
        price_col="PVP-VIGENTE",
    )

with tab_3:
    st.subheader("CV TOOLS Todo")
    render_search(
        cv_tools_df,
        placeholder="Ejemplo: señal, cono, cartel, 0808A",
        key="cv_tools_search",
        price_col="PVP",
    )