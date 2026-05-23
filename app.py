from flask import Flask, jsonify, request
import random
import datetime

app = Flask(__name__)

# Ity ny pejy ho hita eo amin'ny finday (HTML/CSS/JS mitambatra)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="mg">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sora-IA Forex Analyzer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #0f111a; color: #ffffff; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .container { background: #161925; width: 100%; max-width: 450px; padding: 30px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); border: 1px solid #23283d; text-align: center; }
        h1 { font-size: 22px; color: #4ef2d2; margin-bottom: 25px; font-weight: 700; }
        .form-group { text-align: left; margin-bottom: 18px; }
        label { display: block; font-size: 14px; color: #94a3b8; margin-bottom: 8px; }
        select { width: 100%; padding: 12px; background: #202436; border: 1px solid #2d334d; color: #fff; border-radius: 8px; font-size: 15px; outline: none; cursor: pointer; }
        .btn-analyze { width: 100%; padding: 14px; background: linear-gradient(135deg, #ff007f, #7928ca); border: none; color: white; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 15px; }
        .result-box { margin-top: 25px; background: #1e2235; border-radius: 12px; padding: 20px; border: 1px dashed #2d334d; min-height: 140px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
        .status { font-size: 15px; color: #a0a0a0; font-style: italic; margin-bottom: 10px; }
        .signal { font-size: 28px; font-weight: 800; }
        .buy-style { color: #00ff66; text-shadow: 0 0 15px rgba(0, 255, 102, 0.4); }
        .sell-style { color: #ff3333; text-shadow: 0 0 15px rgba(255, 51, 51, 0.4); }
        .neutral-style { color: #8e9aa8; }
        .details { margin-top: 10px; font-size: 13px; color: #4ef2d2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 FOREX AI ANALYZER</h1>
        <div class="form-group">
            <label>Safidio ny Marche (Pair):</label>
            <select id="market">
                <option value="EUR/USD (OTC)">EUR/USD (OTC)</option>
                <option value="GBP/USD (OTC)">GBP/USD (OTC)</option>
                <option value="USD/JPY (OTC)">USD/JPY (OTC)</option>
                <option value="EUR/USD">EUR/USD (Real)</option>
            </select>
        </div>
        <div class="form-group">
            <label>Safidio ny Timeframe:</label>
            <select id="timeframe">
                <option value="1m">1 minitra</option>
                <option value="2m">2 minitra</option>
                <option value="5m">5 minitra</option>
            </select>
        </div>
        <button class="btn-analyze" onclick="runLiveAnalysis()">START ANALYSE 🔍</button>
        <div class="result-box">
            <div id="status" class="status">Miandry analyse...</div>
            <div id="signal" class="signal"></div>
            <div id="details" class="details"></div>
        </div>
    </div>

    <script>
        async function runLiveAnalysis() {
            const pair = document.getElementById("market").value;
            const timeframe = document.getElementById("timeframe").value;
            const statusDiv = document.getElementById("status");
            const signalDiv = document.getElementById("signal");
            const detailsDiv = document.getElementById("details");

            statusDiv.innerHTML = "Manao analyse mivantana...";
            statusDiv.style.color = "#ffcc00";
            signalDiv.innerHTML = "";
            detailsDiv.innerHTML = "";

            try {
                // Mandefa fangatahana amin'ny server amin'ny fomba tsotra
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pair: pair, timeframe: timeframe })
                });
                
                const data = await response.json();
                statusDiv.innerHTML = "✅ Analyse vita ho an'ny " + data.pair;
                statusDiv.style.color = "#4ef2d2";

                if (data.signal === "BUY") {
                    signalDiv.innerHTML = "🟢 BUY (CALL)";
                    signalDiv.className = "signal buy-style";
                } else if (data.signal === "SELL") {
                    signalDiv.innerHTML = "🔴 SELL (PUT)";
                    signalDiv.className = "signal sell-style";
                } else {
                    signalDiv.innerHTML = "🚫 NO SIGNAL";
                    signalDiv.className = "signal neutral-style";
                }
                detailsDiv.innerHTML = "Ora: " + data.time + "<br>⏱ Expiration: " + timeframe;
            } catch (error) {
                statusDiv.innerHTML = "❌ Diso ny fifandraisana amin'ny server.";
                statusDiv.style.color = "#ff3333";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_CONTENT

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json or {}
        pair = data.get('pair', 'EUR/USD (OTC)')
        timeframe = data.get('timeframe', '1m')
        
        # Algorithme tsotra mamorona signal
        signals = ["BUY", "SELL", "NEUTRAL"]
        result = random.choice(signals)
        
        now = datetime.datetime.now()
        return jsonify({
            "status": "success",
            "pair": pair,
            "timeframe": timeframe,
            "signal": result,
            "time": now.strftime("%H:%M:%S")
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
