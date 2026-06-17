from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# Ticker mapping ho an'ny data marina
ticker_map = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "GOLD": "GC=F"
}

def get_real_data(ticker):
    # Maka data 1 andro farany amin'ny 1 min interval
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    # Kajy Bollinger Bands
    df['SMA'] = df['Close'].rolling(window=20).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['Upper'] = df['SMA'] + (df['STD'] * 2)
    df['Lower'] = df['SMA'] - (df['STD'] * 2)
    
    # Kajy RSI
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = -delta.clip(upper=0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df.iloc[-1]

@app.route('/api/analyze')
def analyze():
    market = request.args.get('market', 'EUR/USD')
    ticker = ticker_map.get(market, "EURUSD=X")
    
    try:
        data = get_real_data(ticker)
        price = float(data['Close'])
        rsi = float(data['RSI'])
        
        # LOGIC TENA IZY (Confluence)
        if rsi < 30 and price <= data['Lower']:
            return jsonify({"signal": "🟢 HIGHER (CALL)", "style": "buy-style", "rsi": round(rsi, 2)})
        elif rsi > 70 and price >= data['Upper']:
            return jsonify({"signal": "🔴 LOWER (PUT)", "style": "sell-style", "rsi": round(rsi, 2)})
        else:
            return jsonify({"signal": "⚪ NEUTRAL (STANDBY)", "style": "neutral-style", "rsi": round(rsi, 2)})
    except Exception as e:
        return jsonify({"signal": "Error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
