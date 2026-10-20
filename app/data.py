from pathlib import Path

import pandas as pd


def load_price_list(
    path: Path,
    header_row: int,
    columns: dict[str, str],
) -> pd.DataFrame:
    """Read an Excel price list and return it with columns Modelo, Descripción, PVP.

    `columns` maps the column names in the Excel file to the standard names.
    """
    df = pd.read_excel(path, header=header_row)

    # Clean possible hidden spaces in column names
    df.columns = df.columns.str.strip()

    # Keep only the needed columns, renamed to the same names for every price list
    df = df[list(columns)].rename(columns=columns)

    # Normalize searchable text
    df["Modelo"] = df["Modelo"].astype(str).str.upper().str.strip()
    df["Descripción"] = df["Descripción"].astype(str).str.strip()
    df["PVP"] = pd.to_numeric(df["PVP"], errors="coerce")

    return df


def search_products(df: pd.DataFrame, query: str) -> pd.DataFrame:
    query = query.upper().strip()

    if not query:
        return pd.DataFrame()

    exact = df[df["Modelo"] == query]

    if not exact.empty:
        return exact

    partial = df[
        df["Modelo"].str.contains(query, na=False, regex=False)
        | df["Descripción"].str.upper().str.contains(query, na=False, regex=False)
    ]

    return partial
