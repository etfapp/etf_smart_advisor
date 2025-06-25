
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
        return self.taiwan_etf_symbols
    
    def get_etf_data(self, symbol: str, period: str = "1y") -> Optional[Dict]:
        """獲取單一 ETF 數據"""
        try:
            # 移除 .TW 後綴進行顯示
            display_symbol = symbol.replace(".TW", "")
            
            # 使用 yfinance 獲取數據
            ticker = yf.Ticker(symbol)
            
            # 獲取基本資訊
            info = ticker.info
            
            # 獲取歷史價格數據
            hist = ticker.history(period=period)
            
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
            
            return {
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
            
        except Exception as e:
            logger.error(f"獲取 {symbol} 數據時發生錯誤: {e}")
            return None
    
    def get_all_etf_data(self) -> List[Dict]:
        """獲取所有台股 ETF 數據"""
        etf_data = []
        
        for symbol in self.taiwan_etf_symbols:
            data = self.get_etf_data(symbol)
            if data:
                etf_data.append(data)
            time.sleep(0.1)  # 避免請求過於頻繁
        
        logger.info(f"成功獲取 {len(etf_data)} 檔 ETF 數據")
        return etf_data
    
    def get_market_data(self) -> Dict:
        """獲取市場數據"""
        try:
            # 獲取台股加權指數
            taiex = yf.Ticker("^TWII")
            taiex_hist = taiex.history(period="3mo")
            
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
                vix_hist = vix.history(period="1mo")
                vix_value = float(vix_hist["Close"].iloc[-1]) if not vix_hist.empty else 20
            except:
                vix_value = 20  # 預設值
            
            return {
                "taiex_price": round(taiex_price, 2),
                "taiex_change": round(taiex_change, 2),
                "taiex_change_percent": round(taiex_change_percent, 2),
                "taiex_rsi": round(taiex_rsi, 2),
                "vix": round(vix_value, 2),
                "economic_indicator": "綠燈",  # 預設值，實際應從政府網站獲取
                "updated_at": datetime.now().isoformat()
            }
            
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


