"""KPI definitions - single source of truth shared by Streamlit, notebook and tests.

Definitions (also mirrored in sql/06_kpi_queries.sql and powerbi/DAX_Measures.md):
  Total Bookings           = count of bookings (rows)
  Successful Bookings      = Booking_Status == 'Success'
  Success Rate             = Successful / Total
  Cancellation Rate        = (Canceled by Customer + Canceled by Driver) / Total
  Driver Not Found Rate    = Driver Not Found / Total
  Total Booking Value      = SUM(Booking_Value) over ALL bookings (intended fare, NOT revenue)
  Successful Booking Value = SUM(Booking_Value) where Status == 'Success'
                             (this answers SQL question 9; it still includes rides
                             flagged Incomplete = 'Yes')
  Fully Completed Value    = Success AND Incomplete_Rides == 'No'
  Avg Ride Distance        = mean Ride_Distance over Success bookings (non-success = 0 km)
  Avg Customer/Driver Rating = mean over rated (Success) bookings
No cost data exists, so profit/margin cannot be computed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _div(a: float, b: float) -> float:
    return float(a) / float(b) if b else float("nan")


def headline_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    ok = df[df["Is_Success"]]
    cust = int(df["Is_Customer_Cancel"].sum())
    drv = int(df["Is_Driver_Cancel"].sum())
    nodrv = int(df["Booking_Status"].eq("Driver Not Found").sum())
    return {
        "total_bookings": total,
        "successful_bookings": len(ok),
        "success_rate": _div(len(ok), total),
        "customer_cancellations": cust,
        "driver_cancellations": drv,
        "driver_not_found": nodrv,
        "cancellation_rate": _div(cust + drv, total),
        "driver_not_found_rate": _div(nodrv, total),
        "incomplete_rides": int(df["Is_Incomplete"].sum()),
        "total_booking_value": float(df["Booking_Value"].sum()),
        "successful_booking_value": float(ok["Booking_Value"].sum()),
        "fully_completed_value": float(df.loc[df["Is_Completed_Ride"], "Booking_Value"].sum()),
        "avg_booking_value": float(df["Booking_Value"].mean()) if total else float("nan"),
        "avg_ride_distance": float(ok["Ride_Distance"].mean()) if len(ok) else float("nan"),
        "total_ride_distance": float(ok["Ride_Distance"].sum()),
        "avg_customer_rating": float(ok["Customer_Rating"].mean()) if len(ok) else float("nan"),
        "avg_driver_rating": float(ok["Driver_Rating"].mean()) if len(ok) else float("nan"),
    }


def vehicle_scorecard(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("Vehicle_Type")
    out = g.agg(
        total_bookings=("Booking_ID", "size"),
        successful=("Is_Success", "sum"),
        cust_cancel=("Is_Customer_Cancel", "sum"),
        drv_cancel=("Is_Driver_Cancel", "sum"),
        total_value=("Booking_Value", "sum"),
    )
    ok = df[df["Is_Success"]].groupby("Vehicle_Type")
    out["success_value"] = ok["Booking_Value"].sum()
    out["avg_distance"] = ok["Ride_Distance"].mean()
    out["total_distance"] = ok["Ride_Distance"].sum()
    out["avg_customer_rating"] = ok["Customer_Rating"].mean()
    out["avg_driver_rating"] = ok["Driver_Rating"].mean()
    out["success_rate"] = out["successful"] / out["total_bookings"]
    out["cancellation_rate"] = (out["cust_cancel"] + out["drv_cancel"]) / out["total_bookings"]
    return out.reset_index().sort_values("total_bookings", ascending=False)


def pareto(series: pd.Series) -> pd.DataFrame:
    s = series.sort_values(ascending=False)
    d = s.rename("value").to_frame()
    d["share"] = d["value"] / d["value"].sum()
    d["cum_share"] = d["share"].cumsum()
    return d.reset_index()


def iqr_outliers(s: pd.Series, k: float = 1.5) -> pd.Series:
    q1, q3 = s.quantile([0.25, 0.75])
    i = q3 - q1
    return (s < q1 - k * i) | (s > q3 + k * i)


def hour_dow_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Booking counts, hour x weekday. Cells are NOT normalised for the number of
    each weekday in the window (July 2024 has 5 Mon/Tue/Wed, 4 of the rest)."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    m = df.pivot_table(index="Booking_Hour", columns="Day_Name", values="Booking_ID",
                       aggfunc="count", fill_value=0)
    return m.reindex(columns=[d for d in days if d in m.columns])


def per_weekday_average(df: pd.DataFrame) -> pd.DataFrame:
    """Average bookings per calendar day for each weekday (fixes the 5-vs-4 count bias)."""
    daily = df.groupby(["Booking_Date", "Day_Name"]).size().rename("n").reset_index()
    out = daily.groupby("Day_Name")["n"].agg(["mean", "count"]).rename(
        columns={"mean": "avg_bookings_per_day", "count": "days_in_window"})
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return out.reindex([d for d in order if d in out.index]).reset_index()
