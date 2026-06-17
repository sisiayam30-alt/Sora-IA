from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# Fiasan'ny AI: Mikajy ny indicators
def get_analysis(market):
    ticker = market + "=X"
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    # Bollinger Bands
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['Upper'] = df['SMA_20'] + (df['STD'] * 2)
    df['Lower'] = df['SMA_20'] - (df['STD'] * 2)
    
    # RSI 14
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
    market = request.args.get('market', 'EURUSD')
    try:
        data = get_analysis(market)
        price = float(data['Close'])
        rsi = float(data['RSI'])
        
        # LOGIC TENA IZY (Sivana matanjaka)
        # CALL: RSI ambany 30 + Vidiny mikasika na ambany Lower Band
        if rsi < 30 and price <= data['Lower']:
            return jsonify({"signal": "🟢 HIGHER (CALL)", "style": "buy-style", "rsi": round(rsi,2)})
        # PUT: RSI ambony 70 + Vidiny mikasika na ambony Upper Band
        elif rsi > 70 and price >= data['Upper']:
            return jsonify({"signal": "🔴 LOWER (PUT)", "style": "sell-style", "rsi": round(rsi,2)})
        else:
            return jsonify({"signal": "🚫 NO SIGNAL", "style": "nosignal-style", "rsi": round(rsi,2)})
    except Exception as e:
        return jsonify({"signal": "Error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
