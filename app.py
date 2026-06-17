from flask import Flask, render_template, request, jsonify # Ovay ny 'render_request' ho 'request'
import yfinance as yf
import pandas as pd

app = Flask(__name__, template_folder=".")

def calculate_indicators(df):
    # Kajy SMA 14
    df['SMA'] = df['Close'].rolling(window=14).mean()
    
    # Kajy RSI 14
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
    # Fanitsiana: 'render_request' dia tokony ho 'request'
    market = request.args.get('market', 'EUR/USD')
    timeframe = request.args.get('timeframe', '1 MIN')
    
    clean_market = market.replace(" (OTC)", "").replace(" (Real)", "")
    
    ticker_map = {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
        "AUD/USD": "AUDUSD=X", "USD/CHF": "CHF=X", "EUR/GBP": "EURGBP=X",
        "GOLD": "GC=F", "SILVER": "SI=F", "CRUDE OIL": "CL=F"
    }
    
    ticker = ticker_map.get(clean_market, "EURUSD=X")
    
    try:
        data = yf.download(tickers=ticker, period="1d", interval="1m", progress=False)
        if data.empty:
            return jsonify({"status": "error", "message": "Tsy azo ny data"})
        
        data = calculate_indicators(data)
        last_row = data.iloc[-1]
        
        # Fampitandremana: Ataovy antoka fa 'float' no ampiasaina
        current_price = float(last_row['Close'])
        rsi_value = float(last_row['RSI'])
        sma_value = float(last_row['SMA'])
        
        if rsi_value < 35 and current_price > sma_value:
            signal = "🟢 HIGHER (CALL)"
            style = "buy-style"
        elif rsi_value > 65 and current_price < sma_value:
            signal = "🔴 LOWER (PUT)"
            style = "sell-style"
        else:
            signal = "🚫 NO SIGNAL"
            style = "nosignal-style"
            
        return jsonify({
            "status": "success",
            "signal": signal,
            "style": style,
            "rsi": round(rsi_value, 2),
            "price": round(current_price, 5)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
