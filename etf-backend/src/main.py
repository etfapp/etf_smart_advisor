import os
import sys
import logging
import time
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 引入專案模組
from src.models.user import db
from src.routes.user import user_bp
from src.data_fetcher_optimized import OptimizedDataFetcher
from src.investment_engine_optimized import OptimizedInvestmentEngine

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
data_fetcher = OptimizedDataFetcher()
investment_engine = OptimizedInvestmentEngine()

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
    start_time = time.time()
    try:
        user_profile = request.json or {}
        logger.info(f"開始處理投資建議請求，用戶配置: {user_profile}")
        
        # 獲取市場數據
        logger.info("開始獲取市場數據...")
        market_data = data_fetcher.get_market_data()
        logger.info(f"市場數據獲取完成，耗時: {time.time() - start_time:.2f}秒")
        
        # 獲取 ETF 數據
        logger.info("開始獲取ETF數據...")
        etf_start_time = time.time()
        etf_data = data_fetcher.get_all_etf_data()
        etf_elapsed = time.time() - etf_start_time
        logger.info(f"ETF數據獲取完成，獲得 {len(etf_data)} 檔ETF，耗時: {etf_elapsed:.2f}秒")
        
        # 生成投資建議
        logger.info("開始生成投資建議...")
        recommendation_start_time = time.time()
        recommendation = investment_engine.get_daily_recommendation(
            user_profile, etf_data, market_data
        )
        recommendation_elapsed = time.time() - recommendation_start_time
        logger.info(f"投資建議生成完成，耗時: {recommendation_elapsed:.2f}秒")
        
        total_elapsed = time.time() - start_time
        logger.info(f"投資建議請求處理完成，總耗時: {total_elapsed:.2f}秒")
        
        return jsonify(recommendation)
        
    except Exception as e:
        total_elapsed = time.time() - start_time
        logger.error(f"獲取每日建議錯誤，耗時: {total_elapsed:.2f}秒，錯誤: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'服務暫時不可用，請稍後再試。錯誤代碼: {str(e)[:50]}',
            'elapsed_time': total_elapsed
        }), 500

@app.route('/api/etf-list', methods=['GET'])
def get_etf_list():
    """獲取所有 ETF 清單"""
    try:
        import json
        import os
        
        # 讀取驗證過的 ETF 清單文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        etf_list_path = os.path.join(current_dir, 'verified_etf_list.json')
        
        with open(etf_list_path, 'r', encoding='utf-8') as f:
            etf_list = json.load(f)
        
        # 轉換格式以符合前端期望
        formatted_etf_list = []
        for etf in etf_list:
            formatted_etf_list.append({
                'symbol': etf['symbol'],
                'name': etf['name'],
                'valid': etf.get('valid', True)
            })
        
        return jsonify(formatted_etf_list)
        
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
        # 簡單的健康檢查 - 檢查ETF清單是否可用
        etf_list = data_fetcher.get_taiwan_etf_list()
        return jsonify({
            'status': 'healthy',
            'etf_count': len(etf_list),
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/custom-recommendation', methods=['POST'])
def custom_recommendation():
    """自訂投資建議"""

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
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)


