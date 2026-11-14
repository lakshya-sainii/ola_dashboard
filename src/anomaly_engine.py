"""Statistical anomaly flags. An anomaly is a statistical outlier, NOT evidence of fraud."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .kpi_engine import iqr_outliers


def _sev(share: float) -> str:
    return "High" if share > 0.05 else "Medium" if share > 0.01 else "Low"


def detect(df: pd.DataFrame) -> list[dict]:
    out: list[dict] = []
    if df.empty:
        return out
    # 1. Booking value outliers within vehicle type (IQR, k=1.5)
    flags = df.groupby("Vehicle_Type")["Booking_Value"].transform(iqr_outliers)
    n = int(flags.sum())
    out.append({"title": "High booking values within vehicle type", "method": "IQR (1.5x) per vehicle type",
        "metric": "Booking_Value", "count": n, "share": n / len(df), "severity": _sev(n / len(df)),
        "records": df[flags].nlargest(200, "Booking_Value"),
        "limitation": "Booking_Value is right-skewed; long-distance rides legitimately sit above the fence."})
    ok = df[df["Is_Success"] & (df["Ride_Distance"] > 0)].copy()
    if len(ok) > 30:
        # 2. Value per km outliers
        ok["value_per_km"] = ok["Booking_Value"] / ok["Ride_Distance"]
        f2 = iqr_outliers(ok["value_per_km"])
        n2 = int(f2.sum())
        out.append({"title": "Unusual fare per km (successful rides)", "method": "IQR (1.5x) on Booking_Value / Ride_Distance",
            "metric": "value_per_km", "count": n2, "share": n2 / len(ok), "severity": _sev(n2 / len(ok)),
            "records": ok[f2].nlargest(200, "value_per_km"),
            "limitation": "Short rides inflate per-km values (minimum fares). Pricing rules are not in the data."})
    # 3. Daily volume z-score
    daily = df.groupby("Booking_Date").size()
    if len(daily) >= 7 and daily.std() > 0:
        z = (daily - daily.mean()) / daily.std()
        hit = z[z.abs() > 2]
        out.append({"title": "Days with unusual booking volume", "method": "Z-score |z| > 2 on daily bookings",
            "metric": "daily bookings", "count": int(len(hit)), "share": len(hit) / len(daily),
            "severity": "Medium" if len(hit) else "Low",
            "records": hit.rename("z_score").reset_index(),
            "limitation": "Only ~31 daily points; weekday mix (5 vs 4 occurrences) also moves volumes."})
    return out
