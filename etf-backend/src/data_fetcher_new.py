import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import time
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        """初始化數據獲取器，使用驗證過的ETF清單"""
        # 快取機制
        self.cache = {}
        self.cache_ttl = {}
        self.cache_lock = threading.Lock()
        self.cache_duration = 300  # 5分鐘快取
        
        # 載入驗證過的ETF清單
        self.verified_etf_list = self._load_verified_etf_list()
        self.valid_etf_symbols = [f"{etf['symbol']}.TW" for etf in self.verified_etf_list]
        
        logger.info(f"載入 {len(self.verified_etf_list)} 檔驗證有效的ETF")

    def _load_verified_etf_list(self) -> List[Dict]:
        """載入驗證過的ETF清單"""
        try:
            # 嘗試從當前目錄載入
            file_path = os.path.join(os.path.dirname(__file__), 'verified_etf_list.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                etf_list = json.load(f)
            return etf_list
        except FileNotFoundError:
            logger.error("找不到 verified_etf_list.json 文件")
            return []
        except json.JSONDecodeError:
            logger.error("verified_etf_list.json 格式錯誤")
            return []

    def get_taiwan_etf_list(self) -> List[str]:
        """獲取台灣ETF清單"""
        return self.valid_etf_symbols

    def _is_cache_valid(self, key: str) -> bool:
        """檢查快取是否有效"""
        with self.cache_lock:
            if key not in self.cache_ttl:
                return False
            return time.time() - self.cache_ttl[key] < self.cache_duration

    def _get_from_cache(self, key: str):
        """從快取獲取數據"""
        with self.cache_lock:
            return self.cache.get(key)

    def _set_cache(self, key: str, value):
        """設置快取"""
        with self.cache_lock:
            self.cache[key] = value
            self.cache_ttl[key] = time.time()

    def get_etf_data(self, symbol: str, timeout: int = 5) -> Optional[Dict]:
        """
        獲取單個ETF的數據
        
        Args:
            symbol: ETF代碼 (如 '0050.TW')
            timeout: 超時時間（秒）
        
        Returns:
            包含ETF數據的字典，如果失敗則返回None
        """
        cache_key = f"etf_data_{symbol}"
        
        # 檢查快取
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)
        
        try:
            ticker = yf.Ticker(symbol)
            
            # 獲取歷史數據（最近30天）
            hist = ticker.history(period="1mo")
            if hist.empty:
                logger.warning(f"無法獲取 {symbol} 的歷史數據")
                return None
            
            # 獲取基本資訊
            info = ticker.info
            
            # 計算技術指標
            close_prices = hist['Close']
            
            # RSI
            rsi = self._calculate_rsi(close_prices)
            
            # MACD
            macd_line, signal_line, histogram = self._calculate_macd(close_prices)
            
            # KD指標
            k_percent, d_percent = self._calculate_kd(hist)
            
            # 組織數據
            etf_data = {
                'symbol': symbol.replace('.TW', ''),
                'name': info.get('longName', info.get('shortName', symbol)),
                'current_price': float(close_prices.iloc[-1]),
                'previous_close': float(close_prices.iloc[-2]) if len(close_prices) > 1 else float(close_prices.iloc[-1]),
                'volume': int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else 0,
                'market_cap': info.get('marketCap', 0),
                'expense_ratio': info.get('annualReportExpenseRatio', 0),
                'technical_indicators': {
                    'rsi': float(rsi) if not np.isnan(rsi) else 50.0,
                    'macd': {
                        'macd_line': float(macd_line) if not np.isnan(macd_line) else 0.0,
                        'signal_line': float(signal_line) if not np.isnan(signal_line) else 0.0,
                        'histogram': float(histogram) if not np.isnan(histogram) else 0.0
                    },
                    'kd': {
                        'k_percent': float(k_percent) if not np.isnan(k_percent) else 50.0,
                        'd_percent': float(d_percent) if not np.isnan(d_percent) else 50.0
                    }
                },
                'price_change': float(close_prices.iloc[-1] - close_prices.iloc[-2]) if len(close_prices) > 1 else 0.0,
                'price_change_percent': float((close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2] * 100) if len(close_prices) > 1 else 0.0
            }
            
            # 設置快取
            self._set_cache(cache_key, etf_data)
            
            return etf_data
            
        except Exception as e:
            logger.warning(f"無法獲取 {symbol} 的數據: {e}")
            return None

    def get_all_etf_data(self, max_workers: int = 8, batch_size: int = 25) -> List[Dict]:
        """
        並行獲取所有ETF數據
        
        Args:
            max_workers: 最大並行工作數
            batch_size: 每批處理的ETF數量
        
        Returns:
            ETF數據列表
        """
        start_time = time.time()
        etf_symbols = self.get_taiwan_etf_list()
        
        logger.info(f"開始並行獲取 {len(etf_symbols)} 檔ETF數據，分為 {(len(etf_symbols) + batch_size - 1) // batch_size} 批次")
        
        all_etf_data = []
        
        # 分批處理
        for i in range(0, len(etf_symbols), batch_size):
            batch = etf_symbols[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(etf_symbols) + batch_size - 1) // batch_size
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_symbol = {executor.submit(self.get_etf_data, symbol): symbol for symbol in batch}
                
                batch_data = []
                for future in as_completed(future_to_symbol):
                    result = future.result()
                    if result:
                        batch_data.append(result)
                
                all_etf_data.extend(batch_data)
                logger.info(f"完成第 {batch_num}/{total_batches} 批次，獲得 {len(batch_data)} 檔ETF數據")
        
        elapsed_time = time.time() - start_time
        logger.info(f"並行獲取完成，總共獲得 {len(all_etf_data)} 檔ETF數據，耗時 {elapsed_time:.2f} 秒")
        
        return all_etf_data

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """計算RSI指標"""
        if len(prices) < period + 1:
            return 50.0
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not rsi.empty else 50.0

    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """計算MACD指標"""
        if len(prices) < slow:
            return 0.0, 0.0, 0.0
        
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return (
            macd_line.iloc[-1] if not macd_line.empty else 0.0,
            signal_line.iloc[-1] if not signal_line.empty else 0.0,
            histogram.iloc[-1] if not histogram.empty else 0.0
        )

    def _calculate_kd(self, data: pd.DataFrame, k_period: int = 9, d_period: int = 3):
        """計算KD指標"""
        if len(data) < k_period:
            return 50.0, 50.0
        
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return (
            k_percent.iloc[-1] if not k_percent.empty else 50.0,
            d_percent.iloc[-1] if not d_percent.empty else 50.0
        )

    def get_etf_info(self, symbol: str) -> Optional[Dict]:
        """獲取ETF基本資訊"""
        cache_key = f"etf_info_{symbol}"
        
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            etf_info = {
                'symbol': symbol.replace('.TW', ''),
                'name': info.get('longName', info.get('shortName', symbol)),
                'category': info.get('category', ''),
                'family': info.get('family', ''),
                'expense_ratio': info.get('annualReportExpenseRatio', 0),
                'net_assets': info.get('totalAssets', 0),
                'inception_date': info.get('fundInceptionDate', ''),
                'currency': info.get('currency', 'TWD')
            }
            
            self._set_cache(cache_key, etf_info)
            return etf_info
            
        except Exception as e:
            logger.warning(f"無法獲取 {symbol} 的基本資訊: {e}")
            return None

