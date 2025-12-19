"""
Render Deployment Entry Point for Universal RL Dashboard
"""
import os
import streamlit as st
from universal_dashboard import *

# Render configuration
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    # Run Streamlit with Render configuration
    st.set_page_config(
        page_title="Universal RL Dashboard - Fusion Sprint",
        page_icon="🤖",
        layout="wide"
    )
    
    # The dashboard code will run automatically when imported
    pass