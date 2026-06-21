import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import warnings

warnings.filterwarnings('ignore')

# 1. Email Function
def send_email_alert(subject, message):
    sender_email = "TUMHARI_EMAIL@gmail.com"  # Apna email daalo
    app_password = "xxxx xxxx xxxx xxxx"      # Apna 16-digit password daalo
    receiver_email = "TUMHARI_EMAIL@gmail.com"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("✅ Alert Sent Successfully!")
    except Exception as e:
        print("❌ Email Failed:", e)

print("👻 Waking up Ghost Mode...")
symbol = "RELIANCE.NS"

# 2. Download Data & Train AI
df = yf.download(tickers=symbol, period="10y", interval="1d", progress=False)
if not df.empty:
    df = df.squeeze()
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['Daily_Return'] = df['Close'].pct_change()
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df = df.dropna()

    features = ['Close', 'SMA_10', 'SMA_50', 'Daily_Return']
    X = df[features]
    y = df['Target']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    latest_data = X.iloc[-1:]
    pred = int(model.predict(latest_data)[0])

    # 3. Send Email Alert
    status = "UP 🟢" if pred == 1 else "DOWN 🔴"
    body = f"Ultimate AI Bot - Ghost Mode\n\nStock: {symbol}\nAI Prediction for Tomorrow: Market will go {status}\n\nHappy Auto-Trading!"
    
    send_email_alert(f"🤖 AI Daily Report: {symbol} {status}", body)
    print("💤 Job Done. Going back to sleep.")
