"""
簡化版數據獲取器 - 用於演示
"""

import random
from datetime import datetime
from typing import Dict, List, Optional

class DataFetcher:
    """簡化版數據獲取器"""
    
    def __init__(self):
        # 台股 ETF 示例數據
        self.etf_data = [
            {
                'symbol': '0050',
                'name': '元大台灣50',
                'current_price': 147.50,
                'change': 1.20,
                'change_percent': 0.82,
                'volume': 15420000,
                'dividend_yield': 3.85,
                'market_cap_billions': 2850.5,
                'expense_ratio': 0.32,
                'annual_return': 12.45,
                'rsi': 45.2,
                'macd_line': 0.15,
                'macd_signal': 0.12,
                'macd_histogram': 0.03,
                'ma_5': 146.8,
                'ma_20': 145.2,
                'ma_60': 142.1,
                'signal': '綠燈'
            },
            {
                'symbol': '0056',
                'name': '元大高股息',
                'current_price': 38.45,
                'change': -0.15,
                'change_percent': -0.39,
                'volume': 8520000,
                'dividend_yield': 6.25,
                'market_cap_billions': 1250.8,
                'expense_ratio': 0.74,
                'annual_return': 8.92,
                'rsi': 52.8,
                'macd_line': -0.08,
                'macd_signal': -0.05,
                'macd_histogram': -0.03,
                'ma_5': 38.6,
                'ma_20': 38.9,
                'ma_60': 39.2,
                'signal': '黃燈'
            },
            {
                'symbol': '00878',
                'name': '國泰永續高股息',
                'current_price': 22.85,
                'change': 0.05,
                'change_percent': 0.22,
                'volume': 12850000,
                'dividend_yield': 5.45,
                'market_cap_billions': 985.2,
                'expense_ratio': 0.85,
                'annual_return': 15.68,
                'rsi': 38.5,
                'macd_line': 0.22,
                'macd_signal': 0.18,
                'macd_histogram': 0.04,
                'ma_5': 22.7,
                'ma_20': 22.3,
                'ma_60': 21.8,
                'signal': '綠燈'
            },
            {
                'symbol': '00713',
                'name': '元大台灣高息低波',
                'current_price': 45.20,
                'change': -0.30,
                'change_percent': -0.66,
                'volume': 3250000,
                'dividend_yield': 4.85,
                'market_cap_billions': 425.6,
                'expense_ratio': 0.68,
                'annual_return': 6.32,
                'rsi': 65.2,
                'macd_line': -0.12,
                'macd_signal': -0.08,
                'macd_histogram': -0.04,
                'ma_5': 45.5,
                'ma_20': 46.1,
                'ma_60': 46.8,
                'signal': '黃燈'
            },
            {
                'symbol': '00881',
                'name': '國泰台灣5G+',
                'current_price': 18.65,
                'change': 0.45,
                'change_percent': 2.47,
                'volume': 5680000,
                'dividend_yield': 2.15,
                'market_cap_billions': 185.4,
                'expense_ratio': 1.05,
                'annual_return': -8.45,
                'rsi': 72.8,
                'macd_line': 0.35,
                'macd_signal': 0.28,
                'macd_histogram': 0.07,
                'ma_5': 18.2,
                'ma_20': 17.8,
                'ma_60': 19.2,
                'signal': '紅燈'
            }
        ]
    
    def get_all_etf_data(self) -> List[Dict]:
        """獲取所有 ETF 數據"""
        # 添加隨機變化模擬即時數據
        for etf in self.etf_data:
            etf['updated_at'] = datetime.now().isoformat()
            # 小幅隨機變化
            etf['current_price'] += random.uniform(-0.5, 0.5)
            etf['current_price'] = round(etf['current_price'], 2)
        
        return self.etf_data.copy()
    
    def get_etf_data(self, symbol: str) -> Optional[Dict]:
        """獲取單一 ETF 數據"""
        symbol_clean = symbol.replace('.TW', '')
        for etf in self.etf_data:
            if etf['symbol'] == symbol_clean:
                etf_copy = etf.copy()
                etf_copy['updated_at'] = datetime.now().isoformat()
                return etf_copy
        return None
    
    def get_market_data(self) -> Dict:
        """獲取市場數據"""
        return {
            'taiex_price': 17850.25,
            'taiex_change': 125.80,
            'taiex_change_percent': 0.71,
            'taiex_rsi': 48.5,
            'vix': 18.2,
            'economic_indicator': '綠燈',
            'updated_at': datetime.now().isoformat()
        }

