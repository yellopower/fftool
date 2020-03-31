#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk

import utils
from fftool import util_ff as ff, setting_fftool
from fftool.m_widget import Start
from fftool.m_widget import TreeViewNew


class Main:
    """检测界面
    """
    is_manual_int = False
    hasShutDown = False
    start_btn = None
    file_chooser = None
    vb_chooser = None

    def __init__(self, parent):
        self.win = parent

    def manual_int(self):
        if self.is_manual_int:
            return
        self.is_manual_int = True
        win = self.win

        # 导入文件 / ↑ / ↓ / - /+
        frame_file = tk.Frame(win, padx=0)
        frame_option = tk.Frame(win, padx=0)
        frame_bottom = tk.Frame(win, padx=0)

        if utils.is_mac:
            w_arr = [50, 300, 220, 240, 70]
        else:
            w_arr = [30, 300, 192, 150, 70]
        file_chooser = TreeViewNew(
            frame_file,
            tree_num=20,
            file_types=[("视频文件", "*.mp4"),
                        ("ts", "*.ts"),
                        ("QuickTime", "*.mov"),
                        ("avi", "*.avi"),
                        ("mkv", "*.mkv"),
                        ("mpg", "*.mpg")
                        ],
            paste_notice=';-) 点我 粘贴媒体文件',
            tree_widths=w_arr
        )

        vb_chooser = MyRadioGroup(frame_option)
        vb_chooser.get_frame().grid(column=3, row=2, sticky=tk.W)

        self.start_btn = Start(frame_bottom, text='开始\n检测', command=self.start_check)
        self.start_btn.grid(column=1, row=1, sticky=tk.W)
        # self.start_btn.set_state(False)

        frame_file.grid(column=1, row=0, sticky=tk.NW)
        frame_option.grid(column=1, row=2, sticky=tk.NW)
        frame_bottom.grid(column=1, row=4, sticky=tk.NW)

        self.file_chooser = file_chooser
        self.vb_chooser = vb_chooser

    def sync_status(self):
        self.manual_int()

    # 点击 开始转码按钮
    def start_check(self):
        # 当前是否有转码任务
        if setting_fftool.has_query:
            utils.showinfo('已经有转码任务了')
            return

        # 文件列表
        # v = self.tree.get_lists()
        v = self.file_chooser.get_lists()

        if not len(v):
            utils.showinfo("还没有导入文件")
            return

        # --------------------------------------------------
        # 取出参数并执行转码操作
        dc = dict.fromkeys(self.seq, "")
        # 要处理的视频文件
        dc["input_files"] = v
        dc["radio_select_var"] = self.vb_chooser.get_rad_var()

        # 禁用开始按钮
        self.clear_query()
        self.lock_btn(True)

        # 执行操作
        # self.trans.process(dc)
        import threading
        self.t1 = threading.Thread(target=self.process, args=(dc, ''))
        self.t1.setDaemon(True)
        self.t1.start()

    def update_query(self, qStr, warning=False):
        # self.logTxt['fg'] = "#ff5643" if warning else "#0096FF"
        # self.logTxt['text'] = qStr
        tup = tuple([qStr])
        var_str = self.start_btn.get_string_var()
        if utils.var_is_empty(var_str):
            new_tup = tup
        else:
            v = utils.var_to_list(var_str)
            if len(v):
                new_tup = utils.append_tup(tuple(v), tup)
            else:
                new_tup = tup
        nArr = list(new_tup)
        nnArr = []
        for item in nArr:
            if item:
                nnArr.append(item)
        tup = tuple(nnArr)
        self.start_btn.set_string_var(tup)

    def clear_query(self):
        tup = tuple([''])
        self.start_btn.set_string_var(tup)

    def lock_btn(self, is_lock):
        setting_fftool.has_query = is_lock
        enable = False if is_lock else True
        self.start_btn.set_state(enable)

    titlePrefix = ''

    def set_title2(self, title, warning=False):
        new_title = utils.get_hms() + " " + title
        utils.set_title(self.titlePrefix + "-" + new_title)
        self.update_query(new_title, warning)
        print(new_title)

    def update_status(self, index, status):
        self.file_chooser.update_status(index, status)

    @staticmethod
    def get_file_desc(file_path, type=1):
        if not os.path.exists(file_path):
            return ''
        size = os.path.getsize(file_path)
        size_str = '{:,}'.format(size)
        kb_str = '%.0f' % (size / 1024)
        mb_str = '%.2f' % (size / 1024 / 1024)
        if type == 1:
            return '{0}KB'.format(kb_str)
        elif type == 2:
            return '{0}MB'.format(mb_str)
        else:
            return '{0}字节（{1}MB）'.format(size_str, mb_str)

    @staticmethod
    def get_bit_desc(k_num):
        size = k_num
        # size_str = '{:,}'.format(size)
        kb_str = '%.0f' % (size / 1024)
        mb_str = '%.2f' % (size / 1024 / 1024)
        if k_num < 1024 * 1024:
            return '{0}K'.format(kb_str)
        else:
            return '{0}M'.format(mb_str)

    seq = ('input_files', 'radio_select_var')

    def process(self, dc, astr=''):
        set_title = self.set_title2

        lists = dc["input_files"]
        radio_select_var = dc["radio_select_var"]

        i_sync = 1
        i_double_time = 2
        i_bitrate_4m = 3
        i_bitrate_8m = 4
        i_bitrate_30m = 5
        i_resolution = 6
        i_time_defalut = 7
        i_time_second = 8
        i_time_minute = 9
        i_file_size_kb = 10
        i_file_size_mb = 11

        mb_int = 1024 * 1024

        for i in range(len(lists)):
            raw_mp4 = lists[i]
            if not os.path.exists(raw_mp4):
                continue

            # 音画同步检测
            if radio_select_var == i_sync:
                ss = ff.check_vcomplex_nosync(raw_mp4)

            # 音画同步检测
            elif radio_select_var == i_double_time:
                ss = ff.check_double_time(raw_mp4)

            # 时长 默认 00:00:00
            elif radio_select_var == i_time_defalut:
                dc = ff.get_video_info(raw_mp4)
                ss = dc['duration'] if 'duration' in dc else "0"
                ss = ff.millisecond_to_stand(float(ss) * 1000)

            # 时长 秒
            elif radio_select_var == i_time_second:
                dc = ff.get_video_info(raw_mp4)
                ss = dc['duration'] if 'duration' in dc else "0"
                ss = str(int(float(ss)))

            # 时长 分钟
            elif radio_select_var == i_time_minute:
                dc = ff.get_video_info(raw_mp4)
                ss = dc['duration'] if 'duration' in dc else "0"
                m = '%.2f' % (float(ss) / 60)
                ss = str(m)

            # 分辨率
            elif radio_select_var == i_resolution:
                dc = ff.get_video_info(raw_mp4)
                ss = dc['v_size'] if 'v_size' in dc else "0x0"

            # 4m
            elif radio_select_var == i_bitrate_4m:
                ss = ff.check_bitrate(raw_mp4)
                k_num = int(ss)
                ss = self.get_bit_desc(k_num)
                if k_num < mb_int * 4:
                    ss += " （未达到）"

            # 8m
            elif radio_select_var == i_bitrate_8m:
                ss = ff.check_bitrate(raw_mp4)
                k_num = int(ss)
                ss = self.get_bit_desc(k_num)
                if k_num < mb_int * 8:
                    ss += " （未达到）"

            # 30m
            elif radio_select_var == i_bitrate_30m:
                ss = ff.check_bitrate(raw_mp4)
                k_num = int(ss)
                ss = self.get_bit_desc(k_num)
                if k_num < mb_int * 30:
                    ss += " （未达到）"

            # 文件大小 kb
            elif radio_select_var == i_file_size_kb:
                ss = self.get_file_desc(raw_mp4, 1)
            # 文件大小 mb
            elif radio_select_var == i_file_size_mb:
                ss = self.get_file_desc(raw_mp4, 2)

            else:
                ss = ""
            self.update_status(i, ss)

        set_title("操作结束！")
        set_title("")

        self.t1 = ""
        self.lock_btn(False)


if __name__ == "__main__":
    pass


class MyRadioGroup:

    def __init__(self, parent):
        frame = tk.LabelFrame(parent, text=' 选项 ', padx=2, pady=4, width=200)
        rad_var = tk.IntVar()
        rad_var.set(1)

        arr = ['音画同步', '双倍时长', '码率 ≥4m', '码率 ≥8m', '码率 ≥30m', '分辨率',
               '视频时长', '视频时长(秒)', '视频时长(分钟)', '文件大小(kb)', '文件大小(mb)']
        count = 0
        for item in arr:
            text = item
            count += 1
            rad = tk.Radiobutton(frame, text=text, variable=rad_var, value=count, command=self.radio_call)

            if count <= 4:
                rad.grid(column=count, row=0, sticky=tk.W)
            else:
                rad.grid(column=count - 4, row=1, sticky=tk.W)

        self.rad_var = rad_var
        self.frame = frame

    def radio_call(self):
        pass

    def get_frame(self):
        return self.frame

    def get_rad_var(self):
        return self.rad_var.get()
