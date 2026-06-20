import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import warnings
from datetime import datetime
import plotly.graph_objects as go

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
# Yeh code Tab 1 me st.button("🔥 FIRE BUY ORDER") ke if block ke andar jayega:

                save_trade(symbol, "BUY", current_price, quantity)
                
                # NAYA ALERTS CODE YAHAN AAYEGA
                alert_subject = f"🚨 TRADE ALERT: BUY {symbol}"
                alert_body = f"Ultimate AI Bot update:\n\nOrder Type: BUY\nStock: {symbol}\nQuantity: {quantity}\nExecuted Price: Rs {current_price:.2f}\n\nHappy Trading!"
                
                with st.spinner("Sending Email Alert..."):
                    if send_email_alert(alert_subject, alert_body):
                        st.success(f"✅ BUY Order Fired for {symbol} at ₹{current_price:.2f} & Alert Sent!")
                    else:
                        st.warning("Order Fired, but Email Alert failed.")
# Page UI Config
st.set_page_config(page_title="Ultimate AI Bot", page_icon="🤖", layout="wide")
st.title("🚀 Ultimate AI Trading Control Center")
st.markdown("---")

# Ab 4 Tabs banenge
tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Manual Setup", "📡 AI Radar", "📊 Live Portfolio", "⏳ Time Machine (Backtest)"])

# ==========================================
# TAB 1: MANUAL SETUP & INTERACTIVE CHART
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚙️ Trade Setup")
        symbol = st.text_input("Stock Symbol", "RELIANCE.NS", key="manual_sym")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        
    with col2:
        st.subheader("⚡ Live Execution")
        if st.button("🔥 FIRE BUY ORDER", use_container_width=True):
            data = yf.download(tickers=symbol, period="5d", interval="1d", progress=False)
            if not data.empty:
                current_price = float(data['Close'].iloc[-1].iloc[0] if hasattr(data['Close'].iloc[-1], 'iloc') else data['Close'].iloc[-1])
                save_trade(symbol, "BUY", current_price, quantity)
                st.success(f"✅ BUY Order Fired for {symbol} at ₹{current_price:.2f}!")
            else:
                st.error("Market Data Error.")

    st.markdown("---")
    st.subheader(f"📊 Live Candlestick Chart: {symbol}")
    chart_data = yf.download(tickers=symbol, period="6mo", interval="1d", progress=False)
    
    if not chart_data.empty:
        chart_data['SMA_50'] = chart_data['Close'].rolling(window=50).mean()
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=chart_data.index,
                        open=chart_data['Open'].squeeze(), high=chart_data['High'].squeeze(),
                        low=chart_data['Low'].squeeze(), close=chart_data['Close'].squeeze(), name='Price'))
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA_50'].squeeze(), 
                                 line=dict(color='orange', width=2), name='50 SMA'))
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=500, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

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
                    # Fixing pandas squeeze issues
                    sma50_val = float(latest['SMA_50'].iloc[0] if hasattr(latest['SMA_50'], 'iloc') else latest['SMA_50'])
                    sma200_val = float(latest['SMA_200'].iloc[0] if hasattr(latest['SMA_200'], 'iloc') else latest['SMA_200'])
                    price_val = float(latest['Close'].iloc[0] if hasattr(latest['Close'], 'iloc') else latest['Close'])
                    
                    if sma50_val > sma200_val:
                        strong_buys.append({"Stock": stock, "Price": round(price_val, 2), "Signal": "STRONG BUY 🚀"})
            except:
                pass
        my_bar.empty()
        if strong_buys: st.dataframe(pd.DataFrame(strong_buys), use_container_width=True)
        else: st.warning("No setup found today.")

# ==========================================
# TAB 3: LIVE PORTFOLIO
# ==========================================
with tab3:
    st.subheader("📒 Live Portfolio & Performance Analytics")
    df_trades = pd.read_sql_query("SELECT * FROM trades", conn)
    if not df_trades.empty:
        st.dataframe(df_trades, use_container_width=True)
    else:
        st.info("Abhi portfolio me koi data nahi hai.")

