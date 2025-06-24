"""
台股 ETF 數據獲取器
負責從各種來源獲取 ETF 和市場數據
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import time
from typing import Dict, List, Optional, Tuple

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """數據獲取器"""
    
    def __init__(self):
        self.taiwan_etf_symbols = [
            # 大盤型 ETF
            '0050.TW', '0051.TW', '006208.TW', '00631L.TW', '00632R.TW',
            # 高股息 ETF  
            '0056.TW', '00878.TW', '00713.TW', '00701.TW', '00730.TW',
            '00731.TW', '00900.TW', '00907.TW', '00918.TW', '00919.TW',
            '00929.TW', '00934.TW', '00936.TW', '00939.TW', '00940.TW',
            # 科技型 ETF
            '00881.TW', '00757.TW', '00762.TW', '00763.TW', '00770.TW',
            '00771.TW', '00876.TW', '00891.TW', '00892.TW', '00896.TW',
            # ESG ETF
            '00692.TW', '00850.TW', '00888.TW', '00895.TW', '00899.TW',
            # 債券型 ETF
            '00679B.TW', '00687B.TW', '00693U.TW', '00694B.TW', '00695B.TW',
            # 國際型 ETF
            '00646.TW', '00647.TW', '00648.TW', '00649.TW', '00652.TW',
            '00653.TW', '00654.TW', '00655.TW', '00656.TW', '00657.TW',
            # 主題型 ETF
            '00735.TW', '00736.TW', '00737.TW', '00738.TW', '00739.TW',
            '00740.TW', '00741.TW', '00742.TW', '00743.TW', '00744.TW'
        ]
        
        self.cache = {}
        self.cache_ttl = {}
        
    def get_taiwan_etf_list(self) -> List[str]:
        """獲取台股 ETF 清單"""
        return self.taiwan_etf_symbols
    
    def get_etf_data(self, symbol: str, period: str = "1y") -> Optional[Dict]:
        """獲取單一 ETF 數據"""
        try:
            # 移除 .TW 後綴進行顯示
            display_symbol = symbol.replace('.TW', '')
            
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
            current_price = float(hist['Close'].iloc[-1])
            prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            change = current_price - prev_price
            change_percent = (change / prev_price) * 100 if prev_price != 0 else 0
            
            # 計算 RSI
            rsi = self._calculate_rsi(hist['Close'])
            
            # 計算 MACD
            macd_line, macd_signal, macd_histogram = self._calculate_macd(hist['Close'])
            
            # 計算移動平均線
            ma_5 = hist['Close'].rolling(window=5).mean().iloc[-1]
            ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            ma_60 = hist['Close'].rolling(window=60).mean().iloc[-1]
            
            # 計算年化報酬率
            if len(hist) >= 252:  # 一年約 252 個交易日
                year_ago_price = hist['Close'].iloc[-252]
                annual_return = ((current_price / year_ago_price) - 1) * 100
            else:
                annual_return = 0
            
            # 獲取成交量
            volume = int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0
            avg_volume = int(hist['Volume'].rolling(window=20).mean().iloc[-1]) if not pd.isna(hist['Volume'].rolling(window=20).mean().iloc[-1]) else 0
            
            # 從 info 中提取基本資料
            dividend_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            market_cap = info.get('totalAssets', 0) / 1e8 if info.get('totalAssets') else 0  # 轉換為億
            expense_ratio = info.get('annualReportExpenseRatio', 0) * 100 if info.get('annualReportExpenseRatio') else 0
            
            # 計算位階燈號
            signal = self._calculate_signal(rsi, macd_line, macd_signal, current_price, ma_20)
            
            return {
                'symbol': display_symbol,
                'name': info.get('longName', display_symbol),
                'current_price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': volume,
                'avg_volume': avg_volume,
                'dividend_yield': round(dividend_yield, 2),
                'market_cap_billions': round(market_cap, 1),
                'expense_ratio': round(expense_ratio, 3),
                'annual_return': round(annual_return, 2),
                'rsi': round(rsi, 2),
                'macd_line': round(macd_line, 4),
                'macd_signal': round(macd_signal, 4),
                'macd_histogram': round(macd_histogram, 4),
                'ma_5': round(ma_5, 2),
                'ma_20': round(ma_20, 2),
                'ma_60': round(ma_60, 2),
                'signal': signal,
                'updated_at': datetime.now().isoformat()
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
            taiex = yf.Ticker('^TWII')
            taiex_hist = taiex.history(period='3mo')
            
            if not taiex_hist.empty:
                taiex_rsi = self._calculate_rsi(taiex_hist['Close'])
                taiex_price = float(taiex_hist['Close'].iloc[-1])
                taiex_change = float(taiex_hist['Close'].iloc[-1] - taiex_hist['Close'].iloc[-2])
                taiex_change_percent = (taiex_change / taiex_hist['Close'].iloc[-2]) * 100
            else:
                taiex_rsi = 50
                taiex_price = 0
                taiex_change = 0
                taiex_change_percent = 0
            
            # 獲取 VIX 指數
            try:
                vix = yf.Ticker('^VIX')
                vix_hist = vix.history(period='1mo')
                vix_value = float(vix_hist['Close'].iloc[-1]) if not vix_hist.empty else 20
            except:
                vix_value = 20  # 預設值
            
            return {
                'taiex_price': round(taiex_price, 2),
                'taiex_change': round(taiex_change, 2),
                'taiex_change_percent': round(taiex_change_percent, 2),
                'taiex_rsi': round(taiex_rsi, 2),
                'vix': round(vix_value, 2),
                'economic_indicator': '綠燈',  # 預設值，實際應從政府網站獲取
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"獲取市場數據時發生錯誤: {e}")
            return {
                'taiex_price': 0,
                'taiex_change': 0,
                'taiex_change_percent': 0,
                'taiex_rsi': 50,
                'vix': 20,
                'economic_indicator': '綠燈',
                'updated_at': datetime.now().isoformat()
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
                         current_price: float, ma_20: float) -> str:
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
        
        # 均線評分
        if current_price > ma_20:
            score += 1  # 價格在均線之上
        else:
            score -= 1  # 價格在均線之下
        
        # 根據總分決定燈號
        if score >= 2:
            return '綠燈'
        elif score >= 0:
            return '黃燈'
        else:
            return '紅燈'

