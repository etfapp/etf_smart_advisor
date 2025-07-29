import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ImprovedDataFetcher:
    """升級後的數據獲取器"""
    
    def __init__(self):
        # 清理後的ETF清單 - 移除重複和無效項目
        self.etf_list = {
            'large_cap': {
                '0050': '元大台灣50',
                '006208': '富邦台50'
            },
            'dividend': {
                '0056': '元大高股息',
                '00878': '國泰永續高股息',
                '00713': '元大台灣高息低波'
            },
            'tech': {
                '0052': '富邦科技',
                '00881': '國泰台灣5G+'
            },
            'mid_small': {
                '0051': '元大中型100',
                '00762': '元大全球AI'
            },
            'bond': {
                '00679B': '元大美債20年',
                '00687B': '國泰20年美債'
            },
            'reit': {
                '00712': '復華富時不動產',
                '01001': '元大台灣ESG永續'
            }
        }
        
        # 數據緩存
        self.cache = {}
        self.cache_ttl = 300  # 5分鐘緩存
        
        # 請求限制
        self.last_request_time = {}
        self.min_request_interval = 1  # 最小請求間隔1秒
    
    def get_etf_list(self) -> Dict:
        """獲取ETF清單"""
        return self.etf_list
    
    def fetch_etf_data(self, symbol: str) -> Optional[Dict]:
        """獲取ETF數據"""
        # 檢查緩存
        cache_key = f"etf_{symbol}"
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached data for {symbol}")
            return self.cache[cache_key]
        
        # 限制請求頻率
        self._rate_limit(symbol)
        
        try:
            logger.info(f"Fetching fresh data for {symbol}")
            
            # 使用yfinance獲取數據
            ticker_symbol = f"{symbol}.TW"
            ticker = yf.Ticker(ticker_symbol)
            
            # 獲取基本信息
            try:
                info = ticker.info
            except Exception as e:
                logger.warning(f"Could not fetch info for {symbol}: {e}")
                info = {}
            
            # 獲取歷史數據
            try:
                hist = ticker.history(period="1y", interval="1d")
                if hist.empty:
                    logger.warning(f"No historical data for {symbol}")
                    return None
            except Exception as e:
                logger.error(f"Error fetching historical data for {symbol}: {e}")
                return None
            
            # 計算技術指標
            technical_data = self._calculate_technical_indicators(hist)
            
            # 獲取ETF名稱
            etf_name = self._get_etf_name(symbol)
            
            # 構建數據結構
            etf_data = {
                'symbol': symbol,
                'name': etf_name,
                'current_price': float(hist['Close'].iloc[-1]),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'aum': info.get('totalAssets'),
                'expense_ratio': info.get('expenseRatio'),
                'avg_volume': float(hist['Volume'].tail(20).mean()),
                'price_data': {
                    'current_price': float(hist['Close'].iloc[-1]),
                    'ma20': float(technical_data['MA20'].iloc[-1]) if not pd.isna(technical_data['MA20'].iloc[-1]) else None,
                    'ma60': float(technical_data['MA60'].iloc[-1]) if not pd.isna(technical_data['MA60'].iloc[-1]) else None,
                    'rsi': float(technical_data['RSI'].iloc[-1]) if not pd.isna(technical_data['RSI'].iloc[-1]) else None,
                    'macd': float(technical_data['MACD'].iloc[-1]) if not pd.isna(technical_data['MACD'].iloc[-1]) else None,
                    'macd_signal': float(technical_data['MACD_Signal'].iloc[-1]) if not pd.isna(technical_data['MACD_Signal'].iloc[-1]) else None,
                    'volatility': float(hist['Close'].pct_change().std() * (252**0.5))
                },
                'performance': {
                    '1d': float((hist['Close'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100) if len(hist) >= 2 else 0,
                    '1w': float((hist['Close'].iloc[-1] / hist['Close'].iloc[-6] - 1) * 100) if len(hist) >= 6 else 0,
                    '1m': float((hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1) * 100) if len(hist) >= 21 else 0,
                    '3m': float((hist['Close'].iloc[-1] / hist['Close'].iloc[-63] - 1) * 100) if len(hist) >= 63 else 0,
                    '1y': float((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100) if len(hist) >= 252 else 0
                },
                'last_updated': datetime.now()
            }
            
            # 更新緩存
            self.cache[cache_key] = etf_data
            logger.info(f"Successfully fetched and cached data for {symbol}")
            
            return etf_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _get_etf_name(self, symbol: str) -> str:
        """獲取ETF名稱"""
        for category in self.etf_list.values():
            if symbol in category:
                return category[symbol]
        return symbol
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標"""
        try:
            # 確保數據不為空
            if df.empty:
                return df
            
            # 移動平均線
            df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['MA60'] = df['Close'].rolling(window=60, min_periods=1).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            
            # 避免除零錯誤
            rs = gain / loss.replace(0, np.nan)
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            ema12 = df['Close'].ewm(span=12, min_periods=1).mean()
            ema26 = df['Close'].ewm(span=26, min_periods=1).mean()
            df['MACD'] = ema12 - ema26
            df['MACD_Signal'] = df['MACD'].ewm(span=9, min_periods=1).mean()
            
            # 布林帶
            df['BB_Middle'] = df['Close'].rolling(window=20, min_periods=1).mean()
            bb_std = df['Close'].rolling(window=20, min_periods=1).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df
    
    def get_market_overview(self) -> Optional[Dict]:
        """獲取市場概況"""
        cache_key = "market_overview"
        if self._is_cache_valid(cache_key):
            logger.info("Using cached market overview")
            return self.cache[cache_key]
        
        try:
            logger.info("Fetching fresh market overview")
            
            # 獲取台股加權指數
            taiex = yf.Ticker("^TWII")
            taiex_data = taiex.history(period="5d")
            
            if taiex_data.empty:
                logger.warning("No TAIEX data available")
                return None
            
            current_price = float(taiex_data['Close'].iloc[-1])
            prev_price = float(taiex_data['Close'].iloc[-2]) if len(taiex_data) >= 2 else current_price
            change_pct = (current_price / prev_price - 1) * 100 if prev_price != 0 else 0
            
            # 計算波動率
            volatility = float(taiex_data['Close'].pct_change().std() * (252**0.5))
            
            # 判斷趨勢
            if change_pct > 1:
                trend = 'strong_up'
                trend_desc = '強勢上漲'
            elif change_pct > 0:
                trend = 'up'
                trend_desc = '溫和上漲'
            elif change_pct > -1:
                trend = 'sideways'
                trend_desc = '橫盤整理'
            else:
                trend = 'down'
                trend_desc = '下跌趨勢'
            
            market_data = {
                'index_value': current_price,
                'change_percent': change_pct,
                'change_points': current_price - prev_price,
                'trend': trend,
                'trend_description': trend_desc,
                'volatility': volatility,
                'volume': float(taiex_data['Volume'].iloc[-1]) if 'Volume' in taiex_data.columns else 0,
                'last_updated': datetime.now()
            }
            
            # 更新緩存
            self.cache[cache_key] = market_data
            logger.info("Successfully fetched and cached market overview")
            
            return market_data
        
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None
    
    def get_batch_etf_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """批量獲取ETF數據"""
        results = {}
        
        for symbol in symbols:
            try:
                data = self.fetch_etf_data(symbol)
                if data:
                    results[symbol] = data
                    
                # 添加延遲避免請求過於頻繁
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error in batch fetch for {symbol}: {e}")
                continue
        
        return results
    
    def get_etf_historical_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """獲取ETF歷史數據"""
        try:
            ticker_symbol = f"{symbol}.TW"
            ticker = yf.Ticker(ticker_symbol)
            
            hist = ticker.history(period=period)
            
            if hist.empty:
                logger.warning(f"No historical data for {symbol}")
                return None
            
            return hist
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def _is_cache_valid(self, key: str) -> bool:
        """檢查緩存是否有效"""
        if key not in self.cache:
            return False
        
        data = self.cache[key]
        if 'last_updated' not in data:
            return False
        
        time_diff = datetime.now() - data['last_updated']
        return time_diff.seconds < self.cache_ttl
    
    def _rate_limit(self, symbol: str):
        """請求頻率限制"""
        current_time = time.time()
        
        if symbol in self.last_request_time:
            time_since_last = current_time - self.last_request_time[symbol]
            if time_since_last < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last
                logger.info(f"Rate limiting: sleeping {sleep_time:.2f}s for {symbol}")
                time.sleep(sleep_time)
        
        self.last_request_time[symbol] = current_time
    
    def clear_cache(self):
        """清除緩存"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_status(self) -> Dict:
        """獲取緩存狀態"""
        return {
            'cache_size': len(self.cache),
            'cached_items': list(self.cache.keys()),
            'cache_ttl': self.cache_ttl
        }
    
    def validate_etf_symbol(self, symbol: str) -> bool:
        """驗證ETF代碼是否有效"""
        for category in self.etf_list.values():
            if symbol in category:
                return True
        return False
    
    def get_etf_category(self, symbol: str) -> Optional[str]:
        """獲取ETF分類"""
        for category_name, etfs in self.etf_list.items():
            if symbol in etfs:
                return category_name
        return None
    
    def search_etf(self, query: str) -> List[Dict]:
        """搜索ETF"""
        results = []
        query_lower = query.lower()
        
        for category_name, etfs in self.etf_list.items():
            for symbol, name in etfs.items():
                if (query_lower in symbol.lower() or 
                    query_lower in name.lower() or
                    query_lower in category_name.lower()):
                    
                    results.append({
                        'symbol': symbol,
                        'name': name,
                        'category': category_name
                    })
        
        return results

