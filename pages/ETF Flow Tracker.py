# Requirements: pip install streamlit yfinance pandas plotly seaborn

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
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
raw = yf.download(etf_ticker, start=start_date, end=end_date, group_by='ticker')

# Sélectionner juste les colonnes de l'ETF
if isinstance(raw.columns, pd.MultiIndex):
    data = raw[etf_ticker].copy()
else:
    data = raw.copy()

# Vérification
if "Close" not in data.columns or "Volume" not in data.columns:
    st.error("❌ Could not find required columns (Close, Volume) in data.")
    st.stop()

# --------------------------------
# Calculs
# --------------------------------
data["Daily $ Flow"] = data["Close"] * data["Volume"] / 1e6
data["Z-score"] = (data["Daily $ Flow"] - data["Daily $ Flow"].rolling(20).mean()) / data["Daily $ Flow"].rolling(20).std()

# --------------------------------
# Graphique principal
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
# Graphique Z-score
# --------------------------------
st.subheader("📉 Flow Z-Score (Volatility-adjusted)")

fig_z = px.line(
    data,
    x=data.index,
    y="Z-score",
    title=f"{etf_name} - Z-Score of Daily Flow",
    labels={"Z-score": "Z-score"}
)
st.plotly_chart(fig_z, use_container_width=True)

# --------------------------------
# Heatmap mensuelle (seaborn)
# --------------------------------
st.subheader("🗓️ Monthly Flow Heatmap")

heatmap_data = data[["Daily $ Flow"]].copy()
heatmap_data["Date"] = heatmap_data.index
heatmap_data["Month"] = heatmap_data["Date"].dt.strftime('%b-%Y')
heatmap_data["Day"] = heatmap_data["Date"].dt.day

pivot = heatmap_data.pivot(index="Day", columns="Month", values="Daily $ Flow")

fig2, ax = plt.subplots(figsize=(12, 5))
sns.heatmap(pivot, cmap="YlOrRd", ax=ax)
plt.title("Heatmap of Daily $ Flows by Month")
st.pyplot(fig2)

# --------------------------------
# Table
# --------------------------------
st.subheader("🧾 Last 10 Days Data")
st.dataframe(data[["Close", "Volume", "Daily $ Flow", "Z-score"]].tail(10))

# --------------------------------
# Export
# --------------------------------
csv = data.to_csv(index=True).encode("utf-8")
st.download_button("📥 Download CSV", data=csv, file_name=f"{etf_ticker}_flows.csv", mime="text/csv")
