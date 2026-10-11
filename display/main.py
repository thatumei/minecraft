import tkinter as tk
from tkinter import ttk
from display.tab1 import Tab1
from display.tab2 import Tab2
from display.tab3 import Tab3
from display.tab4 import Tab4
from display.tab5 import Tab5
from display.tab6 import Tab6
from display.tab7 import Tab7
from display.tab8 import Tab8
# from display.tab9 import Tab9

def setup():
    # 修正1: tk.Tk() に直す必要があります（大文字のTk、かつtkモジュールから呼び出す）
    root = tk.Tk()

    root.title("Minecraft Launcher for 発明クラブ")
    root.geometry("854x480")
    root.resizable(False, False)

    # 修正2: クラスではない（関数の中の）ため、「self.」ではなく「root」やローカル変数にします
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # 修正3: 「self.」を削除し、親（master）には上記で作成した「notebook」を指定します
    tab1 = Tab1(notebook)
    tab2 = Tab2(notebook)
    tab3 = Tab3(notebook)
    tab4 = Tab4(notebook)
    tab5 = Tab5(notebook)
    tab6 = Tab6(notebook)
    tab7 = Tab7(notebook)
    tab8 = Tab8(notebook)
    # tab9 = Tab9(notebook)

    notebook.add(tab1, text="マップ")
    notebook.add(tab2, text="バニラ")
    notebook.add(tab3, text="NeoForge")
    notebook.add(tab4, text="Forge")
    notebook.add(tab5, text="Fabric")
    notebook.add(tab6, text="Quilt")
    notebook.add(tab7, text="Babric")
    notebook.add(tab8, text="Legacy Fabric")
    # notebook.add(tab9, text="インストール済み")

    root.mainloop()