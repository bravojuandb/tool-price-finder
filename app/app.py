from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

from data import load_price_list, search_products


# ---------- Configuration: one entry per price list ----------

DATA_DIR = Path(__file__).resolve().parent.parent / "clean_data"


@dataclass(frozen=True)
class PriceList:
    tab_name: str
    title: str
    path: Path
    header_row: int
    columns: dict[str, str]  # Excel column name -> standard name
    price_label: str  # Price column header shown in the table
    placeholder: str
    key: str


PRICE_LISTS = [
    PriceList(
        tab_name="MAKITA · Máquinas",
        title="MAKITA Máquinas",
        path=DATA_DIR / "makita_tools_2026.xlsx",
        header_row=0,
        columns={"Modelo": "Modelo", "Descripción": "Descripción", "PVP-2026": "PVP"},
        price_label="PVP-2026",
        placeholder="Ejemplo: DHP492, GA9020, lijadora, aspirador",
        key="herramientas_search",
    ),
    PriceList(
        tab_name="MAKITA · Accesorios",
        title="MAKITA Accesorios",
        path=DATA_DIR / "makita_accesorios_26_27.xlsx",
        header_row=1,
        columns={"CODIGO": "Modelo", "DESCRIPCION": "Descripción", "PVP": "PVP"},
        price_label="PVP-VIGENTE",
        placeholder="Ejemplo: broca, disco, batería, cargador",
        key="accesorios_search",
    ),
    PriceList(
        tab_name="CV TOOLS · Todo",
        title="CV TOOLS Todo",
        path=DATA_DIR / "cv_tools_2026_clean.xlsx",
        header_row=0,
        columns={"Modelo": "Modelo", "Descripción": "Descripción", "PVP": "PVP"},
        price_label="PVP",
        placeholder="Ejemplo: señal, cono, cartel, 0808A",
        key="cv_tools_search",
    ),
]


# ---------- Interface ----------

# Caching belongs to the interface, so data.py stays free of Streamlit
load_price_list_cached = st.cache_data(load_price_list)


def render_search(
    df: pd.DataFrame,
    placeholder: str,
    key: str,
    price_label: str,
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
                result[["Modelo", "Descripción", "PVP"]],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "PVP": st.column_config.NumberColumn(
                        price_label,
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

tabs = st.tabs([price_list.tab_name for price_list in PRICE_LISTS])

for tab, price_list in zip(tabs, PRICE_LISTS):
    with tab:
        st.subheader(price_list.title)
        df = load_price_list_cached(
            price_list.path,
            price_list.header_row,
            price_list.columns,
        )
        render_search(
            df,
            placeholder=price_list.placeholder,
            key=price_list.key,
            price_label=price_list.price_label,
        )
