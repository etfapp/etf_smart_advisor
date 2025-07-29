from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import threading
import time
import os
from datetime import datetime

# 導入自定義模組
from data_fetcher import ImprovedDataFetcher
from investment_engine import ImprovedInvestmentEngine
from risk_manager import RiskManager
from portfolio_manager import PortfolioManager
from daily_recommendation_api import add_daily_recommendation_routes

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建Flask應用
app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 全局變量
data_fetcher = None
investment_engine = None
risk_manager = None
portfolio_manager = None

def initialize_app():
    """初始化應用組件"""
    global data_fetcher, investment_engine, risk_manager, portfolio_manager
    
    try:
        logger.info("正在初始化ETF智能投資顧問後端服務...")
        
        # 初始化組件
        data_fetcher = ImprovedDataFetcher()
        investment_engine = ImprovedInvestmentEngine(data_fetcher)
        risk_manager = RiskManager(data_fetcher)
        portfolio_manager = PortfolioManager()
        
        logger.info("應用初始化成功")
        
        # 註冊每日推薦API路由
        add_daily_recommendation_routes(app, data_fetcher, investment_engine, risk_manager)
        logger.info("每日推薦API路由已註冊")
        
    except Exception as e:
        logger.error(f"應用初始化失敗: {e}")

def keep_alive():
    """保持服務活躍，避免Render休眠"""
    while True:
        try:
            time.sleep(600)  # 每10分鐘ping一次
            logger.info("Keep alive ping")
        except Exception as e:
            logger.error(f"Keep alive error: {e}")

# API路由

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'ETF智能投資顧問'
    })

@app.route('/api/market-overview', methods=['GET'])
def get_market_overview():
    """獲取市場概況"""
    try:
        if not data_fetcher:
            initialize_app()
        
        # 獲取台股加權指數數據
        market_data = data_fetcher.get_market_overview()
        
        return jsonify({
            'success': True,
            'data': market_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'index_value': 17500.0,
                'change_percent': 0.5,
                'volatility': 0.15,
                'trend_description': '震盪整理'
            }
        }), 200

@app.route('/api/investment-advice', methods=['GET'])
def get_investment_advice():
    """獲取投資建議"""
    try:
        if not investment_engine:
            initialize_app()
        
        # 獲取參數
        funds = float(request.args.get('funds', 100000))
        risk_tolerance = request.args.get('risk_tolerance', 'medium')
        
        # 生成投資建議
        user_profile = {
            'available_funds': funds,
            'risk_tolerance': risk_tolerance
        }
        
        advice = investment_engine.generate_investment_advice(user_profile)
        recommendations = advice.get('recommendations', [])
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total_funds': funds,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating investment advice: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendations': []
        }), 200

@app.route('/api/execute-investment', methods=['POST'])
def execute_investment():
    """執行投資（模擬）"""
    try:
        if not portfolio_manager:
            initialize_app()
        
        data = request.get_json()
        recommendations = data.get('recommendations', [])
        total_funds = data.get('total_funds', 0)
        
        # 執行投資
        result = portfolio_manager.execute_investment(recommendations, total_funds)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error executing investment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/portfolio/<user_id>', methods=['GET'])
def get_portfolio(user_id):
    """獲取用戶投資組合"""
    try:
        if not portfolio_manager:
            initialize_app()
        
        portfolio = portfolio_manager.get_user_portfolio(user_id)
        
        return jsonify({
            'success': True,
            'portfolio': portfolio,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting portfolio for {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/risk-assessment/<user_id>', methods=['GET'])
def get_risk_assessment(user_id):
    """獲取風險評估"""
    try:
        if not risk_manager or not portfolio_manager:
            initialize_app()
        
        portfolio = portfolio_manager.get_user_portfolio(user_id)
        risk_assessment = risk_manager.assess_portfolio_risk(portfolio)
        
        return jsonify({
            'success': True,
            'risk_assessment': risk_assessment,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting risk assessment for {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/etf-list', methods=['GET'])
def get_etf_list():
    """獲取ETF清單"""
    try:
        if not data_fetcher:
            initialize_app()
        
        etf_list = data_fetcher.get_available_etfs()
        
        return jsonify({
            'success': True,
            'etfs': etf_list,
            'count': len(etf_list),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting ETF list: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'etfs': []
        }), 500

@app.route('/api/etf/<symbol>', methods=['GET'])
def get_etf_data(symbol):
    """獲取特定ETF數據"""
    try:
        if not data_fetcher:
            initialize_app()
        
        etf_data = data_fetcher.fetch_etf_data(symbol)
        
        return jsonify({
            'success': True,
            'data': etf_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting ETF data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'API endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # 初始化應用
    initialize_app()
    
    # 啟動keep-alive線程（僅在生產環境）
    if os.environ.get('RENDER'):
        keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
        keep_alive_thread.start()
        logger.info("Keep-alive thread started for Render deployment")
    
    # 啟動Flask應用
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

