import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import warnings
from datetime import datetime
import plotly.graph_objects as go  # NAYA IMPORT (Advanced Charts ke liye)

warnings.filterwarnings('ignore')

# 1. Database Setup
conn = sqlite3.connect('trade_journal.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades 
             (timestamp TEXT, symbol TEXT, action TEXT, price REAL, quantity INTEGER)''')
conn.commit()

def save_trade(symbol, action, price, quantity):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO trades VALUES (?, ?, ?, ?, ?)", (now, symbol, action, price, quantity))
    conn.commit()

# Page UI Config
st.set_page_config(page_title="Ultimate AI Bot", page_icon="🤖", layout="wide")
st.title("🚀 Ultimate AI Trading Control Center")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["⚙️ Manual Setup", "📡 AI Radar", "📊 Live Portfolio"])

# ==========================================
# TAB 1: MANUAL SETUP & INTERACTIVE CHART
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚙️ Trade Setup")
        symbol = st.text_input("Stock Symbol", "RELIANCE.NS")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        
    with col2:
        st.subheader("⚡ Live Execution")
        if st.button("🔥 FIRE BUY ORDER", use_container_width=True):
            data = yf.download(tickers=symbol, period="5d", interval="1d", progress=False)
            if not data.empty:
                current_price = float(data['Close'].iloc[-1])
                save_trade(symbol, "BUY", current_price, quantity)
                st.success(f"✅ BUY Order Fired for {symbol} at ₹{current_price:.2f}!")
            else:
                st.error("Market Data Error.")

    st.markdown("---")
    st.subheader(f"📊 Live Candlestick Chart: {symbol}")
    
    # NAYA ADVANCED CHARTING SYSTEM
    chart_data = yf.download(tickers=symbol, period="6mo", interval="1d", progress=False)
    if not chart_data.empty:
        # Simple Moving Averages calculate kar rahe hain
        chart_data['SMA_50'] = chart_data['Close'].rolling(window=50).mean()
        
        # Plotly Figure Banana
        fig = go.Figure()
        
        # Candlestick add karna
        fig.add_trace(go.Candlestick(x=chart_data.index,
                        open=chart_data['Open'].squeeze(),
                        high=chart_data['High'].squeeze(),
                        low=chart_data['Low'].squeeze(),
                        close=chart_data['Close'].squeeze(),
                        name='Price'))
        
        # 50 Day Moving Average ki line add karna
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA_50'].squeeze(), 
                                 line=dict(color='orange', width=2), name='50 SMA'))
        
        # Chart ka design professional karna
        fig.update_layout(
            template='plotly_dark', # Dark mode for pro look
            xaxis_rangeslider_visible=False,
            height=500,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        # Streamlit me render karna
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Chart data load nahi ho paaya.")

# ==========================================
# TAB 2 & TAB 3 (Purana Code Same Rahega)
# ==========================================
# (Main yahan code short rakh raha hu taki error na aaye, Tab 2 aur 3 ka code wahi pichla wala rakhna agar alag file me paste kar rahe ho)
