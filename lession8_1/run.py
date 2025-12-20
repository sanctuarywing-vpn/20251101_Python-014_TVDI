"""
台灣股市即時監控 GUI - 快速啟動腳本

這個檔案提供簡單的方式啟動應用
"""

import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from stock_monitor_gui import main
    print("=" * 70)
    print("📊 台灣股市即時監控 GUI")
    print("=" * 70)
    print("\n正在啟動應用...")
    print("\n功能:")
    print("  • 搜尋和監控台灣股票")
    print("  • 自動每分鐘更新股票資訊")
    print("  • 顯示: 股票代碼、名稱、股價、成交量、更新時間")
    print("  • 自動保存觀察清單設定")
    print("\n提示:")
    print("  • 雙擊股票快速加入觀察清單")
    print("  • 右鍵點擊觀察清單快速移除")
    print("  • 勾選『自動更新』啟用定時更新")
    print("\n" + "=" * 70 + "\n")
    
    main()

except ImportError as e:
    print(f"❌ 錯誤: 無法載入必要模組 ({e})")
    print("\n請確保以下檔案存在:")
    print("  • stock_monitor_gui.py")
    print("  • taiwan_stock_crawler.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ 應用啟動失敗: {e}")
    sys.exit(1)
