# Requirements: pip install streamlit yfinance pandas plotly

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# -------------------------------
# Sidebar – User Inputs for Simulation
# -------------------------------
st.sidebar.header("Refining Margin Simulator")

price_crude = st.sidebar.slider("Price of Crude Oil ($/barrel)", 50, 120, 75)
price_refined = st.sidebar.slider("Price of Refined Product ($/barrel)", 60, 140, 100)
refining_costs = st.sidebar.slider("Refining + Transport Costs ($/barrel)", 0, 30, 10)

# Margin Calculation
net_margin = price_refined - price_crude - refining_costs

st.sidebar.markdown(f"**Net Margin: ${net_margin:.2f}/barrel**")

if net_margin > 15:
    st.sidebar.success("✅ Healthy Margin")
elif net_margin > 5:
    st.sidebar.info("⚠️ Tight Margin")
else:
    st.sidebar.error("🔻 Unprofitable")

# -------------------------------
# Main Title
# -------------------------------
st.title("🛢️ Crack Spread Monitor & Refining Margin Tool")

# -------------------------------
# User-defined Date Range
# -------------------------------
st.sidebar.header("Date Range")
default_end = datetime.today()
default_start = default_end - timedelta(days=180)

start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", default_end)

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

# -------------------------------
# Load Data
# -------------------------------
tickers = {
    "WTI Crude Oil": "CL=F",
    "RBOB Gasoline": "RB=F"
}

raw_data = yf.download(
    tickers=list(tickers.values()),
    start=start_date,
    end=end_date,
    auto_adjust=False
)["Close"]

raw_data.columns = list(tickers.keys())
raw_data.dropna(inplace=True)

# Convert RBOB from $/gallon to $/barrel (1 barrel = 42 gallons)
raw_data["RBOB per barrel"] = raw_data["RBOB Gasoline"] * 42
raw_data["Crack Spread"] = raw_data["RBOB per barrel"] - raw_data["WTI Crude Oil"]

# Add 7-day moving average
raw_data["Spread 7D MA"] = raw_data["Crack Spread"].rolling(window=7).mean()

# -------------------------------
# Alerte en cas de crack spread négatif
# -------------------------------
latest_spread = raw_data["Crack Spread"].iloc[-1]
if latest_spread < 0:
    st.error(f"⚠️ Crack Spread actuellement négatif : {latest_spread:.2f} $/barrel")
else:
    st.success(f"✅ Crack Spread actuel : {latest_spread:.2f} $/barrel")

# -------------------------------
# Plotly Interactive Graph
# -------------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(x=raw_data.index, y=raw_data["Crack Spread"], mode="lines", name="Crack Spread"))
fig.add_trace(go.Scatter(x=raw_data.index, y=raw_data["Spread 7D MA"], mode="lines", name="7D MA", line=dict(dash="dot")))
fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.update_layout(title="📈 Crack Spread (RBOB – WTI)", xaxis_title="Date", yaxis_title="Spread ($/barrel)")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Show Table
# -------------------------------
st.subheader("🗃️ Raw Data (Last 15 rows)")
st.dataframe(raw_data[["WTI Crude Oil", "RBOB Gasoline", "RBOB per barrel", "Crack Spread", "Spread 7D MA"]].tail(15))

# -------------------------------
# Export Button
# -------------------------------
csv = raw_data.to_csv(index=True).encode('utf-8')
st.download_button("📥 Télécharger les données CSV", data=csv, file_name="crack_spread_data.csv", mime='text/csv')

# -------------------------------
# Contextual Insights
# -------------------------------
with st.expander("ℹ️ Contexte et Analyse"):
    st.markdown("""
    Le **crack spread** est un indicateur clé de la rentabilité des raffineries.  
    Il reflète l'écart entre le prix du brut et celui des produits raffinés.

    - Un spread élevé signifie des marges de raffinage saines.
    - Un spread négatif peut indiquer une demande faible en essence ou une hausse du prix du brut.

    **Facteurs impactant le spread** :
    - Tensions géopolitiques (ex. Moyen-Orient, OPEP+)
    - Saison (demande d’essence élevée en été)
    - Stocks et raffineries en maintenance
    - Réglementation sur les carburants

    Pour aller plus loin :
    - [EIA Crack Spread Analysis](https://www.eia.gov/todayinenergy/)
    - [OPEC News](https://www.opec.org/opec_web/en/)
    """)
