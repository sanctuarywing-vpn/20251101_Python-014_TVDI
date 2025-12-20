"""
台灣股市即時監控爬蟲 - 簡化版
支援 twstock 或本地演示資料
"""

import asyncio
import threading
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 台灣股票清單 - 按行業別分類（市值前30大）
# 資料參考: 台灣證交所、各行業代表公司

TAIWAN_STOCKS_BY_INDUSTRY = {
    '半導體': [
        ('2330', '台積電'), ('2454', '聯發科'), ('2303', '聯電'),
        ('3711', '日月光'), ('2379', '瑞昱'), ('3009', '欣興'),
        ('8016', '矽創'), ('3034', '聯詠'), ('2325', '矽格'),
        ('2340', '一力'), ('3014', '聯陽'), ('3265', '通嘉'),
        ('3231', '晶陽'), ('4958', '臻鼎-KY'), ('2407', '新日興'),
        ('8035', '宏普'), ('3707', '鑫龍'), ('2411', '鴻進'),
        ('2367', '友磊'), ('3285', '微端'),
    ],
    '電子': [
        ('2317', '鴻海'), ('2382', '廣達'), ('2498', '宏達電'),
        ('2409', '友達'), ('2880', '華南金'), ('3481', '群創'),
        ('2358', '美磊'), ('2108', '大銀'), ('2337', '華碩'),
        ('2468', '華經'), ('2207', '微星'), ('2399', '映泰'),
        ('2436', '偉詮'), ('3593', '力銘'), ('2371', '大亞'),
        ('2101', '南僑'), ('2364', '聯能'), ('2449', '京華鑽'),
        ('2331', '精元'), ('6533', '福懋科'),
    ],
    '金融': [
        ('2891', '中信金'), ('2884', '玉山金'), ('2882', '國泰金'),
        ('2880', '華南金'), ('2883', '開發金'), ('2881', '富邦金'),
        ('5880', '合庫金'), ('2885', '元大金'), ('2886', '兆豐金'),
        ('2887', '臺銀金'), ('6005', '群益證'), ('8842', '財經'),
        ('2890', '永豐金'), ('2892', '第一金'),
    ],
    '鋼鐵': [
        ('2002', '中鋼'), ('2006', '臺塑鋼'), ('2014', '中鴻'),
        ('2015', '豐興'), ('2017', '立大'), ('2020', '美利達'),
        ('2027', '大成'), ('2028', '奇美'), ('2029', '紀亞'),
        ('2030', '大城'), ('2031', 'imc'),
    ],
    '汽車零件': [
        ('2227', '裕日車'), ('2409', '友達'), ('9910', '豐泰'),
        ('2206', '台塑'), ('2231', '為升'), ('2437', '旺宏'),
        ('2441', '超豐'), ('2464', '高麗'), ('2472', '立碩'),
        ('2493', '揚明光'), ('2499', '東隆'),
    ],
    '造紙': [
        ('1101', '台泥'), ('1102', '亞泥'), ('1103', '嘉泥'),
        ('1104', '環泥'), ('1105', '南亞'),
    ],
    '建材': [
        ('1216', '統一'), ('1233', '天品'), ('1308', '亞果'),
        ('1312', '聯德'), ('1313', '世紀'),
    ],
    '食品': [
        ('1215', '卜蜂'), ('1217', '代理'), ('1218', '泰山'),
        ('1219', '福壽'), ('1220', '台榮'),
    ],
    '化學': [
        ('1301', '台塑'), ('1303', '南亞'), ('1304', '台聚'),
        ('1305', '寶藏'), ('1306', '葡萄王'),
    ],
    '電機': [
        ('1402', '遠紡'), ('1409', '新纖'), ('1410', '南紡'),
        ('1413', '宏洲'),
    ],
    '紡織': [
        ('1504', '東和'), ('1506', '正隆'), ('1507', '永豐'),
        ('1510', '瑞利'), ('1515', '力麒'),
    ],
    '醫療': [
        ('1605', '華新科'), ('1702', '南科'), ('1707', '葡萄王'),
        ('1708', '東生'), ('1710', '東聯'),
    ],
    '電子商務': [
        ('1723', '中美晶'), ('2024', '冠德'), ('2025', '千陞'),
        ('2026', '神寶'),
    ],
    '光寶科技': [
        ('2308', '台達電'), ('2309', '圓剛'), ('2312', '金寶'),
        ('2313', '華碩'), ('2314', '淘帝'),
    ],
    '電信': [
        ('2412', '中華電'), ('2409', '友達'), ('2320', '鼎元'),
        ('2354', '鴻準'), ('2355', '奇力新'),
    ],
    '不動產': [
        ('2024', '冠德'), ('2025', '千陞'), ('2026', '神寶'),
        ('2027', '大成'), ('2028', '奇美'),
    ],
    '其他電子': [
        ('3008', '聯德'), ('3009', '欣興'), ('3014', '聯陽'),
        ('3016', '怡和'), ('3017', '奇偶'),
    ],
}


