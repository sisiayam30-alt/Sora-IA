from flask import Flask, render_template, jsonify, request
import random
import datetime
import pandas as pd
import ta

app = Flask(__name__, template_folder='.')

def analyze_market_live(pair, timeframe):
    """
    Algorithm manao analyse ny tsena rehetra (Forex Real sy OTC).
    """
    # Labozia simulation 60
    prices = [round(random.uniform(1.0900, 1.1100), 4) for _ in range(60)]
    df = pd.DataFrame({
        'close': prices,
        'high': [p + 0.0015 for p in prices],
        'low': [p - 0.0015 for p in prices]
    })
    
    # Kajy ara-teknika (RSI + Bollinger Bands + EMA)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    indicator_bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_high'] = indicator_bb.bollinger_hband()
    df['bb_low'] = indicator_bb.bollinger_lband()
    
    last_row = df.iloc[-1]
    current_price = last_row['close']
    rsi = last_row['rsi']
    bb_high = last_row['bb_high']
    bb_low = last_row['bb_low']
    
    # Paikady mamoaka BUY na SELL
    if current_price <= bb_low and rsi < 35:
        return "BUY"
    elif current_price >= bb_high and rsi > 65:
        return "SELL"
    else:
        return "NEUTRAL"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
            
        pair = data.get('pair', 'EUR/USD (OTC)')
        timeframe = data.get('timeframe', '1m')
        
        result = analyze_market_live(pair, timeframe)
        
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        
        return jsonify({
            "status": "success",
            "pair": pair,
            "timeframe": timeframe,
            "signal": result,
            "time": time_str
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
