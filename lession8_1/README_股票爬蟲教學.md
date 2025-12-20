# 股票爬蟲程式完整教學指南

## 📚 目錄
1. [基本概念](#基本概念)
2. [程式結構](#程式結構)
3. [核心功能說明](#核心功能說明)
4. [使用指南](#使用指南)
5. [進階應用](#進階應用)

---

## 基本概念

### 三大關鍵指標

本教學重點教授如何爬蟲與計算三個重要的股票投資指標：

#### 1️⃣ **股價 (Current Price)**
- **定義**: 股票目前的成交價格
- **用途**: 基礎參考，用於計算其他指標
- **單位**: 新台幣（NT$）
- **例子**: 台積電 (2330) 股價 NT$940

#### 2️⃣ **殖利率 (Dividend Yield)**
- **公式**: 
  ```
  殖利率 (%) = (年度現金股利 / 目前股價) × 100%
  ```
- **用途**: 評估股票產生現金流的能力
- **解讀**: 
  - 殖利率 > 5% 通常被認為是高殖利率
  - 越高表示股票相對便宜或公司派息慷慨
- **例子**: 
  - 股價 $940，年度股利 $30
  - 殖利率 = 30 / 940 × 100% = **3.19%**

#### 3️⃣ **年化報酬率 (Annual Return Rate)**
- **公式**:
  ```
  年化報酬率 (%) = (目前股價 - 過去股價) / 過去股價 × 100%
  ```
- **用途**: 評估股票價格漲跌幅度
- **解讀**:
  - 正數表示上漲，負數表示下跌
  - 用於評估短期或長期的資本利得
- **例子**:
  - 過去股價 $850，目前股價 $940
  - 年化報酬率 = (940 - 850) / 850 × 100% = **10.59%**

---

## 程式結構

### 📁 檔案組織

```
lession8_1/
├── stock_financial_crawler.py    # 核心爬蟲模組 ⭐
├── stock_crawler_tutorial.py     # 完整教程與範例
├── main.py                        # GUI 應用程式
├── lession8_1_1.py               # 基礎爬蟲示例
├── lession8_1_2.py               # 進階爬蟲示例
├── lession8_1_3.py               # 實踐練習
└── plan.md                        # 學習計畫
```

### 🔧 核心模組: `stock_financial_crawler.py`

#### 主要類別
```python
class SimpleStockCrawler:
    def get_current_price(stock_code) -> float
    def get_dividend_yield(stock_code, current_price) -> float
    def get_annual_return_rate(stock_code, past_price) -> float
    def fetch_stock_info(stock_code, current_price, annual_dividend, past_price) -> Dict
    def format_stock_display(stock_info) -> str
```

---

## 核心功能說明

### 功能 1: 計算殖利率

```python
from stock_financial_crawler import SimpleStockCrawler

crawler = SimpleStockCrawler()

# 計算殖利率
yield_rate = crawler.calculate_dividend_yield(
    annual_dividend=30.0,   # 年度現金股利
    current_price=940.0     # 目前股價
)
print(f"殖利率: {yield_rate}%")  # 輸出: 3.19%
```

**計算步驟**:
1. 取得年度現金股利（通常在除息後公告）
2. 取得目前股票價格
3. 代入公式: 股利 ÷ 股價 × 100%

### 功能 2: 計算年化報酬率

```python
# 計算年化報酬率
return_rate = crawler.calculate_annual_return_rate(
    current_price=940.0,   # 目前股價
    past_price=850.0       # 過去（一年前）股價
)
print(f"年化報酬率: {return_rate}%")  # 輸出: 10.59%
```

**計算步驟**:
1. 取得目前股價
2. 取得過去股價（通常為一年前的股價）
3. 代入公式: (目前 - 過去) ÷ 過去 × 100%

### 功能 3: 綜合股票資訊爬蟲

```python
# 一次性取得所有資訊
stock_info = await crawler.fetch_stock_info(
    stock_code='2330',
    current_price=940.0,
    annual_dividend=30.0,
    past_price=850.0
)

print(crawler.format_stock_display(stock_info))
# 輸出:
# 股票代碼: 2330
# 目前股價: NT$940.00
# 年度股利: NT$30.00
# 殖利率: 3.19%
# 過去股價: NT$850.00
# 年化報酬率: 10.59%
```

---

## 使用指南

### 基本使用 (範例 1)

**場景**: 快速查詢單支股票的指標

```bash
# 執行基本範例
python stock_financial_crawler.py
```

**程式碼**:
```python
import asyncio
from stock_financial_crawler import SimpleStockCrawler

async def main():
    crawler = SimpleStockCrawler()
    
    result = await crawler.fetch_stock_info(
        stock_code='2330',
        current_price=940.0,
        annual_dividend=30.0,
        past_price=850.0
    )
    
    print(f"殖利率: {result['dividend_yield']}%")
    print(f"年化報酬率: {result['annual_return_rate']}%")

asyncio.run(main())
```

### 批量爬蟲 (範例 2)

**場景**: 同時監控多支股票

```python
# 在 stock_crawler_tutorial.py 中執行
python stock_crawler_tutorial.py

# 或自己編寫:
async def crawl_multiple():
    crawler = SimpleStockCrawler()
    
    stocks = [
        {'code': '2330', 'current_price': 940, 'annual_dividend': 30, 'past_price': 850},
        {'code': '2454', 'current_price': 1100, 'annual_dividend': 25, 'past_price': 950},
    ]
    
    results = []
    for stock in stocks:
        result = await crawler.fetch_stock_info(**stock)
        results.append(result)
    
    return results
```

### 數據分析 (範例 3)

**場景**: 找出最佳投資標的

```python
# 找出高殖利率股票
sorted_by_yield = sorted(
    results,
    key=lambda x: x['dividend_yield'],
    reverse=True
)

print("高殖利率股票 TOP 3:")
for i, stock in enumerate(sorted_by_yield[:3], 1):
    print(f"{i}. {stock['stock_code']}: {stock['dividend_yield']}%")
```

### 數據導出 (範例 4)

**場景**: 保存爬蟲結果供後續分析

```python
import csv
import json

# 導出為 CSV
with open('stocks.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['stock_code', 'dividend_yield', 'annual_return_rate'])
    writer.writeheader()
    writer.writerows(results)

# 導出為 JSON
with open('stocks.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

---

## 進階應用

### 🎯 應用 1: GUI 監控應用 (main.py)

已整合到 Tkinter GUI 應用中，可實時監控多支股票的指標。

```bash
python main.py
```

**功能**:
- 👀 實時監控多支股票
- 🔄 手動/自動更新
- 💾 數據快取

### 🎯 應用 2: 投資決策系統

```python
def investment_decision(stock_info):
    """根據指標給出投資建議"""
    
    yield_rate = stock_info['dividend_yield']
    return_rate = stock_info['annual_return_rate']
    
    if yield_rate > 5 and return_rate > 0:
        return "💰 強烈買入 (高殖利率 + 上漲)"
    elif yield_rate > 3 and return_rate > 0:
        return "📈 買入 (殖利率良好 + 上漲)"
    elif yield_rate > 5:
        return "🤔 可以考慮 (高殖利率但下跌)"
    elif return_rate > 15:
        return "🚀 高成長 (但缺乏現金流)"
    else:
        return "⚠️  觀望 (指標不理想)"
```

### 🎯 應用 3: 實時 API 整合

將本模組與實時股價 API 結合：

```python
# 從 API 取得即時數據
import requests

def get_stock_price_from_api(stock_code):
    """從 API 取得股價"""
    # 例: 使用台灣股市資料 API
    # response = requests.get(f"https://api.twstock.tw/stock/{stock_code}")
    # return response.json()['price']
    pass

# 然後傳入爬蟲計算
result = await crawler.fetch_stock_info(
    stock_code='2330',
    current_price=get_stock_price_from_api('2330'),
    annual_dividend=get_dividend_from_api('2330'),
    past_price=get_past_price_from_api('2330')
)
```

---

## 📊 計算示例表

| 股票 | 股價 | 年度股利 | 殖利率 | 過去股價 | 年化報酬率 | 建議 |
|------|------|--------|--------|---------|----------|------|
| 2330 (台積電) | 940 | 30 | 3.19% | 850 | 10.59% | 📈 買入 |
| 2454 (聯發科) | 1100 | 25 | 2.27% | 950 | 15.79% | 🚀 高成長 |
| 1101 (台泥) | 48 | 2.5 | 5.21% | 45 | 6.67% | 💰 買入 |
| 3008 (聯德) | 28 | 1.8 | 6.43% | 26 | 7.69% | 💰 買入 |

---

## 🛠️ 常見問題 (FAQ)

### Q1: 如何取得實時股價和股利資訊？

**A**: 可使用以下資料來源:
- `twstock` 模組 (台灣股市)
- 台灣證交所官網 API
- 金融資訊網站 (嗎哪、Yahoo 財經)
- 自行爬蟲 (使用 BeautifulSoup, Selenium 等)

### Q2: 殖利率多少才合理？

**A**: 
- 基準: 無風險利率 (定存利率) ≈ 1-2%
- 保守: 3-4%
- 中等: 4-6%
- 積極: > 6%

### Q3: 年化報酬率如何預測未來走勢？

**A**: 
- 過去績效 ≠ 未來表現
- 應結合技術面、基本面分析
- 建議搭配其他指標使用

### Q4: 如何自動更新數據？

**A**: 使用 `schedule` 或 `APScheduler` 庫:
```python
import schedule
import time

def job():
    # 執行爬蟲任務
    pass

schedule.every(1).hours.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

---

## 📚 進一步學習

### 相關主題
- 技術分析指標 (MA, RSI, MACD)
- 基本面分析 (PE, PB 比率)
- 投資組合優化
- 風險管理

### 推薦資源
- 台灣期貨交易所教育中心
- 證券櫃檯買賣中心投資人教育
- Python 量化交易框架 (vnpy, backtrader)

---

## 📝 學習檢查清單

- [ ] 理解股價、殖利率、年化報酬率的計算公式
- [ ] 能獨立編寫股票爬蟲程式
- [ ] 能進行多支股票的批量分析
- [ ] 能將爬蟲結果導出為 CSV/JSON
- [ ] 能整合到自己的投資決策系統
- [ ] 能使用 API 取得實時數據

---

## 作者備註

本教學旨在提供股票爬蟲的基礎概念與實作能力。

**免責聲明**: 本資料僅供教育用途，不構成投資建議。投資前請自行研究，並諮詢專業理財顧問。

**最後更新**: 2025-12-20

---

祝學習愉快！🎓
