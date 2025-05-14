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
end_date_default = datetime.today()
start_date = st.sidebar.date_input("Start Date", end_date_default - timedelta(days=180))
end_date = st.sidebar.date_input("End Date", end_date_default)

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

# --------------------------------
# Download Data
# --------------------------------
st.info(f"📦 Fetching data for `{etf_ticker}`...")
data = yf.download(etf_ticker, start=start_date, end=end_date)

# Flatten MultiIndex if needed
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [col[0] for col in data.columns]

if "Close" not in data.columns or "Volume" not in data.columns:
    st.error("❌ Could not find required columns (Close, Volume) in data.")
    st.stop()

# --------------------------------
# Calculate Flows
# --------------------------------
data["Daily $ Flow"] = data["Close"] * data["Volume"] / 1e6  # in millions USD

# --------------------------------
# Plot
# --------------------------------
fig = px.bar(
    data,
    x=data.index,
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
st.dataframe(data[["Close", "Volume", "Daily $ Flow"]].tail(10))

# --------------------------------
# Export CSV
# --------------------------------
csv = data.to_csv(index=True).encode("utf-8")
st.download_button("📥 Download CSV", data=csv, file_name=f"{etf_ticker}_flows.csv", mime="text/csv")
