"""
台灣股市即時監控 GUI 應用

功能:
1. 載入台灣股票清單
2. 搜尋股票
3. 選擇股票加入觀察清單
4. 每隔 1 分鐘自動更新股票資訊
5. 顯示: 股票代碼、股票名稱、即時股價、成交量、更新時間
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Set, Tuple
from taiwan_stock_crawler import TaiwanStockCrawler


class StockMonitorGUI:
    """股票監控 GUI 應用"""
    
    def __init__(self, root: tk.Tk):
        """初始化應用"""
        self.root = root
        self.root.title("📊 台灣股市即時監控")
        self.root.geometry("1000x600")
        
        # 爬蟲實例
        self.crawler = TaiwanStockCrawler()
        
        # 股票清單
        self.all_stocks: List[Tuple[str, str]] = []
        self.watchlist: Set[str] = set()
        
        # 股票資料快取
        self.stock_data_cache: Dict[str, Dict] = {}
        
        # 自動更新
        self.auto_update_enabled = False
        self.update_timer = None
        self.update_thread = None
        
        # 設定檔路徑
        self.watchlist_file = "watchlist.json"
        
        # 建立 UI
        self.setup_ui()
        
        # 載入股票清單
        self.load_stocks_in_background()
        
        # 載入觀察清單
        self.load_watchlist()
        
        # 綁定關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """建立使用者介面"""
        # 主容器 - 上下分割
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 工具列
        self.setup_toolbar(main_frame)
        
        # 內容區域 - 左右分割
        content_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左側: 股票清單
        self.setup_left_panel(content_paned)
        
        # 右側: 觀察清單
        self.setup_right_panel(content_paned)
    
    def setup_toolbar(self, parent):
        """建立工具列"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=5)
        
        # 狀態標籤
        ttk.Label(toolbar, text="狀態:").pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(toolbar, text="載入中...", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
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
        parent.add(left_frame, weight=1)
        
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
            height=20,
            yscrollcommand=scrollbar.set
        )
        self.stock_tree.column('#0', width=0, stretch=tk.NO)
        self.stock_tree.column('code', anchor=tk.W, width=60)
        self.stock_tree.column('name', anchor=tk.W, width=120)
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
    
    def setup_right_panel(self, parent):
        """建立右側觀察清單面板"""
        right_frame = ttk.LabelFrame(parent, text="👁️ 觀察中的股票", padding=5)
        parent.add(right_frame, weight=2)
        
        # 觀察清單 (Treeview)
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.watch_tree = ttk.Treeview(
            tree_frame,
            columns=('code', 'name', 'price', 'volume', 'time'),
            height=20,
            yscrollcommand=scrollbar.set
        )
        self.watch_tree.column('#0', width=0, stretch=tk.NO)
        self.watch_tree.column('code', anchor=tk.W, width=70)
        self.watch_tree.column('name', anchor=tk.W, width=100)
        self.watch_tree.column('price', anchor=tk.CENTER, width=80)
        self.watch_tree.column('volume', anchor=tk.CENTER, width=100)
        self.watch_tree.column('time', anchor=tk.CENTER, width=80)
        
        self.watch_tree.heading('code', text='代碼')
        self.watch_tree.heading('name', text='名稱')
        self.watch_tree.heading('price', text='股價 (NT$)')
        self.watch_tree.heading('volume', text='成交量 (張)')
        self.watch_tree.heading('time', text='更新時間')
        
        self.watch_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.watch_tree.yview)
        
        # 右鍵菜單
        self.watch_tree.bind('<Button-3>', self.on_right_click_watchlist)
        
        # 移除按鈕
        ttk.Button(
            right_frame,
            text="❌ 移除選中股票",
            command=self.remove_from_watchlist
        ).pack(fill=tk.X, pady=5)
    
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
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("錯誤", f"載入失敗: {e}"))
        
        thread = threading.Thread(target=load_task, daemon=True)
        thread.start()
    
    def refresh_stock_list(self):
        """刷新股票清單顯示"""
        # 清空
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        # 取得選中的行業
        selected_industry = self.industry_var.get()
        
        # 決定要顯示的股票
        if selected_industry == "全部":
            stocks_to_display = self.all_stocks
        else:
            # 從特定行業篩選
            industries_dict = self.crawler.get_industries()
            if selected_industry in industries_dict:
                stocks_to_display = industries_dict[selected_industry]
            else:
                stocks_to_display = []
        
        # 搜尋篩選
        search_text = self.search_var.get().lower()
        for code, name in stocks_to_display:
            if search_text in code.lower() or search_text in name.lower():
                self.stock_tree.insert('', 'end', values=(code, name))
    
    def on_industry_changed(self, *args):
        """行業別變更時觸發"""
        self.refresh_stock_list()
    
    def on_search_changed(self, *args):
        """搜尋框變更時觸發"""
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
        self.refresh_watchlist_display()
        messagebox.showinfo("成功", f"已加入 {code} ({name})")
    
    def remove_from_watchlist(self):
        """移除觀察清單中的股票"""
        selection = self.watch_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "請先選擇一支股票")
            return
        
        item = selection[0]
        code = self.watch_tree.item(item, 'values')[0]
        
        self.watchlist.discard(code)
        self.save_watchlist()
        self.refresh_watchlist_display()
    
    def on_right_click_watchlist(self, event):
        """右鍵菜單"""
        item = self.watch_tree.identify('item', event.x, event.y)
        if not item:
            return
        
        self.watch_tree.selection_set(item)
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="移除", command=self.remove_from_watchlist)
        menu.post(event.x_root, event.y_root)
    
    def refresh_watchlist_display(self):
        """刷新觀察清單顯示"""
        # 清空
        for item in self.watch_tree.get_children():
            self.watch_tree.delete(item)
        
        # 新增項目
        for code in sorted(self.watchlist):
            data = self.stock_data_cache.get(code, {})
            price = data.get('price', 'N/A')
            volume = data.get('volume', 'N/A')
            timestamp = data.get('timestamp', '等待更新')
            name = data.get('name', '載入中...')
            
            if isinstance(price, float):
                price = f"${price:.2f}"
            if isinstance(volume, int):
                volume = f"{volume:,}"
            
            self.watch_tree.insert('', 'end', values=(code, name, price, volume, timestamp))
    
    def save_watchlist(self):
        """保存觀察清單到檔案"""
        with open(self.watchlist_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.watchlist), f, ensure_ascii=False)
    
    def load_watchlist(self):
        """從檔案載入觀察清單"""
        if os.path.exists(self.watchlist_file):
            try:
                with open(self.watchlist_file, 'r', encoding='utf-8') as f:
                    self.watchlist = set(json.load(f))
                self.refresh_watchlist_display()
            except Exception as e:
                print(f"載入觀察清單失敗: {e}")
    
    def manual_update(self):
        """手動更新"""
        if not self.watchlist:
            messagebox.showinfo("提示", "觀察清單為空")
            return
        
        self.status_label.config(text="更新中...", foreground="blue")
        self.root.update()
        
        self.update_stocks()
    
    def update_stocks(self):
        """更新股票資訊"""
        def update_task():
            try:
                # 在事件迴圈中執行
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                results = loop.run_until_complete(
                    self.crawler.fetch_multiple_stocks(list(self.watchlist))
                )
                
                # 更新快取
                for result in results:
                    code = result['code']
                    self.stock_data_cache[code] = result
                
                # 更新 UI
                self.root.after(0, self.refresh_watchlist_display)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.root.after(0, lambda: self.update_time_label.config(text=f"最後更新: {current_time}"))
                self.root.after(0, lambda: self.status_label.config(text="就緒", foreground="green"))
                
                loop.close()
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("錯誤", f"更新失敗: {e}"))
                self.root.after(0, lambda: self.status_label.config(text="錯誤", foreground="red"))
        
        thread = threading.Thread(target=update_task, daemon=True)
        thread.start()
    
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
            # 60 秒後再更新
            self.update_timer = self.root.after(60000, self.schedule_auto_update)
    
    def on_closing(self):
        """應用關閉時"""
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
        self.save_watchlist()
        self.root.destroy()


def main():
    """主程式入口"""
    root = tk.Tk()
    app = StockMonitorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
