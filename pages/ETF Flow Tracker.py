# Requirements: pip install streamlit yfinance pandas plotly

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --------------------------------
# Page config
# --------------------------------
st.set_page_config(page_title="ETF Flow Tracker", layout="wide")
st.title("📊 ETF Flow Tracker")
st.markdown("Visualize daily notional traded for selected ETFs.")

# --------------------------------
# Sidebar Inputs
# --------------------------------
st.sidebar.header("📌 Select an ETF")

etf_options = {
    "SPDR S&P 500 ETF Trust (SPY)": "SPY",
    "iShares Core MSCI EM (IEMG)": "IEMG",
    "Invesco QQQ Trust (QQQ)": "QQQ",
    "iShares Core Euro Stoxx 50 (CSX5.DE)": "CSX5.DE"
}

etf_name = st.sidebar.selectbox("ETF", list(etf_options.keys()))
etf_ticker = etf_options[etf_name]

# Date range
st.sidebar.header("📅 Date Range")
end_date = datetime.today()
start_date = st.sidebar.date_input("Start Date", end_date - timedelta(days=180))
end_date = st.sidebar.date_input("End Date", end_date)

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

# --------------------------------
# Download Data
# --------------------------------
st.info(f"Fetching data for {etf_ticker}...")
raw = yf.download(etf_ticker, start=start_date, end=end_date)

# Vérification des colonnes
if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = [col[0] for col in raw.columns]  # Flatten multi-index

if "Close" not in raw.columns or "Volume" not in raw.columns:
    st.error("Failed to load price or volume data.")
    st.stop()

# --------------------------------
# Calculer les flows
# --------------------------------
raw["Daily $ Flow"] = raw["Close"] * raw["Volume"] / 1e6  # en millions $

# --------------------------------
# Plot
# --------------------------------
fig = px.bar(
    raw,
    x=raw.index,
    y="Daily $ Flow",
    title=f"{etf_name} - Daily Notional Traded ($M)",
    labels={"Daily $ Flow": "$ Millions"},
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# --------------------------------
# Show table
# --------------------------------
st.subheader("🧾 Last 10 Days Data")
st.dataframe(raw[["Close", "Volume", "Daily $ Flow"]].tail(10))

# --------------------------------
# Export CSV
# --------------------------------
csv = raw.to_csv(index=True).encode("utf-8")
st.download_button("📥 Download CSV", data=csv, file_name=f"{etf_ticker}_flows.csv", mime="text/csv")
