from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze')
def analyze():
    symbol = request.args.get('symbol', 'EURUSD=X')
    try:
        # Maka data 5 minitra
        df = yf.download(symbol, period="1d", interval="5m", progress=False)
        if len(df) < 20: return jsonify({"signal": "WAIT", "details": "Miandry data..."})
        
        # Kajy RSI
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(window=14).mean()
        loss = -delta.clip(upper=0).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Kajy SMA
        sma = df['Close'].rolling(window=20).mean().iloc[-1]
        price = df['Close'].iloc[-1]
        
        if rsi < 30 and price > sma:
            return jsonify({"signal": "🟢 CALL", "details": "RSI Oversold + Trend Miakatra"})
        elif rsi > 70 and price < sma:
            return jsonify({"signal": "🔴 PUT", "details": "RSI Overbought + Trend Midina"})
        else:
            return jsonify({"signal": "⚪ WAIT", "details": "Tsy mbola mety ny tsena"})
    except Exception as e:
        return jsonify({"signal": "ERROR", "details": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
