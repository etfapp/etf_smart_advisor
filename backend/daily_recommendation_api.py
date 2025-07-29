"""
每日推薦API端點
為前端提供每日投資推薦功能
"""

from flask import jsonify, request
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def add_daily_recommendation_routes(app, data_fetcher, investment_engine, risk_manager):
    """添加每日推薦相關的API路由"""
    
    @app.route('/api/daily-recommendation', methods=['GET'])
    def get_daily_recommendation():
        """獲取每日投資推薦"""
        try:
            # 獲取參數
            funds = float(request.args.get('funds', 100000))
            risk_tolerance = request.args.get('risk_tolerance', 'medium')
            
            logger.info(f"生成每日推薦 - 資金: {funds}, 風險偏好: {risk_tolerance}")
            
            # 確保組件已初始化
            if not investment_engine:
                return jsonify({
                    'success': False,
                    'error': '投資引擎未初始化',
                    'recommendations': []
                }), 500
            
            # 生成投資建議
            user_profile = {
                'available_funds': funds,
                'risk_tolerance': risk_tolerance,
                'investment_horizon': 'medium_term'  # 中期投資
            }
            
            # 獲取投資建議
            advice = investment_engine.generate_investment_advice(user_profile)
            recommendations = advice.get('recommendations', [])
            
            # 獲取市場概況
            market_data = {}
            try:
                if data_fetcher:
                    market_data = data_fetcher.get_market_overview()
            except Exception as e:
                logger.warning(f"無法獲取市場數據: {e}")
                market_data = {
                    'index_value': 17500.0,
                    'change_percent': 0.5,
                    'volatility': 0.15,
                    'trend_description': '震盪整理'
                }
            
            # 風險評估
            risk_level = 'medium'
            risk_warnings = []
            try:
                if risk_manager and recommendations:
                    risk_assessment = risk_manager.assess_recommendations_risk(recommendations)
                    risk_level = risk_assessment.get('overall_risk', 'medium')
                    risk_warnings = risk_assessment.get('warnings', [])
            except Exception as e:
                logger.warning(f"風險評估失敗: {e}")
            
            # 構建響應
            response_data = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'market_overview': market_data,
                'recommendations': recommendations,
                'total_funds': funds,
                'allocated_funds': sum(rec.get('suggested_amount', 0) for rec in recommendations),
                'risk_assessment': {
                    'level': risk_level,
                    'warnings': risk_warnings
                },
                'summary': {
                    'total_etfs': len(recommendations),
                    'green_signals': len([r for r in recommendations if r.get('signal') == 'green']),
                    'yellow_signals': len([r for r in recommendations if r.get('signal') == 'yellow']),
                    'expected_return': advice.get('expected_return', 0.08)
                }
            }
            
            logger.info(f"每日推薦生成成功 - 推薦{len(recommendations)}檔ETF")
            return jsonify(response_data)
            
        except ValueError as e:
            logger.error(f"參數錯誤: {e}")
            return jsonify({
                'success': False,
                'error': f'參數錯誤: {str(e)}',
                'recommendations': []
            }), 400
            
        except Exception as e:
            logger.error(f"生成每日推薦失敗: {e}")
            return jsonify({
                'success': False,
                'error': f'服務暫時不可用: {str(e)}',
                'recommendations': []
            }), 500
    
    @app.route('/api/daily-recommendation/quick', methods=['GET'])
    def get_quick_recommendation():
        """獲取快速推薦（簡化版）"""
        try:
            # 使用預設參數快速生成推薦
            funds = 100000  # 預設10萬
            risk_tolerance = 'medium'  # 預設中等風險
            
            logger.info("生成快速推薦")
            
            if not investment_engine:
                return jsonify({
                    'success': False,
                    'error': '投資引擎未初始化',
                    'recommendations': []
                }), 500
            
            user_profile = {
                'available_funds': funds,
                'risk_tolerance': risk_tolerance
            }
            
            advice = investment_engine.generate_investment_advice(user_profile)
            recommendations = advice.get('recommendations', [])
            
            # 只返回前5個推薦
            top_recommendations = recommendations[:5]
            
            return jsonify({
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'recommendations': top_recommendations,
                'total_funds': funds,
                'message': '快速推薦已生成'
            })
            
        except Exception as e:
            logger.error(f"生成快速推薦失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'recommendations': []
            }), 500

