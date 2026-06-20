import streamlit as st
import yfinance as yf
import pandas as pd
import warnings
import time

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Ultimate AI Bot", page_icon="🤖", layout="wide")
st.title("🚀 Ultimate AI Trading Control Center")
st.markdown("---")

# Yahan hum Dashboard ko 2 Tabs me divide kar rahe hain
tab1, tab2 = st.tabs(["⚙️ Manual Trade Setup", "📡 AI Market Radar (Multi-Scan)"])

# ==========================================
# TAB 1: MANUAL CONTROL (Tumhara purana code)
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚙️ Trade Setup")
        symbol = st.text_input("Stock Symbol", "RELIANCE.NS")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        target_price = st.number_input("Target Entry Price (₹)", min_value=1.0, value=1000.0)

    with col2:
        st.subheader("🛡️ Risk Management")
        sl_pct = st.number_input("Stop-Loss (%)", min_value=0.1, value=1.0, step=0.1)
        tp_pct = st.number_input("Take-Profit (%)", min_value=0.1, value=2.0, step=0.1)
        upstox_token = st.text_input("Upstox Token", "NSE_EQ|INE002A01018")

    if st.button("🧠 Analyze Market & Get AI Verdict"):
        with st.spinner(f"Analyzing {symbol}..."):
            data = yf.download(tickers=symbol, period="1y", interval="1d", progress=False)
            if not data.empty:
                data['SMA_50'] = data['Close'].rolling(window=50).mean()
                data['SMA_200'] = data['Close'].rolling(window=200).mean()
                
                close_prices = data['Close'].squeeze()
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
                loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
                rs = gain / loss
                data['RSI'] = 100 - (100 / (1 + rs))
                
                latest = data.iloc[-1]
                price = float(latest['Close'].iloc[0]) if hasattr(latest['Close'], 'iloc') else float(latest['Close'])
                sma_50 = float(latest['SMA_50'].iloc[0]) if hasattr(latest['SMA_50'], 'iloc') else float(latest['SMA_50'])
                sma_200 = float(latest['SMA_200'].iloc[0]) if hasattr(latest['SMA_200'], 'iloc') else float(latest['SMA_200'])
                rsi = float(latest['RSI'].iloc[0]) if hasattr(latest['RSI'], 'iloc') else float(latest['RSI'])
                
                buy_points = 0; sell_points = 0
                if sma_50 > sma_200: buy_points += 1
                else: sell_points += 1
                if rsi < 35: buy_points += 1
                elif rsi > 65: sell_points += 1
                    
                net_score = buy_points - sell_points
                
                if net_score >= 2: verdict = "STRONG BUY 🚀"; color = "green"
                elif net_score == 1: verdict = "BUY 🟢"; color = "green"
                elif net_score <= -1: verdict = "SELL/STRONG SELL 🔴"; color = "red"
                else: verdict = "NEUTRAL 🟡"; color = "orange"
                
                st.markdown(f"### 🤖 Verdict: :{color}[{verdict}] (Score: {net_score})")
                st.line_chart(data['Close'])

# ==========================================
# TAB 2: NIFTY 50 RADAR (Naya Feature)
# ==========================================
with tab2:
    st.subheader("📡 Auto-Scan Top Stocks")
    st.write("AI automatically sab stocks check karega aur sirf 'STRONG BUY' wale filter karke nikalega.")
    
    # Top 10 Nifty Stocks ki list testing ke liye
    nifty_list = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
        "SBIN.NS", "ITC.NS", "TATAMOTORS.NS", "SUNPHARMA.NS", "NTPC.NS"
    ]
    
    if st.button("🔍 START RADAR SCAN"):
        strong_buys = []
        
        # Ek progress bar banayenge UI me mast dikhne ke liye
        progress_text = "Scanning Market... Please wait."
        my_bar = st.progress(0, text=progress_text)
        
        for index, stock in enumerate(nifty_list):
            # Progress bar update
            percent_complete = int(((index + 1) / len(nifty_list)) * 100)
            my_bar.progress(percent_complete, text=f"Scanning {stock} ({index+1}/{len(nifty_list)})")
            
            try:
                # 1 saal ka data download
                data = yf.download(tickers=stock, period="1y", interval="1d", progress=False)
                if not data.empty:
                    # Calculations
                    data['SMA_50'] = data['Close'].rolling(window=50).mean()
                    data['SMA_200'] = data['Close'].rolling(window=200).mean()
                    close_prices = data['Close'].squeeze()
                    delta = close_prices.diff()
                    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
                    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
                    rs = gain / loss
                    data['RSI'] = 100 - (100 / (1 + rs))
                    
                    # Latest Data nikalna
                    latest = data.iloc[-1]
                    sma_50 = float(latest['SMA_50'].iloc[0]) if hasattr(latest['SMA_50'], 'iloc') else float(latest['SMA_50'])
                    sma_200 = float(latest['SMA_200'].iloc[0]) if hasattr(latest['SMA_200'], 'iloc') else float(latest['SMA_200'])
                    rsi = float(latest['RSI'].iloc[0]) if hasattr(latest['RSI'], 'iloc') else float(latest['RSI'])
                    price = float(latest['Close'].iloc[0]) if hasattr(latest['Close'], 'iloc') else float(latest['Close'])
                    
                    # Scoring Logic
                    score = 0
                    if sma_50 > sma_200: score += 1
                    else: score -= 1
                    if rsi < 35: score += 1
                    elif rsi > 65: score -= 1
                    
                    # Agar Strong Buy (Score 2) hai toh list me save kar lo
                    if score >= 2:
                        strong_buys.append({
                            "Stock": stock,
                            "Price": round(price, 2),
                            "RSI": round(rsi, 2),
                            "Signal": "STRONG BUY 🚀"
                        })
            except Exception as e:
                pass
            
            time.sleep(0.5) # thoda delay takki server block na kare
            
        my_bar.empty() # Scan khatam hone par bar gayab kar do
        
        st.markdown("---")
        if len(strong_buys) > 0:
            st.success(f"🎉 Radar ne {len(strong_buys)} 'STRONG BUY' opportunities dhundh nikali hain!")
            # Data ko table format me dikhana
            df_results = pd.DataFrame(strong_buys)
            st.dataframe(df_results, use_container_width=True)
        else:
            st.warning("⚖️ Abhi market me kisi bhi stock me 'STRONG BUY' setup nahi ban raha hai. Cash safe rakhein!")