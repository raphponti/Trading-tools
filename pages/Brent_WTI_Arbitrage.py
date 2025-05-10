# Requirements: pip install streamlit yfinance pandas plotly

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ----------------------------------
# Title
# ----------------------------------
st.title("🛢️ Brent-WTI Arbitrage Detector")
st.markdown("""
This tool monitors the spread between **Brent Crude (BZ=F)** and **WTI Crude (CL=F)**, 
calculates a rolling **Z-score**, and flags potential **pricing anomalies** that may offer arbitrage opportunities.
""")

# ----------------------------------
# Sidebar – User inputs
# ----------------------------------
st.sidebar.header("Settings")

lookback_days = st.sidebar.slider("Lookback Period (days)", 90, 365, 180)
z_threshold = st.sidebar.slider("Z-score Anomaly Threshold", 1.5, 3.0, 2.0)

# Date range
end_date = datetime.today()
start_date = end_date - timedelta(days=lookback_days)

# ----------------------------------
# Load data from Yahoo Finance
# ----------------------------------
tickers = {
    "Brent": "BZ=F",
    "WTI": "CL=F"
}

df = yf.download(list(tickers.values()), start=start_date, end=end_date)["Close"]
df.columns = list(tickers.keys())
df.dropna(inplace=True)

# Compute spread and Z-score
df["Spread"] = df["Brent"] - df["WTI"]
df["Spread_Mean"] = df["Spread"].rolling(window=30).mean()
df["Spread_Std"] = df["Spread"].rolling(window=30).std()
df["Z-Score"] = (df["Spread"] - df["Spread_Mean"]) / df["Spread_Std"]

# ----------------------------------
# Alert if current Z-score is high
# ----------------------------------
current_z = df["Z-Score"].iloc[-1]
current_spread = df["Spread"].iloc[-1]

if abs(current_z) > z_threshold:
    st.error(f"🔍 Z-score anomaly detected: **{current_z:.2f}** (Spread = {current_spread:.2f} $/barrel)")
    st.markdown("**Potential arbitrage signal** – consider investigating market fundamentals.")
else:
    st.success(f"✅ Spread within normal range (Z-score = {current_z:.2f})")

# ----------------------------------
# Plot 1: Spread chart with mean ± 2σ
# ----------------------------------
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=df.index, y=df["Spread"], name="Brent – WTI Spread", line=dict(color="orange")))
fig1.add_trace(go.Scatter(x=df.index, y=df["Spread_Mean"], name="30D Mean", line=dict(dash="dot", color="blue")))
fig1.add_trace(go.Scatter(x=df.index, y=df["Spread_Mean"] + 2*df["Spread_Std"], name="+2σ", line=dict(dash="dash", color="green")))
fig1.add_trace(go.Scatter(x=df.index, y=df["Spread_Mean"] - 2*df["Spread_Std"], name="-2σ", line=dict(dash="dash", color="red")))
fig1.update_layout(title="📈 Brent–WTI Spread with Statistical Bands", xaxis_title="Date", yaxis_title="Spread ($/barrel)")
st.plotly_chart(fig1, use_container_width=True)

# ----------------------------------
# Plot 2: Z-score chart
# ----------------------------------
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df.index, y=df["Z-Score"], name="Z-score", line=dict(color="purple")))
fig2.add_hline(y=z_threshold, line_dash="dash", line_color="gray")
fig2.add_hline(y=-z_threshold, line_dash="dash", line_color="gray")
fig2.update_layout(title="📉 Z-score of Brent–WTI Spread", xaxis_title="Date", yaxis_title="Z-score")
st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------
# Data Table
# ----------------------------------
st.subheader("📄 Recent Data")
st.dataframe(df[["Brent", "WTI", "Spread", "Z-Score"]].tail(15))

# ----------------------------------
# Strategy Insights
# ----------------------------------
with st.expander("🧠 Strategy Insights"):
    st.markdown(f"""
    **Current Z-score**: `{current_z:.2f}`  
    **Current Spread**: `{current_spread:.2f} $/barrel`

    - A **Z-score > {z_threshold}** suggests Brent is unusually expensive relative to WTI.
        - ✅ Potential strategy: Sell Brent, Buy WTI (mean reversion play).
    - A **Z-score < -{z_threshold}** suggests WTI is expensive relative to Brent.
        - ✅ Potential strategy: Sell WTI, Buy Brent.

    > Always consider fundamental factors (logistics, inventory levels, export bottlenecks) before acting on statistical signals.
    """)

# ----------------------------------
# Export Button
# ----------------------------------
csv = df.to_csv().encode("utf-8")
st.download_button("📥 Download CSV Data", data=csv, file_name="brent_wti_spread.csv", mime="text/csv")