# ==========================================
# TAB 4: THE TIME MACHINE (BACKTESTING ENGINE)
# ==========================================
with tab4:
    st.subheader("⏳ Strategy Backtesting Engine")
    st.markdown("Check karo ki pichle kuch saalon mein tumhari AI strategy ne kaisa perform kiya hota.")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        bt_symbol = st.text_input("Stock to Test", "RELIANCE.NS", key="bt_sym")
    with col_b2:
        bt_capital = st.number_input("Starting Capital (₹)", min_value=10000, value=100000, step=10000)
    with col_b3:
        bt_period = st.selectbox("Testing Period", ["1y", "2y", "5y", "10y"], index=2) # Default 5 years
        
    if st.button("🚀 RUN TIME MACHINE", use_container_width=True):
        with st.spinner(f"Simulating past {bt_period} of data for {bt_symbol}..."):
            bt_data = yf.download(tickers=bt_symbol, period=bt_period, interval="1d", progress=False)
            
            if not bt_data.empty:
                # Squeeze the dataframe to avoid multi-index issues
                bt_data = bt_data.squeeze()
                
                # 1. Strategy Indicators Calculate karna
                bt_data['SMA_50'] = bt_data['Close'].rolling(window=50).mean()
                bt_data['SMA_200'] = bt_data['Close'].rolling(window=200).mean()
                
                # 2. Buy/Sell Signal Generate karna (1 = Buy, 0 = Sell)
                # .shift(1) isiliye kiya taaki agle din trade ho (Look-ahead bias se bachne ke liye)
                bt_data['Signal'] = (bt_data['SMA_50'] > bt_data['SMA_200']).astype(int).shift(1)
                
                # 3. Returns Calculate karna
                bt_data['Daily_Return'] = bt_data['Close'].pct_change()
                # Strategy Return = Signal (0 ya 1) * Uss din ka return
                bt_data['Strategy_Return'] = bt_data['Daily_Return'] * bt_data['Signal']
                
                # 4. Paisa kitna bana (Cumulative Returns)
                bt_data['Buy_Hold_Growth'] = (1 + bt_data['Daily_Return']).cumprod() * bt_capital
                bt_data['Strategy_Growth'] = (1 + bt_data['Strategy_Return']).cumprod() * bt_capital
                
                # Drop NaN values for clean data
                bt_data = bt_data.dropna()
                
                # 5. Final Results
                final_buy_hold = float(bt_data['Buy_Hold_Growth'].iloc[-1])
                final_strategy = float(bt_data['Strategy_Growth'].iloc[-1])
                
                net_profit = final_strategy - bt_capital
                roi = (net_profit / bt_capital) * 100
                
                # Display Results
                st.markdown("---")
                st.subheader("🏆 Backtest Results")
                
                res_col1, res_col2, res_col3 = st.columns(3)
                res_col1.metric("Final Capital (AI Strategy)", f"₹{final_strategy:,.2f}", f"ROI: {roi:.2f}%")
                res_col2.metric("Net Profit", f"₹{net_profit:,.2f}")
                res_col3.metric("If You Just Bought & Held", f"₹{final_buy_hold:,.2f}")
                
                # Plotly Chart: Strategy vs Buy & Hold
                st.markdown("### 📈 Portfolio Growth Comparison")
                bt_fig = go.Figure()
                bt_fig.add_trace(go.Scatter(x=bt_data.index, y=bt_data['Strategy_Growth'], 
                                            mode='lines', name='Our AI Strategy', line=dict(color='#00ff00', width=2)))
                bt_fig.add_trace(go.Scatter(x=bt_data.index, y=bt_data['Buy_Hold_Growth'], 
                                            mode='lines', name='Buy & Hold (No AI)', line=dict(color='#888888', width=1, dash='dot')))
                
                bt_fig.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='Portfolio Value (₹)', height=400)
                st.plotly_chart(bt_fig, use_container_width=True)
                
            else:
                st.error("⚠️ Error: Data download nahi ho paaya.")
