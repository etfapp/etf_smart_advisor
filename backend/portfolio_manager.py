import json
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class PortfolioManager:
    """投資組合管理器"""
    
    def __init__(self, data_file: str = "portfolios.json"):
        self.data_file = data_file
        self.portfolios = self._load_portfolios()
    
    def _load_portfolios(self) -> Dict:
        """載入投資組合數據"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f"Error loading portfolios: {e}")
            return {}
    
    def _save_portfolios(self):
        """保存投資組合數據"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.portfolios, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving portfolios: {e}")
    
    def get_user_portfolio(self, user_id: str) -> Dict:
        """獲取用戶投資組合"""
        try:
            if user_id not in self.portfolios:
                # 創建新的投資組合
                self.portfolios[user_id] = {
                    'user_id': user_id,
                    'created_at': datetime.now().isoformat(),
                    'total_value': 0,
                    'total_cost': 0,
                    'cash_balance': 0,
                    'holdings': [],
                    'transactions': [],
                    'last_updated': datetime.now().isoformat()
                }
                self._save_portfolios()
            
            portfolio = self.portfolios[user_id].copy()
            
            # 更新持倉的當前價值
            self._update_portfolio_values(portfolio)
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting portfolio for {user_id}: {e}")
            return {
                'user_id': user_id,
                'total_value': 0,
                'total_cost': 0,
                'cash_balance': 0,
                'holdings': [],
                'transactions': [],
                'error': str(e)
            }
    
    def execute_investment(self, recommendations: List[Dict], total_funds: float) -> Dict:
        """執行投資（模擬）"""
        try:
            # 這是模擬執行，實際應用中需要連接券商API
            execution_results = []
            total_invested = 0
            
            for rec in recommendations:
                symbol = rec.get('etf')
                shares = rec.get('shares', 0)
                target_amount = rec.get('target_amount', 0)
                current_price = rec.get('current_price', 0)
                
                if shares > 0 and current_price > 0:
                    # 模擬執行成功
                    actual_amount = shares * current_price
                    execution_results.append({
                        'symbol': symbol,
                        'shares': shares,
                        'price': current_price,
                        'amount': actual_amount,
                        'status': 'executed',
                        'execution_time': datetime.now().isoformat()
                    })
                    total_invested += actual_amount
                else:
                    execution_results.append({
                        'symbol': symbol,
                        'status': 'failed',
                        'reason': '無效的股數或價格'
                    })
            
            return {
                'success': True,
                'total_invested': total_invested,
                'remaining_cash': total_funds - total_invested,
                'executions': execution_results,
                'execution_time': datetime.now().isoformat(),
                'note': '這是模擬執行結果，實際投資需要連接券商系統'
            }
            
        except Exception as e:
            logger.error(f"Error executing investment: {e}")
            return {
                'success': False,
                'error': str(e),
                'executions': []
            }
    
    def add_transaction(self, user_id: str, transaction: Dict) -> bool:
        """添加交易記錄"""
        try:
            portfolio = self.get_user_portfolio(user_id)
            
            # 添加交易記錄
            transaction['transaction_id'] = f"TXN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            transaction['timestamp'] = datetime.now().isoformat()
            
            portfolio['transactions'].append(transaction)
            
            # 更新持倉
            self._update_holdings(portfolio, transaction)
            
            # 更新現金餘額
            if transaction['type'] == 'buy':
                portfolio['cash_balance'] -= transaction['amount']
                portfolio['total_cost'] += transaction['amount']
            elif transaction['type'] == 'sell':
                portfolio['cash_balance'] += transaction['amount']
            
            # 更新投資組合
            portfolio['last_updated'] = datetime.now().isoformat()
            self.portfolios[user_id] = portfolio
            self._save_portfolios()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding transaction for {user_id}: {e}")
            return False
    
    def _update_holdings(self, portfolio: Dict, transaction: Dict):
        """更新持倉"""
        symbol = transaction['symbol']
        shares = transaction['shares']
        price = transaction['price']
        transaction_type = transaction['type']
        
        # 查找現有持倉
        holding_index = -1
        for i, holding in enumerate(portfolio['holdings']):
            if holding['symbol'] == symbol:
                holding_index = i
                break
        
        if transaction_type == 'buy':
            if holding_index >= 0:
                # 更新現有持倉
                holding = portfolio['holdings'][holding_index]
                old_shares = holding['shares']
                old_cost = holding['average_cost'] * old_shares
                
                new_shares = old_shares + shares
                new_cost = old_cost + (shares * price)
                new_average_cost = new_cost / new_shares if new_shares > 0 else 0
                
                holding['shares'] = new_shares
                holding['average_cost'] = new_average_cost
                holding['last_updated'] = datetime.now().isoformat()
            else:
                # 新增持倉
                new_holding = {
                    'symbol': symbol,
                    'shares': shares,
                    'average_cost': price,
                    'current_price': price,
                    'current_value': shares * price,
                    'unrealized_pnl': 0,
                    'weight': 0,  # 將在更新時計算
                    'first_purchase': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
                portfolio['holdings'].append(new_holding)
        
        elif transaction_type == 'sell':
            if holding_index >= 0:
                holding = portfolio['holdings'][holding_index]
                holding['shares'] -= shares
                
                if holding['shares'] <= 0:
                    # 完全賣出，移除持倉
                    portfolio['holdings'].pop(holding_index)
                else:
                    holding['last_updated'] = datetime.now().isoformat()
    
    def _update_portfolio_values(self, portfolio: Dict):
        """更新投資組合價值"""
        try:
            from data_fetcher import ImprovedDataFetcher
            data_fetcher = ImprovedDataFetcher()
            
            total_value = portfolio.get('cash_balance', 0)
            
            for holding in portfolio['holdings']:
                symbol = holding['symbol']
                shares = holding['shares']
                
                # 獲取當前價格
                etf_data = data_fetcher.fetch_etf_data(symbol)
                if etf_data:
                    current_price = etf_data['current_price']
                    holding['current_price'] = current_price
                    holding['current_value'] = shares * current_price
                    
                    # 計算未實現損益
                    cost_basis = shares * holding['average_cost']
                    holding['unrealized_pnl'] = holding['current_value'] - cost_basis
                    holding['unrealized_pnl_pct'] = (holding['unrealized_pnl'] / cost_basis * 100) if cost_basis > 0 else 0
                    
                    total_value += holding['current_value']
                else:
                    # 無法獲取價格時使用平均成本
                    holding['current_value'] = shares * holding['average_cost']
                    holding['unrealized_pnl'] = 0
                    holding['unrealized_pnl_pct'] = 0
                    total_value += holding['current_value']
            
            # 更新權重
            for holding in portfolio['holdings']:
                holding['weight'] = (holding['current_value'] / total_value * 100) if total_value > 0 else 0
            
            # 更新總價值
            portfolio['total_value'] = total_value
            portfolio['total_unrealized_pnl'] = sum(h.get('unrealized_pnl', 0) for h in portfolio['holdings'])
            portfolio['total_return_pct'] = ((total_value / portfolio['total_cost'] - 1) * 100) if portfolio['total_cost'] > 0 else 0
            
        except Exception as e:
            logger.error(f"Error updating portfolio values: {e}")
    
    def get_portfolio_performance(self, user_id: str, period: str = '1m') -> Dict:
        """獲取投資組合績效"""
        try:
            portfolio = self.get_user_portfolio(user_id)
            
            # 計算基本績效指標
            total_value = portfolio.get('total_value', 0)
            total_cost = portfolio.get('total_cost', 0)
            total_return = total_value - total_cost
            total_return_pct = (total_return / total_cost * 100) if total_cost > 0 else 0
            
            # 計算持倉分布
            holdings_summary = []
            for holding in portfolio.get('holdings', []):
                holdings_summary.append({
                    'symbol': holding['symbol'],
                    'weight': holding.get('weight', 0),
                    'return_pct': holding.get('unrealized_pnl_pct', 0),
                    'value': holding.get('current_value', 0)
                })
            
            # 計算風險指標（簡化版）
            if len(holdings_summary) > 0:
                returns = [h['return_pct'] for h in holdings_summary]
                avg_return = sum(returns) / len(returns)
                volatility = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            else:
                avg_return = 0
                volatility = 0
            
            return {
                'total_value': total_value,
                'total_cost': total_cost,
                'total_return': total_return,
                'total_return_pct': total_return_pct,
                'holdings_count': len(portfolio.get('holdings', [])),
                'cash_balance': portfolio.get('cash_balance', 0),
                'avg_return': avg_return,
                'volatility': volatility,
                'holdings_summary': holdings_summary,
                'last_updated': portfolio.get('last_updated')
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio performance for {user_id}: {e}")
            return {
                'total_value': 0,
                'total_return_pct': 0,
                'error': str(e)
            }
    
    def get_transaction_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """獲取交易歷史"""
        try:
            portfolio = self.get_user_portfolio(user_id)
            transactions = portfolio.get('transactions', [])
            
            # 按時間倒序排列
            sorted_transactions = sorted(
                transactions, 
                key=lambda x: x.get('timestamp', ''), 
                reverse=True
            )
            
            return sorted_transactions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting transaction history for {user_id}: {e}")
            return []
    
    def calculate_asset_allocation(self, user_id: str) -> Dict:
        """計算資產配置"""
        try:
            portfolio = self.get_user_portfolio(user_id)
            holdings = portfolio.get('holdings', [])
            
            if not holdings:
                return {
                    'by_category': {},
                    'by_asset_type': {'stock': 0, 'bond': 0, 'reit': 0, 'cash': 100},
                    'diversification_score': 0
                }
            
            from data_fetcher import ImprovedDataFetcher
            data_fetcher = ImprovedDataFetcher()
            
            # 按類別分組
            category_allocation = {}
            asset_type_allocation = {'stock': 0, 'bond': 0, 'reit': 0, 'cash': 0}
            
            total_investment_value = sum(h.get('current_value', 0) for h in holdings)
            cash_balance = portfolio.get('cash_balance', 0)
            total_value = total_investment_value + cash_balance
            
            for holding in holdings:
                symbol = holding['symbol']
                weight = holding.get('weight', 0)
                category = data_fetcher.get_etf_category(symbol)
                
                if category:
                    if category not in category_allocation:
                        category_allocation[category] = 0
                    category_allocation[category] += weight
                    
                    # 映射到資產類型
                    if category in ['large_cap', 'tech', 'mid_small', 'dividend']:
                        asset_type_allocation['stock'] += weight
                    elif category == 'bond':
                        asset_type_allocation['bond'] += weight
                    elif category == 'reit':
                        asset_type_allocation['reit'] += weight
            
            # 現金比例
            if total_value > 0:
                cash_weight = cash_balance / total_value * 100
                asset_type_allocation['cash'] = cash_weight
            
            # 計算分散化分數
            diversification_score = len(category_allocation) * 20  # 每個類別20分，最高100分
            diversification_score = min(100, diversification_score)
            
            return {
                'by_category': category_allocation,
                'by_asset_type': asset_type_allocation,
                'diversification_score': diversification_score,
                'total_value': total_value,
                'investment_value': total_investment_value,
                'cash_balance': cash_balance
            }
            
        except Exception as e:
            logger.error(f"Error calculating asset allocation for {user_id}: {e}")
            return {
                'by_category': {},
                'by_asset_type': {},
                'diversification_score': 0,
                'error': str(e)
            }
    
    def suggest_portfolio_optimization(self, user_id: str) -> Dict:
        """建議投資組合優化"""
        try:
            portfolio = self.get_user_portfolio(user_id)
            allocation = self.calculate_asset_allocation(user_id)
            
            suggestions = []
            
            # 檢查分散化
            diversification_score = allocation.get('diversification_score', 0)
            if diversification_score < 60:
                suggestions.append({
                    'type': 'diversification',
                    'priority': 'high',
                    'message': '建議增加不同類別的ETF以提高分散化',
                    'action': '考慮投資債券ETF或REITs'
                })
            
            # 檢查現金比例
            cash_ratio = allocation.get('by_asset_type', {}).get('cash', 0)
            if cash_ratio > 20:
                suggestions.append({
                    'type': 'cash_management',
                    'priority': 'medium',
                    'message': f'現金比例較高 ({cash_ratio:.1f}%)',
                    'action': '考慮增加投資以提高資金使用效率'
                })
            elif cash_ratio < 5:
                suggestions.append({
                    'type': 'cash_management',
                    'priority': 'low',
                    'message': '現金比例較低，建議保留一定現金作為緊急準備',
                    'action': '考慮保留5-10%的現金比例'
                })
            
            # 檢查單一持倉比例
            holdings = portfolio.get('holdings', [])
            for holding in holdings:
                weight = holding.get('weight', 0)
                if weight > 35:
                    suggestions.append({
                        'type': 'concentration',
                        'priority': 'high',
                        'message': f'{holding["symbol"]} 持倉比例過高 ({weight:.1f}%)',
                        'action': '建議減少單一持倉比例或增加其他投資'
                    })
            
            return {
                'suggestions': suggestions,
                'optimization_score': self._calculate_optimization_score(allocation, holdings),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error suggesting portfolio optimization for {user_id}: {e}")
            return {
                'suggestions': [],
                'optimization_score': 0,
                'error': str(e)
            }
    
    def _calculate_optimization_score(self, allocation: Dict, holdings: List[Dict]) -> int:
        """計算優化分數"""
        score = 0
        
        # 分散化分數 (40%)
        diversification_score = allocation.get('diversification_score', 0)
        score += diversification_score * 0.4
        
        # 現金管理分數 (20%)
        cash_ratio = allocation.get('by_asset_type', {}).get('cash', 0)
        if 5 <= cash_ratio <= 15:
            cash_score = 100
        elif cash_ratio < 5:
            cash_score = cash_ratio / 5 * 100
        else:
            cash_score = max(0, 100 - (cash_ratio - 15) * 5)
        score += cash_score * 0.2
        
        # 持倉集中度分數 (40%)
        concentration_score = 100
        for holding in holdings:
            weight = holding.get('weight', 0)
            if weight > 35:
                concentration_score -= (weight - 35) * 2
        
        concentration_score = max(0, concentration_score)
        score += concentration_score * 0.4
        
        return min(100, max(0, int(score)))
    
    def export_portfolio_data(self, user_id: str) -> Dict:
        """導出投資組合數據"""
        try:
            portfolio = self.get_user_portfolio(user_id)
            performance = self.get_portfolio_performance(user_id)
            allocation = self.calculate_asset_allocation(user_id)
            transactions = self.get_transaction_history(user_id)
            
            return {
                'portfolio': portfolio,
                'performance': performance,
                'allocation': allocation,
                'transactions': transactions,
                'export_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error exporting portfolio data for {user_id}: {e}")
            return {
                'error': str(e),
                'export_time': datetime.now().isoformat()
            }

