from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

from data import load_price_list, search_products


# ---------- Configuration: one entry per price list ----------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "clean_data"
BANNER_FILE = BASE_DIR / "assets" / "banner.jpg"


@dataclass(frozen=True)
class PriceList:
    tab_name: str
    path: Path
    header_row: int
    columns: dict[str, str]  # Excel column name -> standard name
    price_label: str  # Price column header shown in the table
    placeholder: str
    key: str


PRICE_LISTS = [
    PriceList(
        tab_name="MAKITA · Máquinas (oct-2026)",
        path=DATA_DIR / "makita_tools_2026.xlsx",
        header_row=0,
        columns={"Modelo": "Modelo", "Descripción": "Descripción", "PVP-2026": "PVP"},
        price_label="PVP-2026",
        placeholder="Ejemplo: DHP492, GA9020, lijadora, aspirador",
        key="herramientas_search",
    ),
    PriceList(
        tab_name="MAKITA · Accesorios (ago-2026)",
        path=DATA_DIR / "makita_accesorios_26_27.xlsx",
        header_row=1,
        columns={"CODIGO": "Modelo", "DESCRIPCION": "Descripción", "PVP": "PVP"},
        price_label="PVP-VIGENTE",
        placeholder="Ejemplo: broca, disco, batería, cargador",
        key="accesorios_search",
    ),
    PriceList(
        tab_name="CV TOOLS · Todo (ene-2026)",
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
        "Buscar",
        placeholder=placeholder,
        key=key,
        icon=":material/search:",
        label_visibility="collapsed",
    )

    result = search_products(df, query)

    if query:
        if result.empty:
            st.warning("No se ha encontrado nada")
        else:
            st.caption(f"**{len(result)}** resultado(s)")

            st.dataframe(
                result[["Modelo", "Descripción", "PVP"]],
                hide_index=True,
                width="stretch",
                column_config={
                    "PVP": st.column_config.NumberColumn(
                        price_label,
                        format="€ %.2f",
                    )
                },
            )
    else:
        st.caption("Escriba modelo, nombre o descripción")


st.set_page_config(
    page_title="Buscador de precios",
    layout="centered",
)

# Colors and fonts live in .streamlit/config.toml
st.image(BANNER_FILE, width="stretch")
st.title("BUSCADOR DE PRECIOS", text_alignment="center")
st.caption("Solo PVP", text_alignment="center")

tabs = st.tabs([price_list.tab_name for price_list in PRICE_LISTS])

for tab, price_list in zip(tabs, PRICE_LISTS):
    with tab:
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
