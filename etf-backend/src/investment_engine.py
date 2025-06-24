"""
投資判斷引擎
負責市場分析、ETF 評分、資金配置等核心投資邏輯
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class InvestmentEngine:
    """投資判斷引擎"""
    
    def __init__(self):
        self.market_analyzer = MarketAnalyzer()
        self.etf_screener = ETFScreener()
        self.position_calculator = PositionCalculator()
        self.risk_monitor = RiskMonitor()
        self.advice_generator = AdviceGenerator()
    
    def get_daily_recommendation(self, user_profile: Dict, etf_data: List[Dict], market_data: Dict) -> Dict:
        """獲取每日投資建議"""
        try:
            # 1. 分析市場環境
            market_strategy = self.market_analyzer.analyze(market_data)
            
            # 2. 篩選和評分 ETF
            etf_scores = self.etf_screener.screen_and_score(etf_data)
            
            # 3. 計算資金配置
            positions = self.position_calculator.calculate(
                user_profile.get('available_cash', 100000),
                market_strategy,
                etf_scores
            )
            
            # 4. 風險監控
            risk_alerts = self.risk_monitor.check_risks(etf_scores)
            
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
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"投資引擎錯誤: {e}")
            return {
                'success': False,
                'error': str(e)
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
                investment_ratio = 0.8  # 80% 資金投入
                description = "市場處於低位，建議積極進場布局優質 ETF"
            elif total_score >= 40:
                strategy = "平衡策略"
                investment_ratio = 0.6  # 60% 資金投入
                description = "市場處於正常區間，建議平衡配置，分批進場"
            else:
                strategy = "保守策略"
                investment_ratio = 0.3  # 30% 資金投入
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
    """ETF 篩選器"""
    
    def screen_and_score(self, etf_data: List[Dict]) -> List[Dict]:
        """篩選並評分 ETF"""
        scored_etfs = []
        
        for etf in etf_data:
            try:
                # 計算基本面評分
                fundamental_score = self._calculate_fundamental_score(etf)
                
                # 計算技術面評分
                technical_score = self._calculate_technical_score(etf)
                
                # 綜合評分 (基本面 60%, 技術面 40%)
                final_score = fundamental_score * 0.6 + technical_score * 0.4
                
                # 決定評級
                if final_score >= 80:
                    rating = '綠燈'
                    recommendation = '建議進場'
                elif final_score >= 60:
                    rating = '黃燈'
                    recommendation = '可考慮'
                else:
                    rating = '紅燈'
                    recommendation = '暫時觀望'
                
                scored_etf = etf.copy()
                scored_etf.update({
                    'fundamental_score': round(fundamental_score, 1),
                    'technical_score': round(technical_score, 1),
                    'final_score': round(final_score, 1),
                    'rating': rating,
                    'recommendation': recommendation
                })
                
                scored_etfs.append(scored_etf)
                
            except Exception as e:
                logger.error(f"評分 ETF {etf.get('symbol', 'Unknown')} 時發生錯誤: {e}")
                continue
        
        # 按評分排序
        scored_etfs.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return scored_etfs
    
    def _calculate_fundamental_score(self, etf: Dict) -> float:
        """計算基本面評分"""
        score = 0
        
        # 殖利率評分 (40% 權重)
        dividend_yield = etf.get('dividend_yield', 0)
        if dividend_yield > 5:
            dividend_score = 100
        elif dividend_yield > 3:
            dividend_score = 80
        elif dividend_yield > 1:
            dividend_score = 60
        else:
            dividend_score = 40
        
        # 規模評分 (30% 權重)
        market_cap = etf.get('market_cap_billions', 0)
        if market_cap > 100:
            scale_score = 100
        elif market_cap > 50:
            scale_score = 80
        elif market_cap > 10:
            scale_score = 60
        else:
            scale_score = 40
        
        # 費用率評分 (30% 權重)
        expense_ratio = etf.get('expense_ratio', 1)
        if expense_ratio < 0.3:
            expense_score = 100
        elif expense_ratio < 0.5:
            expense_score = 80
        elif expense_ratio < 0.8:
            expense_score = 60
        else:
            expense_score = 40
        
        score = dividend_score * 0.4 + scale_score * 0.3 + expense_score * 0.3
        return score
    
    def _calculate_technical_score(self, etf: Dict) -> float:
        """計算技術面評分"""
        score = 0
        
        # RSI 評分 (40% 權重)
        rsi = etf.get('rsi', 50)
        if rsi < 30:
            rsi_score = 100  # 超賣，進場機會
        elif rsi < 50:
            rsi_score = 75   # 偏弱，可考慮
        elif rsi < 70:
            rsi_score = 50   # 正常區間
        else:
            rsi_score = 25   # 超買，避免
        
        # MACD 評分 (30% 權重)
        macd_line = etf.get('macd_line', 0)
        macd_signal = etf.get('macd_signal', 0)
        
        if macd_line > macd_signal and macd_line > 0:
            macd_score = 100  # 金叉且在零軸上，強勢
        elif macd_line > macd_signal:
            macd_score = 75   # 金叉，轉強
        elif macd_line < macd_signal and macd_line > 0:
            macd_score = 40   # 死叉但在零軸上，轉弱
        else:
            macd_score = 25   # 死叉且在零軸下，弱勢
        
        # 均線評分 (30% 權重)
        current_price = etf.get('current_price', 0)
        ma_20 = etf.get('ma_20', 0)
        ma_60 = etf.get('ma_60', 0)
        
        if current_price > ma_20 > ma_60:
            ma_score = 100  # 多頭排列
        elif current_price > ma_20:
            ma_score = 75   # 價格在短期均線上
        elif current_price > ma_60:
            ma_score = 50   # 價格在長期均線上
        else:
            ma_score = 25   # 價格在均線下
        
        score = rsi_score * 0.4 + macd_score * 0.3 + ma_score * 0.3
        return score

class PositionCalculator:
    """資金配置計算器"""
    
    def calculate(self, available_cash: float, market_strategy: Dict, etf_scores: List[Dict]) -> List[Dict]:
        """計算資金配置"""
        try:
            investment_ratio = market_strategy.get('investment_ratio', 0.5)
            total_investment = available_cash * investment_ratio
            
            # 篩選推薦的 ETF (評分 >= 60)
            recommended_etfs = [etf for etf in etf_scores if etf.get('final_score', 0) >= 60]
            
            if not recommended_etfs:
                return []
            
            # 限制最多 5 檔 ETF
            recommended_etfs = recommended_etfs[:5]
            
            # 根據評分分配權重
            total_score = sum(etf.get('final_score', 0) for etf in recommended_etfs)
            
            positions = []
            remaining_cash = total_investment
            
            for i, etf in enumerate(recommended_etfs):
                if i == len(recommended_etfs) - 1:
                    # 最後一檔使用剩餘資金
                    allocation = remaining_cash
                else:
                    # 根據評分比例分配
                    weight = etf.get('final_score', 0) / total_score
                    allocation = total_investment * weight
                
                current_price = etf.get('current_price', 0)
                if current_price > 0:
                    shares = int(allocation / current_price)
                    actual_amount = shares * current_price
                    
                    if shares > 0:
                        positions.append({
                            'symbol': etf.get('symbol'),
                            'name': etf.get('name'),
                            'shares': shares,
                            'price': current_price,
                            'amount': round(actual_amount, 0),
                            'weight': round((actual_amount / total_investment) * 100, 1),
                            'rating': etf.get('rating'),
                            'recommendation': etf.get('recommendation')
                        })
                        
                        remaining_cash -= actual_amount
            
            return positions
            
        except Exception as e:
            logger.error(f"計算資金配置錯誤: {e}")
            return []

class RiskMonitor:
    """風險監控器"""
    
    def check_risks(self, etf_scores: List[Dict]) -> List[Dict]:
        """檢查風險警示"""
        risk_alerts = []
        
        for etf in etf_scores:
            try:
                symbol = etf.get('symbol', '')
                rsi = etf.get('rsi', 50)
                macd_line = etf.get('macd_line', 0)
                macd_signal = etf.get('macd_signal', 0)
                
                # RSI 過熱警示
                if rsi > 80:
                    risk_alerts.append({
                        'symbol': symbol,
                        'type': '技術指標警示',
                        'level': '高風險',
                        'message': f'{symbol} RSI 達 {rsi:.1f}，嚴重超買，建議減碼',
                        'action': '建議減碼'
                    })
                elif rsi > 70:
                    risk_alerts.append({
                        'symbol': symbol,
                        'type': '技術指標警示',
                        'level': '中風險',
                        'message': f'{symbol} RSI 達 {rsi:.1f}，超買警示，注意風險',
                        'action': '注意觀察'
                    })
                
                # MACD 死叉警示
                if macd_line < macd_signal and etf.get('rating') == '綠燈':
                    risk_alerts.append({
                        'symbol': symbol,
                        'type': '趨勢轉折警示',
                        'level': '中風險',
                        'message': f'{symbol} MACD 出現死叉，趨勢可能轉弱',
                        'action': '謹慎觀察'
                    })
                
            except Exception as e:
                logger.error(f"檢查 {etf.get('symbol', 'Unknown')} 風險時發生錯誤: {e}")
                continue
        
        return risk_alerts

class AdviceGenerator:
    """建議生成器"""
    
    def generate(self, market_strategy: Dict, etf_scores: List[Dict], 
                risk_alerts: List[Dict], user_profile: Dict) -> Dict:
        """生成投資建議"""
        try:
            strategy = market_strategy.get('strategy', '平衡策略')
            description = market_strategy.get('description', '')
            
            # 統計 ETF 評級分布
            green_count = len([etf for etf in etf_scores if etf.get('rating') == '綠燈'])
            yellow_count = len([etf for etf in etf_scores if etf.get('rating') == '黃燈'])
            red_count = len([etf for etf in etf_scores if etf.get('rating') == '紅燈'])
            
            # 生成市場觀點
            market_outlook = self._generate_market_outlook(strategy, green_count, yellow_count, red_count)
            
            # 生成操作建議
            action_advice = self._generate_action_advice(strategy, risk_alerts)
            
            # 生成風險提醒
            risk_reminder = self._generate_risk_reminder(risk_alerts)
            
            return {
                'market_outlook': market_outlook,
                'action_advice': action_advice,
                'risk_reminder': risk_reminder,
                'strategy_description': description,
                'etf_distribution': {
                    'green_lights': green_count,
                    'yellow_lights': yellow_count,
                    'red_lights': red_count
                }
            }
            
        except Exception as e:
            logger.error(f"生成建議錯誤: {e}")
            return {
                'market_outlook': '市場分析暫時無法提供',
                'action_advice': '建議保持觀望',
                'risk_reminder': '請注意投資風險',
                'strategy_description': '建議採用平衡策略'
            }
    
    def _generate_market_outlook(self, strategy: str, green: int, yellow: int, red: int) -> str:
        """生成市場觀點"""
        if strategy == "積極策略":
            return f"市場處於相對低位，目前有 {green} 檔綠燈 ETF 值得關注，建議積極布局優質標的。"
        elif strategy == "保守策略":
            return f"市場風險偏高，僅有 {green} 檔綠燈 ETF，建議保守操作，等待更好進場時機。"
        else:
            return f"市場處於正常區間，有 {green} 檔綠燈、{yellow} 檔黃燈 ETF，建議平衡配置。"
    
    def _generate_action_advice(self, strategy: str, risk_alerts: List[Dict]) -> str:
        """生成操作建議"""
        if strategy == "積極策略":
            return "建議分批進場，優先選擇綠燈 ETF，單次投入不超過總資金的 20%。"
        elif strategy == "保守策略":
            return "建議暫時觀望，如需投資請選擇高股息、低波動的防禦型 ETF。"
        else:
            return "建議採用定期定額方式投入，分散時間風險，逐步建立部位。"
    
    def _generate_risk_reminder(self, risk_alerts: List[Dict]) -> str:
        """生成風險提醒"""
        if not risk_alerts:
            return "目前無特別風險警示，請持續關注市場變化。"
        
        high_risk_count = len([alert for alert in risk_alerts if alert.get('level') == '高風險'])
        
        if high_risk_count > 0:
            return f"注意：有 {high_risk_count} 檔 ETF 出現高風險警示，建議謹慎操作。"
        else:
            return f"有 {len(risk_alerts)} 項風險提醒，請注意相關標的的技術指標變化。"

