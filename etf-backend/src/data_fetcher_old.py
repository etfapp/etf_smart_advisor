import yfinance as yf
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import time
from typing import Dict, List, Optional, Tuple
import json
import concurrent.futures
from functools import lru_cache
import threading

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """
    數據獲取器
    負責從各種來源獲取 ETF 和市場數據
    """
    
    def __init__(self):
        self.taiwan_etf_symbols = self._load_etf_symbols_from_json("etf_list.json")
        self.cache = {}
        self.cache_ttl = {}
        self.cache_lock = threading.Lock()
        self.cache_duration = 300  # 5分鐘快取
        
        # 過濾掉已知無效的ETF（擴大清單）
        self.invalid_etfs = {
            # 原有的無效ETF
            '00635L.TW', '00639B.TW', '00643L.TW', '00644R.TW', '00645L.TW',
            '00649.TW', '00658L.TW', '00659R.TW', '00660R.TW', '00661R.TW',
            '00667L.TW', '00668R.TW', '00672L.TW', '00677U.TW', '00678L.TW',
            '00679B.TW', '00687B.TW', '00694B.TW', '00695B.TW', '00696B.TW',
            '00697B.TW', '00698B.TW', '00704L.TW', '00705L.TW',
            
            # 新發現的700系列無效ETF
            '00716.TW', '00718B.TW', '00719B.TW', '00720B.TW', '00721B.TW',
            '00722B.TW', '00723B.TW', '00724B.TW', '00725B.TW', '00726B.TW',
            '00727B.TW', '00729B.TW', '00732.TW', '00734.TW', '00740.TW',
            '00741.TW', '00742.TW', '00743.TW', '00744.TW', '00745.TW',
            '00746.TW', '00747.TW', '00748.TW', '00749.TW', '00750.TW',
            '00751.TW', '00754R.TW', '00755L.TW', '00756L.TW', '00758.TW',
            '00759.TW', '00760.TW', '00761.TW', '00764.TW', '00765.TW',
            '00766.TW', '00767.TW', '00768.TW', '00769.TW', '00772.TW',
            '00773.TW',
            
            # 780系列無效ETF
            '00782.TW', '00784.TW', '00785.TW', '00786.TW', '00787.TW',
            '00788.TW', '00789.TW', '00790.TW', '00791.TW', '00792.TW',
            '00793.TW', '00794.TW',
            
            # 800系列無效ETF
            '00802.TW', '00803.TW', '00804.TW', '00805.TW', '00806.TW',
            '00807.TW', '00808.TW', '00809.TW', '00810.TW', '00811.TW',
            '00812.TW', '00822.TW', '00823.TW', '00824.TW', '00825.TW',
            '00826.TW', '00827.TW', '00828.TW', '00829.TW', '00831.TW',
            '00832.TW', '00833.TW',
            
            # 840系列無效ETF
            '00842.TW', '00843.TW', '00844.TW', '00845.TW', '00846.TW',
            '00847.TW', '00848.TW', '00849.TW',
            
            # 860系列無效ETF
            '00862.TW', '00863.TW', '00864.TW', '00866.TW', '00867.TW',
            '00868.TW', '00869.TW', '00870.TW', '00871.TW'
        }
        
        # 過濾有效的ETF清單
        self.valid_etf_symbols = [
            symbol for symbol in self.taiwan_etf_symbols 
            if symbol not in self.invalid_etfs
        ]
        
        logger.info(f"載入 {len(self.taiwan_etf_symbols)} 檔ETF，過濾後剩餘 {len(self.valid_etf_symbols)} 檔有效ETF")
        
    def _load_etf_symbols_from_json(self, file_path: str) -> List[str]:
        """從 JSON 文件載入 ETF 代碼清單"""
        try:
            # 使用絕對路徑
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(current_dir, file_path)
            
            with open(full_path, 'r', encoding='utf-8') as f:
                etf_list = json.load(f)
            # 將代碼轉換為 yfinance 格式 (例如: 0050 -> 0050.TW)
            return [f"{etf['symbol']}.TW" for etf in etf_list]
        except FileNotFoundError:
            logger.error(f"ETF 清單文件 {full_path} 未找到。")
            return []
        except Exception as e:
            logger.error(f"載入 ETF 清單時發生錯誤: {e}")
            return []

    def get_taiwan_etf_list(self) -> List[str]:
        """獲取台股 ETF 清單"""
        return self.valid_etf_symbols
    
    def _is_cache_valid(self, key: str) -> bool:
        """檢查快取是否有效"""
        if key not in self.cache_ttl:
            return False
        return time.time() < self.cache_ttl[key]
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """從快取獲取數據"""
        with self.cache_lock:
            if self._is_cache_valid(key):
                return self.cache.get(key)
        return None
    
    def _set_cache(self, key: str, value: Dict) -> None:
        """設置快取"""
        with self.cache_lock:
            self.cache[key] = value
            self.cache_ttl[key] = time.time() + self.cache_duration
    
    def get_etf_data(self, symbol: str, period: str = "1y", timeout: int = 5) -> Optional[Dict]:
        """獲取單一 ETF 數據（帶超時和快取）"""
        # 檢查快取
        cache_key = f"{symbol}_{period}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # 移除 .TW 後綴進行顯示
            display_symbol = symbol.replace(".TW", "")
            
            # 使用 yfinance 獲取數據，設置超時
            ticker = yf.Ticker(symbol)
            
            # 獲取基本資訊
            info = ticker.info
            
            # 獲取歷史價格數據
            hist = ticker.history(period=period, timeout=timeout)
            
            if hist.empty:
                logger.warning(f"無法獲取 {symbol} 的歷史數據")
                return None
            
            # 計算技術指標
            current_price = float(hist["Close"].iloc[-1])
            prev_price = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_price
            change = current_price - prev_price
            change_percent = (change / prev_price) * 100 if prev_price != 0 else 0
            
            # 計算 RSI
            rsi = self._calculate_rsi(hist["Close"])
            
            # 計算 MACD
            macd_line, macd_signal, macd_histogram = self._calculate_macd(hist["Close"])
            
            # 計算 KD
            k_value, d_value = self._calculate_kd(hist["Close"])
            
            # 計算移動平均線
            ma_5 = hist["Close"].rolling(window=5).mean().iloc[-1]
            ma_20 = hist["Close"].rolling(window=20).mean().iloc[-1]
            ma_60 = hist["Close"].rolling(window=60).mean().iloc[-1]
            
            # 計算年化報酬率
            if len(hist) >= 252:  # 一年約 252 個交易日
                year_ago_price = hist["Close"].iloc[-252]
                annual_return = ((current_price / year_ago_price) - 1) * 100
            else:
                annual_return = 0
            
            # 獲取成交量
            volume = int(hist["Volume"].iloc[-1]) if not pd.isna(hist["Volume"].iloc[-1]) else 0
            avg_volume = int(hist["Volume"].rolling(window=20).mean().iloc[-1]) if not pd.isna(hist["Volume"].rolling(window=20).mean().iloc[-1]) else 0
            
            # 從 info 中提取基本資料
            dividend_yield = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
            market_cap = info.get("totalAssets", 0) / 1e8 if info.get("totalAssets") else 0  # 轉換為億
            expense_ratio = info.get("annualReportExpenseRatio", 0) * 100 if info.get("annualReportExpenseRatio") else 0
            
            # 計算位階燈號
            signal = self._calculate_signal(rsi, macd_line, macd_signal, k_value, d_value, current_price, ma_20)
            
            result = {
                "symbol": display_symbol,
                "name": info.get("longName", display_symbol),
                "current_price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": volume,
                "avg_volume": avg_volume,
                "dividend_yield": round(dividend_yield, 2),
                "market_cap_billions": round(market_cap, 1),
                "expense_ratio": round(expense_ratio, 3),
                "annual_return": round(annual_return, 2),
                "rsi": round(rsi, 2),
                "macd_line": round(macd_line, 4),
                "macd_signal": round(macd_signal, 4),
                "macd_histogram": round(macd_histogram, 4),
                "k_value": round(k_value, 2),
                "d_value": round(d_value, 2),
                "ma_5": round(ma_5, 2),
                "ma_20": round(ma_20, 2),
                "ma_60": round(ma_60, 2),
                "signal": signal,
                "updated_at": datetime.now().isoformat()
            }
            
            # 設置快取
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"獲取 {symbol} 數據時發生錯誤: {e}")
            return None
    
    def _fetch_etf_batch(self, symbols: List[str]) -> List[Dict]:
        """批次獲取ETF數據"""
        results = []
        for symbol in symbols:
            try:
                data = self.get_etf_data(symbol, timeout=5)
                if data:
                    results.append(data)
            except Exception as e:
                logger.error(f"批次獲取 {symbol} 時發生錯誤: {e}")
        return results
    
    def get_all_etf_data(self, max_workers: int = 6, batch_size: int = 20) -> List[Dict]:
        """並行獲取所有台股 ETF 數據"""
        start_time = time.time()
        etf_data = []
        
        # 將ETF清單分批
        symbol_batches = [
            self.valid_etf_symbols[i:i + batch_size] 
            for i in range(0, len(self.valid_etf_symbols), batch_size)
        ]
        
        logger.info(f"開始並行獲取 {len(self.valid_etf_symbols)} 檔ETF數據，分為 {len(symbol_batches)} 批次")
        
        # 使用線程池並行處理
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有批次任務
            future_to_batch = {
                executor.submit(self._fetch_etf_batch, batch): batch 
                for batch in symbol_batches
            }
            
            # 收集結果
            completed_batches = 0
            for future in concurrent.futures.as_completed(future_to_batch, timeout=25):
                try:
                    batch_results = future.result(timeout=5)
                    etf_data.extend(batch_results)
                    completed_batches += 1
                    logger.info(f"完成第 {completed_batches}/{len(symbol_batches)} 批次，獲得 {len(batch_results)} 檔ETF數據")
                except Exception as e:
                    batch = future_to_batch[future]
                    logger.error(f"批次處理失敗: {batch[:3]}... 錯誤: {e}")
        
        elapsed_time = time.time() - start_time
        logger.info(f"並行獲取完成，總共獲得 {len(etf_data)} 檔ETF數據，耗時 {elapsed_time:.2f} 秒")
        
        return etf_data
    
    def get_market_data(self) -> Dict:
        """獲取市場數據（帶快取）"""
        cache_key = "market_data"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # 獲取台股加權指數
            taiex = yf.Ticker("^TWII")
            taiex_hist = taiex.history(period="3mo", timeout=5)
            
            if not taiex_hist.empty:
                taiex_rsi = self._calculate_rsi(taiex_hist["Close"])
                taiex_price = float(taiex_hist["Close"].iloc[-1])
                taiex_change = float(taiex_hist["Close"].iloc[-1] - taiex_hist["Close"].iloc[-2])
                taiex_change_percent = (taiex_change / taiex_hist["Close"].iloc[-2]) * 100
            else:
                taiex_rsi = 50
                taiex_price = 0
                taiex_change = 0
                taiex_change_percent = 0
            
            # 獲取 VIX 指數
            try:
                vix = yf.Ticker("^VIX")
                vix_hist = vix.history(period="1mo", timeout=5)
                vix_value = float(vix_hist["Close"].iloc[-1]) if not vix_hist.empty else 20
            except:
                vix_value = 20  # 預設值
            
            result = {
                "taiex_price": round(taiex_price, 2),
                "taiex_change": round(taiex_change, 2),
                "taiex_change_percent": round(taiex_change_percent, 2),
                "taiex_rsi": round(taiex_rsi, 2),
                "vix": round(vix_value, 2),
                "economic_indicator": "綠燈",  # 預設值，實際應從政府網站獲取
                "updated_at": datetime.now().isoformat()
            }
            
            # 設置快取
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"獲取市場數據時發生錯誤: {e}")
            return {
                "taiex_price": 0,
                "taiex_change": 0,
                "taiex_change_percent": 0,
                "taiex_rsi": 50,
                "vix": 20,
                "economic_indicator": "綠燈",
                "updated_at": datetime.now().isoformat()
            }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """計算 RSI 指標"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
        except:
            return 50
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """計算 MACD 指標"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            macd_signal = macd_line.ewm(span=signal).mean()
            macd_histogram = macd_line - macd_signal
            
            return (
                float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else 0,
                float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else 0,
                float(macd_histogram.iloc[-1]) if not pd.isna(macd_histogram.iloc[-1]) else 0
            )
        except:
            return (0, 0, 0)
    
    def _calculate_signal(self, rsi: float, macd_line: float, macd_signal: float, 
                         k_value: float, d_value: float, current_price: float, ma_20: float) -> str:
        """計算位階燈號"""
        score = 0
        
        # RSI 評分
        if rsi < 30:
            score += 2  # 超賣，買進機會
        elif rsi < 50:
            score += 1  # 偏弱，可考慮
        elif rsi > 70:
            score -= 2  # 超買，避免
        
        # MACD 評分
        if macd_line > macd_signal and macd_line > 0:
            score += 2  # 強勢
        elif macd_line > macd_signal:
            score += 1  # 轉強
        elif macd_line < macd_signal:
            score -= 1  # 轉弱
        
        # KD 評分
        if k_value < 20 and d_value < 20 and k_value > d_value:
            score += 2  # 低檔黃金交叉，買進機會
        elif k_value < 50 and d_value < 50 and k_value > d_value:
            score += 1  # 偏弱黃金交叉，可考慮
        elif k_value > 80 and d_value > 80 and k_value < d_value:
            score -= 2  # 高檔死亡交叉，避免
        elif k_value > 50 and d_value > 50 and k_value < d_value:
            score -= 1  # 偏強死亡交叉，轉弱

        # 均線評分
        if current_price > ma_20:
            score += 1  # 價格在均線之上
        else:
            score -= 1  # 價格在均線之下
        
        # 根據總分決定燈號
        if score >= 2:
            return "綠燈"
        elif score >= 0:
            return "黃燈"
        else:
            return "紅燈"

    def _calculate_kd(self, prices: pd.Series, period: int = 9) -> Tuple[float, float]:
        """計算 KD 指標"""
        try:
            low_min = prices.rolling(window=period).min()
            high_max = prices.rolling(window=period).max()
            rsv = ((prices - low_min) / (high_max - low_min)) * 100
            
            k_value = rsv.ewm(com=2).mean()
            d_value = k_value.ewm(com=2).mean()
            
            return (
                float(k_value.iloc[-1]) if not pd.isna(k_value.iloc[-1]) else 50,
                float(d_value.iloc[-1]) if not pd.isna(d_value.iloc[-1]) else 50
            )
        except:
            return (50, 50)

