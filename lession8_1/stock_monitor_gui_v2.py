#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
台灣股市即時監控 GUI 應用 - 進階版本 (v2.0)

新增功能:
1. 市場選擇 (台股、美股)
2. 市場熱圖 (行業漲跌幅)
3. 股票卡片視窗 (流式布局，自動重排)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import random
from taiwan_stock_crawler import TaiwanStockCrawler


class StockCardFrame(ttk.Frame):
    """股票卡片 Frame"""
    
    def __init__(self, parent, code: str, name: str, price: float = 0, 
                 volume: int = 0, change_pct: float = 0, timestamp: str = "", 
                 on_remove=None):
        """初始化卡片"""
        super().__init__(parent, relief=tk.RAISED, borderwidth=2)
        
        self.code = code
        self.name = name
        self.on_remove = on_remove
        
        # 顏色設定 (上漲綠色、下跌紅色)
        color = "#00AA00" if change_pct >= 0 else "#AA0000"
        bg_color = "#F0F0F0"
        
        self.config(padding=10)
        
        # 標題欄 - 代碼 + 名稱 + 關閉按鈕
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(title_frame, text=f"{code}", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        ttk.Label(title_frame, text=f" {name}", font=("Arial", 10)).pack(side=tk.LEFT)
        
        if on_remove:
            ttk.Button(title_frame, text="✕", width=2, command=on_remove).pack(side=tk.RIGHT)
        
        # 股價顯示
        price_frame = ttk.Frame(self)
        price_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(price_frame, text="NT$", font=("Arial", 9)).pack(side=tk.LEFT)
        price_label = ttk.Label(
            price_frame, 
            text=f"{price:.2f}" if isinstance(price, (int, float)) else str(price),
            font=("Arial", 14, "bold"),
            foreground=color
        )
        price_label.pack(side=tk.LEFT, padx=5)
        
        # 漲跌幅
        if isinstance(change_pct, (int, float)):
            change_text = f"{change_pct:+.2f}%"
        else:
            change_text = str(change_pct)
        
        change_label = ttk.Label(
            price_frame,
            text=change_text,
            font=("Arial", 10, "bold"),
            foreground=color
        )
        change_label.pack(side=tk.LEFT)
        
        # 成交量
        volume_frame = ttk.Frame(self)
        volume_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(volume_frame, text="成交量:", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Label(
            volume_frame,
            text=f"{volume:,}" if isinstance(volume, int) else str(volume),
            font=("Arial", 8)
        ).pack(side=tk.LEFT, padx=5)
        
        # 更新時間
        time_frame = ttk.Frame(self)
        time_frame.pack(fill=tk.X, pady=(3, 0))
        
        ttk.Label(
            time_frame,
            text=timestamp if timestamp else "等待更新",
            font=("Arial", 7),
            foreground="gray"
        ).pack(side=tk.LEFT)


class HeatmapFrame(ttk.Frame):
    """市場熱圖框架"""
    
    def __init__(self, parent):
        """初始化熱圖"""
        super().__init__(parent, relief=tk.SUNKEN, borderwidth=1)
        
        # 標題
        title = ttk.Label(self, text="📊 市場熱圖 (行業漲跌幅)", font=("Arial", 10, "bold"))
        title.pack(fill=tk.X, padx=5, pady=5)
        
        # 內容框架 (自動重排)
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置自動換行
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.industry_labels: Dict[str, Dict] = {}
    
    def update_data(self, industry_data: Dict[str, float]):
        """更新熱圖資料"""
        # 清空舊標籤
        for label_info in self.industry_labels.values():
            label_info['widget'].destroy()
        self.industry_labels.clear()
        
        # 建立新標籤
        row = 0
        col = 0
        for industry, change_pct in sorted(industry_data.items()):
            # 顏色: 綠色(上漲) 紅色(下跌) 灰色(平盤)
            if change_pct > 0:
                color = "#00AA00"
                text = f"↑ {change_pct:+.2f}%"
            elif change_pct < 0:
                color = "#AA0000"
                text = f"↓ {change_pct:+.2f}%"
            else:
                color = "#666666"
                text = f"→ {change_pct:+.2f}%"
            
            # 建立行業標籤
            frame = ttk.Frame(self.content_frame, relief=tk.SUNKEN, borderwidth=1)
            frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            
            ttk.Label(frame, text=industry, font=("Arial", 8)).pack(padx=3, pady=2)
            ttk.Label(
                frame,
                text=text,
                font=("Arial", 9, "bold"),
                foreground=color
            ).pack(padx=3, pady=2)
            
            self.industry_labels[industry] = {'widget': frame, 'change': change_pct}
            
            col += 1
            if col >= 4:  # 每行 4 個行業
                col = 0
                row += 1
            
            self.content_frame.grid_rowconfigure(row, weight=1)
            self.content_frame.grid_columnconfigure(col, weight=1)

    def update_stock_heatmap(self, stocks: List[Dict]):
        """以股票清單更新熱圖（顯示個股的漲跌與市值排序）

        stocks: List of dicts with keys: code, name, change_pct, market_cap
        """
        # 清空舊標籤
        for label_info in self.industry_labels.values():
            label_info['widget'].destroy()
        self.industry_labels.clear()

        # 將股票按 market_cap 排序（遞減）並建立方塊
        stocks_sorted = sorted(stocks, key=lambda x: x.get('market_cap', 0), reverse=True)

        row = 0
        col = 0
        # 每行顯示 5 支股票（寬度考量）
        per_row = 5
        for s in stocks_sorted:
            code = s.get('code', '')
            name = s.get('name', '')
            change_pct = s.get('change_pct', 0.0)
            mcap = s.get('market_cap', 0)

            if change_pct > 0:
                color = "#00AA00"
                text = f"{change_pct:+.2f}%"
            elif change_pct < 0:
                color = "#AA0000"
                text = f"{change_pct:+.2f}%"
            else:
                color = "#666666"
                text = f"{change_pct:+.2f}%"

            frame = ttk.Frame(self.content_frame, relief=tk.SUNKEN, borderwidth=1)
            frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

            ttk.Label(frame, text=f"{code} {name}", font=("Arial", 8)).pack(padx=3, pady=2)
            ttk.Label(frame, text=text, font=("Arial", 9, "bold"), foreground=color).pack(padx=3, pady=2)
            ttk.Label(frame, text=f"市值: {int(mcap):,}", font=("Arial", 7), foreground="gray").pack(padx=3, pady=2)

            self.industry_labels[f"{code}"] = {'widget': frame, 'change': change_pct}

            col += 1
            if col >= per_row:
                col = 0
                row += 1

            self.content_frame.grid_rowconfigure(row, weight=1)
            self.content_frame.grid_columnconfigure(col, weight=1)


class StockMonitorGUIv2:
    """股票監控 GUI 應用 - 進階版本"""
    
    def __init__(self, root: tk.Tk):
        """初始化應用"""
        self.root = root
        self.root.title("📊 台灣股市即時監控 - 進階版")
        self.root.geometry("1400x800")
        
        # 爬蟲實例
        self.crawler = TaiwanStockCrawler()
        
        # 市場選擇 (目前支援台股，為未來擴展預留美股)
        self.markets = {
            '台股': {'symbol': 'TW', 'stocks': []},
            '美股': {'symbol': 'US', 'stocks': []},  # 未來功能
        }
        self.current_market = '台股'
        
        # 股票清單
        self.all_stocks: List[Tuple[str, str]] = []
        self.watchlist: Set[str] = set()
        
        # 股票資料快取
        self.stock_data_cache: Dict[str, Dict] = {}
        
        # 行業漲跌幅資料
        self.industry_changes: Dict[str, float] = {}
        
        # 自動更新
        self.auto_update_enabled = False
        self.update_timer = None
        
        # 設定檔路徑
        self.watchlist_file = "watchlist_v2.json"
        
        # 建立 UI
        self.setup_ui()
        
        # 載入股票清單
        self.load_stocks_in_background()
        
        # 載入觀察清單
        self.load_watchlist()
        
        # 綁定關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 綁定視窗大小變更事件
        self.root.bind('<Configure>', self.on_window_resize)
    
    def setup_ui(self):
        """建立使用者介面"""
        # 主容器 - 上下分割
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 工具列
        self.setup_toolbar(main_frame)
        
        # 內容區域 - 左右分割
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左側面板
        left_paned = ttk.PanedWindow(content_frame, orient=tk.VERTICAL)
        left_paned.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        
        # 股票清單面板
        self.setup_left_panel(left_paned)
        
        # 熱圖面板
        self.heatmap_frame = HeatmapFrame(left_paned)
        left_paned.add(self.heatmap_frame)
        
        # 右側面板 - 股票卡片容器
        right_frame = ttk.LabelFrame(content_frame, text="👁️ 觀察中的股票", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 建立可滾動的卡片容器
        self.setup_watchlist_panel(right_frame)
    
    def setup_toolbar(self, parent):
        """建立工具列"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=5)
        
        # 市場選擇
        ttk.Label(toolbar, text="📍 市場:").pack(side=tk.LEFT, padx=5)
        self.market_var = tk.StringVar(value='台股')
        market_combo = ttk.Combobox(
            toolbar,
            textvariable=self.market_var,
            values=['台股', '美股'],
            state="readonly",
            width=10
        )
        market_combo.pack(side=tk.LEFT, padx=5)
        market_combo.bind("<<ComboboxSelected>>", self.on_market_changed)
        
        # 狀態標籤
        ttk.Label(toolbar, text="狀態:").pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(toolbar, text="載入中...", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 分隔符
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 更新按鈕
        ttk.Button(toolbar, text="🔄 立即更新", command=self.manual_update).pack(side=tk.LEFT, padx=5)
        
        # 自動更新開關
        self.auto_update_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            toolbar,
            text="自動更新 (每分鐘)",
            variable=self.auto_update_var,
            command=self.toggle_auto_update
        ).pack(side=tk.LEFT, padx=5)
        
        # 最後更新時間
        self.update_time_label = ttk.Label(toolbar, text="")
        self.update_time_label.pack(side=tk.RIGHT, padx=5)
    
    def setup_left_panel(self, parent):
        """建立左側股票清單面板"""
        left_frame = ttk.LabelFrame(parent, text="📈 股票清單", padding=5)
        parent.add(left_frame)
        
        # 行業別篩選框
        industry_frame = ttk.Frame(left_frame)
        industry_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(industry_frame, text="🏭 行業別:").pack(side=tk.LEFT, padx=5)
        self.industry_var = tk.StringVar(value="全部")
        self.industry_combo = ttk.Combobox(
            industry_frame,
            textvariable=self.industry_var,
            state="readonly",
            width=15
        )
        self.industry_combo.pack(side=tk.LEFT, padx=5)
        self.industry_combo.bind("<<ComboboxSelected>>", self.on_industry_changed)
        
        # 搜尋框
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="🔍 搜尋:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 股票列表 (Treeview)
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.stock_tree = ttk.Treeview(
            tree_frame,
            columns=('code', 'name'),
            height=15,
            yscrollcommand=scrollbar.set
        )
        self.stock_tree.column('#0', width=0, stretch=tk.NO)
        self.stock_tree.column('code', anchor=tk.W, width=60)
        self.stock_tree.column('name', anchor=tk.W, width=100)
        self.stock_tree.heading('code', text='代碼')
        self.stock_tree.heading('name', text='名稱')
        self.stock_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.stock_tree.yview)
        
        # 雙擊加入觀察
        self.stock_tree.bind('<Double-Button-1>', self.on_stock_double_click)
        
        # 加入按鈕
        ttk.Button(
            left_frame,
            text="➕ 加入觀察清單",
            command=self.add_to_watchlist
        ).pack(fill=tk.X, pady=5)
    
    def setup_watchlist_panel(self, parent):
        """建立觀察清單面板 - 卡片流式布局"""
        # 建立可滾動框架
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas 用於滾動
        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.cards_frame = ttk.Frame(self.canvas, relief=tk.FLAT)
        
        self.cards_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 綁定滾輪事件
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)  # Linux
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)  # Linux
        
        # 儲存卡片 widgets
        self.card_widgets: Dict[str, tk.Widget] = {}
    
    def on_mousewheel(self, event):
        """處理滾輪事件"""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
    
    def on_window_resize(self, event=None):
        """視窗大小變更時，重新排列卡片"""
        self.layout_cards()
    
    def layout_cards(self):
        """重新排列卡片布局"""
        if not hasattr(self, 'cards_frame'):
            return
        
        # 清空現有佈局
        for widget in list(self.cards_frame.winfo_children()):
            widget.pack_forget()
        
        # 計算每行卡片數量
        frame_width = self.cards_frame.winfo_width()
        card_width = 220  # 每張卡片約 220px
        cards_per_row = max(1, frame_width // card_width)
        
        # 重新排列卡片
        current_row_frame = None
        cards_in_row = 0
        
        for code in sorted(self.watchlist):
            if cards_in_row == 0:
                current_row_frame = ttk.Frame(self.cards_frame)
                current_row_frame.pack(fill=tk.X, pady=5)
            
            if code in self.card_widgets:
                self.card_widgets[code].pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=False)
                cards_in_row += 1
                
                if cards_in_row >= cards_per_row:
                    cards_in_row = 0
    
    def refresh_stock_list(self):
        """刷新股票清單顯示"""
        # 清空
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        # 取得選中的行業
        selected_industry = self.industry_var.get()

        # 若選擇行業，則顯示該行業市值前 10 支股票；若為全部，顯示全市場（或全部清單）
        industries_dict = self.crawler.get_industries()
        search_text = self.search_var.get().lower()

        stocks_to_display: List[Tuple[str, str]] = []
        if selected_industry == "全部":
            # 取得全市場股票（可能較多）---我們先使用 all_stocks
            stocks_to_display = self.all_stocks
        else:
            if selected_industry in industries_dict:
                # 先取得該行業所有股票，再排序取前 10（依市值）
                ind_list = industries_dict[selected_industry]
                # 計算市值（同步快速估算）
                mcap_list = self.compute_market_caps_for_list(ind_list)
                # 取市值前 10
                top10 = [ (it['code'], it['name']) for it in sorted(mcap_list, key=lambda x: x.get('market_cap',0), reverse=True)[:10] ]
                stocks_to_display = top10

        # 搜尋篩選並填充 Treeview
        for code, name in stocks_to_display:
            if search_text in code.lower() or search_text in name.lower():
                self.stock_tree.insert('', 'end', values=(code, name))
    
    def load_stocks_in_background(self):
        """在背景線程載入股票清單"""
        def load_task():
            try:
                self.all_stocks = self.crawler.load_stock_list()
                
                # 建立行業列表
                industries = list(self.crawler.get_industries().keys())
                industries.insert(0, "全部")
                self.root.after(0, lambda: self.industry_combo.config(values=industries))
                self.root.after(0, lambda: self.industry_combo.set("全部"))
                
                self.root.after(0, self.refresh_stock_list)
                self.root.after(0, lambda: self.status_label.config(text="就緒", foreground="green"))
                
                # 初始化行業熱圖資料
                self.initialize_heatmap()
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("錯誤", f"載入失敗: {e}"))
        
        thread = threading.Thread(target=load_task, daemon=True)
        thread.start()
    
    def initialize_heatmap(self):
        """初始化熱圖資料"""
        industries = self.crawler.get_industries()
        for industry in industries.keys():
            # 模擬行業漲跌幅
            self.industry_changes[industry] = round(random.uniform(-5, 5), 2)
        # 根據目前選擇更新熱圖（預設以市值/行業顯示個股熱圖）
        self.root.after(0, self.update_heatmap_by_selection)

    def compute_market_caps_for_list(self, stocks: List[Tuple[str, str]]) -> List[Dict]:
        """給定 (code, name) 的股票列表，回傳含 market_cap 與隨機 change_pct 的字典列表。

        注意: 若爬蟲不提供市值，這裡會使用簡單的估算（價格 * 模擬流通股數）。
        此方法同步執行，若資料量大請在背景執行。
        """
        results = []
        for code, name in stocks:
            info = self.crawler.get_stock_info(code)
            price = info.get('price') or 0.0
            volume = info.get('volume') or 0

            # 模擬流通股數（若有真實數據可替換）
            # 使用固定或隨機值以便排序穩定
            outstanding = random.randint(50_000_000, 5_000_000_000)
            market_cap = price * outstanding

            change_pct = round(random.uniform(-5, 5), 2)

            results.append({
                'code': code,
                'name': name,
                'price': price,
                'volume': volume,
                'market_cap': market_cap,
                'change_pct': change_pct,
            })

        return results

    def build_market_toplist(self, industry: Optional[str] = None, top_n: int = 10) -> List[Dict]:
        """建立依市值排序的前 N 支股票列表。

        如果 industry 為 None 或 '全部'，則全市場聚合；否則僅該行業。
        返回: List of dicts (code,name,market_cap,change_pct)
        """
        industries = self.crawler.get_industries()
        stocks_pool: List[Tuple[str, str]] = []
        if not industry or industry == '全部':
            # 聚合所有行業
            for ind_list in industries.values():
                stocks_pool.extend(ind_list)
        else:
            stocks_pool = industries.get(industry, [])

        mcap_list = self.compute_market_caps_for_list(stocks_pool)
        mcap_sorted = sorted(mcap_list, key=lambda x: x.get('market_cap', 0), reverse=True)
        return mcap_sorted[:top_n]

    def update_heatmap_by_selection(self):
        """依當前市場與行業選擇，更新熱圖顯示（股票熱圖或行業熱圖）。"""
        selected_industry = self.industry_var.get()
        if selected_industry == '全部' or not selected_industry:
            # 全市場：顯示依市值排序的個股熱圖（前 30）
            top_stocks = self.build_market_toplist(industry=None, top_n=30)
            self.root.after(0, lambda: self.heatmap_frame.update_stock_heatmap(top_stocks))
        else:
            # 指定行業：顯示該行業內依市值排序的個股熱圖（前 30）
            top_stocks = self.build_market_toplist(industry=selected_industry, top_n=30)
            self.root.after(0, lambda: self.heatmap_frame.update_stock_heatmap(top_stocks))
    
    def on_industry_changed(self, *args):
        """行業別變更時觸發"""
        self.refresh_stock_list()
        # 更新熱圖以反映新的行業/市值排序
        self.update_heatmap_by_selection()
    
    def on_search_changed(self, *args):
        """搜尋框變更時觸發"""
        self.refresh_stock_list()
    
    def on_market_changed(self, *args):
        """市場變更時觸發"""
        new_market = self.market_var.get()
        if new_market != self.current_market:
            self.current_market = new_market
            if new_market == '美股':
                messagebox.showinfo("提示", "美股功能即將推出")
                self.market_var.set('台股')
            self.refresh_stock_list()
    
    def on_stock_double_click(self, event):
        """雙擊股票項目時加入觀察"""
        self.add_to_watchlist()
    
    def add_to_watchlist(self):
        """加入股票到觀察清單"""
        selection = self.stock_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "請先選擇一支股票")
            return
        
        item = selection[0]
        code, name = self.stock_tree.item(item, 'values')
        
        if code in self.watchlist:
            messagebox.showinfo("提示", f"股票 {code} 已在觀察清單中")
            return
        
        self.watchlist.add(code)
        self.save_watchlist()
        self.create_stock_card(code, name)
        self.layout_cards()
        messagebox.showinfo("成功", f"已加入 {code} ({name})")
    
    def create_stock_card(self, code: str, name: str):
        """建立股票卡片"""
        data = self.stock_data_cache.get(code, {})
        price = data.get('price', 0)
        volume = data.get('volume', 0)
        timestamp = data.get('timestamp', '')
        
        # 模擬漲跌幅
        change_pct = round(random.uniform(-5, 5), 2)
        
        card = StockCardFrame(
            self.cards_frame,
            code=code,
            name=name,
            price=price,
            volume=volume,
            change_pct=change_pct,
            timestamp=timestamp,
            on_remove=lambda: self.remove_stock_card(code)
        )
        
        self.card_widgets[code] = card
    
    def remove_stock_card(self, code: str):
        """移除股票卡片"""
        self.watchlist.discard(code)
        self.save_watchlist()
        if code in self.card_widgets:
            self.card_widgets[code].destroy()
            del self.card_widgets[code]
        self.layout_cards()
    
    def update_stocks(self):
        """更新股票資訊"""
        def update_task():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                results = loop.run_until_complete(
                    self.crawler.fetch_multiple_stocks(list(self.watchlist))
                )
                
                for result in results:
                    code = result['code']
                    self.stock_data_cache[code] = result
                    
                    # 更新卡片
                    if code in self.card_widgets:
                        data = self.stock_data_cache[code]
                        # 重新建立卡片以更新資料
                        self.card_widgets[code].destroy()
                        self.create_stock_card(code, data.get('name', ''))
                
                self.root.after(0, self.layout_cards)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.root.after(0, lambda: self.update_time_label.config(text=f"最後更新: {current_time}"))
                self.root.after(0, lambda: self.status_label.config(text="就緒", foreground="green"))
                
                # 更新熱圖（重新計算行業快速指標，但顯示以市值/行業選擇的個股熱圖）
                for industry in list(self.industry_changes.keys()):
                    self.industry_changes[industry] = round(random.uniform(-5, 5), 2)
                # 依使用者選擇更新熱圖（會呼叫 update_stock_heatmap）
                self.root.after(0, self.update_heatmap_by_selection)
                
                loop.close()
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("錯誤", f"更新失敗: {e}"))
                self.root.after(0, lambda: self.status_label.config(text="錯誤", foreground="red"))
        
        thread = threading.Thread(target=update_task, daemon=True)
        thread.start()
    
    def manual_update(self):
        """手動更新"""
        if not self.watchlist:
            messagebox.showinfo("提示", "觀察清單為空")
            return
        
        self.status_label.config(text="更新中...", foreground="blue")
        self.root.update()
        self.update_stocks()
    
    def toggle_auto_update(self):
        """切換自動更新"""
        self.auto_update_enabled = self.auto_update_var.get()
        
        if self.auto_update_enabled:
            self.schedule_auto_update()
        else:
            if self.update_timer:
                self.root.after_cancel(self.update_timer)
                self.update_timer = None
    
    def schedule_auto_update(self):
        """排程自動更新"""
        if self.auto_update_enabled:
            self.update_stocks()
            self.update_timer = self.root.after(60000, self.schedule_auto_update)
    
    def save_watchlist(self):
        """保存觀察清單到檔案"""
        with open(self.watchlist_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.watchlist), f, ensure_ascii=False)
    
    def load_watchlist(self):
        """從檔案載入觀察清單"""
        if os.path.exists(self.watchlist_file):
            try:
                with open(self.watchlist_file, 'r', encoding='utf-8') as f:
                    watchlist = json.load(f)
                    for code in watchlist:
                        self.watchlist.add(code)
                        # 從爬蟲取得名稱
                        name = self.get_stock_name(code)
                        self.create_stock_card(code, name)
                    self.layout_cards()
            except Exception as e:
                print(f"載入觀察清單失敗: {e}")
    
    def get_stock_name(self, code: str) -> str:
        """根據代碼取得股票名稱"""
        for ind_stocks in self.crawler.get_industries().values():
            for c, name in ind_stocks:
                if c == code:
                    return name
        return "未知"
    
    def on_closing(self):
        """應用關閉時"""
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
        self.save_watchlist()
        self.root.destroy()


def main():
    """主程式入口"""
    root = tk.Tk()
    app = StockMonitorGUIv2(root)
    root.mainloop()


if __name__ == "__main__":
    main()
