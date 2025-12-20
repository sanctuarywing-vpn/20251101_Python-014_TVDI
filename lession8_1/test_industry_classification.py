#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
行業分類功能測試指令稿
演示新增的行業別篩選功能
"""

from taiwan_stock_crawler import TaiwanStockCrawler

def main():
    """執行行業分類功能測試"""
    
    print("=" * 70)
    print("台灣股市行業分類功能測試")
    print("=" * 70)
    
    crawler = TaiwanStockCrawler()
    
    # 測試 1: 取得所有行業
    print("\n【測試 1】取得所有行業別")
    print("-" * 70)
    industries = crawler.get_industries()
    print(f"✓ 行業數: {len(industries)}")
    print(f"✓ 行業列表:")
    for i, industry in enumerate(industries.keys(), 1):
        count = len(industries[industry])
        print(f"  {i:2d}. {industry:12s} ({count:2d} 支股票)")
    
    # 測試 2: 查看特定行業的股票
    print("\n【測試 2】查看半導體行業的股票")
    print("-" * 70)
    semiconductor_stocks = industries.get('半導體', [])
    print(f"✓ 半導體行業共 {len(semiconductor_stocks)} 支股票")
    print("前 10 支:")
    for code, name in semiconductor_stocks[:10]:
        print(f"  {code}: {name}")
    if len(semiconductor_stocks) > 10:
        print(f"  ... 及其他 {len(semiconductor_stocks) - 10} 支")
    
    # 測試 3: 行業內搜尋
    print("\n【測試 3】在半導體行業內搜尋「聯」")
    print("-" * 70)
    search_results = crawler.search_stocks('聯', '半導體')
    print(f"✓ 搜尋結果: {len(search_results)} 支")
    for code, name in search_results:
        print(f"  {code}: {name}")
    
    # 測試 4: 全市場搜尋
    print("\n【測試 4】全市場搜尋「台」")
    print("-" * 70)
    all_results = crawler.search_stocks('台', industry=None)
    print(f"✓ 搜尋結果: {len(all_results)} 支")
    print("前 10 支:")
    for code, name in all_results[:10]:
        print(f"  {code}: {name}")
    if len(all_results) > 10:
        print(f"  ... 及其他 {len(all_results) - 10} 支")
    
    # 測試 5: 特定行業篩選
    print("\n【測試 5】查看電子行業的股票")
    print("-" * 70)
    electronic_stocks = industries.get('電子', [])
    print(f"✓ 電子行業共 {len(electronic_stocks)} 支股票")
    for code, name in electronic_stocks[:5]:
        print(f"  {code}: {name}")
    if len(electronic_stocks) > 5:
        print(f"  ... 及其他 {len(electronic_stocks) - 5} 支")
    
    # 測試 6: 統計資訊
    print("\n【測試 6】統計資訊")
    print("-" * 70)
    total_stocks = sum(len(stocks) for stocks in industries.values())
    avg_per_industry = total_stocks / len(industries)
    max_industry = max(industries.items(), key=lambda x: len(x[1]))
    min_industry = min(industries.items(), key=lambda x: len(x[1]))
    
    print(f"✓ 行業總數: {len(industries)}")
    print(f"✓ 股票總數: {total_stocks}")
    print(f"✓ 平均每行業: {avg_per_industry:.1f} 支")
    print(f"✓ 股票最多: {max_industry[0]} ({len(max_industry[1])} 支)")
    print(f"✓ 股票最少: {min_industry[0]} ({len(min_industry[1])} 支)")
    
    # 測試 7: 載入完整股票清單
    print("\n【測試 7】載入完整股票清單")
    print("-" * 70)
    all_stocks = crawler.load_stock_list()
    print(f"✓ 載入成功: {len(all_stocks)} 支股票")
    print("前 10 支:")
    for code, name in all_stocks[:10]:
        print(f"  {code}: {name}")
    
    print("\n" + "=" * 70)
    print("✓ 所有測試完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()

