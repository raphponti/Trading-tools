import streamlit as st

st.set_page_config(page_title="Commodity Tools", layout="centered")

st.title("📊 Commodity Analytics Tools")

st.markdown("""
Welcome to my interactive commodity market toolkit.  
Use the **sidebar on the left** or click below to open a tool.
""")

st.markdown("### 🔧 Available Tools")

st.markdown("""
- [🛢️ Crack Spread Monitor](./Crack_Spread_Monitor)
- 🛠️ Brent-WTI Arbitrage *(coming soon)*
- 📈 Forward Curve Viewer *(coming soon)*
""")

st.info("More tools coming soon. Stay tuned!")
