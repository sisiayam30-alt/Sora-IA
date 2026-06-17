from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__, template_folder=".")

# Ticker mapping ho an'ny Forex Real
ticker_map = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CHF": "CHF=X", "EUR/GBP": "EURGBP=X",
    "GOLD": "GC=F", "SILVER": "SI=F", "CRUDE OIL": "CL=F"
}

def calculate_indicators(df):
    # SMA 50 ho an'ny Trend matanjaka kokoa
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # RSI 14
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = -delta.clip(upper=0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/analyze', methods=['GET'])
def analyze():
    market = request.args.get('market', 'EUR/USD')
    clean_market = market.replace(" (OTC)", "").replace(" (Real)", "")
    ticker = ticker_map.get(clean_market, "EURUSD=X")
    
    try:
        # Maka data 1 andro miaraka amin'ny 1 min interval
        data = yf.download(tickers=ticker, period="1d", interval="1m", progress=False)
        
        if data.empty or len(data) < 50:
            return jsonify({"status": "error", "message": "Miandry data..."})
        
        data = calculate_indicators(data)
        last = data.iloc[-1]
        
        price = float(last['Close'])
        rsi = float(last['RSI'])
        sma = float(last['SMA_50'])
        
        # LOGIC: Signal "Strict" - Tsy miresaka raha tsy tena mifanaraka
        if rsi < 30 and price > sma:
            signal = "🟢 HIGHER (CALL)"
            style = "buy-style"
            action = "Trend miakatra + Oversold (RSI)"
        elif rsi > 70 and price < sma:
            signal = "🔴 LOWER (PUT)"
            style = "sell-style"
            action = "Trend midina + Overbought (RSI)"
        else:
            signal = "🚫 NO SIGNAL"
            style = "nosignal-style"
            action = "Tsena tsy mbola azo antoka"
            
        return jsonify({
            "status": "success",
            "signal": signal,
            "style": style,
            "action": action,
            "rsi": round(rsi, 2),
            "price": round(price, 5)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
