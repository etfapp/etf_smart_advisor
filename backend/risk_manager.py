import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class RiskManager:
    """風險管理器"""
    
    def __init__(self, data_fetcher):
        self.data_fetcher = data_fetcher
        
        # 風險閾值設定
        self.risk_thresholds = {
            'max_single_position': 0.35,      # 單一持倉最大比例
            'max_sector_exposure': 0.50,      # 單一類別最大曝險
            'max_portfolio_volatility': 0.25, # 投資組合最大波動率
            'max_drawdown_warning': 0.10,     # 回撤警告閾值
            'max_drawdown_critical': 0.15,    # 回撤嚴重閾值
            'min_diversification': 3,         # 最小分散化ETF數量
            'correlation_threshold': 0.7      # 相關性警告閾值
        }
        
        # 風險等級定義
        self.risk_levels = {
            'low': {'volatility': 0.15, 'max_drawdown': 0.08},
            'medium': {'volatility': 0.20, 'max_drawdown': 0.12},
            'high': {'volatility': 0.30, 'max_drawdown': 0.20}
        }
    
    def assess_portfolio_risk(self, portfolio: Dict) -> Dict:
        """評估投資組合風險"""
        try:
            if not portfolio or not portfolio.get('holdings'):
                return {
                    'overall_risk': 'low',
                    'risk_score': 0,
                    'warnings': [],
                    'recommendations': ['建議開始投資以建立投資組合']
                }
            
            holdings = portfolio['holdings']
            total_value = portfolio.get('total_value', 0)
            
            # 計算各項風險指標
            concentration_risk = self._assess_concentration_risk(holdings, total_value)
            volatility_risk = self._assess_volatility_risk(holdings)
            correlation_risk = self._assess_correlation_risk(holdings)
            sector_risk = self._assess_sector_risk(holdings, total_value)
            
            # 綜合風險評分
            risk_score = self._calculate_overall_risk_score(
                concentration_risk, volatility_risk, correlation_risk, sector_risk
            )
            
            # 生成警告和建議
            warnings = self._generate_risk_warnings(
                concentration_risk, volatility_risk, correlation_risk, sector_risk
            )
            
            recommendations = self._generate_risk_recommendations(
                concentration_risk, volatility_risk, correlation_risk, sector_risk
            )
            
            # 確定整體風險等級
            overall_risk = self._determine_overall_risk_level(risk_score)
            
            return {
                'overall_risk': overall_risk,
                'risk_score': risk_score,
                'concentration_risk': concentration_risk,
                'volatility_risk': volatility_risk,
                'correlation_risk': correlation_risk,
                'sector_risk': sector_risk,
                'warnings': warnings,
                'recommendations': recommendations,
                'assessment_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing portfolio risk: {e}")
            return {
                'overall_risk': 'unknown',
                'risk_score': 50,
                'warnings': ['風險評估暫時無法完成'],
                'recommendations': ['請稍後重試風險評估']
            }
    
    def _assess_concentration_risk(self, holdings: List[Dict], total_value: float) -> Dict:
        """評估集中度風險"""
        if not holdings or total_value <= 0:
            return {'score': 0, 'level': 'low', 'details': {}}
        
        # 計算各持倉比例
        positions = {}
        for holding in holdings:
            symbol = holding.get('symbol')
            value = holding.get('current_value', 0)
            if symbol and value > 0:
                positions[symbol] = value / total_value
        
        if not positions:
            return {'score': 0, 'level': 'low', 'details': {}}
        
        # 找出最大持倉比例
        max_position = max(positions.values())
        
        # 計算集中度風險分數
        if max_position > self.risk_thresholds['max_single_position']:
            score = min(100, (max_position - self.risk_thresholds['max_single_position']) * 200)
            level = 'high' if score > 70 else 'medium'
        else:
            score = max_position / self.risk_thresholds['max_single_position'] * 30
            level = 'low'
        
        return {
            'score': score,
            'level': level,
            'details': {
                'max_position': max_position,
                'positions': positions,
                'threshold': self.risk_thresholds['max_single_position']
            }
        }
    
    def _assess_volatility_risk(self, holdings: List[Dict]) -> Dict:
        """評估波動率風險"""
        if not holdings:
            return {'score': 0, 'level': 'low', 'details': {}}
        
        volatilities = []
        weights = []
        
        for holding in holdings:
            symbol = holding.get('symbol')
            weight = holding.get('weight', 0)
            
            if symbol and weight > 0:
                # 獲取ETF數據
                etf_data = self.data_fetcher.fetch_etf_data(symbol)
                if etf_data and etf_data.get('price_data'):
                    volatility = etf_data['price_data'].get('volatility', 0.2)
                    volatilities.append(volatility)
                    weights.append(weight)
        
        if not volatilities:
            return {'score': 50, 'level': 'medium', 'details': {}}
        
        # 計算加權平均波動率
        portfolio_volatility = np.average(volatilities, weights=weights)
        
        # 計算風險分數
        if portfolio_volatility > self.risk_thresholds['max_portfolio_volatility']:
            score = min(100, (portfolio_volatility - self.risk_thresholds['max_portfolio_volatility']) * 400)
            level = 'high'
        elif portfolio_volatility > 0.15:
            score = (portfolio_volatility - 0.15) / 0.10 * 50 + 30
            level = 'medium'
        else:
            score = portfolio_volatility / 0.15 * 30
            level = 'low'
        
        return {
            'score': score,
            'level': level,
            'details': {
                'portfolio_volatility': portfolio_volatility,
                'individual_volatilities': dict(zip([h.get('symbol') for h in holdings], volatilities)),
                'threshold': self.risk_thresholds['max_portfolio_volatility']
            }
        }
    
    def _assess_correlation_risk(self, holdings: List[Dict]) -> Dict:
        """評估相關性風險"""
        if len(holdings) < 2:
            return {'score': 0, 'level': 'low', 'details': {}}
        
        # 獲取所有ETF的歷史數據
        symbols = [h.get('symbol') for h in holdings if h.get('symbol')]
        
        if len(symbols) < 2:
            return {'score': 0, 'level': 'low', 'details': {}}
        
        # 簡化的相關性評估（基於ETF類別）
        categories = []
        for symbol in symbols:
            category = self.data_fetcher.get_etf_category(symbol)
            if category:
                categories.append(category)
        
        # 計算類別重複度
        unique_categories = len(set(categories))
        total_categories = len(categories)
        
        if total_categories == 0:
            return {'score': 50, 'level': 'medium', 'details': {}}
        
        diversity_ratio = unique_categories / total_categories
        
        # 計算相關性風險分數
        if diversity_ratio < 0.5:  # 類別重複度高
            score = (1 - diversity_ratio) * 100
            level = 'high'
        elif diversity_ratio < 0.8:
            score = (1 - diversity_ratio) * 60
            level = 'medium'
        else:
            score = (1 - diversity_ratio) * 30
            level = 'low'
        
        return {
            'score': score,
            'level': level,
            'details': {
                'diversity_ratio': diversity_ratio,
                'categories': categories,
                'unique_categories': unique_categories
            }
        }
    
    def _assess_sector_risk(self, holdings: List[Dict], total_value: float) -> Dict:
        """評估類別風險"""
        if not holdings or total_value <= 0:
            return {'score': 0, 'level': 'low', 'details': {}}
        
        # 計算各類別曝險
        sector_exposure = {}
        
        for holding in holdings:
            symbol = holding.get('symbol')
            value = holding.get('current_value', 0)
            
            if symbol and value > 0:
                category = self.data_fetcher.get_etf_category(symbol)
                if category:
                    if category not in sector_exposure:
                        sector_exposure[category] = 0
                    sector_exposure[category] += value / total_value
        
        if not sector_exposure:
            return {'score': 0, 'level': 'low', 'details': {}}
        
        # 找出最大類別曝險
        max_exposure = max(sector_exposure.values())
        
        # 計算類別風險分數
        if max_exposure > self.risk_thresholds['max_sector_exposure']:
            score = min(100, (max_exposure - self.risk_thresholds['max_sector_exposure']) * 200)
            level = 'high'
        elif max_exposure > 0.3:
            score = (max_exposure - 0.3) / 0.2 * 50 + 20
            level = 'medium'
        else:
            score = max_exposure / 0.3 * 20
            level = 'low'
        
        return {
            'score': score,
            'level': level,
            'details': {
                'max_exposure': max_exposure,
                'sector_exposure': sector_exposure,
                'threshold': self.risk_thresholds['max_sector_exposure']
            }
        }
    
    def _calculate_overall_risk_score(self, concentration_risk: Dict, 
                                    volatility_risk: Dict, correlation_risk: Dict, 
                                    sector_risk: Dict) -> float:
        """計算整體風險分數"""
        # 各風險因子權重
        weights = {
            'concentration': 0.3,
            'volatility': 0.3,
            'correlation': 0.2,
            'sector': 0.2
        }
        
        overall_score = (
            concentration_risk['score'] * weights['concentration'] +
            volatility_risk['score'] * weights['volatility'] +
            correlation_risk['score'] * weights['correlation'] +
            sector_risk['score'] * weights['sector']
        )
        
        return min(100, max(0, overall_score))
    
    def _determine_overall_risk_level(self, risk_score: float) -> str:
        """確定整體風險等級"""
        if risk_score < 30:
            return 'low'
        elif risk_score < 60:
            return 'medium'
        else:
            return 'high'
    
    def _generate_risk_warnings(self, concentration_risk: Dict, volatility_risk: Dict,
                              correlation_risk: Dict, sector_risk: Dict) -> List[str]:
        """生成風險警告"""
        warnings = []
        
        # 集中度風險警告
        if concentration_risk['level'] == 'high':
            max_pos = concentration_risk['details'].get('max_position', 0)
            warnings.append(f"單一持倉比例過高 ({max_pos:.1%})，建議分散投資")
        
        # 波動率風險警告
        if volatility_risk['level'] == 'high':
            vol = volatility_risk['details'].get('portfolio_volatility', 0)
            warnings.append(f"投資組合波動率偏高 ({vol:.1%})，注意風險控制")
        
        # 相關性風險警告
        if correlation_risk['level'] == 'high':
            warnings.append("投資組合分散化不足，建議增加不同類別的ETF")
        
        # 類別風險警告
        if sector_risk['level'] == 'high':
            max_exp = sector_risk['details'].get('max_exposure', 0)
            warnings.append(f"單一類別曝險過高 ({max_exp:.1%})，建議平衡配置")
        
        return warnings
    
    def _generate_risk_recommendations(self, concentration_risk: Dict, volatility_risk: Dict,
                                     correlation_risk: Dict, sector_risk: Dict) -> List[str]:
        """生成風險建議"""
        recommendations = []
        
        # 基於集中度風險的建議
        if concentration_risk['level'] in ['medium', 'high']:
            recommendations.append("考慮減少大額持倉，增加小額多元化投資")
        
        # 基於波動率風險的建議
        if volatility_risk['level'] == 'high':
            recommendations.append("考慮增加低波動率ETF（如債券ETF）來降低整體風險")
        elif volatility_risk['level'] == 'low':
            recommendations.append("可適度增加成長型ETF來提升報酬潛力")
        
        # 基於相關性風險的建議
        if correlation_risk['level'] in ['medium', 'high']:
            recommendations.append("建議增加不同類別的ETF以提高分散化效果")
        
        # 基於類別風險的建議
        if sector_risk['level'] == 'high':
            sector_details = sector_risk['details'].get('sector_exposure', {})
            max_sector = max(sector_details.keys(), key=lambda k: sector_details[k])
            recommendations.append(f"考慮減少{max_sector}類別的配置，增加其他類別")
        
        # 通用建議
        if not recommendations:
            recommendations.append("目前風險控制良好，建議定期檢視投資組合")
        
        return recommendations
    
    def check_position_limits(self, new_position: Dict, current_portfolio: Dict) -> Dict:
        """檢查新倉位是否超過限制"""
        try:
            symbol = new_position.get('symbol')
            amount = new_position.get('amount', 0)
            
            current_holdings = current_portfolio.get('holdings', [])
            current_total = current_portfolio.get('total_value', 0)
            
            # 計算新的總價值
            new_total = current_total + amount
            
            # 檢查單一持倉限制
            current_position = 0
            for holding in current_holdings:
                if holding.get('symbol') == symbol:
                    current_position = holding.get('current_value', 0)
                    break
            
            new_position_value = current_position + amount
            new_position_ratio = new_position_value / new_total if new_total > 0 else 0
            
            checks = {
                'position_limit_ok': new_position_ratio <= self.risk_thresholds['max_single_position'],
                'position_ratio': new_position_ratio,
                'position_limit': self.risk_thresholds['max_single_position']
            }
            
            # 檢查類別限制
            category = self.data_fetcher.get_etf_category(symbol)
            if category:
                category_total = amount
                for holding in current_holdings:
                    holding_category = self.data_fetcher.get_etf_category(holding.get('symbol', ''))
                    if holding_category == category:
                        category_total += holding.get('current_value', 0)
                
                category_ratio = category_total / new_total if new_total > 0 else 0
                checks.update({
                    'sector_limit_ok': category_ratio <= self.risk_thresholds['max_sector_exposure'],
                    'sector_ratio': category_ratio,
                    'sector_limit': self.risk_thresholds['max_sector_exposure']
                })
            
            return checks
            
        except Exception as e:
            logger.error(f"Error checking position limits: {e}")
            return {
                'position_limit_ok': False,
                'sector_limit_ok': False,
                'error': str(e)
            }
    
    def suggest_rebalancing(self, portfolio: Dict) -> Dict:
        """建議再平衡"""
        try:
            if not portfolio or not portfolio.get('holdings'):
                return {'rebalancing_needed': False, 'suggestions': []}
            
            risk_assessment = self.assess_portfolio_risk(portfolio)
            
            suggestions = []
            rebalancing_needed = False
            
            # 基於風險評估提供再平衡建議
            if risk_assessment['overall_risk'] == 'high':
                rebalancing_needed = True
                
                # 集中度過高的處理
                concentration_risk = risk_assessment.get('concentration_risk', {})
                if concentration_risk.get('level') == 'high':
                    positions = concentration_risk.get('details', {}).get('positions', {})
                    max_symbol = max(positions.keys(), key=lambda k: positions[k])
                    suggestions.append({
                        'action': 'reduce',
                        'symbol': max_symbol,
                        'reason': '單一持倉比例過高',
                        'target_ratio': self.risk_thresholds['max_single_position']
                    })
                
                # 類別曝險過高的處理
                sector_risk = risk_assessment.get('sector_risk', {})
                if sector_risk.get('level') == 'high':
                    sector_exposure = sector_risk.get('details', {}).get('sector_exposure', {})
                    max_sector = max(sector_exposure.keys(), key=lambda k: sector_exposure[k])
                    suggestions.append({
                        'action': 'diversify',
                        'sector': max_sector,
                        'reason': '單一類別曝險過高',
                        'target_ratio': self.risk_thresholds['max_sector_exposure']
                    })
            
            return {
                'rebalancing_needed': rebalancing_needed,
                'suggestions': suggestions,
                'risk_level': risk_assessment['overall_risk']
            }
            
        except Exception as e:
            logger.error(f"Error suggesting rebalancing: {e}")
            return {
                'rebalancing_needed': False,
                'suggestions': [],
                'error': str(e)
            }

