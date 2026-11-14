# QA checklist (honest status)
| Item | Status |
|---|---|
| Preprocessing runs on supplied data; audit JSON written | Tested |
| KPIs, filters, AI answers, anomaly module on real data (pandas) | Tested |
| SQL 02-06 execute (35 statements) in SQLite; 10 business answers equal pandas | Tested |
| SQL on MySQL 8 | NOT tested (no MySQL available); dialect-specific: HOUR(), boolean sums |
| app.py / charts.py compile (py_compile) | Tested |
| Streamlit app launch, visuals, navigation, filters in UI, downloads | NOT tested - streamlit/plotly not installed, no network |
| Cinematic opening | CSS-animated intro with reduced-motion fallback; no video/image assets (assets/ folders empty) |
| Power BI .pbix | NOT delivered; DAX, theme and guide provided |
| EDA notebook | See notebooks/; executed with matplotlib/seaborn only |
| Separate modules listed in the brief but merged: navigation, components, validation, config, analytics, insight_engine, feature_engineering | Merged into app.py/preprocessing.py/kpi_engine.py |
| Embedded Power BI in Streamlit (brief use-case) | Not done |
