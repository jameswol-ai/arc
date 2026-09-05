# =========================================================
# Forex data, rates, conversion, history, forest
# =========================================================
import random

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

STATIC_FX = {
    "Kenya": 129.49,
    "Uganda": 3665.20,
    "Tanzania": 2625.00,
    "South Sudan": 4626.40,
    "Rwanda": 1330.00,
    "Ethiopia": 125.00,
}
BASE_FX = {
    "Kenya": ("KES", "KSh", 1.00, "East Africa"),
    "Uganda": ("UGX", "USh", 0.95, "East Africa"),
    "Tanzania": ("TZS", "TSh", 0.98, "East Africa"),
    "South Sudan": ("SSP", "SSP", 1.35, "East Africa"),
    "Rwanda": ("RWF", "FRw", 0.85, "Central Africa"),
    "Ethiopia": ("ETB", "Br", 0.80, "Horn of Africa"),
}


def _fetch_live():
    try:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD", timeout=5
        )
        response.raise_for_status()
        data = response.json().get("rates", {})
        mapping = {
            "Kenya": "KES",
            "Uganda": "UGX",
            "Tanzania": "TZS",
            "South Sudan": "SSP",
            "Rwanda": "RWF",
            "Ethiopia": "ETB",
        }
        return {country: data[currency] for country, currency in mapping.items() if currency in data}
    except (requests.RequestException, ValueError, TypeError):
        return {}


@st.cache_resource
def init_fx():
    live = _fetch_live()
    current_rates = {}
    baseline_rates = {}
    currency_info = {}
    for country, (currency, symbol, multiplier, region) in BASE_FX.items():
        rate = live.get(country, STATIC_FX[country])
        current_rates[country] = rate
        baseline_rates[country] = rate * random.uniform(0.995, 1.005)
        currency_info[country] = {
            "currency": currency,
            "symbol": symbol,
            "multiplier": multiplier,
            "region": region,
        }
    return current_rates, baseline_rates, currency_info


_CURRENT_RATES, _BASELINE_RATES, _CURRENCY_INFO = init_fx()


def get_fx(country):
    if country not in _CURRENCY_INFO:
        raise KeyError(f"Unsupported country: {country}")
    return _CURRENCY_INFO[country].copy() | {"rate": _CURRENT_RATES[country]}


def get_all_countries():
    return list(STATIC_FX.keys())


def convert_currency(amount, frm, to):
    if frm == to:
        return amount
    usd = amount if frm == "USD" else amount / _CURRENT_RATES[frm]
    return usd if to == "USD" else usd * _CURRENT_RATES[to]


def fetch_hist(start, end):
    try:
        url = (
            "https://api.exchangerate.host/timeseries"
            f"?start_date={start}&end_date={end}&base=USD&symbols=KES,UGX,TZS,SSP,RWF,ETB"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json().get("rates", {})
        if not data:
            return None
        dates = sorted(data)
        currencies = ["KES", "UGX", "TZS", "SSP", "RWF", "ETB"]
        df = pd.DataFrame(
            {currency: [data[date].get(currency) for date in dates] for currency in currencies},
            index=pd.to_datetime(dates),
        ).ffill()
        return df
    except (requests.RequestException, ValueError, TypeError):
        return None


def plot_hist(df):
    fig = go.Figure()
    colors = {
        "KES": "#c96b3b",
        "UGX": "#5c8d89",
        "TZS": "#d6a85f",
        "SSP": "#9b6b9e",
        "RWF": "#4d7ea8",
        "ETB": "#7a8b99",
    }
    for currency in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[currency],
                mode="lines",
                name=currency,
                line=dict(color=colors.get(currency, "#94a3b8")),
            )
        )
    fig.update_layout(
        title="East African FX Rates | 60 days",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#d8dee9",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def forest(base, days=7, n_paths=100, vol=0.008):
    rng = np.random.default_rng(42)
    p = [rng.normal(0, vol, days) for _ in range(n_paths)]
    sim_paths = np.cumprod(1 + np.array(p), axis=1) * base
    fig = go.Figure()
    x = list(range(1, days + 1))
    band_colors = [
        (95, "rgba(201, 107, 59, 0.08)"),
        (80, "rgba(201, 107, 59, 0.15)"),
        (50, "rgba(201, 107, 59, 0.25)"),
    ]
    for perc, fill_color in band_colors:
        lower = np.percentile(sim_paths, (100 - perc) / 2, axis=0)
        upper = np.percentile(sim_paths, 100 - (100 - perc) / 2, axis=0)
        fig.add_trace(go.Scatter(x=x, y=upper, mode="lines", line=dict(width=0), showlegend=False))
        fig.add_trace(
            go.Scatter(
                x=x,
                y=lower,
                mode="lines",
                fill="tonexty",
                fillcolor=fill_color,
                line=dict(width=0),
                name=f"{perc}% confidence",
            )
        )
    median = np.median(sim_paths, axis=0)
    fig.add_trace(
        go.Scatter(
            x=x,
            y=median,
            mode="lines+markers",
            name="Median",
            line=dict(color="#e6b17e", width=2.5),
            marker=dict(color="#f1d0b0", size=6),
        )
    )
    fig.update_layout(
        title="Weekly Forecast",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#d8dee9",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig
