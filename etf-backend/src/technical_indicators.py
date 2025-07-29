"""
真實技術指標計算模組
提供RSI、MACD、移動平均線等技術指標的計算
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """技術指標計算器"""
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """計算RSI指標"""
        try:
            if len(prices) < period + 1:
                return 50.0  # 數據不足時返回中性值
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        except Exception as e:
            logger.warning(f"RSI計算錯誤: {e}")
            return 50.0
    
    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """計算MACD指標"""
        try:
            if len(prices) < slow + signal:
                return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}
            
            exp1 = prices.ewm(span=fast).mean()
            exp2 = prices.ewm(span=slow).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=signal).mean()
            histogram = macd - signal_line
            
            return {
                'macd': float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 0.0,
                'signal': float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else 0.0,
                'histogram': float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else 0.0
            }
        except Exception as e:
            logger.warning(f"MACD計算錯誤: {e}")
            return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}
    
    @staticmethod
    def calculate_moving_averages(prices: pd.Series) -> Dict[str, float]:
        """計算移動平均線"""
        try:
            ma5 = prices.rolling(window=5).mean().iloc[-1] if len(prices) >= 5 else prices.iloc[-1]
            ma10 = prices.rolling(window=10).mean().iloc[-1] if len(prices) >= 10 else prices.iloc[-1]
            ma20 = prices.rolling(window=20).mean().iloc[-1] if len(prices) >= 20 else prices.iloc[-1]
            ma50 = prices.rolling(window=50).mean().iloc[-1] if len(prices) >= 50 else prices.iloc[-1]
            
            current_price = prices.iloc[-1]
            
            return {
                'ma5': float(ma5) if not pd.isna(ma5) else float(current_price),
                'ma10': float(ma10) if not pd.isna(ma10) else float(current_price),
                'ma20': float(ma20) if not pd.isna(ma20) else float(current_price),
                'ma50': float(ma50) if not pd.isna(ma50) else float(current_price),
                'current_price': float(current_price)
            }
        except Exception as e:
            logger.warning(f"移動平均線計算錯誤: {e}")
            current_price = float(prices.iloc[-1]) if len(prices) > 0 else 50.0
            return {
                'ma5': current_price,
                'ma10': current_price,
                'ma20': current_price,
                'ma50': current_price,
                'current_price': current_price
            }
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """計算布林通道"""
        try:
            if len(prices) < period:
                current_price = float(prices.iloc[-1])
                return {
                    'upper': current_price * 1.02,
                    'middle': current_price,
                    'lower': current_price * 0.98,
                    'bandwidth': 4.0
                }
            
            middle = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper = middle + (std * std_dev)
            lower = middle - (std * std_dev)
            
            current_middle = float(middle.iloc[-1]) if not pd.isna(middle.iloc[-1]) else float(prices.iloc[-1])
            current_upper = float(upper.iloc[-1]) if not pd.isna(upper.iloc[-1]) else current_middle * 1.02
            current_lower = float(lower.iloc[-1]) if not pd.isna(lower.iloc[-1]) else current_middle * 0.98
            
            bandwidth = ((current_upper - current_lower) / current_middle) * 100
            
            return {
                'upper': current_upper,
                'middle': current_middle,
                'lower': current_lower,
                'bandwidth': bandwidth
            }
        except Exception as e:
            logger.warning(f"布林通道計算錯誤: {e}")
            current_price = float(prices.iloc[-1]) if len(prices) > 0 else 50.0
            return {
                'upper': current_price * 1.02,
                'middle': current_price,
                'lower': current_price * 0.98,
                'bandwidth': 4.0
            }
    
    @staticmethod
    def calculate_volume_indicators(prices: pd.Series, volumes: pd.Series) -> Dict[str, float]:
        """計算成交量指標"""
        try:
            if len(volumes) == 0:
                return {
                    'avg_volume_10': 1000000,
                    'avg_volume_30': 1000000,
                    'volume_ratio': 1.0,
                    'price_volume_trend': 0.0
                }
            
            current_volume = float(volumes.iloc[-1]) if not pd.isna(volumes.iloc[-1]) else 1000000
            avg_volume_10 = float(volumes.rolling(window=10).mean().iloc[-1]) if len(volumes) >= 10 else current_volume
            avg_volume_30 = float(volumes.rolling(window=30).mean().iloc[-1]) if len(volumes) >= 30 else current_volume
            
            volume_ratio = current_volume / avg_volume_10 if avg_volume_10 > 0 else 1.0
            
            # 計算價量趨勢
            if len(prices) >= 2 and len(volumes) >= 2:
                price_change = (prices.iloc[-1] - prices.iloc[-2]) / prices.iloc[-2]
                volume_change = (volumes.iloc[-1] - volumes.iloc[-2]) / volumes.iloc[-2] if volumes.iloc[-2] > 0 else 0
                price_volume_trend = price_change * volume_change
            else:
                price_volume_trend = 0.0
            
            return {
                'avg_volume_10': avg_volume_10,
                'avg_volume_30': avg_volume_30,
                'volume_ratio': volume_ratio,
                'price_volume_trend': price_volume_trend
            }
        except Exception as e:
            logger.warning(f"成交量指標計算錯誤: {e}")
            return {
                'avg_volume_10': 1000000,
                'avg_volume_30': 1000000,
                'volume_ratio': 1.0,
                'price_volume_trend': 0.0
            }
    
    @staticmethod
    def calculate_price_levels(prices: pd.Series) -> Dict[str, float]:
        """計算價格水位"""
        try:
            if len(prices) < 5:
                current_price = float(prices.iloc[-1])
                return {
                    'price_52w_high': current_price * 1.2,
                    'price_52w_low': current_price * 0.8,
                    'price_percentile': 50.0,
                    'support_level': current_price * 0.95,
                    'resistance_level': current_price * 1.05
                }
            
            current_price = float(prices.iloc[-1])
            
            # 計算52週高低價（如果數據不足252天，使用現有數據）
            price_52w_high = float(prices.max())
            price_52w_low = float(prices.min())
            
            # 計算價格在區間的位置
            if price_52w_high == price_52w_low:
                price_percentile = 50.0
            else:
                price_percentile = ((current_price - price_52w_low) / (price_52w_high - price_52w_low)) * 100
            
            # 計算支撐和阻力位（基於近期高低點）
            recent_prices = prices.tail(20) if len(prices) >= 20 else prices
            support_level = float(recent_prices.min())
            resistance_level = float(recent_prices.max())
            
            return {
                'price_52w_high': price_52w_high,
                'price_52w_low': price_52w_low,
                'price_percentile': price_percentile,
                'support_level': support_level,
                'resistance_level': resistance_level
            }
        except Exception as e:
            logger.warning(f"價格水位計算錯誤: {e}")
            current_price = float(prices.iloc[-1]) if len(prices) > 0 else 50.0
            return {
                'price_52w_high': current_price * 1.2,
                'price_52w_low': current_price * 0.8,
                'price_percentile': 50.0,
                'support_level': current_price * 0.95,
                'resistance_level': current_price * 1.05
            }
    
    @classmethod
    def calculate_all_indicators(cls, hist_data: pd.DataFrame) -> Dict:
        """計算所有技術指標"""
        try:
            if hist_data.empty:
                return cls._get_default_indicators()
            
            prices = hist_data['Close']
            volumes = hist_data['Volume'] if 'Volume' in hist_data.columns else pd.Series([1000000] * len(hist_data))
            
            # 計算各種技術指標
            rsi = cls.calculate_rsi(prices)
            macd = cls.calculate_macd(prices)
            ma = cls.calculate_moving_averages(prices)
            bb = cls.calculate_bollinger_bands(prices)
            volume_indicators = cls.calculate_volume_indicators(prices, volumes)
            price_levels = cls.calculate_price_levels(prices)
            
            return {
                'rsi': rsi,
                'macd': macd,
                'moving_averages': ma,
                'bollinger_bands': bb,
                'volume_indicators': volume_indicators,
                'price_levels': price_levels,
                'current_price': float(prices.iloc[-1]),
                'data_points': len(hist_data)
            }
        except Exception as e:
            logger.error(f"技術指標計算錯誤: {e}")
            return cls._get_default_indicators()
    
    @staticmethod
    def _get_default_indicators() -> Dict:
        """獲取默認技術指標值"""
        return {
            'rsi': 50.0,
            'macd': {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0},
            'moving_averages': {
                'ma5': 50.0, 'ma10': 50.0, 'ma20': 50.0, 'ma50': 50.0, 'current_price': 50.0
            },
            'bollinger_bands': {
                'upper': 51.0, 'middle': 50.0, 'lower': 49.0, 'bandwidth': 4.0
            },
            'volume_indicators': {
                'avg_volume_10': 1000000, 'avg_volume_30': 1000000, 
                'volume_ratio': 1.0, 'price_volume_trend': 0.0
            },
            'price_levels': {
                'price_52w_high': 60.0, 'price_52w_low': 40.0, 'price_percentile': 50.0,
                'support_level': 47.5, 'resistance_level': 52.5
            },
            'current_price': 50.0,
            'data_points': 0
        }

