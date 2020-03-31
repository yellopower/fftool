#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from pathlib import Path

from fftool.m_widget import Start
from fftool.m_widget import TreeViewNew
from fftool.m_widget import FileChooser
import util_theme
import utils
from fftool import util_ff as ff, setting_fftool


class Main:
    """转码为图片
    """

    def __init__(self, parent):
        self.titlePrefix = ''
        self.dc = dict.fromkeys(self.seq, "")
        self.t1 = ''

        win = parent

        # 颜色
        color = util_theme.COLOR_BLACK

        frame_file = tk.Frame(win)
        frame_group = tk.Frame(win)
        frame_out = tk.Frame(win)
        frame_start = tk.Frame(win)

        file_chooser = TreeViewNew(
            frame_file,
            tree_num=15,
            file_types=[
                ("png", "*.png"),
                ("jpg", "*.jpg"),
                ("jpeg", "*.jpeg"),
                ("webp", "*.webp")
            ],
            paste_notice=';-) 点我 粘贴图像文件'
        )

        cb_var = tk.IntVar()
        cb = tk.Checkbutton(
            frame_group,
            text="保留上层目录",
            fg=color,
            variable=cb_var
        )

        fc_out = FileChooser(
            frame_out,
            btn_text="　输出目录 ",
            action_btn_text='选择目录',
            btn_call=self.goto_out_dir,
            isFolder=True,
            hasGROOVE=True,
            text_width=82
        )

        start = Start(
            frame_start,
            text='转换',
            command=self.start_check
        )
        start.grid(column=1, row=1, sticky=tk.W)

        cb.grid(column=1, row=2, sticky=tk.W)
        fc_out.grid(column=1, row=3, sticky=tk.W)

        frame_file.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        frame_group.grid(column=1, row=3, sticky=tk.N + tk.S + tk.W)
        frame_out.grid(column=1, row=5, sticky=tk.N + tk.S + tk.W)
        frame_start.grid(column=1, row=6, sticky=tk.N + tk.S + tk.W)

        self.file_chooser = file_chooser
        self.keep_parent_var = cb_var
        self.fc_out = fc_out
        self.start = start

        self.auto_select()

    def auto_select(self):
        self.fc_out.set_text(setting_fftool.output_dir)

    def sync_status(self):
        self.fc_out.set_text(setting_fftool.output_dir)

    def start_check(self):
        dc = self.dc

        if setting_fftool.has_query:
            utils.showinfo("有任务正在执行，请稍后")
            return

        arr = self.file_chooser.get_lists()
        if not len(arr):
            utils.showinfo("还没有导入文件")
            return

        # # 禁用开始按钮
        self.clear_query()
        self.lock_btn(True)

        keep_parent_select = True if self.keep_parent_var.get() else False
        # p5 = self.outTxt['text']
        p5 = self.fc_out.get_text()

        dc["list"] = arr
        dc["output_dir"] = p5
        dc["keep_parent_select"] = keep_parent_select

        # 记忆操作
        setting_dc = setting_fftool.read_setting()
        setting_dc["output_dir"] = p5
        setting_fftool.save_setting(setting_dc)

        # 禁用开始按钮
        self.clear_query()
        self.lock_btn(True)

        # 执行操作
        import threading
        self.t1 = threading.Thread(target=self.process, args=(dc, ''))
        self.t1.setDaemon(True)
        self.t1.start()

    def clear_query(self):
        tup = tuple([''])
        self.start.set_string_var(tup)

    @staticmethod
    def lock_btn(is_lock):
        setting_fftool.has_query = is_lock
        # enable = False if is_lock else True
        # utils.setState(self.import_btn, enable)

    def goto_out_dir(self):
        # p5 = self.outTxt['text']
        p5 = self.fc_out.get_text()
        if not p5 or not os.path.exists(p5):
            utils.showinfo("输出路径设置不对")
        else:
            utils.open_dir(p5)

    def update_query(self, query_str, warning=False):
        # self.logTxt['fg'] = "#ff5643" if warning else "#0096FF"
        # self.logTxt['text'] = qStr
        tup = tuple([query_str])
        v_str = self.start.get_string_var()
        if utils.var_is_empty(v_str):
            new_tup = tup
        else:
            v = utils.var_to_list(v_str)
            if len(v):
                new_tup = utils.append_tup(tuple(v), tup)
            else:
                new_tup = tup
        new_arr = list(new_tup)
        final_arr = []
        for item in new_arr:
            if item:
                final_arr.append(item)
        tup = tuple(final_arr)
        self.start.set_string_var(tup)

    def set_title2(self, title, warning=False):
        new_title = utils.get_hms() + " " + title
        utils.set_title(self.titlePrefix + "-" + new_title)
        self.update_query(new_title, warning)
        print(new_title)

    seq = ("list", "output_dir", "keep_parent_select")

    def process(self, dc, astr=''):
        set_title = self.set_title2

        input_list = dc["list"]
        output_dir = dc["output_dir"] + os.sep
        utils.make_dir(output_dir)
        temp_dir = output_dir + 'tempDir' + os.sep
        utils.make_dir(temp_dir)
        utils.hide_file(temp_dir)
        keep_parent_select = dc["keep_parent_select"]

        final_png = ""

        total = len(input_list)
        count = 0
        msg_str = " {0}/{1} {2}"
        for i in range(total):
            count = count + 1
            input_file = input_list[i]
            p = Path(input_file)

            # 保留上层目录结构
            # 排除根目录
            path_root = "{0}{1}".format(p.drive, os.sep)
            path_parent = str(Path(p.parent).name)
            if keep_parent_select and not path_root == path_parent:
                output_sub_dir = "{0}{1}{2}".format(output_dir, path_parent, os.sep)
                utils.make_dir(output_sub_dir)
                output_file = "{0}{1}{2}".format(output_sub_dir, p.stem, ".jpg")
            else:
                output_file = "{0}{1}{2}".format(output_dir, p.stem, ".jpg")

            # 任务信息
            mstr = msg_str.format(count, total, p.name)
            set_title(mstr)

            # 拼接 ffmpeg 参数
            arr = ["ffmpeg -y -i", '"{}"'.format(input_file), '-hide_banner', '"{}"'.format(output_file)]
            ff.execute(" ".join(arr))
            final_png = output_file

        set_title("操作结束！")

        # 自动打开目录
        if final_png:
            utils.open_dir(output_dir)

        self.t1 = ""
        self.lock_btn(False)


if __name__ == "__main__":
    pass
