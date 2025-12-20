"""
股票財務指標完整教程與應用示例

這個程式展示如何使用 stock_financial_crawler 模組
計算股票的股價、殖利率和年化報酬率

主要內容：
1. 基本使用 - 單支股票資料爬蟲
2. 批量爬蟲 - 多支股票並行處理
3. 數據分析 - 對比多支股票指標
4. 存檔導出 - 將結果保存為 CSV/JSON
"""

import asyncio
import csv
import json
from datetime import datetime
from typing import List, Dict
from stock_financial_crawler import SimpleStockCrawler


# ==================== 範例 1: 基本單支股票爬蟲 ====================

async def example_1_single_stock():
    """
    範例 1: 爬蟲單支股票的財務指標
    
    使用場景：
    - 快速查詢某支股票的股價、殖利率、報酬率
    - 手動輸入股票資訊進行計算
    """
    print("=" * 80)
    print("【範例 1】基本單支股票爬蟲")
    print("=" * 80)
    
    crawler = SimpleStockCrawler()
    
    # 台積電 (2330) - 範例數據
    result = await crawler.fetch_stock_info(
        stock_code='2330',
        current_price=940.0,
        annual_dividend=30.0,
        past_price=850.0
    )
    
    print(f"\n股票代碼: {result['stock_code']}")
    print(f"目前股價: NT${result['current_price']:.2f}")
    print(f"年度股利: NT${result['annual_dividend']:.2f}")
    print(f"殖利率: {result['dividend_yield']}%")
    print(f"過去股價: NT${result['past_price']:.2f}")
    print(f"年化報酬率: {result['annual_return_rate']}%")
    
    return result


# ==================== 範例 2: 批量多支股票爬蟲 ====================

async def example_2_multiple_stocks():
    """
    範例 2: 並行爬蟲多支股票
    
    使用場景：
    - 監控多支股票的即時指標
    - 進行投資組合分析
    - 比較不同股票的表現
    """
    print("\n" + "=" * 80)
    print("【範例 2】批量多支股票爬蟲")
    print("=" * 80)
    
    crawler = SimpleStockCrawler()
    
    # 定義多支股票的資料（實際應從 API 或網頁爬蟲取得）
    stocks_data = [
        {
            'code': '2330',
            'name': '台積電',
            'current_price': 940.0,
            'annual_dividend': 30.0,
            'past_price': 850.0
        },
        {
            'code': '2454',
            'name': '聯發科',
            'current_price': 1100.0,
            'annual_dividend': 25.0,
            'past_price': 950.0
        },
        {
            'code': '1101',
            'name': '台泥',
            'current_price': 48.0,
            'annual_dividend': 2.5,
            'past_price': 45.0
        },
        {
            'code': '3008',
            'name': '聯德',
            'current_price': 28.0,
            'annual_dividend': 1.8,
            'past_price': 26.0
        }
    ]
    
    results = []
    
    print(f"\n正在爬蟲 {len(stocks_data)} 支股票...\n")
    
    for stock in stocks_data:
        result = await crawler.fetch_stock_info(
            stock_code=stock['code'],
            current_price=stock['current_price'],
            annual_dividend=stock['annual_dividend'],
            past_price=stock['past_price']
        )
        results.append(result)
        
        # 顯示簡要資訊
        print(f"✓ {stock['code']} ({stock['name']})")
        print(f"  股價: NT${result['current_price']:.2f} | " +
              f"殖利率: {result['dividend_yield']}% | " +
              f"年報: {result['annual_return_rate']}%")
    
    return results


# ==================== 範例 3: 數據分析與比較 ====================

