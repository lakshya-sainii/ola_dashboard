"""Deterministic analytics assistant. Every answer is computed from the filtered data.
Optional LLM wording: set ANTHROPIC_API_KEY (never hard-coded). The LLM only rephrases the
computed evidence; it is never asked to produce numbers."""
from __future__ import annotations
import os
import pandas as pd
from .kpi_engine import headline_kpis, vehicle_scorecard

SUGGESTIONS = [
    "Which vehicle category has the highest booking volume?",
    "What is the most common cancellation reason?",
    "During which hours is booking activity highest?",
    "Which payment method contributes the most booking value?",
    "What is the success rate for each vehicle?",
    "How does customer rating differ across vehicle categories?",
    "Which customers have the highest booking value?",
    "What patterns appear in incomplete rides?",
]


def _resp(answer, metrics, interp, action, table=None, label="Verified metric"):
    return {"answer": answer, "metrics": metrics, "interpretation": interp, "action": action,
            "table": table, "label": label}


def answer(q: str, df: pd.DataFrame) -> dict:
    ql = q.lower().strip()
    if df.empty:
        return _resp("No bookings match the current filters.", [], "Widen or clear the filters.", "Reset filters.")
    sc = vehicle_scorecard(df)
    if "incomplete" in ql:
        inc = df[df["Is_Incomplete"]]
        if inc.empty:
            return _resp("No incomplete rides in the current selection.", [], "-", "-")
        t = inc["Incomplete_Rides_Reason"].value_counts().rename_axis("Reason").reset_index(name="Rides")
        top = t.iloc[0]
        v = inc["Vehicle_Type"].value_counts()
        return _resp(f"{len(inc):,} rides were flagged incomplete; the leading reason is {top.Reason} ({top.Rides:,}).",
            [f"Incomplete rides: {len(inc):,} ({len(inc)/max(df.Is_Success.sum(),1):.1%} of successful bookings)",
             f"Most affected vehicle: {v.index[0]} ({v.iloc[0]:,})"],
            "Incomplete rides are a subset of 'Success' bookings, so Success overstates fully completed trips.",
            "Review whether Customer Demand and Vehicle Breakdown share a root cause by vehicle and hour.", t)
    if "cancel" in ql and ("reason" in ql or "common" in ql or "why" in ql):
        c = df[df["Cancellation_Reason"].notna()]
        if c.empty:
            return _resp("No cancellations in the current selection.", [], "-", "-")
        t = c.groupby(["Cancellation_Category", "Cancellation_Reason"]).size().rename("Cancellations").reset_index() \
              .sort_values("Cancellations", ascending=False)
        r = t.iloc[0]
        return _resp(f"The most common reason is '{r.Cancellation_Reason}' ({r.Cancellation_Category}), {r.Cancellations:,} cancellations "
            f"({r.Cancellations/len(c):.1%} of cancellations).",
            [f"Total cancellations with a recorded reason: {len(c):,}"],
            "Reasons are self-reported labels; they indicate where to investigate, not proven causes.",
            "Sample the top reason by vehicle and hour to test for concentration.", t)
    if "hour" in ql or "peak" in ql or "when" in ql:
        h = df.groupby("Booking_Hour").size().rename("Bookings").reset_index().sort_values("Bookings", ascending=False)
        spread = (h.Bookings.max() - h.Bookings.min()) / h.Bookings.mean()
        return _resp(f"Hour {int(h.iloc[0].Booking_Hour):02d}:00 has the most bookings ({int(h.iloc[0].Bookings):,}); "
            f"the lowest is {int(h.iloc[-1].Booking_Hour):02d}:00 ({int(h.iloc[-1].Bookings):,}).",
            [f"Max-min spread is {spread:.1%} of the mean hourly volume"],
            "Hourly demand is close to flat, so no hour is a strong peak in this data.",
            "Do not rebalance supply by hour on this evidence alone.", h.head(10))
    if "payment" in ql:
        p = df[df["Is_Success"]].groupby("Payment_Method")["Booking_Value"].agg(["count", "sum"]).reset_index() \
              .rename(columns={"count": "Rides", "sum": "Booking_Value"}).sort_values("Booking_Value", ascending=False)
        if p.empty:
            return _resp("No successful rides in this selection.", [], "-", "-")
        p["Share"] = p["Booking_Value"] / p["Booking_Value"].sum()
        return _resp(f"{p.iloc[0].Payment_Method} leads with {p.iloc[0].Booking_Value:,.0f} ({p.iloc[0].Share:.1%}) of successful booking value.",
            ["Payment is recorded for successful rides only"], "Compare shares across payment methods; card use may be small.",
            "Check whether cash-heavy segments correlate with cancellations before drawing conclusions.", p)
    if "success" in ql and "vehicle" in ql or "success rate" in ql:
        t = sc[["Vehicle_Type", "total_bookings", "success_rate"]].sort_values("success_rate", ascending=False)
        return _resp(f"{t.iloc[0].Vehicle_Type} has the highest success rate ({t.iloc[0].success_rate:.1%}); {t.iloc[-1].Vehicle_Type} the lowest ({t.iloc[-1].success_rate:.1%}).",
            [f"Gap between best and worst: {(t.iloc[0].success_rate - t.iloc[-1].success_rate)*100:.2f} pts"],
            ("Differences between vehicles are small (under 2 points); treat them cautiously." if (t.iloc[0].success_rate - t.iloc[-1].success_rate) < 0.02 else "The gap is material; investigate the lowest vehicle."), "Test the gap statistically before acting (see Cancellation Radar).", t)
    if "rating" in ql:
        t = sc[["Vehicle_Type", "avg_customer_rating", "avg_driver_rating"]].sort_values("avg_customer_rating", ascending=False)
        return _resp(f"{t.iloc[0].Vehicle_Type} has the highest average customer rating ({t.iloc[0].avg_customer_rating:.3f}); "
            f"{t.iloc[-1].Vehicle_Type} the lowest ({t.iloc[-1].avg_customer_rating:.3f}).",
            ["Ratings exist only for successful rides"], (f"Spread between best and worst is {t.iloc[0].avg_customer_rating - t.iloc[-1].avg_customer_rating:.3f} rating points."), "Look at low-rating share, not just the mean.", t)
    if "customer" in ql and ("value" in ql or "highest" in ql or "top" in ql):
        t = df.groupby("Customer_ID").agg(Bookings=("Booking_ID", "size"), Booking_Value=("Booking_Value", "sum")) \
              .sort_values("Booking_Value", ascending=False).head(10).reset_index()
        return _resp(f"Top customer by booking value: {t.iloc[0].Customer_ID} ({t.iloc[0].Booking_Value:,.0f} across {t.iloc[0].Bookings} bookings).",
            ["Booking value includes non-successful bookings; it is not lifetime value"], "Booking value is summed over the filtered window; check repeat behaviour before calling anyone high-value.",
            "Use successful value for any loyalty targeting.", t)
    if "vehicle" in ql or "volume" in ql or "category" in ql:
        t = sc[["Vehicle_Type", "total_bookings", "total_value"]]
        return _resp(f"{t.iloc[0].Vehicle_Type} has the highest booking volume ({int(t.iloc[0].total_bookings):,}).",
            [f"{len(t)} vehicle types in selection"], f"Highest vs lowest volume differ by {(t.iloc[0].total_bookings - t.iloc[-1].total_bookings)/t.iloc[0].total_bookings:.1%}.", "Compare success and cancellation rates before sizing fleets.", t)
    k = headline_kpis(df)
    return _resp("I could not map that to a supported analysis, so here is the headline picture.",
        [f"Bookings {k['total_bookings']:,}", f"Success rate {k['success_rate']:.1%}", f"Cancellation rate {k['cancellation_rate']:.1%}"],
        "Try one of the suggested questions.", "Pick a suggested question.", None)


def llm_rephrase(resp: dict) -> str | None:
    """Optional: LLM wording of already-computed evidence. Returns None if unavailable."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        import anthropic
        msg = anthropic.Anthropic(api_key=key).messages.create(
            model=os.getenv("OLA_LLM_MODEL", "claude-sonnet-4-5"), max_tokens=300,
            messages=[{"role": "user", "content": "Rewrite this analytics finding for a manager in 2 sentences. "
                       "Use ONLY these facts, add no numbers.\n" + resp["answer"] + " " + " ".join(resp["metrics"])}])
        return msg.content[0].text
    except Exception:
        return None
