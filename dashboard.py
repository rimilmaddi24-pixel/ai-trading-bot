import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import warnings
import time
from datetime import datetime

warnings.filterwarnings('ignore')

# ==========================================
# DATABASE SETUP (Bot ki Memory)
# ==========================================
conn = sqlite3.connect('trade_journal.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades 
             (timestamp TEXT, symbol TEXT, action TEXT, price REAL, quantity INTEGER)''')
conn.commit()

def save_trade(symbol, action, price, quantity):
    """Yeh function naye trades ko database me save karega"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO trades VALUES (?, ?, ?, ?, ?)", (now, symbol, action, price, quantity))
    conn.commit()

# ==========================================
# PAGE SETUP & TABS
# ==========================================
st.set_page_config(page_title="Ultimate AI Bot", page_icon="🤖", layout="wide")
st.title("🚀 Ultimate AI Trading Control Center")
st.markdown("---")

# Ab 3 Tabs banenge
tab1, tab2, tab3 = st.tabs(["⚙️ Manual Setup", "📡 AI Radar", "📊 Trade Journal & PnL"])

# ==========================================
# TAB 1: MANUAL CONTROL & EXECUTION
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚙️ Trade Setup")
        symbol = st.text_input("Stock Symbol", "RELIANCE.NS")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        target_price = st.number_input("Target Price (₹)", min_value=1.0, value=1000.0)

    with col2:
        st.subheader("⚡ Live Execution")
        upstox_token = st.text_input("Upstox Token", "NSE_EQ|INE002A01018")
        
        # JAB BHI BUY BUTTON DABEGA, DATABASE ME ENTRY HOGI
        if st.button("🔥 FIRE BUY ORDER", use_container_width=True):
            data = yf.download(tickers=symbol, period="1d", interval="1m", progress=False)
            if not data.empty:
                current_price = float(data['Close'].iloc[-1].iloc[0] if hasattr(data['Close'].iloc[-1], 'iloc') else data['Close'].iloc[-1])
                # Database me save karna
                save_trade(symbol, "BUY", current_price, quantity)
                st.success(f"✅ BUY Order Fired for {symbol} at ₹{current_price:.2f}!")
                st.info("Entry saved to Trade Journal.")
            else:
                st.error("Market Data unavailable.")

# ==========================================
# TAB 2: NIFTY 50 RADAR
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
                    data['SMA_50'] = data['Close'].rolling(window=10).mean() # fast for test
                    data['SMA_200'] = data['Close'].rolling(window=20).mean()
                    latest = data.iloc[-1]
                    price = float(latest['Close'].iloc[0]) if hasattr(latest['Close'], 'iloc') else float(latest['Close'])
                    
                    if float(latest['SMA_50'].iloc[0] if hasattr(latest['SMA_50'], 'iloc') else latest['SMA_50']) > float(latest['SMA_200'].iloc[0] if hasattr(latest['SMA_200'], 'iloc') else latest['SMA_200']):
                        strong_buys.append({"Stock": stock, "Price": round(price, 2), "Signal": "STRONG BUY 🚀"})
            except:
                pass
        
        my_bar.empty()
        if strong_buys:
            st.dataframe(pd.DataFrame(strong_buys), use_container_width=True)
        else:
            st.warning("No setup found today.")

# ==========================================
# TAB 3: THE TRADE JOURNAL (Naya Feature)
# ==========================================
with tab3:
    st.subheader("📒 Past Trades & PnL Report")
    st.markdown("Yahan bot tumhare saare executed orders ka hisaab rakhega.")
    
    # Database se saara data nikalna
    df_trades = pd.read_sql_query("SELECT * FROM trades", conn)
    
    if not df_trades.empty:
        st.dataframe(df_trades, use_container_width=True)
        
        # Chota sa hisaab
        total_trades = len(df_trades)
        st.metric(label="Total Trades Executed", value=total_trades)
    else:
        st.info("Abhi tak koi trade nahi liya gaya hai. Tab 1 se ek order fire karke test karo!")
