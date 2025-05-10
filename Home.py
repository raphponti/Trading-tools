import streamlit as st
import base64
from pathlib import Path

st.set_page_config(page_title="Commodity Tools by Raphaël Ponticelli", layout="wide")

# ------------
# Header
# ------------
st.title("📊 Commodity Analytics Tools")
st.markdown("### by Raphaël Ponticelli")

st.markdown("""
Welcome! I'm a finance professional with experience at Société Générale, JP Morgan and Crédit Agricole.  
I develop custom tools in Python to explore **commodity market dynamics**.
""")

# LinkedIn + CV buttons
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("[📎 LinkedIn](https://www.linkedin.com/in/raphaël-ponticelli-100462180/)", unsafe_allow_html=True)

with col2:
    with open("Ponticelli, Raphael - CV.pdf", "rb") as pdf_file:
        pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        href = f'<a href="data:application/octet-stream;base64,{pdf_base64}" download="Raphael_Ponticelli_CV.pdf">📄 Download my CV</a>'
        st.markdown(href, unsafe_allow_html=True)

st.markdown("---")

# ------------
# Tools Display
# ------------
st.subheader("🧰 Available Tools")

tool_cols = st.columns(3)

with tool_cols[0]:
    st.markdown("### 🛢️ Crack Spread Monitor")
    st.markdown("Track gasoline–crude spread and simulate refining margins.")
    st.markdown("[Launch →](./Crack_Spread_Monitor)")

with tool_cols[1]:
    st.markdown("### 🛢️ Brent-WTI Arbitrage")
    st.markdown("Coming soon: detect anomalies in crude benchmark spreads.")
    st.markdown("🚧 Coming soon")

with tool_cols[2]:
    st.markdown("### 📈 Forward Curve Analyzer")
    st.markdown("Coming soon: visualize CL1–CL12 and structure of futures curves.")
    st.markdown("🚧 Coming soon")

st.markdown("---")

st.info("More tools are in development. Stay tuned!")

