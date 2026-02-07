import streamlit as st
import pandas as pd
import json
import os
import time
import asyncio
import websockets
import threading

POS_FILE = 'kalshi_positions.json'
LOG_FILE = 'kalshi_bot.log'
CONFIG_FILE = 'kalshi_config.json'

# WebSocket client to receive live updates from bot
async def ws_listener():
    uri = "ws://127.0.0.1:8765"
    try:
        async with websockets.connect(uri) as ws:
            while True:
                msg = await ws.recv()
                st.session_state['live_data'] = json.loads(msg)
    except Exception as e:
        st.error(f"WebSocket connection failed: {e}")

if 'live_data' not in st.session_state:
    st.session_state['live_data'] = {"positions": {}, "logs": [], "arb_opps": []}
    threading.Thread(target=asyncio.run, args=(ws_listener(),), daemon=True).start()

st.title("Kalshi Trading Bot Dashboard")
st.write("Live updates • Orlando, FL • Feb 2026")

tab1, tab2, tab3 = st.tabs(["Positions & P&L", "Logs", "Arbitrage Opportunities"])

with tab1:
    st.subheader("Current Positions")
    data = st.session_state['live_data'].get('positions', {})
    if data:
        rows = []
        for mid, pos in data.items():
            rows.append({
                'Market': mid,
                'Side': pos.get('side', '?'),
                'Qty': pos.get('qty', 0),
                'Entry': pos.get('entry_price', 0)
            })
        st.dataframe(pd.DataFrame(rows))
    else:
        st.info("No positions loaded yet")

with tab2:
    st.subheader("Recent Logs")
    logs = st.session_state['live_data'].get('logs', [])
    st.text_area("Logs", "\n".join(logs[-30:]), height=400)

with tab3:
    st.subheader("Detected Arbitrage Opportunities")
    opps = st.session_state['live_data'].get('arb_opps', [])
    if opps:
        st.dataframe(pd.DataFrame(opps))
    else:
        st.info("No arbitrage opportunities detected right now")

st.markdown("---")
if st.button("Refresh now"):
    st.rerun()

# Auto-refresh every 10 seconds
time.sleep(10)
st.rerun()
