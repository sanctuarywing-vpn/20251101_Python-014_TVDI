"""
股票爬蟲程式 - 快速開始指南

這個檔案提供快速的程式碼片段，方便直接使用
"""

import asyncio
from stock_financial_crawler import SimpleStockCrawler


# ==================== 快速範例 ====================

async def quick_start():
    """最簡單的使用方式"""
    
    # 步驟 1: 建立爬蟲實例
    crawler = SimpleStockCrawler()
    
    # 步驟 2: 準備股票數據
    stock_info = {
        'stock_code': '2330',        # 股票代碼
        'current_price': 940.0,      # 目前股價
        'annual_dividend': 30.0,     # 年度股利
        'past_price': 850.0          # 過去股價
    }
    
    # 步驟 3: 執行爬蟲
    result = await crawler.fetch_stock_info(**stock_info)
    
    # 步驟 4: 顯示結果
    print(f"股票代碼: {result['stock_code']}")
    print(f"殖利率: {result['dividend_yield']}%")
    print(f"年化報酬率: {result['annual_return_rate']}%")


# ==================== 只計算殖利率 ====================

def quick_dividend_yield():
    """快速計算殖利率"""
    crawler = SimpleStockCrawler()
    
    yield_rate = crawler.calculate_dividend_yield(
        annual_dividend=30.0,    # 年度股利
        current_price=940.0      # 目前股價
    )
    
    print(f"殖利率: {yield_rate}%")


# ==================== 只計算年化報酬率 ====================

def quick_return_rate():
    """快速計算年化報酬率"""
    crawler = SimpleStockCrawler()
    
    return_rate = crawler.calculate_annual_return_rate(
        current_price=940.0,     # 目前股價
        past_price=850.0         # 過去股價
    )
    
    print(f"年化報酬率: {return_rate}%")


# ==================== 多支股票比較 ====================

async def quick_compare_stocks():
    """快速比較多支股票"""
    
    crawler = SimpleStockCrawler()
    
    # 定義股票列表
    stocks = {
        '2330': {'current': 940, 'dividend': 30, 'past': 850},
        '2454': {'current': 1100, 'dividend': 25, 'past': 950},
        '1101': {'current': 48, 'dividend': 2.5, 'past': 45},
    }
    
    results = {}
    
    # 計算所有股票
    for code, data in stocks.items():
        result = await crawler.fetch_stock_info(
            stock_code=code,
            current_price=data['current'],
            annual_dividend=data['dividend'],
            past_price=data['past']
        )
        results[code] = result
    
    # 顯示排名
    print("【高殖利率排名】")
    sorted_yield = sorted(results.items(), key=lambda x: x[1]['dividend_yield'], reverse=True)
    for i, (code, data) in enumerate(sorted_yield, 1):
        print(f"{i}. {code}: {data['dividend_yield']}%")
    
    print("\n【高報酬率排名】")
    sorted_return = sorted(results.items(), key=lambda x: x[1]['annual_return_rate'], reverse=True)
    for i, (code, data) in enumerate(sorted_return, 1):
        print(f"{i}. {code}: {data['annual_return_rate']}%")


# ==================== 投資決策 ====================

def quick_investment_decision(dividend_yield, return_rate):
    """快速判斷買賣決策"""
    
    if dividend_yield > 5 and return_rate > 0:
        return "💰 強烈買入"
    elif dividend_yield > 3 and return_rate > 0:
        return "📈 買入"
    elif return_rate > 15:
        return "🚀 高成長"
    elif dividend_yield > 5:
        return "🤔 可考慮"
    else:
        return "⚠️  觀望"


# ==================== 主程式 ====================

if __name__ == "__main__":
    
    print("=" * 60)
    print("股票爬蟲 - 快速開始")
    print("=" * 60)
    
    print("\n【範例 1】基本使用")
    print("-" * 60)
    asyncio.run(quick_start())
    
    print("\n【範例 2】計算殖利率")
    print("-" * 60)
    quick_dividend_yield()
    
    print("\n【範例 3】計算年化報酬率")
    print("-" * 60)
    quick_return_rate()
    
    print("\n【範例 4】多支股票比較")
    print("-" * 60)
    asyncio.run(quick_compare_stocks())
    
    print("\n【範例 5】投資決策")
    print("-" * 60)
    decision = quick_investment_decision(dividend_yield=5.21, return_rate=6.67)
    print(f"決策: {decision}")
