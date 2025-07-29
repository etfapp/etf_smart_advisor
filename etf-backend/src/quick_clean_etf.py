#!/usr/bin/env python3
"""
快速ETF清單清理腳本
基於已知的有效ETF清單，快速生成清理後的清單
"""

import json

def create_clean_etf_list():
    """創建清理後的ETF清單"""
    
    # 基於測試結果，這些是確認有效的主流ETF
    clean_etf_list = [
        # 市值型ETF
        {"symbol": "0050", "name": "元大台灣50", "category": "市值型", "suffix": ".TW", "valid": True},
        {"symbol": "0051", "name": "元大中型100", "category": "市值型", "suffix": ".TW", "valid": True},
        {"symbol": "006203", "name": "元大MSCI台灣", "category": "市值型", "suffix": ".TW", "valid": True},
        {"symbol": "006204", "name": "永豐臺灣加權", "category": "市值型", "suffix": ".TW", "valid": True},
        {"symbol": "006208", "name": "富邦台50", "category": "市值型", "suffix": ".TW", "valid": True},
        {"symbol": "00690", "name": "兆豐臺灣藍籌30", "category": "市值型", "suffix": ".TW", "valid": True},
        {"symbol": "00692", "name": "富邦公司治理", "category": "市值型", "suffix": ".TW", "valid": True},
        {"symbol": "00850", "name": "元大臺灣ESG永續", "category": "市值型", "suffix": ".TW", "valid": True},
        {"symbol": "00922", "name": "國泰台灣領袖50", "category": "市值型", "suffix": ".TW", "valid": True},
        {"symbol": "00923", "name": "群益台ESG低碳", "category": "市值型", "suffix": ".TW", "valid": True},
        
        # 高股息ETF
        {"symbol": "0056", "name": "元大高股息", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00701", "name": "國泰股利精選30", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00713", "name": "元大台灣高息低波", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00730", "name": "富邦臺灣優質高息", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00731", "name": "復華富時高息低波", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00878", "name": "國泰永續高股息", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00900", "name": "富邦特選高股息30", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00907", "name": "永豐優息存股", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00915", "name": "凱基優選高股息30", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00918", "name": "大華優利高填息30", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00919", "name": "群益台灣精選高息", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00929", "name": "復華台灣科技優息", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00930", "name": "永豐ESG低碳高息", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00932", "name": "兆豐永續高息等權", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00934", "name": "中信成長高股息", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00936", "name": "台新永續高息中小", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00939", "name": "統一台灣高息動能", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00940", "name": "元大台灣價值高息", "category": "高股息", "suffix": ".TW", "valid": True},
        {"symbol": "00943", "name": "群益台灣半導體收益", "category": "高股息", "suffix": ".TW", "valid": True},
        
        # 科技ETF
        {"symbol": "0052", "name": "富邦科技", "category": "科技", "suffix": ".TW", "valid": True},
        {"symbol": "0053", "name": "元大電子", "category": "科技", "suffix": ".TW", "valid": True},
        {"symbol": "00881", "name": "國泰台灣5G+", "category": "科技", "suffix": ".TW", "valid": True},
        {"symbol": "00891", "name": "中信關鍵半導體", "category": "科技", "suffix": ".TW", "valid": True},
        {"symbol": "00892", "name": "富邦台灣半導體", "category": "科技", "suffix": ".TW", "valid": True},
        {"symbol": "00896", "name": "中信綠能及電動車", "category": "科技", "suffix": ".TW", "valid": True},
        {"symbol": "00904", "name": "新光臺灣半導體30", "category": "科技", "suffix": ".TW", "valid": True},
        {"symbol": "00927", "name": "群益半導體收益", "category": "科技", "suffix": ".TW", "valid": True},
        
        # 金融ETF
        {"symbol": "0055", "name": "元大MSCI金融", "category": "金融", "suffix": ".TW", "valid": True},
        {"symbol": "00941", "name": "中信優選金融", "category": "金融", "suffix": ".TW", "valid": True},
        
        # 中小型ETF
        {"symbol": "00733", "name": "富邦臺灣中小", "category": "中小型", "suffix": ".TW", "valid": True},
        
        # 國外ETF (主要的)
        {"symbol": "0061", "name": "元大寶滬深", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "006205", "name": "富邦上証", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "006206", "name": "元大上證50", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "006207", "name": "復華滬深", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00636", "name": "國泰中國A50", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00639", "name": "富邦深100", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00643", "name": "群益深証中小", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00645", "name": "富邦日本", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00646", "name": "元大S&P500", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00652", "name": "富邦印度", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00657", "name": "國泰日經225", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00660", "name": "元大歐洲50", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00661", "name": "元大日經225", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00662", "name": "富邦NASDAQ", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00668", "name": "國泰美國道瓊", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00678", "name": "群益那斯達克生技", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00709", "name": "元大MSCI印度", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00712", "name": "復華富時不動產", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00714", "name": "群益道瓊美國地產", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00717", "name": "富邦美國特別股", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00737", "name": "國泰納斯達克100", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00757", "name": "統一FANG+", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00830", "name": "國泰費城半導體", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00832", "name": "國泰ChinaAMC中證500", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00833", "name": "國泰ChinaAMC滬深300", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00845", "name": "富邦越南", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00846", "name": "元大全球人工智慧", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00847", "name": "永豐美國500大", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00848", "name": "元大全球5G", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00851", "name": "元大全球AI", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00852", "name": "中信中國50", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00853", "name": "群益全球關鍵生技", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00854", "name": "國泰全球品牌50", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00855", "name": "國泰富時中國A50", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00856", "name": "國泰全球智能電動車", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00857", "name": "統一全球新科技", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00858", "name": "富邦全球ESG綠色電力", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00859", "name": "永豐全球優質龍頭", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00875", "name": "國泰網路資安", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00886", "name": "兆豐全球半導體", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00888", "name": "永豐全球不動產", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00889", "name": "復華全球原物料", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00894", "name": "中信小資高價30", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00895", "name": "富邦未來車", "category": "國外", "suffix": ".TW", "valid": True},
        {"symbol": "00897", "name": "群益全球清潔能源", "category": "國外", "suffix": ".TW", "valid": True},
        
        # 槓桿型ETF (主要的)
        {"symbol": "00631L", "name": "元大台灣50正2", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00632R", "name": "元大台灣50反1", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00633L", "name": "富邦上証正2", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00634R", "name": "富邦上証反1", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00647L", "name": "元大S&P500正2", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00648R", "name": "元大S&P500反1", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00663L", "name": "國泰臺灣加權正2", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00664R", "name": "國泰臺灣加權反1", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00670L", "name": "富邦NASDAQ正2", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00671R", "name": "富邦NASDAQ反1", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00675L", "name": "富邦臺灣加權正2", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00676R", "name": "富邦臺灣加權反1", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00685L", "name": "群益臺灣加權正2", "category": "槓桿型", "suffix": ".TW", "valid": True},
        {"symbol": "00686R", "name": "群益臺灣加權反1", "category": "槓桿型", "suffix": ".TW", "valid": True},
        
        # 期貨ETF
        {"symbol": "00635U", "name": "元大S&P黃金", "category": "期貨", "suffix": ".TW", "valid": True},
        {"symbol": "00642U", "name": "元大S&P石油", "category": "期貨", "suffix": ".TW", "valid": True},
        {"symbol": "00673R", "name": "元大S&P原油反1", "category": "期貨", "suffix": ".TW", "valid": True},
        {"symbol": "00674R", "name": "元大S&P黃金反1", "category": "期貨", "suffix": ".TW", "valid": True},
        {"symbol": "00682U", "name": "元大美元指數", "category": "期貨", "suffix": ".TW", "valid": True},
        {"symbol": "00683L", "name": "元大美元指正2", "category": "期貨", "suffix": ".TW", "valid": True},
        {"symbol": "00684R", "name": "元大美元指反1", "category": "期貨", "suffix": ".TW", "valid": True},
        {"symbol": "00693U", "name": "街口S&P黃豆", "category": "期貨", "suffix": ".TW", "valid": True},
    ]
    
    # 按symbol排序
    clean_etf_list.sort(key=lambda x: x['symbol'])
    
    # 保存清理後的清單
    with open('verified_etf_list_cleaned.json', 'w', encoding='utf-8') as f:
        json.dump(clean_etf_list, f, ensure_ascii=False, indent=2)
    
    print(f"已創建清理後的ETF清單，包含 {len(clean_etf_list)} 檔ETF")
    print("清單已保存到 verified_etf_list_cleaned.json")
    
    # 統計各類別數量
    categories = {}
    for etf in clean_etf_list:
        category = etf['category']
        categories[category] = categories.get(category, 0) + 1
    
    print("\n各類別ETF數量:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}檔")
    
    return clean_etf_list

if __name__ == "__main__":
    create_clean_etf_list()

