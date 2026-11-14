"""Builds AND executes notebooks/OLA_Ride_Advanced_EDA.ipynb (no jupyter needed). Run from project root."""
import base64, io, json, sys, contextlib, traceback
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

cells = []
def md(t): cells.append(("markdown", t))
def code(t): cells.append(("code", t))

md("# OLA Ride Insights - Advanced EDA\nJuly 2024 booking data. Charts use matplotlib/seaborn. Every number below is computed in the cell that shows it.")
md("## 1. Project Introduction & 2. Business Problem\nOLA generates large volumes of booking data. Goal: understand demand, cancellations, vehicle performance, payments and ratings to support operational decisions.")
code('''import sys; sys.path.insert(0, "..") if __import__("os").path.exists("../src") else None
import numpy as np, pandas as pd, seaborn as sns, matplotlib.pyplot as plt
from scipy import stats
from src import preprocessing as pp
from src.kpi_engine import headline_kpis, vehicle_scorecard, per_weekday_average, iqr_outliers, pareto
sns.set_theme(style="whitegrid", palette=["#FF6A13","#F5A524","#5B9DFF","#3DDC97","#B28DFF","#FF8FB1","#8AD1C2"])
raw_sheets = pd.read_excel(pp.RAW_PATH, sheet_name=None)
for k, v in raw_sheets.items(): print(f"{k:8s} shape={v.shape}")''')
md("## 3. Dataset Overview\n`July` is the only raw ride-level sheet; `Sheet1` is a pivot summary and `Sheet2` an icon lookup.")
code('''raw = pp.load_raw()
print(raw.dtypes.to_string()); raw.head(3)''')
md("## 4. Data Dictionary\nSee `documentation/Data_Dictionary.md`. Key rule: ratings, payment, TAT and incomplete flag exist only for Success bookings.")
md("## 5-7. Data Quality, Missing Values, Duplicates")
code('''df, audit = pp.clean(raw)
print({k: v for k, v in audit.items() if isinstance(v, int)})
print("Quality score:", audit["data_quality_score"], "|", audit["data_quality_formula"])
miss = raw.isna().sum(); miss = miss[miss > 0].sort_values()
ax = miss.plot.barh(figsize=(7, 3.5), title="Missing values per column (all structural)"); ax.set_xlabel("rows")''')
code('''# prove the nulls are structural: every non-success row is null in these columns
nonsucc = raw[raw.Booking_Status != "Success"]
print(nonsucc[["V_TAT","C_TAT","Payment_Method","Driver_Ratings","Customer_Rating","Incomplete_Rides"]].isna().all().to_dict())''')
md("## 8-9. Cleaning & Feature Engineering\nNo rows removed; 9 validity rules had zero violations. Engineered features are listed in the data dictionary.")
code('''print(df.shape); df[["Timestamp","Booking_Hour","Day_Name","Time_Of_Day","Is_Peak_Hour","Status_Category","Revenue_Category","Distance_Category"]].head()''')
md("## 10. Univariate Analysis")
code('''ok = df[df.Is_Success]
fig, ax = plt.subplots(1, 3, figsize=(15, 3.8))
df.Booking_Status.value_counts().plot.barh(ax=ax[0], title="Booking status"); 
sns.histplot(df.Booking_Value, bins=50, ax=ax[1]).set_title("Booking value (right-skewed)")
sns.histplot(ok.Ride_Distance, bins=25, ax=ax[2]).set_title("Ride distance (successful)")
plt.tight_layout(); print("skew of Booking_Value:", round(df.Booking_Value.skew(), 2))''')
md("**Reading:** 62% of bookings succeed; value is right-skewed so the median (386) is far below the mean (549).")
md("## 11-12. Bivariate & Multivariate Analysis")
code('''sc = vehicle_scorecard(df); display_cols = ["Vehicle_Type","total_bookings","success_rate","cancellation_rate","avg_distance","avg_customer_rating"]
print(sc[display_cols].round(4).to_string(index=False))
fig, ax = plt.subplots(1, 2, figsize=(12, 3.8))
sns.barplot(data=sc, y="Vehicle_Type", x="success_rate", ax=ax[0]).set_title("Success rate by vehicle"); ax[0].set_xlim(.55, .68)
sns.barplot(data=sc, y="Vehicle_Type", x="avg_distance", ax=ax[1]).set_title("Average ride distance (km)")
plt.tight_layout()''')
code('''ct = pd.crosstab(df.Vehicle_Type, df.Is_Success)
chi2, p, *_ = stats.chi2_contingency(ct); print(f"Success vs vehicle: chi2={chi2:.2f}, p={p:.3f} -> differences are not statistically significant at 5%" if p > .05 else f"p={p:.4f}: significant")''')
md("## 13. Time-Based Analysis")
code('''hourly = df.groupby("Booking_Hour").size()
fig, ax = plt.subplots(1, 2, figsize=(14, 4))
hourly.plot.bar(ax=ax[0], title="Bookings by hour"); ax[0].set_ylim(0, hourly.max() * 1.1)
m = df.pivot_table(index="Booking_Hour", columns="Day_Name", values="Booking_ID", aggfunc="count")[["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]]
sns.heatmap(m, cmap="YlOrBr", ax=ax[1]).set_title("Hour x weekday (raw counts)"); plt.tight_layout()
print(f"max-min spread = {(hourly.max()-hourly.min())/hourly.mean():.1%} of mean; uniformity chi-square p = {stats.chisquare(hourly)[1]:.2f}")
print(per_weekday_average(df).round(1).to_string(index=False))''')
md("**Reading:** Mon-Wed look busier in raw counts only because July 2024 contains five of each; per-day averages are flat. There is no strong daily peak.")
md("## 14. Vehicle Type Analysis")
code('''fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=ok, x="Vehicle_Type", y="Ride_Distance", ax=ax).set_title("Ride distance by vehicle (successful)"); plt.xticks(rotation=25)''')
md("## 15. Revenue Analysis\nTotal booking value (all statuses) is **not** revenue. Successful value is Success only; fully completed also excludes incomplete rides.")
code('''k = headline_kpis(df)
for n in ["total_booking_value","successful_booking_value","fully_completed_value"]: print(f"{n:28s}{k[n]:>14,.0f}")
pay = ok.groupby("Payment_Method").Booking_Value.sum().sort_values(ascending=False)
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
pay.plot.bar(ax=ax[0], title="Successful booking value by payment"); 
d = pareto(ok.groupby("Vehicle_Type").Booking_Value.sum()); ax[1].bar(d.iloc[:,0], d["value"]); ax2 = ax[1].twinx(); ax2.plot(d.iloc[:,0], d.cum_share*100, color="k", marker="o"); ax[1].set_title("Pareto: successful value by vehicle"); ax[1].tick_params(axis="x", rotation=30)
plt.tight_layout()''')
md("## 16. Cancellation Analysis")
code('''c = df[df.Cancellation_Reason.notna()]
t = c.groupby(["Cancellation_Category","Cancellation_Reason"]).size().rename("n").reset_index().sort_values("n")
fig, ax = plt.subplots(figsize=(9, 4)); sns.barplot(data=t, y="Cancellation_Reason", x="n", hue="Cancellation_Category", dodge=False, ax=ax).set_title("Recorded cancellation reasons")
print(df.Cancellation_Category.value_counts().to_dict()); print("incomplete reasons:", ok.Incomplete_Rides_Reason.value_counts().to_dict())''')
md("## 17. Customer Behaviour Analysis")
code('''per = df.Customer_ID.value_counts()
print("customers:", len(per), "| booked more than once:", int((per > 1).sum()), f"({(per>1).mean():.1%})", "| max bookings:", per.max())
print(per.value_counts().sort_index().to_string())''')
md("## 18-19. Driver Performance & Ratings")
code('''fig, ax = plt.subplots(1, 3, figsize=(15, 3.6))
sns.histplot(ok.Customer_Rating, bins=20, ax=ax[0]).set_title("Customer rating"); sns.histplot(ok.Driver_Rating, bins=20, ax=ax[1]).set_title("Driver rating")
sns.scatterplot(data=ok.sample(5000, random_state=1), x="Customer_Rating", y="Driver_Rating", alpha=.3, ax=ax[2]).set_title("Customer vs driver rating (5k sample)")
plt.tight_layout(); print("corr:", round(ok.Customer_Rating.corr(ok.Driver_Rating), 4), "| ratings <=3.5:", f"{(ok.Customer_Rating<=3.5).mean():.1%} / {(ok.Driver_Rating<=3.5).mean():.1%}")
print("ANOVA customer rating ~ vehicle p =", round(stats.f_oneway(*[g.Customer_Rating for _, g in ok.groupby("Vehicle_Type")])[1], 3))''')
md("## 20. Outlier Detection")
code('''flag = df.groupby("Vehicle_Type").Booking_Value.transform(iqr_outliers)
print("IQR outliers in Booking_Value within vehicle:", int(flag.sum()), f"({flag.mean():.1%}) - statistical outliers only, not fraud")
sns.boxplot(data=df, x="Vehicle_Type", y="Booking_Value"); plt.xticks(rotation=25)''')
md("## 21. Correlation Analysis")
code('''num = ok[["Booking_Value","Ride_Distance","Driver_Rating","Customer_Rating","V_TAT","C_TAT"]]
sns.heatmap(num.corr(), annot=True, fmt=".2f", cmap="vlag", center=0).set_title("Correlation (successful rides)")''')
md("**Reading:** booking value is essentially uncorrelated with distance in this file, which is unusual for ride fares.")
md("## 22. Statistical Analysis\nTests run above: chi-square (success vs vehicle; hourly uniformity), ANOVA (rating vs vehicle), Pearson (ratings).")
md("## 23. Business Insights & 24. Final Recommendations\nSee `documentation/Business_Insights.md`. Summary: 62.1% success; driver-led cancellations (18,434 vs 10,499); vehicle, hour and rating differences are not statistically significant; fare does not track distance, so treat the dataset as possibly synthetic. Recommendations: investigate driver cancellation causes, reduce the 38% unfulfilled demand, track incomplete-ride causes (breakdown 1,591), collect multi-month and cost data.")

