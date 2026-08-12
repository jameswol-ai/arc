# =========================================================
# Forex data, rates, conversion, history, forest
# =========================================================
import requests, random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

STATIC_FX = {"Kenya":129.49, "Uganda":3665.20, "Tanzania":2625.00, "South Sudan":4626.40, "Rwanda":1330.00, "Ethiopia":125.00}
BASE_FX = {
    "Kenya": ("KES","KSh",1.00,"East Africa"),
    "Uganda": ("UGX","USh",0.95,"East Africa"),
    "Tanzania": ("TZS","TSh",0.98,"East Africa"),
    "South Sudan": ("SSP","SSP",1.35,"East Africa"),
    "Rwanda": ("RWF","FRw",0.85,"Central Africa"),
    "Ethiopia": ("ETB","Br",0.80,"Horn of Africa")
}

def _fetch_live():
    try:
        data = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()["rates"]
        mapping = {"Kenya":"KES","Uganda":"UGX","Tanzania":"TZS","South Sudan":"SSP","Rwanda":"RWF","Ethiopia":"ETB"}
        return {c: data[m[c]] for c in mapping if m[c] in data}
    except:
        return {}

@st.cache_resource
def init_fx():
    live = _fetch_live()
    current_rates = {}
    baseline_rates = {}
    currency_info = {}
    for c, (cur, sym, mult, reg) in BASE_FX.items():
        rate = live.get(c, STATIC_FX[c])
        current_rates[c] = rate
        baseline_rates[c] = rate * random.uniform(0.995, 1.005)
        currency_info[c] = {"currency": cur, "symbol": sym, "multiplier": mult, "region": reg}
    return current_rates, baseline_rates, currency_info

_CURRENT_RATES, _BASELINE_RATES, _CURRENCY_INFO = init_fx()

def get_fx(country):
    return _CURRENCY_INFO[country].copy() | {"rate": _CURRENT_RATES[country]}

def get_all_countries():
    return list(STATIC_FX.keys())

def convert_currency(amount, frm, to):
    if frm == to: return amount
    usd = amount if frm == "USD" else amount / _CURRENT_RATES[frm]
    return usd if to == "USD" else usd * _CURRENT_RATES[to]

def fetch_hist(start, end):
    try:
        url = f"https://api.exchangerate.host/timeseries?start_date={start}&end_date={end}&base=USD&symbols=KES,UGX,TZS,SSP,RWF,ETB"
        data = requests.get(url, timeout=10).json()["rates"]
        df = pd.DataFrame({c: [data[d].get(c) for d in sorted(data)] for c in ["KES","UGX","TZS","SSP","RWF","ETB"]},
                          index=pd.to_datetime(sorted(data.keys()))).ffill()
        return df
    except:
        return None

def plot_hist(df):
    fig = go.Figure()
    colors = {"KES":"#888","UGX":"#aaa","TZS":"#666","SSP":"#999","RWF":"#777","ETB":"#555"}
    for c in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[c], mode='lines', name=c, line=dict(color=colors.get(c,'#94a3b8'))))
    fig.update_layout(title="East African FX Rates – 60 days",
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      font_color='#aaaaaa', margin=dict(l=20,r=20,t=40,b=20))
    return fig

def forest(base, days=7, n_paths=100, vol=0.008):
    rng = np.random.default_rng(42)
    p = [rng.normal(0, vol, days) for _ in range(n_paths)]
    sim_paths = np.cumprod(1 + np.array(p), axis=1) * base
    fig = go.Figure()
    x = list(range(1, days+1))
    band_colors = [
        (95, "rgba(70, 130, 200, 0.08)"),
        (80, "rgba(70, 130, 200, 0.15)"),
        (50, "rgba(70, 130, 200, 0.25)")
    ]
    for perc, fill_color in band_colors:
        lower = np.percentile(sim_paths, (100-perc)/2, axis=0)
        upper = np.percentile(sim_paths, 100 - (100-perc)/2, axis=0)
        fig.add_trace(go.Scatter(x=x, y=upper, mode='lines', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=x, y=lower, mode='lines', fill='tonexty', fillcolor=fill_color,
                                 line=dict(width=0), name=f'{perc}% confidence'))
    median = np.median(sim_paths, axis=0)
    fig.add_trace(go.Scatter(x=x, y=median, mode='lines+markers', name='Median',
                             line=dict(color='#7bb8ff', width=2.5),
                             marker=dict(color='#b0d0ff', size=6)))
    fig.update_layout(title="Weekly Forecast",
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      font_color='#aaaaaa', margin=dict(l=20,r=20,t=40,b=20),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return fig