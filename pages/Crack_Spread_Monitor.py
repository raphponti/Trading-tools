# Requirements: pip install streamlit yfinance pandas plotly openai

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from openai import OpenAI
import os

# -------------------------------
# Sidebar 
# -------------------------------
st.sidebar.header("Refining Margin Simulator")

price_crude = st.sidebar.slider("Crude Oil Price ($/barrel)", 50, 120, 75)
price_refined = st.sidebar.slider("Refined Product Price ($/barrel)", 60, 140, 100)
refining_costs = st.sidebar.slider("Refining + Transport Costs ($/barrel)", 0, 30, 10)
show_ma = st.sidebar.checkbox("Show 7-Day Moving Average", value=True)

net_margin = price_refined - price_crude - refining_costs
st.sidebar.markdown(f"**Net Margin: ${net_margin:.2f}/barrel**")
if net_margin > 15:
    st.sidebar.success("✅ Healthy Margin")
elif net_margin > 5:
    st.sidebar.info("⚠️ Tight Margin")
else:
    st.sidebar.error("🔻 Unprofitable")

# -------------------------------
# Date Selection
# -------------------------------
st.sidebar.header("Select Date Range")
default_end = datetime.today()
default_start = default_end - timedelta(days=180)

start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", default_end)

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

# -------------------------------
# Title
# -------------------------------
st.title("🛢️ Crack Spread Monitor & Refining Margin Tool")

# -------------------------------
# Load Data
# -------------------------------
tickers = {"WTI Crude Oil": "CL=F", "RBOB Gasoline": "RB=F"}
raw_data = yf.download(list(tickers.values()), start=start_date, end=end_date)["Close"]
raw_data.columns = list(tickers.keys())
raw_data.dropna(inplace=True)

raw_data["RBOB per barrel"] = raw_data["RBOB Gasoline"] * 42
raw_data["Crack Spread"] = raw_data["RBOB per barrel"] - raw_data["WTI Crude Oil"]
raw_data["Spread 7D MA"] = raw_data["Crack Spread"].rolling(window=7).mean()

# -------------------------------
# Alert
# -------------------------------
latest_spread = raw_data["Crack Spread"].iloc[-1]
if latest_spread < 0:
    st.error(f"⚠️ Crack Spread is currently negative: ${latest_spread:.2f}/barrel")
else:
    st.success(f"✅ Crack Spread is currently: ${latest_spread:.2f}/barrel")

# -------------------------------
# Graph
# -------------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=raw_data.index,
    y=raw_data["Crack Spread"],
    name="Crack Spread",
    mode="lines",
    line=dict(color="orange" if latest_spread > 0 else "red")
))
if show_ma:
    fig.add_trace(go.Scatter(
        x=raw_data.index,
        y=raw_data["Spread 7D MA"],
        name="7D Moving Average",
        mode="lines",
        line=dict(dash="dot", color="blue")
    ))
fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.update_layout(title="📈 Crack Spread (RBOB – WTI)", xaxis_title="Date", yaxis_title="Spread ($/barrel)")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Data Table + Export
# -------------------------------
st.subheader("📄 Last 15 Data Points")
st.dataframe(raw_data[["WTI Crude Oil", "RBOB Gasoline", "RBOB per barrel", "Crack Spread", "Spread 7D MA"]].tail(15))
csv = raw_data.to_csv().encode("utf-8")
st.download_button("📥 Download CSV", data=csv, file_name="crack_spread_data.csv", mime="text/csv")

# -------------------------------
# AI Commentary
# -------------------------------
with st.expander("🧠 Market Commentary (AI Generated)"):
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning("Please set your OpenAI API key to enable this feature.")
    else:
        client = OpenAI(api_key=api_key)
        prompt = f"""
        The current crack spread is {latest_spread:.2f} USD/barrel.
        As a market strategist, explain why the spread is at this level.
        Consider supply/demand, seasonality, geopolitical context, and market conditions.
        Then suggest 1–2 strategies a trader could explore in this environment.
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error from OpenAI: {e}")

# -------------------------------
# Education
# -------------------------------
with st.expander("ℹ️ What is the Crack Spread?"):
    st.markdown("""
    The **crack spread** measures the profitability of turning crude oil into refined products like gasoline.  
    A high spread implies strong refining margins; a negative spread suggests cost pressures or weak demand.

    **Influencing factors include**:
    - Crude oil price volatility
    - Gasoline demand (e.g. seasonal driving trends)
    - Geopolitical events (e.g. OPEC decisions, wars)
    - Refinery capacity and outages

    🔗 [EIA Today in Energy](https://www.eia.gov/todayinenergy/)  
    🔗 [OPEC Newsroom](https://www.opec.org/opec_web/en/)
    """)