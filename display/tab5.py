import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from start import start  # start.py からインポート


class Tab5(ttk.Frame):

  def __init__(self, master, start_callback=None, loader_name="fabric"):
    super().__init__(master)
    # 外部関数が渡されていなければ start.py の start を使用
    self.start_callback = start_callback if start_callback else start
    self.loader_name = loader_name  # 例: "fabric" (バニラの場合は空文字にする等)

    self.all_rows = []
    self.headers = []
    self.sort_col = None
    self.sort_reverse = False

    # --- 上部：コントロールフレーム ---
    frame_top = ttk.Frame(self, padding=10)
    frame_top.pack(fill=tk.X, padx=5)

    # ゲームバージョン絞り込み
    ttk.Label(frame_top, text="ゲームVer:").pack(side=tk.LEFT, padx=2)
    self.entry_filter = ttk.Entry(frame_top, width=10)
    self.entry_filter.pack(side=tk.LEFT, padx=2)
    self.entry_filter.bind(
        "<Return>", lambda event: self.apply_filters_and_sort()
    )

    ttk.Button(
        frame_top, text="絞り込み", command=self.apply_filters_and_sort
    ).pack(side=tk.LEFT, padx=2)
    ttk.Button(frame_top, text="クリア", command=self.reset_filter).pack(
        side=tk.LEFT, padx=2
    )

    # --- ユーザー名入力欄 ---
    ttk.Label(frame_top, text="User:").pack(side=tk.LEFT, padx=(15, 2))
    self.entry_user = ttk.Entry(frame_top, width=12)
    self.entry_user.pack(side=tk.LEFT, padx=2)
    self.entry_user.insert(0, "Player")  # デフォルト値

    # 再取得ボタン
    ttk.Button(frame_top, text="再取得", command=self.load_data).pack(
        side=tk.RIGHT, padx=2
    )

    # --- 中央：テーブル（Treeview） ---
    frame_mid = ttk.Frame(self, padding=10)
    frame_mid.pack(fill=tk.BOTH, expand=True)

    self.tree_scroll_y = ttk.Scrollbar(frame_mid, orient=tk.VERTICAL)
    self.tree_scroll_x = ttk.Scrollbar(frame_mid, orient=tk.HORIZONTAL)

    self.tree = ttk.Treeview(
        frame_mid,
        yscrollcommand=self.tree_scroll_y.set,
        xscrollcommand=self.tree_scroll_x.set,
        selectmode="browse",
    )

    self.tree_scroll_y.config(command=self.tree.yview)
    self.tree_scroll_x.config(command=self.tree.xview)

    self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ダブルクリックで実行
    self.tree.bind("<Double-1>", self.on_row_click)

    # データ読み込み
    self.load_data()

  def load_data(self):
    try:
      result = subprocess.run(
          "portablemc search -k fabric",
          shell=True,
          capture_output=True,
          text=True,
          encoding="utf-8",
          errors="ignore",
      )

      if result.returncode != 0:
        messagebox.showerror("実行エラー", f"失敗しました:\n{result.stderr}")
        return

      lines = result.stdout.strip().splitlines()
      parsed_rows = []
      for line in lines:
        if not line.strip() or any(
            c in line for c in ["┌", "├", "└", "─"]
        ):
          continue
        parts = [p.strip() for p in line.split("│")]
        cells = [p for p in parts if p != ""]
        if cells:
          parsed_rows.append(cells)

      if not parsed_rows:
        return

      self.headers = parsed_rows[0]
      self.all_rows = parsed_rows[1:]

      self.tree["columns"] = self.headers
      self.tree["show"] = "headings"

      for header in self.headers:
        self.tree.heading(
            header, text=header, command=lambda h=header: self.sort_column(h)
        )
        self.tree.column(header, width=150, anchor=tk.W)

      self.apply_filters_and_sort()

    except Exception as e:
      messagebox.showerror("例外発生", str(e))

  def apply_filters_and_sort(self):
    if not self.all_rows:
      return

    keyword = self.entry_filter.get().strip().lower()

    filtered = []
    for row in self.all_rows:
      version = row[0] if len(row) > 0 else ""
      game_ver = row[1] if len(row) > 1 else ""
      channel = row[2] if len(row) > 2 else ""

      if keyword and keyword not in game_ver.lower():
        continue

      filtered.append(row)

    if self.sort_col in self.headers:
      col_idx = self.headers.index(self.sort_col)
      try:
        filtered.sort(
            key=lambda x: (
                float(x[col_idx])
                if x[col_idx].replace(".", "", 1).isdigit()
                else x[col_idx]
            ),
            reverse=self.sort_reverse,
        )
      except Exception:
        filtered.sort(
            key=lambda x: x[col_idx] if len(x) > col_idx else "",
            reverse=self.sort_reverse,
        )

    self.tree.delete(*self.tree.get_children())
    for row in filtered:
      if len(row) < len(self.headers):
        row.extend([""] * (len(self.headers) - len(row)))
      self.tree.insert("", tk.END, values=row)

  def sort_column(self, col):
    if self.sort_col == col:
      self.sort_reverse = not self.sort_reverse
    else:
      self.sort_col = col
      self.sort_reverse = False
    self.apply_filters_and_sort()

  def reset_filter(self):
    self.entry_filter.delete(0, tk.END)
    self.sort_col = None
    self.sort_reverse = False
    self.apply_filters_and_sort()

  def on_row_click(self, event):
    selected_items = self.tree.selection()
    if not selected_items:
      return

    item_id = selected_items[0]
    row_values = self.tree.item(item_id, "values")

    if row_values:
      version = row_values[0]  # Version
      username = self.entry_user.get().strip()  # ユーザー名入力欄の値

      # 外部関数 start(loader, version, username) を呼び出す
      self.start_callback(self.loader_name, version, username)