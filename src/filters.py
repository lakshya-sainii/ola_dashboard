"""Single filter engine used by every page, KPI, chart and AI answer."""
from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class FilterState:
    date_start: pd.Timestamp | None = None
    date_end: pd.Timestamp | None = None
    vehicles: list[str] = field(default_factory=list)
    statuses: list[str] = field(default_factory=list)
    payments: list[str] = field(default_factory=list)
    customer_query: str = ""
    booking_query: str = ""

    def active_count(self, df_min, df_max) -> int:
        n = 0
        n += bool(self.date_start is not None and (self.date_start > df_min or self.date_end < df_max))
        n += bool(self.vehicles) + bool(self.statuses) + bool(self.payments)
        n += bool(self.customer_query.strip()) + bool(self.booking_query.strip())
        return int(n)

    def summary(self) -> list[str]:
        out = []
        if self.date_start is not None:
            out.append(f"{self.date_start:%d %b} - {self.date_end:%d %b %Y}")
        if self.vehicles: out.append("Vehicle: " + ", ".join(self.vehicles))
        if self.statuses: out.append("Status: " + ", ".join(self.statuses))
        if self.payments: out.append("Payment: " + ", ".join(self.payments))
        if self.customer_query.strip(): out.append(f"Customer ~ {self.customer_query.strip()}")
        if self.booking_query.strip(): out.append(f"Booking ~ {self.booking_query.strip()}")
        return out


def apply_filters(df: pd.DataFrame, f: FilterState) -> pd.DataFrame:
    m = pd.Series(True, index=df.index)
    if f.date_start is not None and f.date_end is not None:
        m &= df["Booking_Date"].between(pd.Timestamp(f.date_start), pd.Timestamp(f.date_end))
    if f.vehicles: m &= df["Vehicle_Type"].isin(f.vehicles)
    if f.statuses: m &= df["Booking_Status"].isin(f.statuses)
    if f.payments: m &= df["Payment_Method"].isin(f.payments)
    if f.customer_query.strip():
        m &= df["Customer_ID"].str.contains(f.customer_query.strip(), case=False, na=False, regex=False)
    if f.booking_query.strip():
        m &= df["Booking_ID"].str.contains(f.booking_query.strip(), case=False, na=False, regex=False)
    return df[m]
