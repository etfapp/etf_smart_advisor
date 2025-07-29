#!/usr/bin/env python3
"""
ETF清單清理腳本
移除重複項目，清理無效ETF，補充遺漏的主流ETF
"""

import json
import yfinance as yf
from collections import defaultdict
import time

def load_etf_list():
    """載入原始ETF清單"""
    with open('verified_etf_list.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def remove_duplicates(etf_list):
    """移除重複項目，保留最完整的記錄"""
    # 按symbol分組
    grouped = defaultdict(list)
    for etf in etf_list:
        grouped[etf['symbol']].append(etf)
    
    cleaned_list = []
    for symbol, etfs in grouped.items():
        if len(etfs) == 1:
            cleaned_list.append(etfs[0])
        else:
            # 選擇最完整的記錄（有更多字段的）
            best_etf = max(etfs, key=lambda x: len(x))
            # 合併類別信息
            categories = set()
            for etf in etfs:
                if 'category' in etf:
                    categories.add(etf['category'])
            
            if categories:
                best_etf['category'] = list(categories)[0]  # 取第一個類別
                if len(categories) > 1:
                    best_etf['additional_categories'] = list(categories)[1:]
            
            cleaned_list.append(best_etf)
    
    return cleaned_list

def validate_etf_data(symbol):
    """驗證ETF是否能獲取數據"""
    try:
        # 嘗試不同的後綴
        suffixes = ['.TW', '.TWO']
        for suffix in suffixes:
            ticker_symbol = f"{symbol}{suffix}"
            ticker = yf.Ticker(ticker_symbol)
            
            # 嘗試獲取基本信息
            info = ticker.info
            if info and 'regularMarketPrice' in info:
                return True, suffix
            
            # 嘗試獲取歷史數據
            hist = ticker.history(period='5d')
            if not hist.empty:
                return True, suffix
        
        return False, None
    except Exception as e:
        print(f"驗證 {symbol} 時發生錯誤: {e}")
        return False, None

def add_missing_etfs():
    """補充遺漏的主流ETF"""
    missing_etfs = [
        # 高股息ETF
        {"symbol": "00919", "name": "群益台灣精選高息", "category": "高股息"},
        {"symbol": "00929", "name": "復華台灣科技優息", "category": "高股息"},
        {"symbol": "00934", "name": "中信成長高股息", "category": "高股息"},
        {"symbol": "00936", "name": "台新永續高息中小", "category": "高股息"},
        {"symbol": "00940", "name": "元大台灣價值高息", "category": "高股息"},
        
        # 科技ETF
        {"symbol": "00891", "name": "中信關鍵半導體", "category": "科技"},
        {"symbol": "00892", "name": "富邦台灣半導體", "category": "科技"},
        {"symbol": "00904", "name": "新光臺灣半導體30", "category": "科技"},
        
        # ESG ETF
        {"symbol": "00850", "name": "元大臺灣ESG永續", "category": "ESG"},
        {"symbol": "00922", "name": "國泰台灣領袖50", "category": "ESG"},
        {"symbol": "00923", "name": "群益台ESG低碳", "category": "ESG"},
        
        # 市值型ETF
        {"symbol": "00690", "name": "兆豐臺灣藍籌30", "category": "市值型"},
        {"symbol": "00692", "name": "富邦公司治理", "category": "市值型"},
    ]
    
    return missing_etfs

def clean_etf_list():
    """主要清理函數"""
    print("開始清理ETF清單...")
    
    # 1. 載入原始清單
    original_list = load_etf_list()
    print(f"原始ETF數量: {len(original_list)}")
    
    # 2. 移除重複項目
    cleaned_list = remove_duplicates(original_list)
    print(f"移除重複後ETF數量: {len(cleaned_list)}")
    
    # 3. 驗證ETF數據可用性
    print("驗證ETF數據可用性...")
    valid_etfs = []
    invalid_etfs = []
    
    for i, etf in enumerate(cleaned_list):
        print(f"驗證 {i+1}/{len(cleaned_list)}: {etf['symbol']}")
        is_valid, suffix = validate_etf_data(etf['symbol'])
        
        if is_valid:
            etf['suffix'] = suffix
            etf['valid'] = True
            valid_etfs.append(etf)
        else:
            etf['valid'] = False
            invalid_etfs.append(etf)
        
        # 避免過於頻繁的API調用
        time.sleep(0.1)
    
    print(f"有效ETF數量: {len(valid_etfs)}")
    print(f"無效ETF數量: {len(invalid_etfs)}")
    
    # 4. 補充遺漏的主流ETF
    missing_etfs = add_missing_etfs()
    print(f"補充ETF數量: {len(missing_etfs)}")
    
    # 驗證補充的ETF
    for etf in missing_etfs:
        is_valid, suffix = validate_etf_data(etf['symbol'])
        if is_valid:
            etf['suffix'] = suffix
            etf['valid'] = True
            # 檢查是否已存在
            if not any(e['symbol'] == etf['symbol'] for e in valid_etfs):
                valid_etfs.append(etf)
    
    # 5. 保存清理後的清單
    final_list = sorted(valid_etfs, key=lambda x: x['symbol'])
    
    with open('verified_etf_list_cleaned.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
    
    # 6. 保存無效ETF清單供參考
    with open('invalid_etf_list.json', 'w', encoding='utf-8') as f:
        json.dump(invalid_etfs, f, ensure_ascii=False, indent=2)
    
    print(f"清理完成！最終有效ETF數量: {len(final_list)}")
    print("清理後的清單已保存到 verified_etf_list_cleaned.json")
    print("無效ETF清單已保存到 invalid_etf_list.json")
    
    return final_list, invalid_etfs

if __name__ == "__main__":
    clean_etf_list()

