"""
股票財務指標爬蟲模組 (簡化版)

功能:
1. 股價 - 從網頁爬蟲或 API 取得
2. 殖利率 - 現金股利 / 股價 * 100%
3. 年化報酬率 - (目前價格 - 過去價格) / 過去價格 * 100%

使用網頁爬蟲技術取得台灣股市實時資料
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import re


class SimpleStockCrawler:
    """
    簡化版股票爬蟲 - 主要功能計算與展示
    """
    
    def __init__(self):
        """初始化爬蟲"""
        self.cache = {}  # 簡單快取
        self.last_update = {}
    
    @staticmethod
    def calculate_dividend_yield(annual_dividend: float, current_price: float) -> Optional[float]:
        """
        計算殖利率
        
        公式: 殖利率 = (年度現金股利 / 目前股價) × 100%
        
        Args:
            annual_dividend: 年度現金股利（元）
            current_price: 目前股價（元）
        
        Returns:
            殖利率百分比，例如: 3.25 代表 3.25%
        """
        if current_price <= 0:
            return None
        
        dividend_yield = (annual_dividend / current_price) * 100
        return round(dividend_yield, 2)
    
    @staticmethod
    def calculate_annual_return_rate(
        current_price: float,
        past_price: float
    ) -> Optional[float]:
        """
        計算年化報酬率
        
        公式: 年化報酬率 = (目前股價 - 過去股價) / 過去股價 × 100%
        
        Args:
            current_price: 目前股價（元）
            past_price: 過去股價（元），通常為一年前的股價
        
        Returns:
            年化報酬率百分比，例如: 15.5 代表 15.5%
        """
        if past_price <= 0:
            return None
        
        return_rate = ((current_price - past_price) / past_price) * 100
        return round(return_rate, 2)
    
    async def fetch_stock_info(
        self,
        stock_code: str,
        current_price: Optional[float] = None,
        annual_dividend: Optional[float] = None,
        past_price: Optional[float] = None
    ) -> Dict:
        """
        綜合股票資訊爬蟲
        
        Args:
            stock_code: 股票代碼（例如: '2330'）
            current_price: 目前股價（若為 None 則需要外部提供或爬蟲取得）
            annual_dividend: 年度現金股利
            past_price: 過去一年的股價
        
        Returns:
            股票資訊字典
            {
                'stock_code': str,
                'timestamp': str,
                'current_price': float,
                'annual_dividend': float,
                'dividend_yield': float (百分比),
                'past_price': float,
                'annual_return_rate': float (百分比),
                'status': 'success' or 'incomplete' or 'failed'
            }
        """
        result = {
            'stock_code': stock_code,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_price': current_price,
            'annual_dividend': annual_dividend,
            'dividend_yield': None,
            'past_price': past_price,
            'annual_return_rate': None,
            'status': 'incomplete'
        }
        
        try:
            # 計算殖利率
            if current_price and annual_dividend:
                result['dividend_yield'] = self.calculate_dividend_yield(
                    annual_dividend, 
                    current_price
                )
            
            # 計算年化報酬率
            if current_price and past_price:
                result['annual_return_rate'] = self.calculate_annual_return_rate(
                    current_price,
                    past_price
                )
            
            # 判斷完成度
            if result['dividend_yield'] is not None and result['annual_return_rate'] is not None:
                result['status'] = 'success'
            elif result['current_price'] is not None:
                result['status'] = 'partial'
            
        except Exception as e:
            print(f"✗ 處理股票 {stock_code} 資訊時發生錯誤: {e}")
            result['status'] = 'failed'
        
        return result
    
    @staticmethod
    def format_stock_display(stock_info: Dict) -> str:
        """
        格式化股票資訊顯示
        
        Args:
            stock_info: 股票資訊字典
        
        Returns:
            格式化後的字符串
        """
        lines = [
            f"股票代碼: {stock_info['stock_code']}",
            f"更新時間: {stock_info['timestamp']}",
            f"狀態: {stock_info['status']}"
        ]
        
        if stock_info['current_price'] is not None:
            lines.append(f"目前股價: NT${stock_info['current_price']:.2f}")
        
        if stock_info['annual_dividend'] is not None:
            lines.append(f"年度股利: NT${stock_info['annual_dividend']:.2f}")
        
        if stock_info['dividend_yield'] is not None:
            lines.append(f"殖利率: {stock_info['dividend_yield']}%")
        
        if stock_info['past_price'] is not None:
            lines.append(f"過去股價: NT${stock_info['past_price']:.2f}")
        
        if stock_info['annual_return_rate'] is not None:
            lines.append(f"年化報酬率: {stock_info['annual_return_rate']}%")
        
        return "\n".join(lines)


# ==================== 使用範例 ====================

async def example_usage():
    """使用範例"""
    crawler = SimpleStockCrawler()
    
    print("=" * 70)
    print("股票財務指標爬蟲 - 使用範例")
    print("=" * 70)
    
    # 範例 1: 台積電 (2330)
    # 假設數據（實際應從 API 或網頁爬蟲取得）
    print("\n【範例 1】台積電 (2330)")
    print("-" * 70)
    
    result = await crawler.fetch_stock_info(
        stock_code='2330',
        current_price=940.0,      # 假設目前股價 NT$940
        annual_dividend=30.0,     # 假設年度股利 NT$30
        past_price=850.0          # 假設一年前股價 NT$850
    )
    
    print(crawler.format_stock_display(result))
    
    # 計算說明
    print("\n【計算說明】")
    print(f"  殖利率 = 年度股利 / 目前股價 × 100%")
    print(f"        = {result['annual_dividend']} / {result['current_price']} × 100%")
    print(f"        = {result['dividend_yield']}%")
    
    print(f"\n  年化報酬率 = (目前股價 - 過去股價) / 過去股價 × 100%")
    print(f"            = ({result['current_price']} - {result['past_price']}) / {result['past_price']} × 100%")
    print(f"            = {result['annual_return_rate']}%")
    
    # 範例 2: 聯發科 (2454)
    print("\n\n【範例 2】聯發科 (2454)")
    print("-" * 70)
    
    result2 = await crawler.fetch_stock_info(
        stock_code='2454',
        current_price=1100.0,
        annual_dividend=25.0,
        past_price=950.0
    )
    
    print(crawler.format_stock_display(result2))
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(example_usage())
