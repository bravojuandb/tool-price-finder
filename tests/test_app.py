from streamlit.testing.v1 import AppTest


def run_app() -> AppTest:
    return AppTest.from_file("../app/app.py").run(timeout=60)


def test_app_loads_every_price_list():
    at = run_app()

    assert not at.exception
    assert len(at.tabs) == 3


def test_search_shows_results_table():
    at = run_app()

    at.text_input(key="herramientas_search").input("taladro percutor").run(timeout=60)

    assert not at.exception
    assert at.success
    assert list(at.dataframe[0].value.columns) == ["Modelo", "Descripción", "PVP"]
