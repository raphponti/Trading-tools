import streamlit as st
import base64
from pathlib import Path

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Market Tools by Raphaël Ponticelli", layout="wide")

# -------------------------------
# Header
# -------------------------------
st.title("📊 Market Analytics Tools")
st.markdown("### by Raphaël Ponticelli")

st.markdown("""
Welcome! I'm a finance professional with experience at Société Générale, JP Morgan and Crédit Agricole.  
I develop interactive Python tools to analyze **ETF flows**, **market dislocations**, and **commodity dynamics**.
""")

# -------------------------------
# LinkedIn + CV
# -------------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("[📎 LinkedIn](https://www.linkedin.com/in/raphaël-ponticelli-100462180/)", unsafe_allow_html=True)

with col2:
    cv_path = Path("Ponticelli, Raphael - CV.pdf")
    if cv_path.exists():
        with open(cv_path, "rb") as pdf_file:
            pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
            href = f'<a href="data:application/octet-stream;base64,{pdf_base64}" download="Raphael_Ponticelli_CV.pdf">📄 Download my CV</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("CV not found. Please upload `Ponticelli, Raphael - CV.pdf`.")

st.markdown("---")

# -------------------------------
# ETF Tools
# -------------------------------
st.subheader("📈 ETF Analytics")

etf_cols = st.columns(2)

with etf_cols[0]:
    st.markdown("### 💸 ETF Flow Tracker")
    st.markdown("Visualize daily notional traded per ETF and detect unusual spikes.")
    st.markdown("[▶️ Launch](./ETF_Flow_Tracker)")

with etf_cols[1]:
    st.markdown("### 📉 ETF vs Proxy Tracker")
    st.markdown("Compare ETF prices to index proxies and detect NAV dislocations via Z-score.")
    st.markdown("[▶️ Launch](./ETF_vs_Proxy_Tracker)")

st.markdown("---")

# -------------------------------
# Commodity Tools
# -------------------------------
st.subheader("🛢️ Commodity Analytics")

commo_cols = st.columns(3)

with commo_cols[0]:
    st.markdown("### 🛢️ Crack Spread Monitor")
    st.markdown("Track gasoline–crude spread and simulate refining margins.")
    st.markdown("[▶️ Launch](./Crack_Spread_Monitor)")

with commo_cols[1]:
    st.markdown("### 🛢️ Brent-WTI Arbitrage")
    st.markdown("Detect anomalies in benchmark spreads using Z-score analysis.")
    st.markdown("[▶️ Launch](./Brent_WTI_Arbitrage)")

with commo_cols[2]:
    st.markdown("### 📈 Forward Curve Analyzer")
    st.markdown("Visualize CL1–CL12 to assess market structure (contango/backwardation).")
    st.markdown("🚧 Coming soon")

st.markdown("---")
st.info("More tools are in development. Stay tuned!")
