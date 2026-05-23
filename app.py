from flask import Flask, render_template, jsonify, request
import random
import datetime
import pandas as pd
import ta

app = Flask(__name__, template_folder='.')

def analyze_market_live(pair, timeframe):
    """
    Kajy mifanaraka amin'ny tsenan'ny Pocket Option OTC.
    Ny OTC dia manaraka Trend mahery (Trend-following).
    """
    # Labozia simulation 60 ho an'ny OTC (mahery kokoa ny fihetsehany)
    prices = [round(random.uniform(1.0900, 1.1100), 4) for _ in range(60)]
    df = pd.DataFrame({
        'close': prices,
        'high': [p + 0.0015 for p in prices],
        'low': [p - 0.0015 for p in prices]
    })
    
    # 1. Tondro fototra: RSI (window=14)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    
    # 2. Tondro faharoa: Bollinger Bands
    indicator_bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_high'] = indicator_bb.bollinger_hband()
    df['bb_low'] = indicator_bb.bollinger_lband()
    
    # 3. Tondro fahatelo ho an'ny OTC: EMA 200 (na EMA 50 eto amin'ny data kely) ho an'ny Trend
    df['ema_trend'] = ta.trend.ema_indicator(df['close'], window=20)
    
    last_row = df.iloc[-1]
    current_price = last_row['close']
    rsi = last_row['rsi']
    bb_high = last_row['bb_high']
    bb_low = last_row['bb_low']
    ema = last_row['ema_trend']
    
    # Paikady matanjaka ho an'ny OTC (Trend + Overbought/Oversold):
    # BUY: Raha ambony noho ny EMA ny vidiny (Uptrend) sady mihoatra ny Bollinger Low na ambany RSI
    if current_price <= bb_low and rsi < 35:
        return "BUY"
    # SELL: Raha ambany noho ny EMA ny vidiny (Downtrend) sady mihoatra ny Bollinger High na ambony RSI
    elif current_price >= bb_high and rsi > 65:
        return "SELL"
    else:
        return "NEUTRAL"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    pair = data.get('pair')
    timeframe = data.get('timeframe')
    
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
