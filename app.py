from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# Lisitry ny pairs (Ny OTC dia mampiasa ny "Real" pairs ho referansy)
ticker_map = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "USD/CHF": "CHF=X",
    "EUR/GBP": "EURGBP=X", "EUR/JPY": "EURJPY=X", "GBP/JPY": "GBPJPY=X",
    "GOLD": "GC=F", "SILVER": "SI=F", "OIL": "CL=F"
}

def get_analysis(market, tf):
    ticker = ticker_map.get(market, "EURUSD=X")
    # Maka data (1 minitra na 5 minitra)
    df = yf.download(ticker, period="1d", interval=tf, progress=False)
    
    # Kajy Bollinger Bands
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['Upper'] = df['SMA_20'] + (df['STD'] * 2)
    df['Lower'] = df['SMA_20'] - (df['STD'] * 2)
    
    # Kajy RSI 14
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = -delta.clip(upper=0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df.iloc[-1]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/analyze')
def analyze():
    market = request.args.get('market', 'EUR/USD')
    tf = request.args.get('tf', '1m') # Minitra
    try:
        data = get_analysis(market, tf)
        price = float(data['Close'])
        rsi = float(data['RSI'])
        
        # LOGIC TENA IZY: Tsy misy kisendrasendra
        if rsi < 30 and price <= data['Lower']:
            return jsonify({"signal": "🟢 HIGHER (CALL)", "style": "buy-style", "rsi": round(rsi,2)})
        elif rsi > 70 and price >= data['Upper']:
            return jsonify({"signal": "🔴 LOWER (PUT)", "style": "sell-style", "rsi": round(rsi,2)})
        else:
            return jsonify({"signal": "🚫 NO SIGNAL", "style": "nosignal-style", "rsi": round(rsi,2)})
    except Exception as e:
        return jsonify({"signal": "Error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
