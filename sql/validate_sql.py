"""Runs sql/02-06 against an in-memory SQLite copy of the cleaned data and checks the 10
business answers + KPIs against pandas. MySQL-only functions are translated by regex.
Not a substitute for a test run on MySQL 8 (documented limitation)."""
import re, sqlite3, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data/processed/ola_clean.csv")
cols = ["Booking_ID","Booking_Status","Customer_ID","Vehicle_Type","Pickup_Location","Drop_Location","V_TAT","C_TAT",
        "Canceled_Rides_by_Customer","Canceled_Rides_by_Driver","Incomplete_Rides","Incomplete_Rides_Reason",
        "Booking_Value","Payment_Method","Ride_Distance","Driver_Rating","Customer_Rating","Timestamp"]
load = df[cols].rename(columns={"Timestamp": "Booking_Timestamp"})
load.to_csv(ROOT / "data/processed/ola_sql_load.csv", index=False)
con = sqlite3.connect(":memory:")
load.to_sql("ola_bookings", con, index=False)

def to_sqlite(sql):
    sql = re.sub(r"HOUR\(([^)]+)\)", r"CAST(strftime('%H', \1) AS INTEGER)", sql)
    return sql.replace("CREATE OR REPLACE VIEW", "CREATE VIEW")

def statements(path):
    text = re.sub(r"--[^\n]*", "", Path(path).read_text())
    return [s.strip() for s in text.split(";") if s.strip()]

fails, ran = 0, 0
for f in ["02_data_validation", "03_business_queries", "04_advanced_analytics", "05_views", "06_kpi_queries"]:
    for s in statements(ROOT / f"sql/{f}.sql"):
        try:
            con.execute(to_sqlite(s)).fetchall(); ran += 1
        except Exception as e:
            fails += 1; print("FAIL", f, e, "\n", s[:120])
print(f"executed {ran} statements, {fails} failures")

q = lambda s: con.execute(s).fetchall()
ok = df[df.Is_Success]
checks = {
 "Q1 success rows": (len(q("SELECT * FROM ola_bookings WHERE Booking_Status='Success'")), len(ok)),
 "Q3 cust cancels": (q("SELECT COUNT(*) FROM ola_bookings WHERE Booking_Status='Canceled by Customer'")[0][0], int(df.Is_Customer_Cancel.sum())),
 "Q5 driver personal/car": (q("SELECT COUNT(*) FROM ola_bookings WHERE Canceled_Rides_by_Driver='Personal & Car related issue'")[0][0],
                            int((df.Canceled_Rides_by_Driver=='Personal & Car related issue').sum())),
 "Q6 sedan max/min": (q("SELECT MAX(Driver_Rating),MIN(Driver_Rating) FROM ola_bookings WHERE Vehicle_Type='Prime Sedan'")[0],
                      (ok[ok.Vehicle_Type=='Prime Sedan'].Driver_Rating.max(), ok[ok.Vehicle_Type=='Prime Sedan'].Driver_Rating.min())),
 "Q7 UPI rows": (len(q("SELECT * FROM ola_bookings WHERE Payment_Method='UPI'")), int((df.Payment_Method=='UPI').sum())),
 "Q9 success value": (q("SELECT SUM(Booking_Value) FROM ola_bookings WHERE Booking_Status='Success'")[0][0], int(ok.Booking_Value.sum())),
 "Q10 incomplete": (len(q("SELECT * FROM ola_bookings WHERE Incomplete_Rides='Yes'")), int(df.Is_Incomplete.sum())),
 "Q2 avg dist (Auto)": (q("SELECT AVG(Ride_Distance) FROM ola_bookings WHERE Booking_Status='Success' AND Vehicle_Type='Auto'")[0][0],
                        ok[ok.Vehicle_Type=='Auto'].Ride_Distance.mean()),
 "Q8 avg cust rating (Mini)": (q("SELECT AVG(Customer_Rating) FROM ola_bookings WHERE Vehicle_Type='Mini'")[0][0],
                               ok[ok.Vehicle_Type=='Mini'].Customer_Rating.mean()),
 "Q4 top customer n": (q("SELECT COUNT(*) c FROM ola_bookings GROUP BY Customer_ID ORDER BY c DESC LIMIT 1")[0][0], int(df.Customer_ID.value_counts().iloc[0])),
}
bad = 0
for k, (a, b) in checks.items():
    good = (all(abs(x - y) < 1e-9 for x, y in zip(a, b)) if isinstance(a, tuple) else abs(a - b) < 1e-9)
    bad += not good
    print(("PASS " if good else "FAIL ") + k, a, b)
sys.exit(1 if (fails or bad) else 0)
