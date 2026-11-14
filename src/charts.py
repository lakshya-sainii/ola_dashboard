"""Reusable Plotly chart builders sharing one theme. Each returns a figure."""
from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .styling import TOKENS as T
from .kpi_engine import hour_dow_matrix, pareto

PALETTE = [T["orange"], T["amber"], T["blue"], T["good"], "#B28DFF", "#FF8FB1", "#8AD1C2"]
STATUS_COLORS = {"Success": T["good"], "Canceled by Driver": T["bad"], "Canceled by Customer": T["amber"], "Driver Not Found": T["blue"]}


def theme(fig: go.Figure, title: str | None = None, h: int = 380) -> go.Figure:
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=T["ink"]), height=h, colorway=PALETTE,
        margin=dict(l=10, r=10, t=50 if title else 20, b=10), title=dict(text=title, x=0.01, font=dict(size=15)) if title else None,
        legend=dict(orientation="h", y=-0.2), hoverlabel=dict(bgcolor=T["panel"]))
    fig.update_xaxes(gridcolor="rgba(255,255,255,.06)"); fig.update_yaxes(gridcolor="rgba(255,255,255,.06)")
    return fig


def activity_timeline(df: pd.DataFrame, grain: str = "Daily") -> go.Figure:
    rule = {"Hourly": "h", "Daily": "D", "Weekly": "W", "Monthly": "MS"}[grain]
    g = df.set_index("Timestamp").groupby(pd.Grouper(freq=rule)).agg(
        Bookings=("Booking_ID", "size"), Successful=("Is_Success", "sum"),
        Cancelled=("Is_Customer_Cancel", "sum"), Driver=("Is_Driver_Cancel", "sum"), Value=("Booking_Value", "sum")).reset_index()
    g["Cancelled"] = g["Cancelled"] + g["Driver"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g["Timestamp"], y=g["Bookings"], name="Bookings", line=dict(color=T["orange"], width=2.5), fill="tozeroy", fillcolor="rgba(255,106,19,.10)"))
    fig.add_trace(go.Scatter(x=g["Timestamp"], y=g["Successful"], name="Successful", line=dict(color=T["good"], width=1.8)))
    fig.add_trace(go.Scatter(x=g["Timestamp"], y=g["Cancelled"], name="Cancelled", line=dict(color=T["bad"], width=1.8)))
    return theme(fig, f"Mobility activity - {grain.lower()}")


def status_donut(df: pd.DataFrame) -> go.Figure:
    s = df["Booking_Status"].value_counts()
    fig = go.Figure(go.Pie(labels=s.index, values=s.values, hole=.62, marker=dict(colors=[STATUS_COLORS.get(i, T["mute"]) for i in s.index]),
                           textinfo="percent", hovertemplate="%{label}<br>%{value:,} bookings<extra></extra>"))
    return theme(fig, "Booking outcome composition", 340)


def hour_dow_heatmap(df: pd.DataFrame, title="Bookings by hour and weekday") -> go.Figure:
    m = hour_dow_matrix(df)
    fig = go.Figure(go.Heatmap(z=m.values, x=m.columns, y=m.index, colorscale=[[0, "#14171D"], [1, T["orange"]]],
        hovertemplate="%{x} %{y}:00<br>%{z:,} bookings<extra></extra>"))
    fig.update_yaxes(autorange="reversed", dtick=2)
    return theme(fig, title, 460)


def bar_h(d: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, fmt: str = ",.0f") -> go.Figure:
    d = d.sort_values(x)
    fig = px.bar(d, x=x, y=y, orientation="h", color=color, text=d[x].map(lambda v: format(v, fmt)))
    fig.update_traces(marker_color=T["orange"] if color is None else None, textposition="outside")
    return theme(fig, title)


def pareto_chart(counts: pd.Series, title: str) -> go.Figure:
    p = pareto(counts)
    fig = go.Figure()
    fig.add_bar(x=p.iloc[:, 0], y=p["value"], name="Count", marker_color=T["orange"])
    fig.add_scatter(x=p.iloc[:, 0], y=p["cum_share"] * 100, name="Cumulative %", yaxis="y2", line=dict(color=T["amber"]))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105], ticksuffix="%", showgrid=False))
    return theme(fig, title)


def box_by(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    return theme(px.box(df, x=x, y=y, color=x, points=False), title)


def treemap(df: pd.DataFrame, path: list[str], values: str, title: str) -> go.Figure:
    return theme(px.treemap(df, path=path, values=values, color_discrete_sequence=PALETTE), title)


def scatter_vehicle(sc: pd.DataFrame) -> go.Figure:
    fig = px.scatter(sc, x="avg_distance", y="success_rate", size="total_bookings", color="Vehicle_Type", hover_data=["total_value"])
    fig.update_yaxes(tickformat=".1%")
    return theme(fig, "Distance vs success rate (bubble = bookings)")


def sankey_status(df: pd.DataFrame) -> go.Figure:
    c = df.dropna(subset=["Cancellation_Category"]).groupby(["Booking_Status", "Cancellation_Reason"], dropna=False).size().reset_index(name="n")
    c["Cancellation_Reason"] = c["Cancellation_Reason"].fillna("No reason recorded")
    src = list(c["Booking_Status"].unique()); dst = list(c["Cancellation_Reason"].unique()); labels = src + dst
    fig = go.Figure(go.Sankey(node=dict(label=labels, color=T["orange"]),
        link=dict(source=[labels.index(a) for a in c["Booking_Status"]], target=[labels.index(b) for b in c["Cancellation_Reason"]], value=c["n"])))
    return theme(fig, "Booking status to recorded reason", 420)
