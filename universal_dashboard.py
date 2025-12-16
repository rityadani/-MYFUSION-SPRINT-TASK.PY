"""
Universal RL Dashboard - Visualize RL decisions per app
Requires: pip install streamlit pandas plotly
Run: streamlit run universal_dashboard.py
"""
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Universal RL Dashboard", layout="wide")

st.title("🤖 Universal RL Decision Dashboard")
st.markdown("Real-time RL decisions, rewards, and state transitions")

# Load data
@st.cache_data(ttl=5)
def load_rl_events():
    """Load RL events from CSV"""
    log_file = "logs/rl_universal/rl_events.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        return df
    return pd.DataFrame()

@st.cache_data(ttl=10)
def load_policy():
    """Load current policy"""
    policy_file = "rl/policy_runtime.json"
    if os.path.exists(policy_file):
        with open(policy_file, 'r') as f:
            return json.load(f)
    return {}

@st.cache_data(ttl=10)
def load_summary():
    """Load test summary"""
    summary_file = "reports/fusion_rl_summary.json"
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as f:
            return json.load(f)
    return {}

# Sidebar - App selector
st.sidebar.header("🎯 App Selection")
df = load_rl_events()

if not df.empty:
    apps = df['app_name'].unique().tolist()
    selected_app = st.sidebar.selectbox("Select App", apps)
    
    # Filter by app
    app_df = df[df['app_name'] == selected_app]
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Decisions", len(app_df))
    
    with col2:
        total_reward = app_df['reward'].astype(float).sum()
        st.metric("Total Reward", f"{total_reward:.2f}")
    
    with col3:
        avg_q = app_df['q_value'].astype(float).mean()
        st.metric("Avg Q-Value", f"{avg_q:.4f}")
    
    with col4:
        unique_actions = app_df['action'].nunique()
        st.metric("Actions Used", unique_actions)
    
    # Last 10 decisions
    st.subheader(f"📋 Last 10 RL Decisions - {selected_app}")
    recent = app_df.tail(10)[['timestamp', 'env', 'state', 'action', 'reward', 'q_value']]
    st.dataframe(recent, use_container_width=True)
    
    # Reward curve
    st.subheader("📈 Reward Curve Over Time")
    app_df['cumulative_reward'] = app_df['reward'].astype(float).cumsum()
    fig_reward = px.line(app_df, y='cumulative_reward', 
                         title=f'Cumulative Reward - {selected_app}',
                         labels={'cumulative_reward': 'Cumulative Reward', 'index': 'Decision #'})
    st.plotly_chart(fig_reward, use_container_width=True)
    
    # Action frequency
    st.subheader("📊 Action Frequency")
    action_counts = app_df['action'].value_counts()
    fig_actions = px.bar(x=action_counts.index, y=action_counts.values,
                         labels={'x': 'Action', 'y': 'Count'},
                         title=f'Action Distribution - {selected_app}')
    st.plotly_chart(fig_actions, use_container_width=True)
    
    # State transitions
    st.subheader("🔄 State Transitions Log")
    transitions = app_df[['timestamp', 'state', 'action']].tail(20)
    st.dataframe(transitions, use_container_width=True)
    
    # Policy viewer
    st.subheader("🧠 Current Policy (Q-Table)")
    policy = load_policy()
    if policy and 'q_table' in policy:
        q_table = policy['q_table']
        # Filter for selected app
        app_q = {k: v for k, v in q_table.items() if selected_app in k}
        if app_q:
            q_df = pd.DataFrame(list(app_q.items()), columns=['State-Action', 'Q-Value'])
            q_df = q_df.sort_values('Q-Value', ascending=False)
            st.dataframe(q_df.head(20), use_container_width=True)
        else:
            st.info("No policy learned yet for this app")
    
else:
    st.warning("⚠ No RL events found. Run `python run_universal_rl_cycle.py` first.")

# Summary section
st.sidebar.markdown("---")
st.sidebar.header("📊 Overall Summary")
summary = load_summary()
if summary:
    st.sidebar.metric("Apps Tested", summary.get('total_apps', 0))
    st.sidebar.metric("Total Actions", summary.get('total_actions_taken', 0))
    st.sidebar.metric("Total Rewards", f"{summary.get('total_rewards_accumulated', 0):.2f}")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Ritesh DevOps - Fusion Sprint**")
st.sidebar.markdown("RL Decision Intelligence Layer")
