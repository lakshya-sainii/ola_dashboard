"""Cached data access. Builds the processed file on first run if it is missing."""
from __future__ import annotations
import json
import pandas as pd
from . import preprocessing as pp

DATE_COLS = ["Timestamp", "Booking_Date"]


def load_clean() -> pd.DataFrame:
    csv = pp.OUT_DIR / "ola_clean.csv"
    if not csv.exists():
        pp.run()
    df = pd.read_csv(csv, parse_dates=DATE_COLS)
    for c in ["Is_Weekend", "Is_Peak_Hour", "Is_Success", "Is_Incomplete", "Is_Completed_Ride",
              "Is_Customer_Cancel", "Is_Driver_Cancel"]:
        df[c] = df[c].astype(bool)
    return df


def load_audit() -> dict:
    p = pp.OUT_DIR / "cleaning_audit.json"
    if not p.exists():
        pp.run()
    return json.loads(p.read_text())
