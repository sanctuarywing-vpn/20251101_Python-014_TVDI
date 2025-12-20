#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
台灣股市監控系統 - 啟動器 v2
支援原始版本和進階版本
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys


def launch_original():
    """啟動原始版本 GUI"""
    try:
        from stock_monitor_gui import main
        main()
    except Exception as e:
        messagebox.showerror("錯誤", f"無法啟動原始版本: {e}")


def launch_advanced():
    """啟動進階版本 GUI"""
    try:
        from stock_monitor_gui_v2 import main
        main()
    except Exception as e:
        messagebox.showerror("錯誤", f"無法啟動進階版本: {e}")


def show_launcher():
    """顯示啟動器選擇菜單"""
    root = tk.Tk()
    root.title("🚀 台灣股市監控系統 - 版本選擇")
    root.geometry("400x300")
    
    # 標題
    title = ttk.Label(
        root,
        text="📊 台灣股市監控系統\n版本選擇",
        font=("Arial", 14, "bold"),
        justify=tk.CENTER
    )
    title.pack(pady=20)
    
    # 版本信息框架
    info_frame = ttk.LabelFrame(root, text="可用版本", padding=10)
    info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 版本 1.0
    v1_frame = ttk.LabelFrame(info_frame, text="版本 1.0 - 標準版", padding=5)
    v1_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(
        v1_frame,
        text="✓ 股票清單搜尋\n✓ 觀察清單管理\n✓ 自動更新機制\n✓ 行業別篩選",
        justify=tk.LEFT,
        font=("Arial", 9)
    ).pack(anchor=tk.W, padx=5, pady=5)
    
    ttk.Button(
        v1_frame,
        text="▶ 啟動標準版",
        command=lambda: [root.destroy(), launch_original()]
    ).pack(fill=tk.X, padx=5, pady=5)
    
    # 版本 2.0
    v2_frame = ttk.LabelFrame(info_frame, text="版本 2.0 - 進階版 (NEW)", padding=5)
    v2_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(
        v2_frame,
        text="✓ 所有標準版功能\n✓ 市場選擇 (台股/美股)\n✓ 市場熱圖 (行業漲跌幅)\n✓ 股票卡片視窗 (流式布局)",
        justify=tk.LEFT,
        font=("Arial", 9),
        foreground="#00AA00"
    ).pack(anchor=tk.W, padx=5, pady=5)
    
    ttk.Button(
        v2_frame,
        text="▶ 啟動進階版 ⭐",
        command=lambda: [root.destroy(), launch_advanced()]
    ).pack(fill=tk.X, padx=5, pady=5)
    
    # 按鈕框架
    button_frame = ttk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    ttk.Button(root, text="退出", command=root.quit).pack(side=tk.RIGHT, padx=5)
    
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "v1":
            launch_original()
        elif sys.argv[1] == "v2":
            launch_advanced()
        else:
            print("用法: python run_v2.py [v1|v2]")
            print("  v1 - 啟動標準版")
            print("  v2 - 啟動進階版")
    else:
        show_launcher()
