import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import warnings
from datetime import datetime

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

tab1, tab2, tab3 = st.tabs(["⚙️ Manual Setup", "📡 AI Radar", "📊 Trade Journal & Live PnL"])

# ==========================================
# TAB 1: MANUAL SETUP
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

# ==========================================
# TAB 2: AI RADAR
# ==========================================
with tab2:
    st.subheader("📡 Auto-Scan Top Stocks")
    nifty_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
    if st.button("🔍 START RADAR SCAN"):
        strong_buys = []
        my_bar = st.progress(0, text="Scanning Market...")
        for index, stock in enumerate(nifty_list):
            my_bar.progress(int(((index + 1) / len(nifty_list)) * 100), text=f"Scanning {stock}")
            try:
                data = yf.download(tickers=stock, period="1mo", interval="1d", progress=False)
                if not data.empty:
                    data['SMA_50'] = data['Close'].rolling(window=5).mean()
                    data['SMA_200'] = data['Close'].rolling(window=10).mean()
                    latest = data.iloc[-1]
                    if float(latest['SMA_50']) > float(latest['SMA_200']):
                        strong_buys.append({"Stock": stock, "Price": round(float(latest['Close']), 2), "Signal": "STRONG BUY 🚀"})
            except:
                pass
        my_bar.empty()
        if strong_buys: st.dataframe(pd.DataFrame(strong_buys), use_container_width=True)
        else: st.warning("No setup found today.")

# ==========================================
# TAB 3: THE TRADE JOURNAL & LIVE PnL (UPGRADED)
# ==========================================
with tab3:
    st.subheader("📒 Live Portfolio & Performance Analytics")
    
    df_trades = pd.read_sql_query("SELECT * FROM trades", conn)
    
    if not df_trades.empty:
        # Displaying past transactions log
        st.markdown("### 🗂️ Transaction Log")
        st.dataframe(df_trades, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📈 Live Open Positions & PnL")
        
        # Real-time PnL Calculation Logic
        total_investment = 0.0
        total_current_value = 0.0
        
        # Grid layout for position statistics
        for index, row in df_trades.iterrows():
            stk = row['symbol']
            buy_p = float(row['price'])
            qty = int(row['quantity'])
            
            # Fetching fresh current price for real-time tracking
            with st.spinner(f"Updating Live Price for {stk}..."):
                stk_data = yf.download(tickers=stk, period="5d", interval="1d", progress=False)
                if not stk_data.empty:
                    live_p = float(stk_data['Close'].iloc[-1])
                else:
                    live_p = buy_p
            
            pnl_per_share = live_p - buy_p
            total_pnl = pnl_per_share * qty
            
            total_investment += (buy_p * qty)
            total_current_value += (live_p * qty)
            
            # Stylized display row for individual active trades
            pnl_color = "green" if total_pnl >= 0 else "red"
            st.markdown(f"**Stock:** `{stk}` | **Bought At:** ₹{buy_p:.2f} | **Live Price:** ₹{live_p:.2f} | **Qty:** {qty} | **PnL:** :{pnl_color}[₹{total_pnl:.2f}]")
            
        st.markdown("---")
        
        # Summary Cards for Whole Portfolio
        net_pnl = total_current_value - total_investment
        net_color = "green" if net_pnl >= 0 else "red"
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Investment Value", f"₹{total_investment:.2f}")
        col_m2.metric("Current Portfolio Value", f"₹{total_current_value:.2f}")
        col_m3.metric("Net Return (PnL)", f"₹{net_pnl:.2f}", delta=f"{((net_pnl/total_investment)*100):.2f}%" if total_investment > 0 else "0%")
        
    else:
        st.info("Abhi portfolio me koi data nahi hai. Tab 1 se mock BUY order trigger karke dekho!")
