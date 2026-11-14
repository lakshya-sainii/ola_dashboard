"""OLA Ride Insights - preprocessing pipeline.

Raw workbook layout (verified by inspection):
  * 'July'   -> the ONLY raw ride-level sheet (103,024 bookings, 1-31 Jul 2024)
  * 'Sheet1' -> pivot-style summary (avg distance / status counts) - NOT raw
  * 'Sheet2' -> vehicle-type -> icon URL lookup - NOT raw
Raw data is never modified; cleaned output goes to data/processed/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

RAW_SHEET = "July"
ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "OLA_DataSet.xlsx"
OUT_DIR = ROOT / "data" / "processed"

VEHICLE_LABELS = {"eBike": "E-Bike"}  # brief/slides use "E-Bike"
STATUS_CATEGORY = {
    "Success": "Completed",
    "Canceled by Customer": "Cancelled",
    "Canceled by Driver": "Cancelled",
    "Driver Not Found": "Unfulfilled",
}
# Peak hours are DERIVED from the data (top quartile of hourly booking counts),
# not assumed. Observed hourly demand is nearly flat, so "peak" is a mild
# relative label - see Business_Insights.md for the caveat.
PEAK_QUANTILE = 0.75


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    sheets = pd.read_excel(path, sheet_name=None)
    if RAW_SHEET not in sheets:
        raise ValueError(f"Expected raw sheet '{RAW_SHEET}', found {list(sheets)}")
    return sheets[RAW_SHEET]


def _bucket(s: pd.Series, bins, labels) -> pd.Series:
    return pd.cut(s, bins=bins, labels=labels, include_lowest=True).astype("string")


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return (cleaned dataframe, audit dict). The raw frame is untouched."""
    df = raw.copy()
    audit: dict = {"original_rows": int(len(raw))}
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]

    # --- integrity ---------------------------------------------------------
    audit["duplicate_rows"] = int(df.duplicated().sum())
    audit["duplicate_booking_ids"] = int(df["Booking_ID"].duplicated().sum())
    df = df.drop_duplicates(subset="Booking_ID")

    # --- strings -----------------------------------------------------------
    for c in ["Booking_ID", "Customer_ID", "Booking_Status", "Vehicle_Type",
              "Pickup_Location", "Drop_Location", "Payment_Method",
              "Canceled_Rides_by_Customer", "Canceled_Rides_by_Driver",
              "Incomplete_Rides", "Incomplete_Rides_Reason"]:
        df[c] = df[c].astype("string").str.strip()
    df["Vehicle_Type"] = df["Vehicle_Type"].replace(VEHICLE_LABELS)

    # --- timestamp: Date already carries the time; cross-check with Time ---
    df["Timestamp"] = pd.to_datetime(df["Date"], errors="coerce")
    t = df["Time"].astype(str)
    audit["timestamp_time_mismatch"] = int(
        (df["Timestamp"].dt.strftime("%H:%M:%S") != t).sum())
    df["Booking_Date"] = df["Timestamp"].dt.normalize()

    # --- validity rules (counted and reported; nothing silently dropped) ---
    audit["invalid_rating_count"] = int(
        ((df["Driver_Ratings"] < 1) | (df["Driver_Ratings"] > 5) |
         (df["Customer_Rating"] < 1) | (df["Customer_Rating"] > 5)).sum())
    audit["nonpositive_booking_value"] = int((df["Booking_Value"] <= 0).sum())
    audit["negative_distance"] = int((df["Ride_Distance"] < 0).sum())
    success = df["Booking_Status"].eq("Success")
    audit["success_with_zero_distance"] = int((success & (df["Ride_Distance"] == 0)).sum())
    audit["nonsuccess_with_distance"] = int((~success & (df["Ride_Distance"] > 0)).sum())
    audit["nonsuccess_with_rating"] = int((~success & df["Driver_Ratings"].notna()).sum())
    audit["status_vs_reason_inconsistent"] = int(
        (df["Booking_Status"].eq("Canceled by Customer") != df["Canceled_Rides_by_Customer"].notna()).sum()
        + (df["Booking_Status"].eq("Canceled by Driver") != df["Canceled_Rides_by_Driver"].notna()).sum())

    # Structural NaNs (ratings, payment, TAT, incomplete flag) are "not
    # applicable" for non-Success bookings and are preserved, not imputed.

    # --- engineered features ----------------------------------------------
    ts = df["Timestamp"]
    df["Booking_Hour"] = ts.dt.hour
    df["Day"] = ts.dt.day
    df["Day_Name"] = ts.dt.day_name()
    df["Day_Of_Week"] = ts.dt.dayofweek
    df["Month"] = ts.dt.month
    df["Week"] = ts.dt.isocalendar().week.astype(int)
    df["Is_Weekend"] = df["Day_Of_Week"].ge(5)
    hourly = df.groupby("Booking_Hour").size()
    peak_hours = set(hourly[hourly >= hourly.quantile(PEAK_QUANTILE)].index)
    audit["peak_hours_derived"] = sorted(int(h) for h in peak_hours)
    df["Is_Peak_Hour"] = df["Booking_Hour"].isin(peak_hours)
    df["Time_Of_Day"] = pd.cut(
        df["Booking_Hour"], bins=[-1, 5, 11, 16, 20, 23],
        labels=["Night", "Morning", "Afternoon", "Evening", "Late Evening"]).astype("string")
    df["Status_Category"] = df["Booking_Status"].map(STATUS_CATEGORY)
    df["Is_Success"] = df["Booking_Status"].eq("Success")
    df["Is_Incomplete"] = df["Incomplete_Rides"].eq("Yes").fillna(False).astype(bool)
    df["Is_Completed_Ride"] = (df["Is_Success"] & df["Incomplete_Rides"].eq("No")).fillna(False).astype(bool)
    df["Is_Customer_Cancel"] = df["Booking_Status"].eq("Canceled by Customer")
    df["Is_Driver_Cancel"] = df["Booking_Status"].eq("Canceled by Driver")
    df["Cancellation_Category"] = np.select(
        [df["Is_Customer_Cancel"], df["Is_Driver_Cancel"], df["Booking_Status"].eq("Driver Not Found")],
        ["Customer", "Driver", "No Driver Found"], default="")
    df["Cancellation_Category"] = df["Cancellation_Category"].replace("", pd.NA)
    df["Cancellation_Reason"] = df["Canceled_Rides_by_Customer"].fillna(df["Canceled_Rides_by_Driver"])
    df["Revenue_Category"] = _bucket(df["Booking_Value"], [0, 250, 500, 1000, 5000],
                                     ["Low (<=250)", "Medium (251-500)", "High (501-1000)", "Premium (>1000)"])
    dist = _bucket(df["Ride_Distance"], [0, 10, 25, 50], ["Short (<=10km)", "Medium (11-25km)", "Long (>25km)"])
    df["Distance_Category"] = dist.where(df["Is_Success"])
    df["Customer_Rating_Group"] = _bucket(df["Customer_Rating"], [0, 3.5, 4.5, 5],
                                          ["Low (<=3.5)", "Good (3.6-4.5)", "Excellent (>4.5)"])
    df["Driver_Rating_Group"] = _bucket(df["Driver_Ratings"], [0, 3.5, 4.5, 5],
                                        ["Low (<=3.5)", "Good (3.6-4.5)", "Excellent (>4.5)"])
    df = df.rename(columns={"Driver_Ratings": "Driver_Rating"})
    df = df.drop(columns=["Date", "Time", "Vehicle_Images"])

    # --- audit -------------------------------------------------------------
    audit["cleaned_rows"] = int(len(df))
    audit["rows_removed"] = audit["original_rows"] - audit["cleaned_rows"]
    audit["date_min"] = str(df["Timestamp"].min())
    audit["date_max"] = str(df["Timestamp"].max())
    audit["missing_values_raw"] = {k: int(v) for k, v in raw.isna().sum().items() if v}
    rules = ["duplicate_booking_ids", "invalid_rating_count", "nonpositive_booking_value",
             "negative_distance", "success_with_zero_distance", "nonsuccess_with_distance",
             "nonsuccess_with_rating", "status_vs_reason_inconsistent", "timestamp_time_mismatch"]
    violations = sum(audit[k] for k in rules)
    audit["data_quality_score"] = round(100 * (1 - violations / (audit["original_rows"] * len(rules))), 2)
    audit["data_quality_formula"] = f"100 x (1 - rule violations / (rows x {len(rules)} validity rules))"
    audit["note_structural_missing"] = (
        "V_TAT, C_TAT, Payment_Method, ratings and Incomplete_Rides are null for every non-Success "
        "booking by design (not applicable) and are preserved as null.")
    return df, audit


def run() -> pd.DataFrame:
    df, audit = clean(load_raw())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_DIR / "ola_clean.csv", index=False)
    (OUT_DIR / "cleaning_audit.json").write_text(json.dumps(audit, indent=2))
    return df


if __name__ == "__main__":
    d = run()
    print((OUT_DIR / "cleaning_audit.json").read_text())
    print(d.shape)