async def example_3_data_analysis(results: List[Dict]):
    """
    範例 3: 對爬蟲結果進行分析與比較
    
    使用場景：
    - 找出高殖利率股票
    - 找出高報酬率股票
    - 建立投資決策指標
    """
    print("\n" + "=" * 80)
    print("【範例 3】數據分析與比較")
    print("=" * 80)
    
    # 過濾有效資料
    valid_results = [r for r in results if r['status'] == 'success']
    
    if not valid_results:
        print("沒有有效的數據")
        return
    
    print("\n【殖利率排序】（高到低）")
    print("-" * 80)
    sorted_by_yield = sorted(
        valid_results,
        key=lambda x: x['dividend_yield'] if x['dividend_yield'] else 0,
        reverse=True
    )
    for i, r in enumerate(sorted_by_yield, 1):
        print(f"{i}. {r['stock_code']}: {r['dividend_yield']}%")
    
    print("\n【年化報酬率排序】（高到低）")
    print("-" * 80)
    sorted_by_return = sorted(
        valid_results,
        key=lambda x: x['annual_return_rate'] if x['annual_return_rate'] else 0,
        reverse=True
    )
    for i, r in enumerate(sorted_by_return, 1):
        print(f"{i}. {r['stock_code']}: {r['annual_return_rate']}%")
    
    # 計算平均值
    avg_yield = sum(r['dividend_yield'] for r in valid_results if r['dividend_yield']) / len([r for r in valid_results if r['dividend_yield']])
    avg_return = sum(r['annual_return_rate'] for r in valid_results if r['annual_return_rate']) / len([r for r in valid_results if r['annual_return_rate']])
    
    print("\n【統計數據】")
    print("-" * 80)
    print(f"平均殖利率: {avg_yield:.2f}%")
    print(f"平均年化報酬率: {avg_return:.2f}%")


# ==================== 範例 4: 數據存檔導出 ====================

async def example_4_export_data(results: List[Dict]):
    """
    範例 4: 將爬蟲結果導出為 CSV 和 JSON 格式
    
    使用場景：
    - 建立股票投資資料庫
    - 進行長期監控與分析
    - 與其他工具整合
    """
    print("\n" + "=" * 80)
    print("【範例 4】數據存檔導出")
    print("=" * 80)
    
    # 導出為 CSV
    csv_filename = f"stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    print(f"\n正在導出 CSV: {csv_filename}")
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                'stock_code', 'timestamp', 'current_price',
                'annual_dividend', 'dividend_yield',
                'past_price', 'annual_return_rate', 'status'
            ]
        )
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"✓ CSV 檔案已保存: {csv_filename}")
    
    # 導出為 JSON
    json_filename = f"stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print(f"正在導出 JSON: {json_filename}")
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✓ JSON 檔案已保存: {json_filename}")


# ==================== 範例 5: 互動式命令列界面 ====================

async def example_5_interactive_cli():
    """
    範例 5: 互動式命令列程式
    
    使用場景：
    - 實時查詢股票指標
    - 教學與演示
    - 快速驗證數據
    """
    print("\n" + "=" * 80)
    print("【範例 5】互動式命令列界面")
    print("=" * 80)
    
    crawler = SimpleStockCrawler()
    
    print("\n歡迎使用股票財務指標查詢工具")
    print("指令: 'add' 新增股票 | 'list' 顯示清單 | 'analyze' 分析 | 'exit' 退出")
    
    stocks = {}
    
    while True:
        cmd = input("\n請輸入指令: ").strip().lower()
        
        if cmd == 'exit':
            print("謝謝使用，再見！")
            break
        
        elif cmd == 'add':
            code = input("股票代碼 (例: 2330): ").strip()
            try:
                current_price = float(input("目前股價 (元): "))
                annual_dividend = float(input("年度股利 (元): "))
                past_price = float(input("過去股價 (元): "))
                
                result = await crawler.fetch_stock_info(
                    stock_code=code,
                    current_price=current_price,
                    annual_dividend=annual_dividend,
                    past_price=past_price
                )
                stocks[code] = result
                print(f"✓ 已新增股票 {code}")
            except ValueError:
                print("✗ 輸入格式錯誤")
        
        elif cmd == 'list':
            if not stocks:
                print("尚未新增任何股票")
            else:
                for code, data in stocks.items():
                    print(f"\n{code}:")
                    print(crawler.format_stock_display(data))
        
        elif cmd == 'analyze':
            if stocks:
                results = list(stocks.values())
                await example_3_data_analysis(results)
            else:
                print("請先新增股票")


# ==================== 主程式 ====================

async def main():
    """執行所有範例"""
    
    # 範例 1: 單支股票
    await example_1_single_stock()
    
    # 範例 2: 多支股票
    results = await example_2_multiple_stocks()
    
    # 範例 3: 數據分析
    await example_3_data_analysis(results)
    
    # 範例 4: 數據導出
    await example_4_export_data(results)
    
    # 範例 5: 互動式 CLI（可選）
    # 取消下行註釋即可體驗互動模式
    # await example_5_interactive_cli()
    
    print("\n" + "=" * 80)
    print("所有範例執行完畢！")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
