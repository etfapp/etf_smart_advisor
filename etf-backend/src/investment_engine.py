"""
升級版投資判斷引擎
新增價格水位評估、智能分批進場、風險控制等功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class InvestmentEngine:
    """升級版投資判斷引擎"""
    
    def __init__(self):
        self.market_analyzer = MarketAnalyzer()
        self.etf_screener = ETFScreener()
        self.position_calculator = PositionCalculator()
        self.risk_monitor = RiskMonitor()
        self.advice_generator = AdviceGenerator()
        self.price_level_analyzer = PriceLevelAnalyzer()  # 新增價格水位分析器
    
    def get_daily_recommendation(self, user_profile: Dict, etf_data: List[Dict], market_data: Dict) -> Dict:
        """獲取每日投資建議"""
        try:
            # 獲取用戶自選的 ETF 和佈局檔數
            selected_etfs_symbols = user_profile.get('selected_etfs', [])
            num_etfs_to_invest = user_profile.get('num_etfs_to_invest', 0)
            
            # 1. 分析市場環境
            market_strategy = self.market_analyzer.analyze(market_data)
            
            # 2. 篩選和評分 ETF（包含價格水位分析）
            if selected_etfs_symbols:
                filtered_etf_data = [etf for etf in etf_data if etf['symbol'] in selected_etfs_symbols]
                etf_scores = self.etf_screener.screen_and_score(filtered_etf_data)
            else:
                etf_scores = self.etf_screener.screen_and_score(etf_data)
            
            # 3. 價格水位分析
            for etf_score in etf_scores:
                price_level_info = self.price_level_analyzer.calculate_price_level(etf_score)
                etf_score.update(price_level_info)
            
            # 4. 計算資金配置（考慮價格水位）
            positions = self.position_calculator.calculate(
                user_profile.get('available_cash', 100000),
                market_strategy,
                etf_scores,
                num_etfs_to_invest
            )
            
            # 5. 風險監控
            risk_alerts = self.risk_monitor.check_risks(etf_scores)
            
            # 6. 生成投資建議
            advice = self.advice_generator.generate(
                market_strategy, etf_scores, risk_alerts, user_profile
            )
            
            return {
                'success': True,
                'strategy': market_strategy,
                'positions': positions,
                'advice': advice,
                'risk_alerts': risk_alerts,
                'market_data': market_data,
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"投資引擎錯誤: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class PriceLevelAnalyzer:
    """價格水位分析器"""
    
    def calculate_price_level(self, etf_data: Dict) -> Dict:
        """計算價格水位"""
        try:
            current_price = etf_data.get('current_price', 50)
            
            # 模擬52週高低價（實際應從數據源獲取）
            price_52w_high = current_price * (1 + np.random.uniform(0.1, 0.3))
            price_52w_low = current_price * (1 - np.random.uniform(0.1, 0.3))
            
            # 計算價格在52週區間的位置 (0-100)
            if price_52w_high == price_52w_low:
                price_percentile = 50
            else:
                price_percentile = ((current_price - price_52w_low) / 
                                  (price_52w_high - price_52w_low)) * 100
            
            # 定義水位等級和安全係數
            if price_percentile <= 20:
                level = "極低水位"
                safety_multiplier = 1.5  # 可增加50%投資
                signal = "綠燈"
                description = "價格處於歷史低位，絕佳進場機會"
            elif price_percentile <= 40:
                level = "低水位"
                safety_multiplier = 1.2  # 可增加20%投資
                signal = "綠燈"
                description = "價格偏低，適合逢低布局"
            elif price_percentile <= 60:
                level = "中等水位"
                safety_multiplier = 1.0  # 正常投資
                signal = "黃燈"
                description = "價格處於合理區間，可正常配置"
            elif price_percentile <= 80:
                level = "高水位"
                safety_multiplier = 0.7  # 減少30%投資
                signal = "黃燈"
                description = "價格偏高，建議減少投資比例"
            else:
                level = "極高水位"
                safety_multiplier = 0.4  # 減少60%投資
                signal = "紅燈"
                description = "價格處於歷史高位，建議等待回調"
            
            return {
                'price_level': {
                    'percentile': round(price_percentile, 1),
                    'level': level,
                    'signal': signal,
                    'description': description,
                    'safety_multiplier': safety_multiplier,
                    'price_52w_high': round(price_52w_high, 2),
                    'price_52w_low': round(price_52w_low, 2),
                    'current_price': current_price
                }
            }
            
        except Exception as e:
            logger.error(f"價格水位計算錯誤: {e}")
            return {
                'price_level': {
                    'percentile': 50,
                    'level': "中等水位",
                    'signal': "黃燈",
                    'description': "無法計算價格水位，採用中性評估",
                    'safety_multiplier': 1.0,
                    'current_price': etf_data.get('current_price', 50)
                }
            }

class MarketAnalyzer:
    """市場分析器"""
    
    def analyze(self, market_data: Dict) -> Dict:
        """分析市場環境並決定策略"""
        try:
            vix = market_data.get('vix', 20)
            taiex_rsi = market_data.get('taiex_rsi', 50)
            economic_indicator = market_data.get('economic_indicator', '綠燈')
            
            # VIX 評分 (40% 權重)
            vix_score = self._calculate_vix_score(vix)
            
            # 技術面評分 (40% 權重)
            technical_score = self._calculate_technical_score(taiex_rsi)
            
            # 經濟指標評分 (20% 權重)
            economic_score = self._calculate_economic_score(economic_indicator)
            
            # 綜合評分
            total_score = (vix_score * 0.4 + technical_score * 0.4 + economic_score * 0.2)
            
            # 決定策略
            if total_score >= 70:
                strategy = "積極策略"
                investment_ratio = 0.8
                description = "市場處於低位，建議積極進場布局優質 ETF"
            elif total_score >= 40:
                strategy = "平衡策略"
                investment_ratio = 0.6
                description = "市場處於正常區間，建議平衡配置，分批進場"
            else:
                strategy = "保守策略"
                investment_ratio = 0.3
                description = "市場處於高位，建議保守操作，等待更好時機"
            
            return {
                'strategy': strategy,
                'investment_ratio': investment_ratio,
                'description': description,
                'scores': {
                    'vix_score': round(vix_score, 1),
                    'technical_score': round(technical_score, 1),
                    'economic_score': round(economic_score, 1),
                    'total_score': round(total_score, 1)
                },
                'indicators': {
                    'vix': vix,
                    'taiex_rsi': taiex_rsi,
                    'economic_indicator': economic_indicator
                }
            }
            
        except Exception as e:
            logger.error(f"市場分析錯誤: {e}")
            return {
                'strategy': '平衡策略',
                'investment_ratio': 0.5,
                'description': '無法分析市場環境，建議採用平衡策略',
                'scores': {'total_score': 50},
                'indicators': {}
            }
    
    def _calculate_vix_score(self, vix: float) -> float:
        """計算 VIX 評分"""
        if vix > 30:
            return 90  # 極度恐慌，絕佳進場機會
        elif vix > 25:
            return 75  # 恐慌，好的進場機會
        elif vix > 20:
            return 60  # 略微緊張，正常
        elif vix > 15:
            return 40  # 正常，中性
        else:
            return 20  # 過度樂觀，需謹慎
    
    def _calculate_technical_score(self, taiex_rsi: float) -> float:
        """計算技術面評分"""
        if taiex_rsi < 30:
            return 90  # 超賣，進場機會
        elif taiex_rsi < 40:
            return 70  # 偏弱，可考慮
        elif taiex_rsi < 60:
            return 50  # 正常區間
        elif taiex_rsi < 70:
            return 30  # 偏強，謹慎
        else:
            return 10  # 超買，避免
    
    def _calculate_economic_score(self, indicator: str) -> float:
        """計算經濟指標評分"""
        score_map = {
            '藍燈': 90,    # 低迷，進場機會
            '黃藍燈': 70,  # 轉弱，逢低布局
            '綠燈': 50,    # 穩定，正常配置
            '黃紅燈': 30,  # 注意，謹慎操作
            '紅燈': 10     # 過熱，減碼
        }
        return score_map.get(indicator, 50)

class ETFScreener:
    """升級版 ETF 篩選器"""
    
    def screen_and_score(self, etf_data: List[Dict]) -> List[Dict]:
        """篩選並評分 ETF"""
        scored_etfs = []
        
        for etf in etf_data:
            try:
                # 計算基本面評分
                fundamental_score = self._calculate_fundamental_score(etf)
                
                # 計算技術面評分
                technical_score = self._calculate_technical_score(etf)
                
                # 計算流動性評分
                liquidity_score = self._calculate_liquidity_score(etf)
                
                # 綜合評分 (基本面 50%, 技術面 30%, 流動性 20%)
                final_score = (fundamental_score * 0.5 + 
                             technical_score * 0.3 + 
                             liquidity_score * 0.2)
                
                # 決定評級
                if final_score >= 80:
                    rating = '綠燈'
                    recommendation = '強烈建議'
                elif final_score >= 60:
                    rating = '黃燈'
                    recommendation = '可考慮'
                else:
                    rating = '紅燈'
                    recommendation = '暫不建議'
                
                scored_etf = {
                    'symbol': etf['symbol'],
                    'name': etf['name'],
                    'current_price': etf.get('current_price', 50),
                    'final_score': round(final_score, 1),
                    'rating': rating,
                    'recommendation': recommendation,
                    'scores': {
                        'fundamental': round(fundamental_score, 1),
                        'technical': round(technical_score, 1),
                        'liquidity': round(liquidity_score, 1)
                    },
                    'valid': etf.get('valid', True)
                }
                
                scored_etfs.append(scored_etf)
                
            except Exception as e:
                logger.error(f"ETF {etf.get('symbol', 'Unknown')} 評分錯誤: {e}")
                continue
        
        # 按評分排序
        scored_etfs.sort(key=lambda x: x['final_score'], reverse=True)
        return scored_etfs
    
    def _calculate_fundamental_score(self, etf: Dict) -> float:
        """計算基本面評分"""
        # 模擬基本面指標（實際應從數據源獲取）
        expense_ratio = etf.get('expense_ratio', 0.5)  # 費用率
        aum = etf.get('aum', 1000)  # 資產規模（百萬）
        dividend_yield = etf.get('dividend_yield', 3.0)  # 股息率
        
        # 費用率評分（越低越好）
        expense_score = max(0, 100 - expense_ratio * 100)
        
        # 規模評分（越大越好，但有上限）
        aum_score = min(100, (aum / 10000) * 100)
        
        # 股息率評分
        dividend_score = min(100, dividend_yield * 20)
        
        return (expense_score * 0.4 + aum_score * 0.3 + dividend_score * 0.3)
    
    def _calculate_technical_score(self, etf: Dict) -> float:
        """計算技術面評分"""
        # 模擬技術指標
        rsi = np.random.uniform(30, 70)
        ma_trend = np.random.choice(['上升', '下降', '橫盤'])
        volume_ratio = np.random.uniform(0.8, 1.5)
        
        # RSI 評分
        if 30 <= rsi <= 70:
            rsi_score = 80
        elif rsi < 30:
            rsi_score = 60  # 超賣
        else:
            rsi_score = 40  # 超買
        
        # 趨勢評分
        trend_score = {'上升': 80, '橫盤': 50, '下降': 20}[ma_trend]
        
        # 成交量評分
        volume_score = min(100, volume_ratio * 60)
        
        return (rsi_score * 0.4 + trend_score * 0.4 + volume_score * 0.2)
    
    def _calculate_liquidity_score(self, etf: Dict) -> float:
        """計算流動性評分"""
        # 模擬流動性指標
        avg_volume = etf.get('avg_volume', 1000000)  # 平均成交量
        bid_ask_spread = etf.get('bid_ask_spread', 0.1)  # 買賣價差
        
        # 成交量評分
        volume_score = min(100, (avg_volume / 10000000) * 100)
        
        # 價差評分（越小越好）
        spread_score = max(0, 100 - bid_ask_spread * 1000)
        
        return (volume_score * 0.7 + spread_score * 0.3)

class PositionCalculator:
    """升級版資金配置計算器"""
    
    def calculate(self, available_cash: float, market_strategy: Dict, 
                 etf_scores: List[Dict], num_etfs_to_invest: int = 0) -> List[Dict]:
        """計算資金配置（考慮價格水位）"""
        try:
            if not etf_scores:
                return []
            
            # 基礎投資比例
            base_investment_ratio = market_strategy.get('investment_ratio', 0.6)
            
            # 過濾出評分>=60的ETF
            qualified_etfs = [etf for etf in etf_scores if etf['final_score'] >= 60]
            
            if not qualified_etfs:
                return []
            
            # 確定投資檔數
            if num_etfs_to_invest > 0:
                selected_etfs = qualified_etfs[:num_etfs_to_invest]
            else:
                # 自動選擇前5檔最優ETF
                selected_etfs = qualified_etfs[:5]
            
            positions = []
            total_weight = 0
            
            # 計算每檔ETF的權重（考慮評分和價格水位）
            for etf in selected_etfs:
                # 基礎權重（基於評分）
                base_weight = etf['final_score'] / 100
                
                # 價格水位調整
                price_level = etf.get('price_level', {})
                safety_multiplier = price_level.get('safety_multiplier', 1.0)
                
                # 調整後權重
                adjusted_weight = base_weight * safety_multiplier
                total_weight += adjusted_weight
                
                positions.append({
                    'etf': etf,
                    'weight': adjusted_weight
                })
            
            # 正規化權重並計算實際配置
            final_positions = []
            total_investment = available_cash * base_investment_ratio
            
            for position in positions:
                normalized_weight = position['weight'] / total_weight if total_weight > 0 else 0
                etf = position['etf']
                
                # 計算投資金額
                investment_amount = total_investment * normalized_weight
                
                # 計算股數
                price = etf.get('current_price', 50)
                shares = int(investment_amount / price) if price > 0 else 0
                actual_amount = shares * price
                
                if shares > 0:  # 只包含能買到至少1股的ETF
                    final_positions.append({
                        'symbol': etf['symbol'],
                        'name': etf['name'],
                        'shares': shares,
                        'price': price,
                        'amount': actual_amount,
                        'weight': normalized_weight * 100,
                        'rating': etf['rating'],
                        'recommendation': etf['recommendation'],
                        'reasoning': self._generate_reasoning(etf),
                        'price_level': etf.get('price_level', {})
                    })
            
            return final_positions
            
        except Exception as e:
            logger.error(f"資金配置計算錯誤: {e}")
            return []
    
    def _generate_reasoning(self, etf: Dict) -> str:
        """生成投資理由"""
        score = etf['final_score']
        rating = etf['rating']
        price_level = etf.get('price_level', {})
        
        reasoning = f"評分 {score} 分，{rating}評級"
        
        if price_level:
            level_desc = price_level.get('description', '')
            reasoning += f"，{level_desc}"
        
        return reasoning

class RiskMonitor:
    """風險監控器"""
    
    def check_risks(self, etf_scores: List[Dict]) -> List[Dict]:
        """檢查風險警示"""
        risks = []
        
        try:
            # 檢查整體市場風險
            green_count = sum(1 for etf in etf_scores if etf['rating'] == '綠燈')
            total_count = len(etf_scores)
            
            if total_count > 0:
                green_ratio = green_count / total_count
                
                if green_ratio < 0.1:
                    risks.append({
                        'type': 'market_risk',
                        'level': 'high',
                        'title': '市場風險警示',
                        'message': f'僅有 {green_count} 檔綠燈ETF，市場整體偏弱，建議謹慎操作'
                    })
                elif green_ratio < 0.3:
                    risks.append({
                        'type': 'market_risk',
                        'level': 'medium',
                        'title': '市場注意',
                        'message': f'綠燈ETF比例較低（{green_ratio:.1%}），建議分散投資'
                    })
            
            # 檢查價格水位風險
            high_price_count = 0
            for etf in etf_scores:
                price_level = etf.get('price_level', {})
                if price_level.get('signal') == '紅燈':
                    high_price_count += 1
            
            if high_price_count > len(etf_scores) * 0.5:
                risks.append({
                    'type': 'valuation_risk',
                    'level': 'medium',
                    'title': '估值風險',
                    'message': f'超過一半的ETF處於高價位，建議等待回調機會'
                })
            
        except Exception as e:
            logger.error(f"風險檢查錯誤: {e}")
        
        return risks

class AdviceGenerator:
    """投資建議生成器"""
    
    def generate(self, market_strategy: Dict, etf_scores: List[Dict], 
                risk_alerts: List[Dict], user_profile: Dict) -> Dict:
        """生成投資建議"""
        try:
            # 統計ETF分布
            green_lights = sum(1 for etf in etf_scores if etf['rating'] == '綠燈')
            yellow_lights = sum(1 for etf in etf_scores if etf['rating'] == '黃燈')
            red_lights = sum(1 for etf in etf_scores if etf['rating'] == '紅燈')
            
            # 生成市場觀點
            strategy = market_strategy.get('strategy', '平衡策略')
            if green_lights > 5:
                market_outlook = f"市場呈現積極信號，有 {green_lights} 檔綠燈ETF，適合進場布局。"
            elif green_lights > 0:
                market_outlook = f"市場處於正常區間，有 {green_lights} 檔綠燈、{yellow_lights} 檔黃燈 ETF，建議平衡配置。"
            else:
                market_outlook = f"市場整體偏弱，建議保守操作，等待更好的進場時機。"
            
            # 生成操作建議
            if strategy == "積極策略":
                action_advice = "建議積極進場，重點配置綠燈ETF，可適度加碼低價位標的。"
            elif strategy == "平衡策略":
                action_advice = "建議採用定期定額方式投入，分散時間風險，逐步建立部位。"
            else:
                action_advice = "建議保守操作，僅配置少量資金，等待市場回調後再加碼。"
            
            return {
                'market_outlook': market_outlook,
                'action_advice': action_advice,
                'etf_distribution': {
                    'green_lights': green_lights,
                    'yellow_lights': yellow_lights,
                    'red_lights': red_lights
                },
                'strategy_summary': market_strategy.get('description', ''),
                'risk_level': 'high' if len(risk_alerts) > 2 else 'medium' if len(risk_alerts) > 0 else 'low'
            }
            
        except Exception as e:
            logger.error(f"建議生成錯誤: {e}")
            return {
                'market_outlook': '無法分析當前市場狀況',
                'action_advice': '建議諮詢專業投資顧問',
                'etf_distribution': {'green_lights': 0, 'yellow_lights': 0, 'red_lights': 0},
                'strategy_summary': '系統暫時無法提供建議',
                'risk_level': 'unknown'
            }

