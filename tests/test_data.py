import pandas as pd
import pytest

from data import load_price_list, search_products


@pytest.fixture
def products() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Modelo": ["DHP482", "DHP482Z", "GA9020", "HW41165", "VC008GZ09"],
            "Descripción": [
                "Taladro percutor 18V",
                "Taladro percutor 18V sin batería",
                "Amoladora 230mm",
                "Manguera desatascadora 10mts.",
                None,
            ],
            "PVP": [199.0, 129.0, 210.0, 35.0, 498.0],
        }
    )


# ---------- search_products ----------


def test_empty_query_returns_nothing(products):
    assert search_products(products, "").empty
    assert search_products(products, "   ").empty


def test_exact_model_match_wins(products):
    result = search_products(products, "DHP482")

    assert list(result["Modelo"]) == ["DHP482"]


def test_query_ignores_case_and_spaces(products):
    result = search_products(products, "  ga9020 ")

    assert list(result["Modelo"]) == ["GA9020"]


def test_partial_match_on_model(products):
    result = search_products(products, "dhp")

    assert list(result["Modelo"]) == ["DHP482", "DHP482Z"]


def test_partial_match_on_description(products):
    result = search_products(products, "amoladora")

    assert list(result["Modelo"]) == ["GA9020"]


def test_all_words_must_match_in_any_order(products):
    result = search_products(products, "percutor taladro batería")

    assert list(result["Modelo"]) == ["DHP482Z"]


def test_words_can_match_model_and_description(products):
    result = search_products(products, "dhp sin")

    assert list(result["Modelo"]) == ["DHP482Z"]


@pytest.mark.parametrize("query", ["(", "[", "*", "+", "?"])
def test_regex_characters_do_not_break_search(products, query):
    assert search_products(products, query).empty


def test_dot_is_searched_literally(products):
    result = search_products(products, ".")

    assert list(result["Modelo"]) == ["HW41165"]


def test_no_match_returns_empty(products):
    assert search_products(products, "zzzz").empty


def test_missing_description_is_still_found_by_model(products):
    result = search_products(products, "vc008")

    assert list(result["Modelo"]) == ["VC008GZ09"]


# ---------- load_price_list ----------


def write_excel(path, rows: list[list]) -> None:
    pd.DataFrame(rows).to_excel(path, header=False, index=False)


def test_load_selects_renames_and_normalizes(tmp_path):
    path = tmp_path / "tarifa.xlsx"
    write_excel(
        path,
        [
            ["Tarifa 2026", None, None, None],
            [" CODIGO ", "DESCRIPCION", "EAN", "PVP"],
            [" dhp482 ", "  Taladro percutor  ", "8412345", "199.5"],
        ],
    )

    df = load_price_list(
        path,
        header_row=1,
        columns={"CODIGO": "Modelo", "DESCRIPCION": "Descripción", "PVP": "PVP"},
    )

    assert list(df.columns) == ["Modelo", "Descripción", "PVP"]
    assert df.loc[0, "Modelo"] == "DHP482"
    assert df.loc[0, "Descripción"] == "Taladro percutor"
    assert df.loc[0, "PVP"] == 199.5


def test_load_turns_invalid_prices_into_missing(tmp_path):
    path = tmp_path / "tarifa.xlsx"
    write_excel(path, [["Modelo", "Descripción", "PVP"], ["A1", "Algo", "consultar"]])

    df = load_price_list(
        path,
        header_row=0,
        columns={"Modelo": "Modelo", "Descripción": "Descripción", "PVP": "PVP"},
    )

    assert pd.isna(df.loc[0, "PVP"])


def test_load_fails_when_a_column_is_missing(tmp_path):
    path = tmp_path / "tarifa.xlsx"
    write_excel(path, [["Modelo", "Descripción", "PVP"], ["A1", "Algo", 10]])

    with pytest.raises(KeyError):
        load_price_list(
            path,
            header_row=0,
            columns={"REFERENCIA": "Modelo", "Descripción": "Descripción", "PVP": "PVP"},
        )
