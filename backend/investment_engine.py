import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ImprovedInvestmentEngine:
    """升級後的投資引擎"""
    
    def __init__(self, data_fetcher):
        self.data_fetcher = data_fetcher
        
        # 調整後的因子權重 - 提高基本面比重
        self.factor_weights = {
            'fundamental': 0.50,  # 從0.30提升到0.50
            'technical': 0.30,    # 從0.40降到0.30
            'market': 0.20        # 保持0.20
        }
        
        # 放寬評分標準 - 確保有實用的投資建議
        self.score_thresholds = {
            'strong_buy': 70,     # 從80降到70
            'buy': 55,           # 從65降到55
            'hold': 40,          # 從50降到40
            'sell': 25           # 從35降到25
        }
        
        # ETF分類 - 清理後的清單
        self.etf_categories = {
            'large_cap': ['0050', '006208'],
            'dividend': ['0056', '00878', '00713'],
            'tech': ['0052', '00881'],
            'mid_small': ['0051', '00762'],
            'bond': ['00679B', '00687B'],
            'reit': ['00712', '01001']
        }
    
    def generate_investment_advice(self, user_profile: Dict) -> Dict:
        """生成投資建議"""
        try:
            logger.info(f"Generating investment advice for profile: {user_profile}")
            
            # 獲取市場環境
            market_condition = self._assess_market_condition()
            
            # 獲取所有ETF評分
            etf_scores = self._get_all_etf_scores()
            
            # 篩選推薦ETF
            recommended_etfs = self._select_recommended_etfs(etf_scores)
            
            # 計算資金配置
            allocation = self._calculate_allocation(
                recommended_etfs, 
                user_profile['available_funds'],
                user_profile.get('risk_level', 'moderate')
            )
            
            # 生成詳細建議
            recommendations = self._generate_detailed_recommendations(
                allocation, etf_scores
            )
            
            return {
                'success': True,
                'market_condition': market_condition,
                'recommendations': recommendations,
                'total_expected_return': self._calculate_portfolio_expected_return(recommendations),
                'risk_level': self._assess_portfolio_risk_level(recommendations),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating investment advice: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': []
            }
    
    def _assess_market_condition(self) -> str:
        """評估市場環境"""
        try:
            market_data = self.data_fetcher.get_market_overview()
            
            if not market_data:
                return 'neutral'
            
            change_pct = market_data.get('change_percent', 0)
            
            if change_pct > 1:
                return 'bullish'
            elif change_pct < -1:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error assessing market condition: {e}")
            return 'neutral'
    
    def _get_all_etf_scores(self) -> Dict:
        """獲取所有ETF評分"""
        etf_scores = {}
        
        # 獲取所有ETF代碼
        all_etfs = []
        for category_etfs in self.etf_categories.values():
            all_etfs.extend(category_etfs)
        
        for symbol in all_etfs:
            try:
                etf_data = self.data_fetcher.fetch_etf_data(symbol)
                if etf_data:
                    score = self._calculate_etf_score(etf_data)
                    etf_scores[symbol] = score
                    
            except Exception as e:
                logger.error(f"Error scoring ETF {symbol}: {e}")
                continue
        
        return etf_scores
    
    def _calculate_etf_score(self, etf_data: Dict) -> Dict:
        """計算ETF評分"""
        try:
            # 基本面評分
            fundamental_score = self._calculate_fundamental_score(etf_data)
            
            # 技術面評分
            technical_score = self._calculate_technical_score(etf_data)
            
            # 市場環境評分
            market_score = self._calculate_market_score()
            
            # 綜合評分
            total_score = (
                fundamental_score * self.factor_weights['fundamental'] +
                technical_score * self.factor_weights['technical'] +
                market_score * self.factor_weights['market']
            )
            
            return {
                'total_score': total_score,
                'fundamental_score': fundamental_score,
                'technical_score': technical_score,
                'market_score': market_score,
                'recommendation': self._get_recommendation(total_score)
            }
            
        except Exception as e:
            logger.error(f"Error calculating ETF score: {e}")
            return {
                'total_score': 50,
                'fundamental_score': 50,
                'technical_score': 50,
                'market_score': 50,
                'recommendation': 'hold'
            }
    
    def _calculate_fundamental_score(self, etf_data: Dict) -> float:
        """計算基本面評分"""
        score = 0
        
        try:
            # 估值指標（權重40%）
            pe_ratio = etf_data.get('pe_ratio')
            if pe_ratio and pe_ratio > 0:
                # PE評分：15以下滿分，25以上0分
                pe_score = max(0, min(100, (25 - pe_ratio) / 10 * 100))
                score += pe_score * 0.4
            else:
                score += 50 * 0.4  # 無數據時給中性評分
            
            # 股息率（權重30%）
            dividend_yield = etf_data.get('dividend_yield', 0)
            if dividend_yield:
                dividend_yield_pct = dividend_yield * 100
                # 股息率評分：4%以上滿分
                div_score = min(dividend_yield_pct / 4 * 100, 100)
                score += div_score * 0.3
            else:
                score += 30 * 0.3  # 無股息時給較低評分
            
            # 規模和流動性（權重30%）
            aum = etf_data.get('aum', 0)
            if aum:
                # AUM評分：100億以上滿分
                aum_score = min(aum / 10000000000 * 100, 100)
                score += aum_score * 0.3
            else:
                score += 50 * 0.3  # 無數據時給中性評分
            
        except Exception as e:
            logger.error(f"Error in fundamental score calculation: {e}")
            score = 50  # 錯誤時返回中性評分
        
        return score
    
    def _calculate_technical_score(self, etf_data: Dict) -> float:
        """計算技術面評分"""
        try:
            price_data = etf_data.get('price_data', {})
            if not price_data:
                return 50  # 無數據時返回中性評分
            
            score = 0
            current_price = price_data.get('current_price', 0)
            
            # 趨勢評分（權重50%）
            ma20 = price_data.get('ma20')
            ma60 = price_data.get('ma60')
            
            trend_score = 0
            if ma20 and ma60 and current_price:
                if current_price > ma20:
                    trend_score += 50
                if current_price > ma60:
                    trend_score += 30
                if ma20 > ma60:
                    trend_score += 20
            else:
                trend_score = 50  # 無數據時給中性評分
            
            score += trend_score * 0.5
            
            # 動量評分（權重30%）
            rsi = price_data.get('rsi')
            if rsi:
                if rsi < 30:
                    momentum_score = 90  # 超賣，好買點
                elif rsi > 70:
                    momentum_score = 10  # 超買，不建議買入
                else:
                    momentum_score = 50  # 正常範圍
            else:
                momentum_score = 50
            
            score += momentum_score * 0.3
            
            # 波動率評分（權重20%）
            volatility = price_data.get('volatility', 0.2)
            # 波動率15-25%為最佳範圍
            if 0.15 <= volatility <= 0.25:
                vol_score = 100
            elif volatility < 0.15:
                vol_score = 70  # 波動太小，報酬可能有限
            else:
                vol_score = max(0, 100 - (volatility - 0.25) * 200)
            
            score += vol_score * 0.2
            
            return score
            
        except Exception as e:
            logger.error(f"Error in technical score calculation: {e}")
            return 50
    
    def _calculate_market_score(self) -> float:
        """計算市場環境評分"""
        try:
            market_data = self.data_fetcher.get_market_overview()
            
            if not market_data:
                return 50
            
            change_pct = market_data.get('change_percent', 0)
            
            # 市場趨勢評分
            if change_pct > 2:
                return 80  # 強勢上漲
            elif change_pct > 0:
                return 65  # 溫和上漲
            elif change_pct > -2:
                return 50  # 橫盤整理
            else:
                return 30  # 下跌趨勢
                
        except Exception as e:
            logger.error(f"Error in market score calculation: {e}")
            return 50
    
    def _get_recommendation(self, score: float) -> str:
        """根據評分獲取推薦等級"""
        if score >= self.score_thresholds['strong_buy']:
            return 'strong_buy'
        elif score >= self.score_thresholds['buy']:
            return 'buy'
        elif score >= self.score_thresholds['hold']:
            return 'hold'
        else:
            return 'sell'
    
    def _select_recommended_etfs(self, etf_scores: Dict) -> List[str]:
        """選擇推薦ETF"""
        # 篩選買入級別的ETF
        buy_etfs = [
            etf for etf, score in etf_scores.items() 
            if score['total_score'] >= self.score_thresholds['buy']
        ]
        
        if not buy_etfs:
            # 如果沒有達到買入標準的ETF，選擇評分最高的3個
            sorted_etfs = sorted(
                etf_scores.items(), 
                key=lambda x: x[1]['total_score'], 
                reverse=True
            )
            buy_etfs = [etf for etf, _ in sorted_etfs[:3]]
        
        return buy_etfs
    
    def _calculate_allocation(self, recommended_etfs: List[str], 
                           available_funds: float, risk_level: str) -> Dict:
        """計算資金配置"""
        allocation = {}
        
        if not recommended_etfs:
            return allocation
        
        # 根據風險等級調整配置
        if risk_level == 'conservative':
            stock_ratio = 0.6
            max_single_etf = 0.3
        elif risk_level == 'aggressive':
            stock_ratio = 0.9
            max_single_etf = 0.4
        else:  # moderate
            stock_ratio = 0.75
            max_single_etf = 0.35
        
        # 計算每個ETF的配置
        stock_funds = available_funds * stock_ratio
        etf_count = len(recommended_etfs)
        
        # 平均分配，但不超過單一ETF上限
        base_allocation = min(stock_funds / etf_count, available_funds * max_single_etf)
        
        for etf in recommended_etfs:
            allocation[etf] = base_allocation
        
        return allocation
    
    def _generate_detailed_recommendations(self, allocation: Dict, 
                                         etf_scores: Dict) -> List[Dict]:
        """生成詳細投資建議"""
        recommendations = []
        
        for etf, amount in allocation.items():
            try:
                etf_data = self.data_fetcher.fetch_etf_data(etf)
                if not etf_data:
                    continue
                
                current_price = etf_data.get('current_price', 0)
                if current_price <= 0:
                    continue
                
                # 計算股數（台股以千股為單位）
                shares = int(amount / current_price / 1000) * 1000
                actual_amount = shares * current_price
                
                if shares > 0:
                    recommendation = {
                        'etf': etf,
                        'etf_name': etf_data.get('name', etf),
                        'target_amount': actual_amount,
                        'shares': shares,
                        'current_price': current_price,
                        'expected_return': self._estimate_expected_return(etf, etf_scores.get(etf, {})),
                        'risk_level': self._assess_etf_risk_level(etf),
                        'reason': self._get_investment_reason(etf, etf_scores.get(etf, {})),
                        'score': etf_scores.get(etf, {}).get('total_score', 0)
                    }
                    recommendations.append(recommendation)
                    
            except Exception as e:
                logger.error(f"Error generating recommendation for {etf}: {e}")
                continue
        
        return recommendations
    
    def _estimate_expected_return(self, etf: str, score_data: Dict) -> float:
        """估算預期報酬率"""
        # 基於評分估算預期報酬
        total_score = score_data.get('total_score', 50)
        
        # 基礎報酬率 + 評分調整
        base_return = 0.06  # 6%基礎報酬
        score_adjustment = (total_score - 50) / 50 * 0.04  # 評分每高10分增加0.8%報酬
        
        expected_return = base_return + score_adjustment
        
        # 限制在合理範圍內
        return max(0.02, min(0.15, expected_return))
    
    def _assess_etf_risk_level(self, etf: str) -> str:
        """評估ETF風險等級"""
        risk_mapping = {
            '0050': '中', '006208': '中',      # 大盤ETF
            '0056': '低', '00878': '低',       # 高股息ETF
            '0051': '高', '00762': '高',       # 中小型ETF
            '0052': '高', '00881': '高',       # 科技ETF
            '00679B': '低', '00687B': '低',    # 債券ETF
            '00712': '中', '01001': '中'       # REITs ETF
        }
        
        return risk_mapping.get(etf, '中')
    
    def _get_investment_reason(self, etf: str, score_data: Dict) -> str:
        """獲取投資理由"""
        total_score = score_data.get('total_score', 50)
        fundamental_score = score_data.get('fundamental_score', 50)
        technical_score = score_data.get('technical_score', 50)
        
        reasons = []
        
        if fundamental_score > 70:
            reasons.append("基本面表現優異")
        if technical_score > 70:
            reasons.append("技術面呈現買入信號")
        if total_score > 80:
            reasons.append("綜合評分優秀")
        
        if not reasons:
            reasons.append("相對表現較佳")
        
        # ETF特性描述
        etf_descriptions = {
            '0050': '追蹤台灣50指數，市場代表性強',
            '006208': '追蹤台灣50指數，費用率較低',
            '0056': '高股息策略，提供穩定現金流',
            '00878': '國泰永續高股息，ESG概念',
            '0052': '科技類ETF，參與科技成長趨勢',
            '00881': '國泰台灣5G+，5G概念投資'
        }
        
        description = etf_descriptions.get(etf, '優質ETF標的')
        
        return f"{description}，{' '.join(reasons)}"
    
    def _calculate_portfolio_expected_return(self, recommendations: List[Dict]) -> float:
        """計算投資組合預期報酬"""
        if not recommendations:
            return 0
        
        total_amount = sum(rec['target_amount'] for rec in recommendations)
        if total_amount == 0:
            return 0
        
        weighted_return = sum(
            rec['target_amount'] * rec['expected_return'] 
            for rec in recommendations
        ) / total_amount
        
        return weighted_return
    
    def _assess_portfolio_risk_level(self, recommendations: List[Dict]) -> str:
        """評估投資組合風險等級"""
        if not recommendations:
            return '低'
        
        risk_scores = {'低': 1, '中': 2, '高': 3}
        total_amount = sum(rec['target_amount'] for rec in recommendations)
        
        if total_amount == 0:
            return '低'
        
        weighted_risk = sum(
            rec['target_amount'] * risk_scores.get(rec['risk_level'], 2)
            for rec in recommendations
        ) / total_amount
        
        if weighted_risk <= 1.5:
            return '低'
        elif weighted_risk <= 2.5:
            return '中'
        else:
            return '高'
    
    def run_backtest(self, start_date: str, end_date: str, 
                    initial_funds: float) -> Dict:
        """運行回測"""
        try:
            # 這裡實現簡單的回測邏輯
            # 實際實現中需要獲取歷史數據並模擬投資過程
            
            return {
                'success': True,
                'start_date': start_date,
                'end_date': end_date,
                'initial_funds': initial_funds,
                'final_value': initial_funds * 1.08,  # 模擬8%報酬
                'total_return': 0.08,
                'annual_return': 0.08,
                'max_drawdown': 0.12,
                'sharpe_ratio': 0.65,
                'message': '回測功能開發中，顯示模擬結果'
            }
            
        except Exception as e:
            logger.error(f"Error in backtest: {e}")
            return {
                'success': False,
                'error': str(e)
            }