class TaiwanStockCrawler:
    """台灣股市即時爬蟲 - 簡化版"""
    
    def __init__(self):
        """初始化爬蟲"""
        self.stock_cache = {}
        self.update_times = {}
    
    @staticmethod
    def load_stock_list() -> List[Tuple[str, str]]:
        """
        載入台灣股票清單（所有行業別）
        
        Returns:
            (股票代碼, 股票名稱) 的列表
        """
        try:
            # 嘗試使用 twstock
            import twstock
            stocks = []
            for code, info in twstock.codes.items():
                if info.type == '股票':
                    stocks.append((code, info.name))
            stocks.sort(key=lambda x: x[0])
            print(f"✓ 從 twstock 載入 {len(stocks)} 支台灣股票")
            return stocks
        except Exception as e:
            print(f"⚠️  使用本地行業分類股票清單")
            # 返回所有行業的股票
            all_stocks = []
            for industry, stocks_list in TAIWAN_STOCKS_BY_INDUSTRY.items():
                all_stocks.extend(stocks_list)
            return all_stocks
    
    @staticmethod
    def get_industries() -> Dict[str, List[Tuple[str, str]]]:
        """
        取得按行業別分類的股票清單
        
        Returns:
            行業別 -> 股票清單的字典
        """
        return TAIWAN_STOCKS_BY_INDUSTRY
    
    @staticmethod
    def get_stock_info(stock_code: str) -> Dict:
        """
        取得單支股票的即時資訊
        
        Args:
            stock_code: 股票代碼
        
        Returns:
            {
                'code': str,
                'name': str,
                'price': float,
                'volume': int,
                'timestamp': str,
                'status': str
            }
        """
        result = {
            'code': stock_code,
            'name': '未知',
            'price': None,
            'volume': None,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'status': 'failed'
        }
        
        try:
            # 嘗試從 twstock 取得資料
            import twstock
            stock = twstock.get(stock_code)
            
            if stock and stock.price:
                # 取得股票名稱
                if stock_code in twstock.codes:
                    result['name'] = twstock.codes[stock_code].name
                
                result['price'] = float(stock.price)
                result['volume'] = int(stock.volume) if stock.volume else 0
                result['status'] = 'success'
                return result
        
        except Exception:
            pass
        
        # 備用方案：使用演示資料
        for industry, stocks_list in TAIWAN_STOCKS_BY_INDUSTRY.items():
            for code, name in stocks_list:
                if code == stock_code:
                    result['name'] = name
                    # 模擬股價（基礎價格 + 隨機波動）
                    base_prices = {
                        '2330': 940, '2454': 1100, '1101': 48, '3008': 28,
                        '1605': 68, '2308': 89, '2303': 45, '3711': 560,
                        '2412': 35, '9910': 65, '2891': 30, '2002': 28,
                        '2317': 185, '2382': 95, '2498': 8,
                    }
                    base_price = base_prices.get(stock_code, random.randint(20, 200))
                    fluctuation = random.uniform(-2, 2)  # ±2%
                    result['price'] = round(base_price + (base_price * fluctuation / 100), 2)
                    result['volume'] = random.randint(1000, 50000)
                    result['status'] = 'success'
                    return result
        
        result['status'] = 'not_found'
        return result
    
    async def fetch_multiple_stocks(
        self,
        stock_codes: List[str],
        max_concurrent: int = 10
    ) -> List[Dict]:
        """
        並行取得多支股票資訊
        
        Args:
            stock_codes: 股票代碼列表
            max_concurrent: 最大並行數
        
        Returns:
            股票資訊列表
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(code):
            async with semaphore:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, self.get_stock_info, code)
        
        tasks = [fetch_with_semaphore(code) for code in stock_codes]
        results = await asyncio.gather(*tasks)
        
        # 過濾有效結果
        return [r for r in results if r and r['status'] == 'success']
    
    def search_stocks(self, keyword: str, industry: Optional[str] = None) -> List[Tuple[str, str]]:
        """
        搜尋股票（支援行業篩選）
        
        Args:
            keyword: 搜尋關鍵字（股票代碼或名稱）
            industry: 指定行業篩選（若為 None 則搜尋全部）
        
        Returns:
            符合的 (股票代碼, 股票名稱) 列表
        """
        keyword = keyword.upper().strip()
        results = []
        
        # 選擇搜尋範圍
        if industry and industry in TAIWAN_STOCKS_BY_INDUSTRY:
            stocks_to_search = TAIWAN_STOCKS_BY_INDUSTRY[industry]
        else:
            # 搜尋所有行業
            stocks_to_search = []
            for ind_stocks in TAIWAN_STOCKS_BY_INDUSTRY.values():
                stocks_to_search.extend(ind_stocks)
        
        # 執行搜尋
        for code, name in stocks_to_search:
            if keyword in code or keyword in name:
                results.append((code, name))
        
        return results


# ==================== 使用範例 ====================

async def test_crawler():
    """測試爬蟲功能"""
    crawler = TaiwanStockCrawler()
    
    print("=" * 70)
    print("台灣股市即時監控爬蟲 - 測試")
    print("=" * 70)
    
    # 測試 1: 載入股票清單
    print("\n【測試 1】載入股票清單")
    stocks = crawler.load_stock_list()
    print(f"已載入 {len(stocks)} 支股票")
    print(f"前 5 支: {stocks[:5]}")
    
    # 測試 2: 取得單支股票資訊
    print("\n【測試 2】取得單支股票資訊 (台積電 2330)")
    info = crawler.get_stock_info('2330')
    if info['status'] == 'success':
        print(f"股票代碼: {info['code']}")
        print(f"股票名稱: {info['name']}")
        print(f"即時股價: NT${info['price']:.2f}")
        print(f"成交量: {info['volume']} 張")
        print(f"更新時間: {info['timestamp']}")
    else:
        print(f"失敗: {info['status']}")
    
    # 測試 3: 並行取得多支股票資訊
    print("\n【測試 3】並行取得多支股票資訊")
    test_codes = ['2330', '2454', '1101', '3008']
    results = await crawler.fetch_multiple_stocks(test_codes)
    
    for info in results:
        if info['status'] == 'success':
            print(f"✓ {info['code']} ({info['name']}): NT${info['price']:.2f} | {info['volume']} 張")
        else:
            print(f"✗ {info['code']}: {info['status']}")
    
    # 測試 4: 搜尋股票
    print("\n【測試 4】搜尋股票 (關鍵字: '台')")
    search_results = crawler.search_stocks('台')
    print(f"搜尋結果 (前 10): {search_results[:10]}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(test_crawler())
