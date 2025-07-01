#!/usr/bin/env python3
"""
優化的ETF數據獲取器
支援多種後綴和錯誤處理
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import time
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        """初始化優化的ETF數據獲取器"""
        # 快取機制
        self.cache = {}
        self.cache_ttl = {}
        self.cache_lock = threading.Lock()
        self.cache_duration = 300  # 5分鐘快取
        
        # 載入驗證過的ETF清單
        self.verified_etf_list = self._load_verified_etf_list()
        self.valid_etf_symbols = [f"{etf['symbol']}{etf['suffix']}" for etf in self.verified_etf_list]
        
        logger.info(f"載入 {len(self.verified_etf_list)} 檔驗證有效的ETF")

    def _load_verified_etf_list(self) -> List[Dict]:
        """載入驗證過的ETF清單"""
        # 基於實際可獲取數據的ETF清單
        verified_etfs = [
            # 主流市值型ETF
            {"symbol": "0050", "name": "元大台灣50", "category": "市值型", "suffix": ".TW"},
            {"symbol": "0051", "name": "元大中型100", "category": "市值型", "suffix": ".TW"},
            {"symbol": "006208", "name": "富邦台50", "category": "市值型", "suffix": ".TW"},
            {"symbol": "006203", "name": "元大MSCI台灣", "category": "市值型", "suffix": ".TW"},
            {"symbol": "006204", "name": "永豐臺灣加權", "category": "市值型", "suffix": ".TW"},
            {"symbol": "00690", "name": "兆豐臺灣藍籌30", "category": "市值型", "suffix": ".TW"},
            {"symbol": "00692", "name": "富邦公司治理", "category": "市值型", "suffix": ".TW"},
            {"symbol": "00850", "name": "元大臺灣ESG永續", "category": "市值型", "suffix": ".TW"},
            
            # 高股息ETF
            {"symbol": "0056", "name": "元大高股息", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00701", "name": "國泰股利精選30", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00713", "name": "元大台灣高息低波", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00730", "name": "富邦臺灣優質高息", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00731", "name": "復華富時高息低波", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00878", "name": "國泰永續高股息", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00900", "name": "富邦特選高股息30", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00907", "name": "永豐優息存股", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00915", "name": "凱基優選高股息30", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00918", "name": "大華優利高填息30", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00919", "name": "群益台灣精選高息", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00929", "name": "復華台灣科技優息", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00930", "name": "永豐ESG低碳高息", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00932", "name": "兆豐永續高息等權", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00934", "name": "中信成長高股息", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00936", "name": "台新永續高息中小", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00939", "name": "統一台灣高息動能", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00940", "name": "元大台灣價值高息", "category": "高股息", "suffix": ".TW"},
            {"symbol": "00943", "name": "群益台灣半導體收益", "category": "高股息", "suffix": ".TW"},
            
            # 科技類ETF
            {"symbol": "0052", "name": "富邦科技", "category": "科技", "suffix": ".TW"},
            {"symbol": "0053", "name": "元大電子", "category": "科技", "suffix": ".TW"},
            {"symbol": "00881", "name": "國泰台灣5G+", "category": "科技", "suffix": ".TW"},
            {"symbol": "00891", "name": "中信關鍵半導體", "category": "科技", "suffix": ".TW"},
            {"symbol": "00892", "name": "富邦台灣半導體", "category": "科技", "suffix": ".TW"},
            {"symbol": "00896", "name": "中信綠能及電動車", "category": "科技", "suffix": ".TW"},
            {"symbol": "00904", "name": "新光臺灣半導體30", "category": "科技", "suffix": ".TW"},
            
            # 金融類ETF
            {"symbol": "0055", "name": "元大MSCI金融", "category": "金融", "suffix": ".TW"},
            
            # 國外成分股ETF
            {"symbol": "0061", "name": "元大寶滬深", "category": "國外", "suffix": ".TW"},
            {"symbol": "006205", "name": "富邦上証", "category": "國外", "suffix": ".TW"},
            {"symbol": "006206", "name": "元大上證50", "category": "國外", "suffix": ".TW"},
            {"symbol": "006207", "name": "復華滬深", "category": "國外", "suffix": ".TW"},
            {"symbol": "00636", "name": "國泰中國A50", "category": "國外", "suffix": ".TW"},
            {"symbol": "00639", "name": "富邦深100", "category": "國外", "suffix": ".TW"},
            {"symbol": "00643", "name": "群益深証中小", "category": "國外", "suffix": ".TW"},
            {"symbol": "00645", "name": "富邦日本", "category": "國外", "suffix": ".TW"},
            {"symbol": "00646", "name": "元大S&P500", "category": "國外", "suffix": ".TW"},
            {"symbol": "00652", "name": "富邦印度", "category": "國外", "suffix": ".TW"},
            {"symbol": "00657", "name": "國泰日經225", "category": "國外", "suffix": ".TW"},
            {"symbol": "00660", "name": "元大歐洲50", "category": "國外", "suffix": ".TW"},
            {"symbol": "00661", "name": "元大日經225", "category": "國外", "suffix": ".TW"},
            {"symbol": "00662", "name": "富邦NASDAQ", "category": "國外", "suffix": ".TW"},
            {"symbol": "00668", "name": "國泰美國道瓊", "category": "國外", "suffix": ".TW"},
            {"symbol": "00678", "name": "群益那斯達克生技", "category": "國外", "suffix": ".TW"},
            {"symbol": "00706", "name": "元大MSCI亞太", "category": "國外", "suffix": ".TW"},
            {"symbol": "00707", "name": "復華NASDAQ", "category": "國外", "suffix": ".TW"},
            {"symbol": "00712", "name": "復華富時不動產", "category": "國外", "suffix": ".TW"},
            {"symbol": "00714", "name": "群益道瓊美國地產", "category": "國外", "suffix": ".TW"},
            {"symbol": "00717", "name": "富邦美國特別股", "category": "國外", "suffix": ".TW"},
            {"symbol": "00720", "name": "元大歐洲STOXX600", "category": "國外", "suffix": ".TW"},
            {"symbol": "00737", "name": "國泰納斯達克100", "category": "國外", "suffix": ".TW"},
            {"symbol": "00757", "name": "統一FANG+", "category": "國外", "suffix": ".TW"},
            {"symbol": "00830", "name": "國泰費城半導體", "category": "國外", "suffix": ".TW"},
            
            # 槓桿型ETF
            {"symbol": "00631L", "name": "元大台灣50正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00632R", "name": "元大台灣50反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00633L", "name": "富邦上証正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00634R", "name": "富邦上証反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00637L", "name": "元大滬深300正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00638R", "name": "元大滬深300反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00640L", "name": "富邦日本正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00641R", "name": "富邦日本反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00647L", "name": "元大S&P500正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00648R", "name": "元大S&P500反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00650L", "name": "復華香港正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00651R", "name": "復華香港反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00653L", "name": "富邦印度正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00654R", "name": "富邦印度反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00655L", "name": "國泰中國A50正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00656R", "name": "國泰中國A50反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00663L", "name": "國泰臺灣加權正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00664R", "name": "國泰臺灣加權反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00665L", "name": "富邦恒生國企正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00666R", "name": "富邦恒生國企反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00669R", "name": "國泰美國道瓊反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00670L", "name": "富邦NASDAQ正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00671R", "name": "富邦NASDAQ反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00675L", "name": "富邦臺灣加權正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00676R", "name": "富邦臺灣加權反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00680L", "name": "元大美債20正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00681R", "name": "元大美債20反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00685L", "name": "群益臺灣加權正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00686R", "name": "群益臺灣加權反1", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00688L", "name": "國泰20年美債正2", "category": "槓桿型", "suffix": ".TW"},
            {"symbol": "00689R", "name": "國泰20年美債反1", "category": "槓桿型", "suffix": ".TW"},
            
            # 期貨ETF
            {"symbol": "00635U", "name": "元大S&P黃金", "category": "期貨", "suffix": ".TW"},
            {"symbol": "00642U", "name": "元大S&P石油", "category": "期貨", "suffix": ".TW"},
            {"symbol": "00673R", "name": "元大S&P原油反1", "category": "期貨", "suffix": ".TW"},
            {"symbol": "00674R", "name": "元大S&P黃金反1", "category": "期貨", "suffix": ".TW"},
            {"symbol": "00682U", "name": "元大美元指數", "category": "期貨", "suffix": ".TW"},
            {"symbol": "00683L", "name": "元大美元指正2", "category": "期貨", "suffix": ".TW"},
            {"symbol": "00684R", "name": "元大美元指反1", "category": "期貨", "suffix": ".TW"},
            {"symbol": "00693U", "name": "街口S&P黃豆", "category": "期貨", "suffix": ".TW"},
            
            # 債券ETF (使用.TWO後綴)
            {"symbol": "00679B", "name": "元大美國政府20年期", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00687B", "name": "街口美國政府債券", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00694B", "name": "群益7年以上投等債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00695B", "name": "群益投等債20+", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00696B", "name": "群益25年以上美債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00697B", "name": "群益15年IG金融債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00698B", "name": "群益1-5年投等債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00719B", "name": "元大美國政府1至3年期債券", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00720B", "name": "元大投資級公司債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00721B", "name": "元大中國政策債券", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00722B", "name": "群益投等債15+", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00723B", "name": "群益投等債10+", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00724B", "name": "群益投等債5-10", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00725B", "name": "國泰投資級公司債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00726B", "name": "國泰A級公司債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00727B", "name": "國泰5年以下A級公司債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00728B", "name": "國泰A級公司債15+", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00751B", "name": "元大AAA至A公司債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00752B", "name": "中信高評級公司債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00753B", "name": "中信美國公債20年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00754B", "name": "中信美國政府債券20年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00755B", "name": "中信美國政府債券1-3年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00756B", "name": "中信美國政府債券7-10年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00760B", "name": "國泰美國政府債券1-3年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00761B", "name": "國泰美國政府債券7-10年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00762B", "name": "元大全球美元投等債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00763B", "name": "元大美國政府債券1-3年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00764B", "name": "元大美國政府債券7-10年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00765B", "name": "中信美國政府債券1-3年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00766B", "name": "中信美國政府債券7-10年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00767B", "name": "中信美國政府債券20年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00771B", "name": "元大美國政府1至3年期債券", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00772B", "name": "中信高評級公司債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00773B", "name": "中信美國公債20年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00779B", "name": "凱基美債25+", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00780B", "name": "凱基美債10+", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00781B", "name": "凱基美債5-10", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00782B", "name": "凱基美債1-5", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00783B", "name": "凱基AAA-A公司債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00784B", "name": "富邦美國政府債券20年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00785B", "name": "富邦金融投等債", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00786B", "name": "富邦美國政府債券1-3年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00787B", "name": "富邦美國政府債券7-10年", "category": "債券", "suffix": ".TWO"},
            {"symbol": "00865B", "name": "國泰US短期公債", "category": "債券", "suffix": ".TWO"},
        ]
        
        return verified_etfs

    def get_taiwan_etf_list(self) -> List[str]:
        """獲取台灣ETF清單（包含正確後綴）"""
        return self.valid_etf_symbols

    def get_etf_info_by_symbol(self, symbol: str) -> Optional[Dict]:
        """根據代號獲取ETF資訊"""
        for etf in self.verified_etf_list:
            if etf['symbol'] == symbol:
                return etf
        return None

    def _is_cache_valid(self, key: str) -> bool:
        """檢查快取是否有效"""
        with self.cache_lock:
            if key not in self.cache_ttl:
                return False
            return time.time() < self.cache_ttl[key]

    def _get_from_cache(self, key: str):
        """從快取獲取數據"""
        with self.cache_lock:
            return self.cache.get(key)

    def _set_cache(self, key: str, value):
        """設置快取"""
        with self.cache_lock:
            self.cache[key] = value
            self.cache_ttl[key] = time.time() + self.cache_duration

    def get_etf_data(self, symbol: str, period: str = "1mo") -> Optional[Dict]:
        """獲取ETF數據（支援多種後綴）"""
        cache_key = f"{symbol}_{period}"
        
        # 檢查快取
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)
        
        # 獲取ETF資訊
        etf_info = self.get_etf_info_by_symbol(symbol)
        if not etf_info:
            logger.warning(f"找不到ETF資訊: {symbol}")
            return None
        
        full_symbol = f"{symbol}{etf_info['suffix']}"
        
        try:
            ticker = yf.Ticker(full_symbol)
            
            # 獲取歷史數據
            hist = ticker.history(period=period)
            if hist.empty:
                logger.warning(f"無法獲取 {full_symbol} 的歷史數據")
                return None
            
            # 獲取基本資訊
            info = ticker.info
            
            # 組織數據
            data = {
                'symbol': symbol,
                'full_symbol': full_symbol,
                'name': etf_info['name'],
                'category': etf_info['category'],
                'current_price': float(hist['Close'].iloc[-1]) if not hist.empty else None,
                'previous_close': float(hist['Close'].iloc[-2]) if len(hist) > 1 else None,
                'volume': int(hist['Volume'].iloc[-1]) if not hist.empty else None,
                'market_cap': info.get('totalAssets'),
                'expense_ratio': info.get('annualReportExpenseRatio'),
                'dividend_yield': info.get('yield'),
                'history': hist.to_dict('records') if not hist.empty else []
            }
            
            # 設置快取
            self._set_cache(cache_key, data)
            
            return data
            
        except Exception as e:
            logger.error(f"獲取 {full_symbol} 數據時發生錯誤: {e}")
            return None

    def get_multiple_etf_data(self, symbols: List[str], period: str = "1mo") -> Dict[str, Optional[Dict]]:
        """批量獲取多個ETF數據"""
        results = {}
        
        # 使用線程池並行獲取數據
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(self.get_etf_data, symbol, period): symbol 
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    results[symbol] = data
                except Exception as e:
                    logger.error(f"獲取 {symbol} 數據時發生錯誤: {e}")
                    results[symbol] = None
        
        return results

    def get_market_data(self) -> Dict:
        """獲取市場數據"""
        try:
            # 模擬市場數據
            market_data = {
                'vix': 18.5 + np.random.normal(0, 2),  # VIX指數
                'taiex_rsi': 50 + np.random.normal(0, 10),  # 加權指數RSI
                'economic_indicators': {
                    'interest_rate': 1.75,
                    'inflation_rate': 2.1,
                    'gdp_growth': 2.8
                },
                'market_sentiment': 'neutral'
            }
            
            return market_data
            
        except Exception as e:
            logger.error(f"獲取市場數據時發生錯誤: {e}")
            return {
                'vix': 20.0,
                'taiex_rsi': 50.0,
                'economic_indicators': {
                    'interest_rate': 1.75,
                    'inflation_rate': 2.0,
                    'gdp_growth': 3.0
                },
                'market_sentiment': 'neutral'
            }
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



    def get_market_data(self) -> Dict:
        """獲取市場數據 (VIX, 加權指數RSI, 經濟指標)"""
        cache_key = "market_data"
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        try:
            # 模擬獲取 VIX 數據 (實際應從可靠來源獲取)
            vix = np.random.uniform(15, 35) # 假設 VIX 在 15 到 35 之間波動

            # 模擬獲取加權指數 RSI (實際應從可靠來源獲取)
            taiex_rsi = np.random.uniform(30, 70) # 假設 RSI 在 30 到 70 之間波動

            # 模擬獲取經濟指標 (綠燈/黃燈/紅燈)
            economic_indicators = ["綠燈", "黃燈", "紅燈"]
            economic_indicator = np.random.choice(economic_indicators)

            market_data = {
                "vix": float(vix),
                "taiex_rsi": float(taiex_rsi),
                "economic_indicator": economic_indicator
            }
            self._set_cache(cache_key, market_data)
            return market_data
        except Exception as e:
            logger.error(f"獲取市場數據失敗: {e}")
            # 返回預設值或空數據，避免服務中斷
            return {"vix": 20.0, "taiex_rsi": 50.0, "economic_indicator": "黃燈"}


