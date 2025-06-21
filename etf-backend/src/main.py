import os
import sys
import logging
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 引入專案模組
from src.models.user import db
from src.routes.user import user_bp
from src.demo_data_fetcher import DataFetcher
from src.investment_engine import InvestmentEngine

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# 允許所有來源的 CORS 請求，這是最寬鬆的設定，用於測試。生產環境應限制特定來源。
# 由於 Render 預設會將服務部署在一個動態的子網域，直接指定 Vercel 網址可能不夠。
# 為了確保 CORS 不再是問題，暫時允許所有來源。
# 在實際生產環境中，應將 ALLOWED_ORIGINS 設定為 Vercel 的實際網址。
CORS(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_key_here') # 使用環境變數設定 SECRET_KEY

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# 註冊藍圖
app.register_blueprint(user_bp, url_prefix='/api')

# 初始化核心模組
data_fetcher = DataFetcher()
investment_engine = InvestmentEngine()

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 Not Found: {request.url}")
    return jsonify({"success": False, "error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_server_error(error):
    logger.exception("500 Internal Server Error") # 記錄完整的錯誤堆棧
    return jsonify({"success": False, "error": "Internal server error"}), 500

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
        market_data = data_fetcher.get_market_data() # 嘗試獲取數據以檢查數據源連線
        return jsonify({
            'status': 'healthy',
            'timestamp': market_data.get('updated_at'),
            'service': 'ETF Smart Advisor API'
        })
        
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# 靜態文件服務 (用於前端部署)
@app.route('/', defaults={'path': ''}) # 確保根路徑也能被處理
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        logger.error("Static folder not configured")
        return "Static folder not configured", 404

    # 嘗試直接提供文件
    full_path = os.path.join(static_folder_path, path)
    if path != "" and os.path.exists(full_path) and os.path.isfile(full_path):
        return send_from_directory(static_folder_path, path)
    else:
        # 如果不是文件，則嘗試提供 index.html (適用於單頁應用)
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            logger.error(f"index.html not found in {static_folder_path}")
            return "index.html not found", 404


if __name__ == '__main__':
    # 在生產環境中，請使用 Gunicorn 或其他 WSGI 伺服器來運行應用程式
    # 例如：gunicorn -w 4 main:app -b 0.0.0.0:5000
    app.run(host='0.0.0.0', port=5000, debug=True)


