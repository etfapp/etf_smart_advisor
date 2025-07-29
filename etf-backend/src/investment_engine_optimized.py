"""
優化版投資判斷引擎
整合真實技術指標，調整評分標準，提升投資建議準確性
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class OptimizedInvestmentEngine:
    """優化版投資判斷引擎"""
    
    def __init__(self):
        self.market_analyzer = OptimizedMarketAnalyzer()
        self.etf_screener = OptimizedETFScreener()
        self.position_calculator = OptimizedPositionCalculator()
        self.risk_monitor = OptimizedRiskMonitor()
        self.advice_generator = OptimizedAdviceGenerator()
    
    def get_daily_recommendation(self, user_profile: Dict, etf_data: List[Dict], market_data: Dict) -> Dict:
        """獲取每日投資建議"""
        try:
            # 獲取用戶自選的 ETF 和佈局檔數
            selected_etfs_symbols = user_profile.get('selected_etfs', [])
            num_etfs_to_invest = user_profile.get('num_etfs_to_invest', 0)
            
            # 1. 分析市場環境
            market_strategy = self.market_analyzer.analyze(market_data)
            
            # 2. 篩選和評分 ETF
            if selected_etfs_symbols:
                filtered_etf_data = [etf for etf in etf_data if etf['symbol'] in selected_etfs_symbols]
                etf_scores = self.etf_screener.screen_and_score(filtered_etf_data)
            else:
                etf_scores = self.etf_screener.screen_and_score(etf_data)
            
            # 3. 計算資金配置
            positions = self.position_calculator.calculate(
                user_profile.get('available_cash', 100000),
                market_strategy,
                etf_scores,
                num_etfs_to_invest
            )
            
            # 4. 風險監控
            risk_alerts = self.risk_monitor.check_risks(etf_scores, market_data)
            
            # 5. 生成投資建議
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
                'etf_analysis': {
                    'total_analyzed': len(etf_data),
                    'qualified_etfs': len([etf for etf in etf_scores if etf['final_score'] >= 40]),
                    'recommended_etfs': len([etf for etf in etf_scores if etf['final_score'] >= 60])
                },
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"投資引擎錯誤: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class OptimizedMarketAnalyzer:
    """優化版市場分析器"""
    
    def analyze(self, market_data: Dict) -> Dict:
        """分析市場環境並決定策略"""
        try:
            vix = market_data.get('vix', 20)
            taiex_rsi = market_data.get('taiex_rsi', 50)
            taiex_trend = market_data.get('taiex_trend', '橫盤')
            economic_indicator = market_data.get('economic_indicator', '綠燈')
            
            # VIX 評分 (30% 權重)
            vix_score = self._calculate_vix_score(vix)
            
            # 技術面評分 (40% 權重)
            technical_score = self._calculate_technical_score(taiex_rsi, taiex_trend)
            
            # 經濟指標評分 (30% 權重)
            economic_score = self._calculate_economic_score(economic_indicator)
            
            # 綜合評分
            total_score = (vix_score * 0.3 + technical_score * 0.4 + economic_score * 0.3)
            
            # 決定策略（調整門檻，使建議更實用）
            if total_score >= 65:
                strategy = "積極策略"
                investment_ratio = 0.8
                description = "市場處於低位，建議積極進場布局優質 ETF"
            elif total_score >= 35:  # 降低門檻
                strategy = "平衡策略"
                investment_ratio = 0.6
                description = "市場處於正常區間，建議平衡配置，分批進場"
            else:
                strategy = "保守策略"
                investment_ratio = 0.4  # 提高最低投資比例
                description = "市場處於高位，建議保守操作，但仍可適度配置"
            
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
                    'taiex_trend': taiex_trend,
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
            return 85  # 極度恐慌，絕佳進場機會
        elif vix > 25:
            return 70  # 恐慌，好的進場機會
        elif vix > 20:
            return 55  # 略微緊張，正常
        elif vix > 15:
            return 45  # 正常，中性
        else:
            return 30  # 過度樂觀，需謹慎
    
    def _calculate_technical_score(self, taiex_rsi: float, taiex_trend: str) -> float:
        """計算技術面評分"""
        # RSI評分
        if taiex_rsi < 30:
            rsi_score = 85  # 超賣，進場機會
        elif taiex_rsi < 40:
            rsi_score = 70  # 偏弱，可考慮
        elif taiex_rsi < 60:
            rsi_score = 50  # 正常區間
        elif taiex_rsi < 70:
            rsi_score = 35  # 偏強，謹慎
        else:
            rsi_score = 20  # 超買，避免
        
        # 趨勢評分
        trend_score = {'上升': 70, '橫盤': 50, '下降': 30}.get(taiex_trend, 50)
        
        # 綜合技術面評分
        return (rsi_score * 0.7 + trend_score * 0.3)
    
    def _calculate_economic_score(self, indicator: str) -> float:
        """計算經濟指標評分"""
        score_map = {
            '藍燈': 80,    # 低迷，進場機會
            '黃藍燈': 65,  # 轉弱，逢低布局
            '綠燈': 50,    # 穩定，正常配置
            '黃紅燈': 35,  # 注意，謹慎操作
            '紅燈': 20     # 過熱，減碼
        }
        return score_map.get(indicator, 50)

class OptimizedETFScreener:
    """優化版 ETF 篩選器"""
    
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
                
                # 計算價格水位評分
                price_level_score = self._calculate_price_level_score(etf)
                
                # 綜合評分 (調整權重)
                final_score = (fundamental_score * 0.3 + 
                             technical_score * 0.4 + 
                             liquidity_score * 0.15 +
                             price_level_score * 0.15)
                
                # 決定評級（降低門檻）
                if final_score >= 70:
                    rating = '綠燈'
                    recommendation = '強烈建議'
                elif final_score >= 50:  # 降低門檻
                    rating = '黃燈'
                    recommendation = '可考慮'
                elif final_score >= 30:  # 新增中等評級
                    rating = '橙燈'
                    recommendation = '謹慎考慮'
                else:
                    rating = '紅燈'
                    recommendation = '暫不建議'
                
                # 計算價格水位信息
                price_level_info = self._get_price_level_info(etf)
                
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
                        'liquidity': round(liquidity_score, 1),
                        'price_level': round(price_level_score, 1)
                    },
                    'price_level': price_level_info,
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
        try:
            fundamental = etf.get('fundamental_indicators', {})
            
            # 費用率評分（越低越好）
            expense_ratio = fundamental.get('expense_ratio', 0.5)
            expense_score = max(0, 100 - expense_ratio * 100)
            
            # 資產規模評分
            aum = fundamental.get('aum', 1000000000)
            aum_score = min(100, (aum / 10000000000) * 100)  # 100億為滿分
            
            # 股息率評分
            dividend_yield = fundamental.get('dividend_yield', 0.03)
            dividend_score = min(100, dividend_yield * 2000)  # 5%為滿分
            
            # 夏普比率評分
            sharpe_ratio = fundamental.get('sharpe_ratio', 0.0)
            sharpe_score = max(0, min(100, (sharpe_ratio + 1) * 50))  # -1到1映射到0-100
            
            return (expense_score * 0.3 + aum_score * 0.2 + 
                   dividend_score * 0.3 + sharpe_score * 0.2)
        except Exception as e:
            logger.warning(f"基本面評分計算錯誤: {e}")
            return 50.0
    
    def _calculate_technical_score(self, etf: Dict) -> float:
        """計算技術面評分"""
        try:
            technical = etf.get('technical_indicators', {})
            
            # RSI 評分
            rsi = technical.get('rsi', 50)
            if 30 <= rsi <= 70:
                rsi_score = 80
            elif rsi < 30:
                rsi_score = 90  # 超賣，機會
            elif rsi > 70:
                rsi_score = 40  # 超買，謹慎
            else:
                rsi_score = 60
            
            # MACD 評分
            macd_data = technical.get('macd', {})
            macd = macd_data.get('macd', 0)
            signal = macd_data.get('signal', 0)
            if macd > signal:
                macd_score = 70  # 金叉，看漲
            else:
                macd_score = 40  # 死叉，看跌
            
            # 移動平均線評分
            ma_data = technical.get('moving_averages', {})
            current_price = ma_data.get('current_price', 50)
            ma20 = ma_data.get('ma20', 50)
            ma50 = ma_data.get('ma50', 50)
            
            if current_price > ma20 > ma50:
                ma_score = 80  # 多頭排列
            elif current_price > ma20:
                ma_score = 60  # 短期強勢
            elif current_price < ma20 < ma50:
                ma_score = 30  # 空頭排列
            else:
                ma_score = 50  # 中性
            
            # 布林通道評分
            bb_data = technical.get('bollinger_bands', {})
            bb_upper = bb_data.get('upper', 52)
            bb_lower = bb_data.get('lower', 48)
            bb_middle = bb_data.get('middle', 50)
            
            if current_price < bb_lower:
                bb_score = 85  # 超賣區，機會
            elif current_price > bb_upper:
                bb_score = 35  # 超買區，謹慎
            elif bb_lower < current_price < bb_middle:
                bb_score = 70  # 下半部，偏多
            else:
                bb_score = 50  # 中性
            
            return (rsi_score * 0.3 + macd_score * 0.25 + 
                   ma_score * 0.25 + bb_score * 0.2)
        except Exception as e:
            logger.warning(f"技術面評分計算錯誤: {e}")
            return 50.0
    
    def _calculate_liquidity_score(self, etf: Dict) -> float:
        """計算流動性評分"""
        try:
            liquidity = etf.get('liquidity_indicators', {})
            
            # 平均成交量評分
            avg_volume = liquidity.get('avg_volume', 1000000)
            volume_score = min(100, (avg_volume / 10000000) * 100)  # 1000萬為滿分
            
            # 成交量波動率評分（越低越好）
            volume_volatility = liquidity.get('volume_volatility', 0.3)
            volatility_score = max(0, 100 - volume_volatility * 200)
            
            # 買賣價差評分（越小越好）
            bid_ask_spread = liquidity.get('bid_ask_spread', 0.1)
            spread_score = max(0, 100 - bid_ask_spread * 1000)
            
            return (volume_score * 0.5 + volatility_score * 0.25 + spread_score * 0.25)
        except Exception as e:
            logger.warning(f"流動性評分計算錯誤: {e}")
            return 50.0
    
    def _calculate_price_level_score(self, etf: Dict) -> float:
        """計算價格水位評分"""
        try:
            technical = etf.get('technical_indicators', {})
            price_levels = technical.get('price_levels', {})
            
            price_percentile = price_levels.get('price_percentile', 50)
            
            # 價格水位評分（越低越好，表示進場機會）
            if price_percentile <= 20:
                return 90  # 極低水位，絕佳機會
            elif price_percentile <= 40:
                return 75  # 低水位，好機會
            elif price_percentile <= 60:
                return 50  # 中等水位，中性
            elif price_percentile <= 80:
                return 35  # 高水位，謹慎
            else:
                return 20  # 極高水位，避免
        except Exception as e:
            logger.warning(f"價格水位評分計算錯誤: {e}")
            return 50.0
    
    def _get_price_level_info(self, etf: Dict) -> Dict:
        """獲取價格水位信息"""
        try:
            technical = etf.get('technical_indicators', {})
            price_levels = technical.get('price_levels', {})
            
            price_percentile = price_levels.get('price_percentile', 50)
            current_price = etf.get('current_price', 50)
            
            # 定義水位等級和安全係數
            if price_percentile <= 20:
                level = "極低水位"
                safety_multiplier = 1.3  # 可增加30%投資
                signal = "綠燈"
                description = "價格處於歷史低位，絕佳進場機會"
            elif price_percentile <= 40:
                level = "低水位"
                safety_multiplier = 1.15  # 可增加15%投資
                signal = "綠燈"
                description = "價格偏低，適合逢低布局"
            elif price_percentile <= 60:
                level = "中等水位"
                safety_multiplier = 1.0  # 正常投資
                signal = "黃燈"
                description = "價格處於合理區間，可正常配置"
            elif price_percentile <= 80:
                level = "高水位"
                safety_multiplier = 0.8  # 減少20%投資
                signal = "橙燈"
                description = "價格偏高，建議減少投資比例"
            else:
                level = "極高水位"
                safety_multiplier = 0.6  # 減少40%投資
                signal = "紅燈"
                description = "價格處於歷史高位，建議等待回調"
            
            return {
                'percentile': round(price_percentile, 1),
                'level': level,
                'signal': signal,
                'description': description,
                'safety_multiplier': safety_multiplier,
                'price_52w_high': price_levels.get('price_52w_high', current_price * 1.2),
                'price_52w_low': price_levels.get('price_52w_low', current_price * 0.8),
                'current_price': current_price
            }
        except Exception as e:
            logger.warning(f"價格水位信息獲取錯誤: {e}")
            current_price = etf.get('current_price', 50)
            return {
                'percentile': 50,
                'level': "中等水位",
                'signal': "黃燈",
                'description': "無法計算價格水位，採用中性評估",
                'safety_multiplier': 1.0,
                'current_price': current_price
            }

class OptimizedPositionCalculator:
    """優化版資金配置計算器"""
    
    def calculate(self, available_cash: float, market_strategy: Dict, 
                 etf_scores: List[Dict], num_etfs_to_invest: int = 0) -> List[Dict]:
        """計算資金配置"""
        try:
            if not etf_scores:
                return []
            
            # 基礎投資比例
            base_investment_ratio = market_strategy.get('investment_ratio', 0.6)
            
            # 過濾出評分>=40的ETF（降低門檻）
            qualified_etfs = [etf for etf in etf_scores if etf['final_score'] >= 40]
            
            if not qualified_etfs:
                # 如果沒有符合條件的ETF，選擇評分最高的前3檔
                qualified_etfs = etf_scores[:3]
            
            # 確定投資檔數
            if num_etfs_to_invest > 0:
                selected_etfs = qualified_etfs[:num_etfs_to_invest]
            else:
                # 自動選擇前5檔最優ETF
                selected_etfs = qualified_etfs[:5]
            
            if not selected_etfs:
                return []
            
            positions = []
            total_weight = 0
            
            # 計算每檔ETF的權重
            for etf in selected_etfs:
                # 基礎權重（基於評分）
                base_weight = max(0.1, etf['final_score'] / 100)  # 最低10%權重
                
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
                normalized_weight = position['weight'] / total_weight if total_weight > 0 else 1.0 / len(positions)
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
                        'price_level': etf.get('price_level', {}),
                        'scores': etf.get('scores', {})
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
        
        # 添加技術面信息
        scores = etf.get('scores', {})
        if scores.get('technical', 0) >= 60:
            reasoning += "，技術面表現良好"
        elif scores.get('technical', 0) <= 40:
            reasoning += "，技術面偏弱但具潛力"
        
        return reasoning

class OptimizedRiskMonitor:
    """優化版風險監控器"""
    
    def check_risks(self, etf_scores: List[Dict], market_data: Dict) -> List[Dict]:
        """檢查風險警示"""
        risks = []
        
        try:
            # 檢查整體市場風險
            green_count = sum(1 for etf in etf_scores if etf['rating'] == '綠燈')
            yellow_count = sum(1 for etf in etf_scores if etf['rating'] == '黃燈')
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
                elif green_ratio < 0.2:
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
                if price_level.get('signal') in ['紅燈', '橙燈']:
                    high_price_count += 1
            
            if high_price_count > len(etf_scores) * 0.6:
                risks.append({
                    'type': 'valuation_risk',
                    'level': 'medium',
                    'title': '估值風險',
                    'message': f'超過六成的ETF處於高價位，建議等待回調機會'
                })
            
            # 檢查市場技術指標風險
            taiex_rsi = market_data.get('taiex_rsi', 50)
            vix = market_data.get('vix', 20)
            
            if taiex_rsi > 75:
                risks.append({
                    'type': 'technical_risk',
                    'level': 'medium',
                    'title': '技術面風險',
                    'message': f'台股RSI達 {taiex_rsi:.1f}，市場可能過熱，建議謹慎'
                })
            
            if vix > 35:
                risks.append({
                    'type': 'volatility_risk',
                    'level': 'high',
                    'title': '波動率風險',
                    'message': f'VIX指數達 {vix:.1f}，市場恐慌情緒高漲，注意風險控制'
                })
            
        except Exception as e:
            logger.error(f"風險檢查錯誤: {e}")
        
        return risks

class OptimizedAdviceGenerator:
    """優化版投資建議生成器"""
    
    def generate(self, market_strategy: Dict, etf_scores: List[Dict], 
                risk_alerts: List[Dict], user_profile: Dict) -> Dict:
        """生成投資建議"""
        try:
            # 統計ETF分布
            green_lights = sum(1 for etf in etf_scores if etf['rating'] == '綠燈')
            yellow_lights = sum(1 for etf in etf_scores if etf['rating'] == '黃燈')
            orange_lights = sum(1 for etf in etf_scores if etf['rating'] == '橙燈')
            red_lights = sum(1 for etf in etf_scores if etf['rating'] == '紅燈')
            
            # 生成市場觀點
            strategy = market_strategy.get('strategy', '平衡策略')
            if green_lights >= 3:
                market_outlook = f"市場呈現積極信號，有 {green_lights} 檔綠燈ETF，適合進場布局。"
            elif green_lights + yellow_lights >= 5:
                market_outlook = f"市場處於正常區間，有 {green_lights} 檔綠燈、{yellow_lights} 檔黃燈 ETF，建議平衡配置。"
            else:
                market_outlook = f"市場整體偏弱，但仍有 {green_lights + yellow_lights} 檔可考慮的ETF，建議謹慎操作。"
            
            # 生成操作建議
            if strategy == "積極策略":
                action_advice = "建議積極進場，重點配置綠燈ETF，可適度加碼低價位標的。"
            elif strategy == "平衡策略":
                action_advice = "建議採用定期定額方式投入，分散時間風險，逐步建立部位。"
            else:
                action_advice = "建議保守操作，優先選擇高評分ETF，等待更好的進場時機。"
            
            # 生成具體建議
            specific_advice = []
            
            # 高股息ETF建議
            high_dividend_etfs = [etf for etf in etf_scores if '高股息' in etf.get('name', '') and etf['final_score'] >= 50]
            if high_dividend_etfs:
                specific_advice.append(f"高股息ETF中，{high_dividend_etfs[0]['name']} 表現較佳，適合穩健投資者。")
            
            # 科技ETF建議
            tech_etfs = [etf for etf in etf_scores if any(keyword in etf.get('name', '') for keyword in ['科技', '半導體', '5G']) and etf['final_score'] >= 50]
            if tech_etfs:
                specific_advice.append(f"科技類ETF中，{tech_etfs[0]['name']} 具成長潛力，適合積極投資者。")
            
            return {
                'market_outlook': market_outlook,
                'action_advice': action_advice,
                'specific_advice': specific_advice,
                'etf_distribution': {
                    'green_lights': green_lights,
                    'yellow_lights': yellow_lights,
                    'orange_lights': orange_lights,
                    'red_lights': red_lights
                },
                'strategy_summary': market_strategy.get('description', ''),
                'risk_level': 'high' if len(risk_alerts) > 2 else 'medium' if len(risk_alerts) > 0 else 'low',
                'investment_tips': self._generate_investment_tips(market_strategy, etf_scores)
            }
            
        except Exception as e:
            logger.error(f"建議生成錯誤: {e}")
            return {
                'market_outlook': '無法分析當前市場狀況',
                'action_advice': '建議諮詢專業投資顧問',
                'specific_advice': [],
                'etf_distribution': {'green_lights': 0, 'yellow_lights': 0, 'orange_lights': 0, 'red_lights': 0},
                'strategy_summary': '系統暫時無法提供建議',
                'risk_level': 'unknown',
                'investment_tips': []
            }
    
    def _generate_investment_tips(self, market_strategy: Dict, etf_scores: List[Dict]) -> List[str]:
        """生成投資小貼士"""
        tips = []
        
        strategy = market_strategy.get('strategy', '平衡策略')
        
        if strategy == "積極策略":
            tips.append("市場處於低位，可考慮分批加碼優質ETF")
            tips.append("重點關注技術面強勢且價格水位偏低的標的")
        elif strategy == "保守策略":
            tips.append("市場偏高，建議等待回調機會再進場")
            tips.append("可先配置少量資金，觀察市場變化")
        else:
            tips.append("採用定期定額策略，分散時間風險")
            tips.append("平衡配置不同類型ETF，降低集中風險")
        
        # 根據ETF評分分布給建議
        high_score_etfs = [etf for etf in etf_scores if etf['final_score'] >= 70]
        if len(high_score_etfs) >= 3:
            tips.append("當前有多檔高評分ETF可選擇，建議分散投資")
        
        return tips

