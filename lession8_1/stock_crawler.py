"""
股票資料爬蟲模組

提供股價、殖利率、年化報酬率等資訊爬蟲功能
使用 twstock API 取得台灣股市實時資料
"""

import asyncio
from datetime import datetime
from typing import Dict, Optional, List

# 嘗試匯入 twstock，若未安裝則使用備用方案
try:
    import twstock
    TWSTOCK_AVAILABLE = True
except ImportError:
    TWSTOCK_AVAILABLE = False
    print("警告: twstock 未安裝，部分功能可能不可用")


class StockCrawler:
    """股票爬蟲類別 - 使用 twstock 取得台灣股市資料"""
    
    def __init__(self):
        """初始化爬蟲"""
        self.twstock_client = twstock
    
    def get_current_price(self, stock_code: str) -> Optional[float]:
        """
        取得目前股價
        
        Args:
            stock_code: 股票代碼（例如 '2330'）
        
        Returns:
            當前股價，失敗時返回 None
        """
        try:
            quote = self.twstock_client.get(stock_code)
            if quote and hasattr(quote, 'price'):
                return float(quote.price)
        except Exception as e:
            print(f"✗ 取得 {stock_code} 股價失敗: {e}")
        return None
    
    def get_dividend_yield(self, stock_code: str, current_price: Optional[float] = None) -> Optional[float]:
        """
        計算殖利率 = (最近一年現金股利 / 目前股價) × 100%
        
        Args:
            stock_code: 股票代碼
            current_price: 目前股價（若為 None 則自動取得）
        
        Returns:
            殖利率（百分比），例如 3.25，失敗時返回 None
        """
        try:
            # 若未提供股價，則自動取得
            if current_price is None:
                current_price = self.get_current_price(stock_code)
            
            if not current_price or current_price <= 0:
                return None
            
            # 取得股利資訊
            dividend_info = self.twstock_client.get_dividend(stock_code)
            if dividend_info and isinstance(dividend_info, list):
                total_dividend = 0
                count = 0
                
                # 取最近一年內（4 季）的現金股利
                for div in dividend_info:
                    if count >= 4:  # 最多取 4 筆（一年）
                        break
                    try:
                        cash_div = float(div.get('cash_dividend', 0))
                        if cash_div > 0:
                            total_dividend += cash_div
                        count += 1
                    except (ValueError, TypeError):
                        count += 1
                        continue
                
                if total_dividend > 0:
                    dividend_yield = (total_dividend / current_price) * 100
                    return round(dividend_yield, 2)
        except Exception as e:
            print(f"✗ 取得 {stock_code} 股利資訊失敗: {e}")
        
        return None
    
    def get_annual_return_rate(self, stock_code: str, days: int = 252) -> Optional[float]:
        """
        計算年化報酬率 = (目前價格 - 過去價格) / 過去價格 × 100%
        
        基於過去 252 個交易日（≈ 1 年）的價格變動計算
        
        Args:
            stock_code: 股票代碼
            days: 計算天數（預設 252 交易日 ≈ 1 年）
        
        Returns:
            年化報酬率（百分比），失敗時返回 None
        """
        try:
            # 取得歷史月度收益資訊
            history = self.twstock_client.get_month_revenue(stock_code)
            
            if not history or not isinstance(history, list) or len(history) < 2:
                return None
            
            # 按日期排序（舊到新）
            try:
                sorted_history = sorted(history, key=lambda x: x.date if hasattr(x, 'date') else datetime.now())
            except Exception:
                sorted_history = history
            
            # 確保有足夠的歷史資料
            if len(sorted_history) >= 2:
                try:
                    # 取最新與最舊的價格
                    latest_price = float(sorted_history[-1].close if hasattr(sorted_history[-1], 'close') else sorted_history[-1].get('close', 0))
                    oldest_price = float(sorted_history[0].close if hasattr(sorted_history[0], 'close') else sorted_history[0].get('close', 0))
                    
                    if oldest_price > 0 and latest_price > 0:
                        return_rate = ((latest_price - oldest_price) / oldest_price) * 100
                        return round(return_rate, 2)
                except (ValueError, AttributeError, TypeError):
                    return None
        
        except Exception as e:
            print(f"✗ 取得 {stock_code} 年化報酬率失敗: {e}")
        
        return None
    
    async def fetch_stock_data(self, stock_code: str) -> Dict:
        """
        綜合爬蟲：取得股價、殖利率、年化報酬率
        
        Args:
            stock_code: 股票代碼
        
        Returns:
            包含所有資訊的字典
            {
                'stock_code': str,
                'timestamp': str,
                'current_price': float or None,
                'dividend_yield': float or None,
                'annual_return_rate': float or None,
                'status': 'success' or 'failed'
            }
        """
        result = {
            'stock_code': stock_code,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_price': None,
            'dividend_yield': None,
            'annual_return_rate': None,
            'status': 'failed'
        }
        
        try:
            # 1. 取得目前股價
            current_price = self.get_current_price(stock_code)
            if current_price is None:
                print(f"✗ 無法取得 {stock_code} 的股價")
                return result
            
            result['current_price'] = current_price
            
            # 2. 計算殖利率
            dividend_yield = self.get_dividend_yield(stock_code, current_price)
            result['dividend_yield'] = dividend_yield
            
            # 3. 計算年化報酬率
            annual_return = self.get_annual_return_rate(stock_code)
            result['annual_return_rate'] = annual_return
            
            result['status'] = 'success'
        
        except Exception as e:
            print(f"✗ 股票 {stock_code} 爬蟲發生錯誤: {e}")
        
        return result
    
    async def fetch_multiple_stocks(self, stock_codes: List[str], max_concurrent: int = 5) -> List[Dict]:
        """
        並行爬取多支股票資料
        
        Args:
            stock_codes: 股票代碼列表
            max_concurrent: 最大並行數量
        
        Returns:
            股票資料列表
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(code):
            async with semaphore:
                return await self.fetch_stock_data(code)
        
        tasks = [fetch_with_semaphore(code) for code in stock_codes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 過濾掉異常結果
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
        
        return valid_results


# ==================== 測試程式 ====================

async def test_crawler():
    """測試爬蟲功能"""
    crawler = StockCrawler()
    
    # 定義要監控的股票代碼
    stock_codes = ['2330', '2454']  # 台積電、聯發科
    
    print("=" * 70)
    print("股票資訊爬蟲 - 測試")
    print("=" * 70)
    
    results = await crawler.fetch_multiple_stocks(stock_codes)
    
    for data in results:
        print(f"\n股票代碼: {data['stock_code']}")
        print(f"  狀態: {data['status']}")
        if data['status'] == 'success':
            print(f"  股價: NT${data['current_price']:.2f}" if data['current_price'] else "  股價: N/A")
            print(f"  殖利率: {data['dividend_yield']}%" if data['dividend_yield'] is not None else "  殖利率: N/A")
            print(f"  年化報酬率: {data['annual_return_rate']}%" if data['annual_return_rate'] is not None else "  年化報酬率: N/A")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(test_crawler())
