# Requirements: pip install streamlit yfinance pandas plotly

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --------------------------------
# Config Streamlit
# --------------------------------
st.set_page_config(page_title="ETF vs Proxy Tracker", layout="wide")
st.title("📈 ETF vs Proxy Tracker")
st.markdown("Compare ETF performance against its benchmark proxy and identify dislocations (Z-score).")

# --------------------------------
# Sidebar Inputs
# --------------------------------
st.sidebar.header("📌 Select ETF and Proxy")

etf_mapping = {
    "SPDR S&P 500 ETF Trust (SPY)": {"ticker": "SPY", "proxy": "^GSPC", "currency": "USD"},
    "Invesco QQQ Trust (QQQ)": {"ticker": "QQQ", "proxy": "^IXIC", "currency": "USD"},
    "iShares Core MSCI EM (IEMG)": {"ticker": "IEMG", "proxy": "EEM", "currency": "USD"},
    "iShares Core Euro Stoxx 50 (CSX5.DE)": {"ticker": "CSX5.DE", "proxy": "^STOXX50E", "currency": "EUR"}
}

etf_name = st.sidebar.selectbox("ETF", list(etf_mapping.keys()))
etf_ticker = etf_mapping[etf_name]["ticker"]
proxy_ticker = etf_mapping[etf_name]["proxy"]
currency = etf_mapping[etf_name]["currency"]

# Date range
st.sidebar.header("📅 Date Range")
end_date = datetime.today()
start_date = st.sidebar.date_input("Start Date", end_date - timedelta(days=180))
end_date = st.sidebar.date_input("End Date", end_date)

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

# Z-score window
st.sidebar.header("⚙️ Z-score Settings")
window = st.sidebar.selectbox("Rolling Window (days)", [10, 20, 30], index=1)

# --------------------------------
# Download Data
# --------------------------------
st.info(f"📦 Fetching data for `{etf_ticker}` and `{proxy_ticker}`...")
data = yf.download([etf_ticker, proxy_ticker], start=start_date, end=end_date)["Close"]

# If multi-index, flatten columns
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [f"{col[1]}" for col in data.columns]

data.dropna(inplace=True)

# --------------------------------
# FX Adjustment (if needed)
# --------------------------------
if currency == "EUR":
    fx = yf.download("EURUSD=X", start=start_date, end=end_date)["Close"]
    fx.name = "EURUSD"
    data = data.join(fx, how="left")
    data[etf_ticker] = data[etf_ticker] * data["EURUSD"]

# --------------------------------
# Calculate Spread and Z-score
# --------------------------------
data["Spread"] = data[etf_ticker] - data[proxy_ticker]
data["Z-score"] = (data["Spread"] - data["Spread"].rolling(window).mean()) / data["Spread"].rolling(window).std()

# --------------------------------
# Plot Z-score
# --------------------------------
fig = px.line(
    data,
    x=data.index,
    y="Z-score",
    title=f"{etf_name} vs Proxy - Rolling Z-score ({window}d)",
    labels={"Z-score": "Z-score"},
    height=500
)
fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.add_hline(y=1.5, line_dash="dot", line_color="green")
fig.add_hline(y=-1.5, line_dash="dot", line_color="red")
st.plotly_chart(fig, use_container_width=True)

# --------------------------------
# Last Data Points
# --------------------------------
st.subheader("🧾 Latest Data")
st.dataframe(data[[etf_ticker, proxy_ticker, "Spread", "Z-score"]].tail(10))

# --------------------------------
# Export CSV
# --------------------------------
csv = data.to_csv(index=True).encode("utf-8")
st.download_button("📥 Download CSV", data=csv, file_name=f"{etf_ticker}_vs_proxy.csv", mime="text/csv")
