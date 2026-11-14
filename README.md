# OLA Ride Insights - Mobility Intelligence

Final internship project: SQL, Python EDA, Power BI package and a Streamlit app on OLA's July 2024 booking data.

## Run
```
pip install -r requirements.txt
python src/preprocessing.py          # builds data/processed/ (also auto-runs on first app start)
python sql/validate_sql.py           # SQL vs pandas check (SQLite)
streamlit run app.py
```
## Layout
`app.py` entry point | `src/` modules | `sql/` six MySQL 8 files + validator | `notebooks/` EDA | `powerbi/` DAX, theme, guide | `documentation/` report, insights, dictionary, methodology, QA.

## Data facts (verified)
Only sheet `July` is raw (103,024 rows, 1-31 Jul 2024). `Sheet1` (pivot) and `Sheet2` (icon URLs) are not raw. See `documentation/Data_Dictionary.md`.

## Status
See `documentation/QA_Checklist.md` for what was tested and what was not (Streamlit UI and MySQL were not run in the build sandbox; the `.pbix` is not included).
