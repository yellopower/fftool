#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import tkinter as tk
import tkinter.font as tk_font
from tkinter import ttk

import util_theme
import utils
from atool import setting_atool
from fftool import util_ff as ff, setting_fftool


class Main:
    """工具主入口
    """

    title = "转码工具箱_v2.9.8 (20200329)"
    tabs = []

    def __init__(self):
        # ffmpeg 静态类初始化
        ff.ffmpeg_path = ff.init_ffmpeg()
        setting_fftool.output_dir = setting_fftool.get_output_dir()

        if utils.is_windows:
            py_parent = os.getcwd()
        else:
            py_parent = os.path.dirname(__file__)

        utils.ffmpeg_path = ff.ffmpeg_path
        utils.py_parent = py_parent
        setting_atool.py_parent = py_parent
        setting_atool.init_tool()
        self.win = None
        self.note_book = None
        self.android_index = 100

    def run_func(self):
        """启动函数
        """
        self.setup()
        self.setup_after()

    def setup(self):
        """创建 ui
        """
        # tk 构建开始
        win = tk.Tk()
        win.title(str(self.title))
        utils.win = win
        self.win = win
        
        # 嗅探启动参数 测试用
        import sys
        argv = sys.argv.copy()
        if len(argv) > 1:
            argv_str = " ".join(argv)
            utils.clipboard_set(argv_str)

            argv.pop(0)
            argv_str = " ".join(argv)
            win.title(argv_str)

        # print( tkFont.families() )
        font_default = tk_font.Font(family="微软雅黑", size=9)
        setting_fftool.font_default = font_default

        # 创建 tab 和 各 tab界面
        tabs = []
        note_book = ttk.Notebook(self.win)
        self.note_book = note_book

        # 片头和水印
        tab = tk.Frame(note_book)
        note_book.add(tab, text='小胶水', image='1.png')  # 片头 片尾 水印
        import fftool.tab_complex as cc
        tabs.append(cc.Main(tab))

        # 2合1
        tab = tk.Frame(note_book)
        note_book.add(tab, text='AB胶')  # 2合1
        import fftool.tab_concat as cc
        tabs.append(cc.Main(tab))

        # import ui.vconcats as cc
        # con = cc.VideoConcats()
        # tab = tk.Frame(note_book)
        # note_book.add(tab, text='多合1')
        # con.setup(tab)
        # tab_content_objs.append(con)

        # # 修剪
        # import fftool.ui.video_cut as cc
        # con = cc.VideoCutLite()
        # tab = tk.Frame(note_book)
        # note_book.add(tab, text='修剪')
        # con.setup(tab)
        # tabs.append(con)

        # mp3
        tab = tk.Frame(note_book)
        note_book.add(tab, text='小剪刀')  # 剪片头/片尾 码率
        import fftool.tab_bitrate as cc
        tabs.append(cc.Main(tab))

        # 片头和水印_检测
        tab = tk.Frame(note_book)
        note_book.add(tab, text='检测')
        import fftool.tab_checker as cc
        tabs.append(cc.Main(tab))

        # 转格式 tab 里面包含多个 tab
        tab = tk.Frame(note_book)
        note_book.add(tab, text='格式工厂')
        main_note_book = MainNoteBook(tab)
        tabs.append(main_note_book)

        # 重命名
        tab = tk.Frame(note_book)
        note_book.add(tab, text='重命名')
        import fftool.tab_rename as cc
        tabs.append(cc.Main(tab))

        # APP转码
        tab = tk.Frame(note_book)
        note_book.add(tab, text='APP转码')
        import fftool.tap_app as cc
        tabs.append(cc.Main(tab))

        # 安卓工具箱
        tab = tk.Frame(note_book)
        note_book.add(tab, text='安卓')
        import atool.tab_android as cc
        tabs.append(cc.Main(tab))

        self.tabs = tabs
        # self.android_index = 7

        # 选中上次打开的 tab
        index = setting_fftool.read_tab_index()
        if not index:
            index = "0"
        if int(index) >= len(note_book.children):
            index = '0'

        note_book.select(index)
        index = self.note_book.index(self.note_book.select())
        self.tabs[index].manual_int()
        note_book.bind("<<NotebookTabChanged>>", self.routine)
        note_book.grid()

    def routine(self, _):
        """选中tab时保存索引值到配置中
        """
        index = self.note_book.index(self.note_book.select())
        self.tabs[index].sync_status()
        setting_fftool.save_tab_index(str(index))
        # if index == self.android_index:
        #     # self.win.resizable(width=True, height=True)
        #     # self.win.minsize(20, 1)
        #     self.win.geometry("50x1+1280+720")
        # else:
        #     self.win.geometry("80x1")

    def setup_after(self):
        """ui 设置完成
        """
        if utils.is_windows:
            f = util_theme.img_win_icon
            if os.path.exists(f):
                self.win.iconbitmap(f)
        # else:
        #     self.win.iconbitmap(util_theme.img_mac_icon)
        self.win.mainloop()


class MainNoteBook:
    is_manual_int = False
    note_book = None
    tabs = None

    def __init__(self, _parent):
        self.win = _parent

    def manual_int(self):
        if self.is_manual_int:
            return
        self.is_manual_int = True
        win = self.win
        # 创建 tab 和 各 tab界面
        tabs = []
        note_book = ttk.Notebook(win)

        # mp3
        tab = tk.Frame(note_book)
        note_book.add(tab, text='mp3')
        import fftool.tab_mp3 as cc
        tabs.append(cc.Main(tab))

        # 图片
        tab = tk.Frame(note_book)
        note_book.add(tab, text='jpg')
        import fftool.tab_image as cc
        tabs.append(cc.Main(tab))

        note_book.bind("<<NotebookTabChanged>>", self.routine)
        note_book.grid()

        self.note_book = note_book
        self.tabs = tabs

    def routine(self, _):
        """选中tab时保存索引值到配置中
        """
        index = self.note_book.index(self.note_book.select())
        self.tabs[index].sync_status()
        # setting_fftool.save_tab_index(str(index))

    def sync_status(self):
        self.manual_int()
        for tab in self.tabs:
            tab.sync_status()


if __name__ == "__main__":
    g = Main()
    g.run_func()
