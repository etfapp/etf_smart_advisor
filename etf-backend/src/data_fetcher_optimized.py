#!/usr/bin/env python3
"""
優化的ETF數據獲取器
整合真實技術指標計算，提升數據準確性
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
from technical_indicators import TechnicalIndicators

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedDataFetcher:
    def __init__(self):
        """初始化優化的ETF數據獲取器"""
        # 快取機制
        self.cache = {}
        self.cache_ttl = {}
        self.cache_lock = threading.Lock()
        self.cache_duration = 300  # 5分鐘快取
        
        # 載入清理後的ETF清單
        self.verified_etf_list = self._load_verified_etf_list()
        self.valid_etf_symbols = [f"{etf['symbol']}{etf['suffix']}" for etf in self.verified_etf_list]
        
        # 技術指標計算器
        self.tech_indicators = TechnicalIndicators()
        
        logger.info(f"載入 {len(self.verified_etf_list)} 檔驗證有效的ETF")

    def _load_verified_etf_list(self) -> List[Dict]:
        """載入驗證過的ETF清單"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            etf_list_path = os.path.join(current_dir, 'verified_etf_list.json')
            
            with open(etf_list_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入ETF清單失敗: {e}")
            return []

    def get_taiwan_etf_list(self) -> List[Dict]:
        """獲取台灣ETF清單"""
        return self.verified_etf_list

    def _is_cache_valid(self, key: str) -> bool:
        """檢查快取是否有效"""
        with self.cache_lock:
            if key not in self.cache_ttl:
                return False
            return time.time() < self.cache_ttl[key]

    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """從快取獲取數據"""
        with self.cache_lock:
            if self._is_cache_valid(key):
                return self.cache.get(key)
            return None

    def _set_cache(self, key: str, data: Dict):
        """設置快取"""
        with self.cache_lock:
            self.cache[key] = data
            self.cache_ttl[key] = time.time() + self.cache_duration

    def get_etf_data(self, symbol: str, suffix: str = '.TW') -> Optional[Dict]:
        """獲取單個ETF的詳細數據"""
        ticker_symbol = f"{symbol}{suffix}"
        cache_key = f"etf_data_{ticker_symbol}"
        
        # 檢查快取
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            # 獲取歷史數據（1個月）
            hist = ticker.history(period='1mo')
            if hist.empty:
                logger.warning(f"無法獲取 {ticker_symbol} 的歷史數據")
                return None
            
            # 獲取基本信息
            info = ticker.info
            current_price = float(hist['Close'].iloc[-1])
            
            # 計算技術指標
            technical_data = self.tech_indicators.calculate_all_indicators(hist)
            
            # 計算基本面指標
            fundamental_data = self._calculate_fundamental_indicators(info, hist)
            
            # 計算流動性指標
            liquidity_data = self._calculate_liquidity_indicators(hist)
            
            etf_data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'current_price': current_price,
                'technical_indicators': technical_data,
                'fundamental_indicators': fundamental_data,
                'liquidity_indicators': liquidity_data,
                'valid': True,
                'last_updated': time.time()
            }
            
            # 設置快取
            self._set_cache(cache_key, etf_data)
            
            return etf_data
            
        except Exception as e:
            logger.warning(f"獲取 {ticker_symbol} 數據失敗: {e}")
            return None

    def _calculate_fundamental_indicators(self, info: Dict, hist: pd.DataFrame) -> Dict:
        """計算基本面指標"""
        try:
            # 從info中提取基本面數據
            expense_ratio = info.get('annualReportExpenseRatio', 0.5)  # 費用率
            aum = info.get('totalAssets', 1000000000)  # 資產規模
            dividend_yield = info.get('yield', 0.03)  # 股息率
            
            # 計算價格波動率
            if len(hist) >= 20:
                returns = hist['Close'].pct_change().dropna()
                volatility = float(returns.std() * np.sqrt(252))  # 年化波動率
            else:
                volatility = 0.2  # 默認20%
            
            # 計算夏普比率（簡化版）
            if volatility > 0:
                avg_return = float(returns.mean() * 252) if len(hist) >= 20 else 0.05
                risk_free_rate = 0.02  # 假設無風險利率2%
                sharpe_ratio = (avg_return - risk_free_rate) / volatility
            else:
                sharpe_ratio = 0.0
            
            return {
                'expense_ratio': expense_ratio,
                'aum': aum,
                'dividend_yield': dividend_yield,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio
            }
        except Exception as e:
            logger.warning(f"基本面指標計算錯誤: {e}")
            return {
                'expense_ratio': 0.5,
                'aum': 1000000000,
                'dividend_yield': 0.03,
                'volatility': 0.2,
                'sharpe_ratio': 0.0
            }

    def _calculate_liquidity_indicators(self, hist: pd.DataFrame) -> Dict:
        """計算流動性指標"""
        try:
            if hist.empty or 'Volume' not in hist.columns:
                return {
                    'avg_volume': 1000000,
                    'volume_volatility': 0.3,
                    'bid_ask_spread': 0.1
                }
            
            volumes = hist['Volume']
            avg_volume = float(volumes.mean())
            volume_volatility = float(volumes.std() / volumes.mean()) if volumes.mean() > 0 else 0.3
            
            # 簡化的買賣價差估算（基於價格波動）
            prices = hist['Close']
            price_volatility = float(prices.pct_change().std())
            bid_ask_spread = price_volatility * 0.5  # 估算值
            
            return {
                'avg_volume': avg_volume,
                'volume_volatility': volume_volatility,
                'bid_ask_spread': bid_ask_spread
            }
        except Exception as e:
            logger.warning(f"流動性指標計算錯誤: {e}")
            return {
                'avg_volume': 1000000,
                'volume_volatility': 0.3,
                'bid_ask_spread': 0.1
            }

    def get_batch_etf_data(self, etf_list: List[Dict], max_workers: int = 10) -> List[Dict]:
        """批量獲取ETF數據"""
        valid_etfs = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任務
            future_to_etf = {
                executor.submit(self.get_etf_data, etf['symbol'], etf['suffix']): etf 
                for etf in etf_list
            }
            
            # 收集結果
            for future in as_completed(future_to_etf):
                etf_info = future_to_etf[future]
                try:
                    result = future.result()
                    if result:
                        valid_etfs.append(result)
                except Exception as e:
                    logger.error(f"獲取 {etf_info['symbol']} 數據時發生錯誤: {e}")
        
        logger.info(f"成功獲取 {len(valid_etfs)} 檔ETF數據")
        return valid_etfs

    def get_all_etf_data(self) -> List[Dict]:
        """獲取所有ETF數據"""
        logger.info("開始獲取所有ETF數據...")
        start_time = time.time()
        
        # 分批處理，避免過多並發請求
        batch_size = 25
        all_etfs = []
        
        for i in range(0, len(self.verified_etf_list), batch_size):
            batch = self.verified_etf_list[i:i + batch_size]
            logger.info(f"處理第 {i//batch_size + 1} 批，共 {len(batch)} 檔ETF")
            
            batch_results = self.get_batch_etf_data(batch)
            all_etfs.extend(batch_results)
            
            # 批次間稍作停頓，避免API限制
            if i + batch_size < len(self.verified_etf_list):
                time.sleep(1)
        
        elapsed_time = time.time() - start_time
        logger.info(f"ETF數據獲取完成，共 {len(all_etfs)} 檔，耗時 {elapsed_time:.2f} 秒")
        
        return all_etfs

    def get_market_data(self) -> Dict:
        """獲取市場數據"""
        try:
            # 獲取台股指數數據
            taiex = yf.Ticker('^TWII')
            taiex_hist = taiex.history(period='1mo')
            
            if not taiex_hist.empty:
                taiex_prices = taiex_hist['Close']
                taiex_rsi = self.tech_indicators.calculate_rsi(taiex_prices)
                
                # 計算台股趨勢
                ma20 = taiex_prices.rolling(20).mean().iloc[-1] if len(taiex_prices) >= 20 else taiex_prices.iloc[-1]
                current_price = taiex_prices.iloc[-1]
                trend = "上升" if current_price > ma20 else "下降"
            else:
                taiex_rsi = 50.0
                trend = "橫盤"
            
            # VIX數據（使用美股VIX作為參考）
            try:
                vix = yf.Ticker('^VIX')
                vix_hist = vix.history(period='5d')
                vix_value = float(vix_hist['Close'].iloc[-1]) if not vix_hist.empty else 20.0
            except:
                vix_value = 20.0
            
            # 經濟指標（簡化版）
            economic_indicator = self._get_economic_indicator(taiex_rsi, vix_value)
            
            return {
                'taiex_rsi': taiex_rsi,
                'taiex_trend': trend,
                'vix': vix_value,
                'economic_indicator': economic_indicator,
                'last_updated': time.time()
            }
            
        except Exception as e:
            logger.error(f"獲取市場數據失敗: {e}")
            return {
                'taiex_rsi': 50.0,
                'taiex_trend': '橫盤',
                'vix': 20.0,
                'economic_indicator': '綠燈',
                'last_updated': time.time()
            }

    def _get_economic_indicator(self, taiex_rsi: float, vix: float) -> str:
        """根據技術指標推估經濟指標"""
        # 簡化的經濟指標判斷
        if vix > 30 or taiex_rsi < 30:
            return '藍燈'  # 低迷
        elif vix > 25 or taiex_rsi < 40:
            return '黃藍燈'  # 轉弱
        elif vix < 15 and taiex_rsi > 70:
            return '紅燈'  # 過熱
        elif vix < 20 and taiex_rsi > 60:
            return '黃紅燈'  # 注意
        else:
            return '綠燈'  # 穩定

