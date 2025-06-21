import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.demo_data_fetcher import DataFetcher
from src.investment_engine import InvestmentEngine
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app, resources={r"/api/*": {"origins": "https://etf-smart-advisor.vercel.app"}})
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# 啟用 CORS

app.register_blueprint(user_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# 初始化核心模組
data_fetcher = DataFetcher()
investment_engine = InvestmentEngine()

@app.route('/api/daily-recommendation', methods=['POST'])
def get_daily_recommendation():
    """獲取每日投資建議"""
    try:
        user_profile = request.json or {}
        
        # 獲取市場數據
        market_data = data_fetcher.get_market_data()
        
        # 獲取 ETF 數據
        etf_data = data_fetcher.get_all_etf_data()
        
        # 生成投資建議
        recommendation = investment_engine.get_daily_recommendation(
            user_profile, etf_data, market_data
        )
        
        return jsonify(recommendation)
        
    except Exception as e:
        logger.error(f"獲取每日建議錯誤: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/etf/<symbol>', methods=['GET'])
def get_etf_detail(symbol):
    """獲取 ETF 詳細資訊"""
    try:
        # 添加 .TW 後綴
        full_symbol = f"{symbol}.TW"
        data = data_fetcher.get_etf_data(full_symbol)
        
        if data:
            return jsonify({
                'success': True,
                'data': data
            })
        else:
            return jsonify({
                'success': False,
                'error': f'無法獲取 {symbol} 的數據'
            }), 404
            
    except Exception as e:
        logger.error(f"獲取 ETF {symbol} 詳細資訊錯誤: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-status', methods=['GET'])
def get_market_status():
    """獲取市場狀態"""
    try:
        market_data = data_fetcher.get_market_data()
        return jsonify({
            'success': True,
            'data': market_data
        })
        
    except Exception as e:
        logger.error(f"獲取市場狀態錯誤: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/etf-list', methods=['GET'])
def get_etf_list():
    """獲取所有 ETF 清單"""
    try:
        etf_data = data_fetcher.get_all_etf_data()
        return jsonify({
            'success': True,
            'data': etf_data,
            'count': len(etf_data)
        })
        
    except Exception as e:
        logger.error(f"獲取 ETF 清單錯誤: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查"""
    try:
        # 簡單的健康檢查
        return jsonify({
            'status': 'healthy',
            'timestamp': data_fetcher.get_market_data().get('updated_at'),
            'service': 'ETF Smart Advisor API'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
