import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIG
st.set_page_config(page_title="Zion Game: Host", layout="wide")

# 2. INITIALIZE SESSION STATE
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0

conn = st.connection("gsheets", type=GSheetsConnection)

# 3. SIDEBAR CONFIG
with st.sidebar:
    st.header("Event Configuration")
    # Note: These sliders are visual; the actual
