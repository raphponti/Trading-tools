import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Commodity Tools", layout="centered")

st.title("📊 Commodity Analytics Tools")

st.markdown("""
Welcome to my interactive commodity market toolkit.  
Select a tool below or use the sidebar on the left.
""")

tool = st.selectbox("🔧 Choose a tool to launch:", [
    "🏠 Home",
    "🛢️ Crack Spread Monitor",
    "🛢️ Brent-WTI Arbitrage (coming soon)",
    "📈 Forward Curve Viewer (coming soon)"
])

if tool == "🛢️ Crack Spread Monitor":
    switch_page("Crack_Spread_Monitor")
elif tool != "🏠 Home":
    st.warning("🚧 This tool is not yet available. Stay tuned!")
