#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk

import util_theme as theme
import utils
from atool import setting_atool as setting
from fftool.m_widget import FileChooser

# 窗口最后的位置
_win_pos = ''


class Main:
    var_cb_auto_open = tk.IntVar()
    var_cb_size = tk.IntVar()
    var_cb_density = tk.IntVar()
    var_text_size = tk.StringVar()
    var_text_density = tk.StringVar()

    top_win = None

    fc_out = None

    input_size = None
    input_density = None
    resolution_scale_option = None

    def __init__(self):
        top_win = tk.Toplevel(utils.win, padx=2, pady=2)
        top_win.title('设置')
        top_win.geometry(_win_pos)
        self.top_win = top_win

        self.create_screen().grid(column=1, row=1, sticky=tk.NW)
        self.create_resolution_diy().grid(column=1, row=2, sticky=tk.NW)

        top_win.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.widget_arr = []
        self.auto_select()

    def create_screen(self):
        """ 自定义分辨率 设置 """
        og = BigTitle(self.top_win, text='截屏')
        frame = og.frame
        frame_main = og.frame_main

        var = self.var_cb_auto_open
        fc = FileChooser(frame_main,
                         label_text="保存路径",
                         action_btn_text='浏览…',
                         action_btn_call=self.change_out_dir,
                         isFolder=True,
                         hasGROOVE=True,
                         text_width=40
                         )
        cb = tk.Checkbutton(frame_main,
                            text="自动打开",
                            fg=theme.COLOR_BLACK,
                            variable=var,
                            command=lambda v=0: setting.modify_one("auto_open", str(var.get())),
                            )
        fc.grid(column=1, row=1, sticky=tk.W)
        cb.grid(column=1, row=2, sticky=tk.W)
        self.fc_out = fc

        return frame

    def create_resolution_diy(self):
        """ 分辨率 自定义 """
        og = BigTitle(self.top_win, text='分辨率 自定义')
        frame = og.frame
        frame_main = og.frame_main

        frame_option = tk.Frame(frame_main)
        frame_notes = tk.Frame(frame_main)

        v1 = self.var_cb_size
        v2 = self.var_cb_density
        cb1 = tk.Checkbutton(frame_option,
                             text=' 宽x高 ',
                             variable=v1,
                             command=lambda v=0: setting.modify_one("size_on", str(v1.get())),
                             fg=theme.COLOR_BLACK
                             )
        txt1 = tk.Entry(frame_option,
                        textvariable=self.var_text_size,
                        validate="focusout",
                        validatecommand=self.validate_size,
                        width=9,
                        fg=theme.COLOR_BLACK,
                        background=theme.COLOR_LIST_BG
                        )

        cb2 = tk.Checkbutton(frame_option,
                             text=' DPI ',
                             variable=v2,
                             command=lambda v=0: setting.modify_one("density_on", str(v2.get())),
                             fg=theme.COLOR_BLACK
                             )
        txt2 = tk.Entry(frame_option,
                        textvariable=self.var_text_density,
                        validate="focusout",
                        validatecommand=self.validate_density,
                        width=4,
                        fg=theme.COLOR_BLACK,
                        background=theme.COLOR_LIST_BG
                        )

        utils.tooltip(cb1, "屏幕分辨率，例如：1280x720")
        utils.tooltip(cb2, "屏幕密度，取值范围为 160~480")

        s = "小天才手表（宽x高:320x360，DPI:320）"
        tk.Label(frame_notes, text=s, fg=theme.COLOR_GRAY).grid(column=1, row=1)

        cb1.grid(column=1, row=1)
        txt1.grid(column=2, row=1)
        cb2.grid(column=3, row=1)
        txt2.grid(column=4, row=1)

        frame_option.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        frame_notes.grid(column=1, row=2, sticky=tk.N + tk.S + tk.W)

        self.input_size = txt1
        self.input_density = txt2

        return frame

    def auto_select(self):
        jf = setting.read_setting()

        # 自动打开
        self.var_cb_auto_open.set(int(jf["auto_open"]))

        # 截图保存路径
        key = 'output_dir'
        if jf[key]:
            fp = jf[key]
            if not os.path.exists(fp):
                fp = setting.output_dir
            self.fc_out.set_text(fp)

        # 分辨率 自定义
        self.var_text_size.set(jf['size'])
        self.var_text_density.set(jf['density'])

        self.var_cb_size.set(int(jf["size_on"]))
        self.var_cb_density.set(int(jf["density_on"]))

    def change_out_dir(self):
        p5 = self.fc_out.get_text()
        if p5 and os.path.exists(p5):
            jf = setting.read_setting()
            jf['output_dir'] = p5
            setting.save_to_json(jf)
            setting.output_dir = p5

    def validate_size(self):
        """ 验证尺寸信息, 合法时则更新设置"""
        setting.modify_one("size", self.var_text_size.get())
        return True

    def validate_density(self):
        """ 验证密度信息, 合法时则更新设置"""
        # num = int(self.var_text_density.get())
        # if num < 120 or num > 480:
        #     utils.showinfo("取值范围在120~480")
        #     return False
        # else:
        #     setting.modify_one("density", self.var_text_density.get())
        #     return True
        setting.modify_one("density", self.var_text_density.get())
        return True

    def on_closing(self):
        self.destroy()

    def destroy(self):
        # tup = (self.top_win,)
        # for w in tup:
        #     w.destroy()
        # del tup

        global _win_pos
        _win_pos = self.top_win.geometry()
        self.top_win.destroy()
        self.top_win = None


class BigTitle:
    """大标题选项组"""

    def __init__(self, parent, text="", notes=''):
        """ 初始化
        :param parent:
        :param text:    选项组标题
        :param notes:   选项组说明
        """
        frame = tk.Frame(parent)

        frame_label = tk.Frame(frame)
        frame_main = tk.Frame(frame)

        label = tk.Label(frame_label, text=text, font=theme.get_big_title())
        label2 = tk.Label(frame_label, text=notes, fg=theme.COLOR_GRAY)

        label.grid(column=1, row=1, sticky=tk.NW)
        label2.grid(column=2, row=1, sticky=tk.NW)

        frame_label.grid(column=1, row=1, sticky=tk.NW)
        frame_main.grid(column=1, row=2)
        tk.Label(frame).grid(column=1, row=3)

        self.frame = frame
        self.frame_main = frame_main

    def get_frame_main(self):
        return self.frame_main

    def get_frame(self):
        return self.frame

    def grid(self, **kw):
        self.frame.grid(kw)


if __name__ == "__main__":
    pass