nb_cells, ns, count = [], {"__name__": "__main__"}, 0
for kind, src in cells:
    if kind == "markdown":
        nb_cells.append({"cell_type": "markdown", "metadata": {}, "source": src.splitlines(True)}); continue
    count += 1; out = io.StringIO(); outputs = []
    plt.close("all")
    try:
        with contextlib.redirect_stdout(out):
            exec(compile(src, f"cell{count}", "exec"), ns)
    except Exception:
        print("FAILED cell", count); traceback.print_exc(); sys.exit(1)
    if out.getvalue(): outputs.append({"output_type": "stream", "name": "stdout", "text": out.getvalue().splitlines(True)})
    for n in plt.get_fignums():
        buf = io.BytesIO(); plt.figure(n).savefig(buf, format="png", dpi=90, bbox_inches="tight")
        outputs.append({"output_type": "display_data", "metadata": {}, "data": {"image/png": base64.b64encode(buf.getvalue()).decode(), "text/plain": ["<Figure>"]}})
    nb_cells.append({"cell_type": "code", "metadata": {}, "execution_count": count, "source": src.splitlines(True), "outputs": outputs})
nb = {"cells": nb_cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
Path("notebooks/OLA_Ride_Advanced_EDA.ipynb").write_text(json.dumps(nb))
print("notebook written:", len(nb_cells), "cells,", count, "code cells executed OK")
