# tool-price-finder

A small Streamlit app to look up public retail prices (PVP) of tools and accessories.

Type a model code or a few words of the description, and the app shows the matching items with their price. Every word must match, in any order, so `taladro percutor 18V` finds "Taladro percutor BL 18V LXT…".

It searches three supplier price lists, one per tab:

| Tab | File |
| --- | --- |
| Makita · Máquinas | `clean_data/makita_tools_2026.xlsx` |
| Makita · Accesorios | `clean_data/makita_accesorios_26_27.xlsx` |
| CV Tools · Todo | `clean_data/cv_tools_2026_clean.xlsx` |

## Run it

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Project structure

```
app/
├── app.py     # Price list settings and the Streamlit interface
└── data.py    # Loading the Excel files and searching them
clean_data/    # Price lists in Excel
assets/        # Banner image
.streamlit/    # Theme (colors and fonts)
tests/         # Tests
```

## Update a price list

1. Put the new Excel file in `clean_data/`.
2. In `app/app.py`, edit its entry in `PRICE_LISTS`: the file name, the header row, and which Excel columns hold the model, description and price.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```
