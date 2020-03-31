#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from pathlib import Path

import util_theme as theme
import utils
from fftool import util_ff as ff, setting_fftool
from fftool.m_widget import FileChooser
from fftool.m_widget import RadiobuttonOption
from fftool.m_widget import Start
from fftool.m_widget import TreeViewNew


class Main:
    """小剪刀
    """
    is_manual_int = False

    file_chooser = None
    bit_option = None
    size_option = None
    dura_option = None
    fc_out = None
    start_btn = None

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
        frame_out = tk.Frame(win, padx=0)
        frame_bottom = tk.Frame(win, padx=0)

        if utils.is_mac:
            w_arr = [50, 300, 220, 240, 70]
        else:
            w_arr = [30, 300, 192, 150, 70]
        file_chooser = TreeViewNew(
            frame_file,
            tree_num=10,
            file_types=[("视频文件", "*.mp4"),
                        ("QuickTime", "*.mov"),
                        ("avi", "*.avi"),
                        ("mkv", "*.mkv"),
                        ("mpg", "*.mpg")
                        ],
            paste_notice=';-) 点我 粘贴媒体文件（支持mp4、mov、avi、mkv、mpg格式）',
            tree_widths=w_arr,
            has_list_btn=True
        )

        # 选项
        bit_option = RadiobuttonOption(frame_option,
                                       title=" 码率（Bitrate） ",
                                       options=['智能', '≥4m', '≥6m', '≥8m', '≥10m'],
                                       set=1
                                       )
        dura_option = MyDurationOption(frame_option)
        size_option = MySizeOption(frame_option)

        bit_option.grid(column=3, row=2, sticky=tk.W)
        dura_option.get_frame().grid(column=3, row=3, sticky=tk.W)
        size_option.get_frame().grid(column=3, row=4, sticky=tk.W)

        fc_out = FileChooser(frame_out,
                             btn_text="　输出目录 ",
                             action_btn_text='选择目录',
                             btn_call=self.goto_out_dir,
                             isFolder=True,
                             hasGROOVE=True,
                             text_width=82
                             )
        frame_out.grid(column=1, row=3, sticky=tk.NW)

        self.start_btn = Start(frame_bottom, text='转码', command=self.start_check)
        self.start_btn.grid(column=1, row=1, sticky=tk.W)
        # self.start_btn.set_state(False)

        frame_file.grid(column=1, row=0, sticky=tk.NW)
        frame_option.grid(column=1, row=2, sticky=tk.NW)
        fc_out.grid(column=1, row=3, sticky=tk.W)
        frame_bottom.grid(column=1, row=4, sticky=tk.NW)

        self.file_chooser = file_chooser
        self.bit_option = bit_option
        self.size_option = size_option
        self.dura_option = dura_option
        self.fc_out = fc_out

    def sync_status(self):
        self.manual_int()
        self.fc_out.set_text(setting_fftool.output_dir)

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

        # 文件列表
        utils.write_txt_by_arr(setting_fftool.list_file, v.copy())

        # 剪片头片尾 检查
        arr = self.dura_option.start_check()
        if bool(arr[0]):
            fast_select = bool(arr[1])
            pt_select = arr[2]
            pt_second = arr[3]
            pw_select = arr[4]
            pw_second = arr[5]
            need_remain = arr[6]
        else:
            return

        # --------------------------------------------------
        # 取出参数并执行转码操作
        dc = dict.fromkeys(self.seq, "")
        # 要处理的视频文件
        dc["input_files"] = v
        dc["radio_select_var"] = self.bit_option.get()
        dc["output_dir"] = self.fc_out.get_text()
        dc["size_cut_select"] = self.size_option.get_checked_bool()

        dc["fast_select"] = fast_select
        dc["pt_select"] = pt_select
        dc["pt_second"] = pt_second
        dc["pw_select"] = pw_select
        dc["pw_second"] = pw_second
        dc["need_remain"] = need_remain

        # 禁用开始按钮
        self.clear_query()
        self.lock_btn(True)

        # 执行操作
        # self.trans.process(dc)
        import threading
        self.t1 = threading.Thread(target=self.process, args=(dc, ''))
        self.t1.setDaemon(True)
        self.t1.start()

    def goto_out_dir(self):
        # p5 = self.outTxt['text']
        p5 = self.fc_out.get_text()
        if not p5 or not os.path.exists(p5):
            utils.showinfo("输出路径设置不对")
        else:
            utils.open_dir(p5)

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

    seq = ('input_files',
           "output_dir",
           'radio_select_var',
           'size_cut_select',
           'fast_select',
           'pt_select',
           'pt_second',
           'pw_select',
           'pw_second',
           'need_remain'
           )

    def process(self, dc, astr=''):
        set_title = self.set_title2

        lists = dc["input_files"]
        radio_select_var = dc["radio_select_var"]
        output_dir = dc["output_dir"] + os.sep

        pt_select = dc["pt_select"]
        pw_select = dc["pw_select"]
        pt_second = dc["pt_second"] / 1000
        pw_second = dc["pw_second"] / 1000
        need_remain = dc["need_remain"]
        fast_select = dc["fast_select"]

        # 视频尺寸超过 1920x1080 10px 以内自动进行裁剪
        size_cut_select = dc["size_cut_select"]
        add_param_str = "-vf crop=1920:1080:0:0 -threads 8 -hide_banner" if size_cut_select else ""
        add_param_str_mov = '-vf "crop=1920:1080:0:0,scale=2*trunc(iw/2):-2,setsar=1" -threads 8 -hide_banner' if size_cut_select else ''

        # 对符合要求的 mov 进行特殊处理
        # -vf "crop=1920:1080:0:0,scale=2*trunc(iw/2):-2,setsar=1"
        mov_param = "-profile:v high -pix_fmt yuv420p"
        vaild_sizes = ['1920x1080',
                       '1280x720',
                       '960x540',
                       '640x360',
                       '1080x1920',
                       '720x1280',
                       '540x960',
                       '360x640'
                       ]

        total = len(lists)
        count = 0
        final_mp4 = ""
        msg_str = " {0}/{1} {2}"
        cut_info_str = "{0}"
        can_fast = False
        is_mov = False
        for i in range(len(lists)):
            count += 1
            raw_mp4 = lists[i]
            if not os.path.exists(raw_mp4):
                continue
            p = Path(raw_mp4)
            suffix = str(p.suffix).lower()
            temp_mp4 = output_dir + str(p.stem) + ".mp4"
            is_mov = True if suffix == ".mov" else False

            # 任务信息
            mstr = msg_str.format(count, total, p.name)
            set_title(mstr)
            final_mp4 = temp_mp4

            # 匹配 尺寸和fps
            tdc = ff.get_video_info(raw_mp4, False)
            v_size = tdc["v_size"] if tdc["v_size"] else "1920x1080"
            fps = tdc["fps"] if tdc["fps"] else "24"
            tdc["fps"] = fps

            duration = float(tdc['duration']) if tdc["duration"] else 0
            duration = float(duration)
            second = duration

            if not duration:
                set_title(cut_info_str.format('读取视频参数失败，不处理该视频'))
                continue

            # 码率 部分
            # crf 不为 0  ff对象则不应用 v_bit_rate等参数
            vb_str = ""
            if radio_select_var == 1:  # 自动
                tdc["crf"] = 18
                can_fast = True

            elif radio_select_var == 2:  # 4m
                vb_str = "4M"
                can_fast = False

            elif radio_select_var == 3:  # 6m
                vb_str = "6M"
                can_fast = False

            elif radio_select_var == 4:  # 8m
                vb_str = "8M"
                can_fast = False

            elif radio_select_var == 5:  # 10m
                vb_str = "10M"
                can_fast = False

            elif radio_select_var == 6:  # 30m
                vb_str = "30M"
                can_fast = False

            # 尺寸 部分
            tdc["v_size"] = v_size
            s_arr = v_size.split("x")
            s_w = int(s_arr[0])
            s_h = int(s_arr[1])
            need_w = s_w > 1920 and s_w <= 1940
            need_h = s_h > 1080 and s_h <= 1100
            need_result = need_w or need_h
            if size_cut_select and need_result:
                tdc["v_size"] = "1920x1080"

                if is_mov:
                    tdc["other_param_add"] = mov_param + " {}".format(add_param_str_mov)
                else:
                    if 'other_param_add' in tdc and tdc["other_param_add"] != '':
                        tdc["other_param_add"] += " {}".format(add_param_str)
                    else:
                        tdc["other_param_add"] = add_param_str
                can_fast = False
            else:
                # 指定 mov 的 尺寸才进行特殊处理
                if is_mov and vaild_sizes.count(v_size) != 0:
                    tdc["other_param_add"] = mov_param

            # 时长 部分
            need_execute = False
            time_start = 0
            time_to = 0
            if pt_select and pt_second != 0:
                if pt_second < second:
                    time_start = pt_second
                    need_execute = True
                else:
                    set_title(cut_info_str.format('片头时长超过视频时长，不进行片头修剪！！！'))

            if pw_select and pw_second != 0:
                if need_remain:
                    time_to = second - pw_second
                else:
                    time_to = pw_second

                if time_to > time_start:
                    need_execute = True
                else:
                    time_to = 0
                    set_title(cut_info_str.format('片尾时长在起始时间之前，不进行片尾修剪！！！'))

            if need_execute:
                if can_fast and fast_select:
                    if suffix == ".mp4":
                        set_title(cut_info_str.format('正在快速修剪！！！'))
                        if "other_param_add" in tdc:
                            tdc['other_param_add'] += " -c copy -copyts"
                        else:
                            tdc['other_param_add'] = "-c copy -copyts"
                else:
                    set_title(cut_info_str.format('正在转换 修剪部分……'))
            #
            # else:
            #     set_title(cut_info_str.format('输入的时长都不正确，不进行片头片尾的修剪！！！'))

            obj = ff.create_obj()
            obj.input_file = raw_mp4
            obj.output_file = temp_mp4
            obj.time_start = time_start
            obj.time_to = time_to
            obj.set_video_info(tdc, vb_str)

            # if fast_select:
            #     obj.other_param = '-c copy -copyts -threads 8'
            # else:
            #     obj.other_param = '-copyts -threads 8'
            obj.execute()

            # self.update_status(i, ss)

        set_title("操作结束！")
        set_title("")

        self.t1 = ""
        self.lock_btn(False)

        # 自动打开目录
        if final_mp4:
            utils.open_dir(output_dir)


class MyDurationOption:

    def __init__(self, parent, no_fast=False):
        frame_group = tk.LabelFrame(parent, text=' 剪片头片尾 ', padx=2, pady=4, width=200)

        self.cb_pt_var1 = tk.IntVar()
        self.cb_pw_var2 = tk.IntVar()
        self.cb_fast_var = tk.IntVar()
        self.cb_mode_var = tk.IntVar()
        cb_pt = tk.Checkbutton(frame_group, variable=self.cb_pt_var1)
        cb_pw = tk.Checkbutton(frame_group, variable=self.cb_pw_var2)

        cb_fast = tk.Checkbutton(frame_group, text=' 转码-极速模式 ', variable=self.cb_fast_var, command=self.cb_fast_call)
        cb_mode = tk.Checkbutton(frame_group, text=' 修剪-起止模式 ', variable=self.cb_mode_var, command=self.cb_mode_call)
        cb_mode.select()
        # cb_pt.select()
        cb_pt.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        cb_pw.grid(column=1, row=2, sticky=tk.N + tk.S + tk.W)
        cb_mode.grid(column=1, row=3, sticky=tk.N + tk.S + tk.W)

        if not no_fast:
            cb_fast.grid(column=1, row=4, sticky=tk.N + tk.S + tk.W)

        pt_input = tk.Text(frame_group, height=1, width=12,
                           fg=theme.COLOR_BLACK,
                           background=theme.COLOR_LIST_BG,
                           wrap=tk.WORD
                           )
        pw_input = utils.clone(pt_input)
        pt_input.grid(column=2, row=1)
        pw_input.grid(column=2, row=2)
        pt_input.insert(tk.INSERT, '6.376')
        pw_input.insert(tk.INSERT, '0')

        pt_label = tk.Label(frame_group, text='秒 这之前的会被剪掉', fg=theme.COLOR_BLACK)
        pw_label = tk.Label(frame_group, text='秒 倒数后的会被剪掉', fg=theme.COLOR_BLACK)
        pt_label.grid(column=3, row=1)
        pw_label.grid(column=3, row=2)

        self.frame = frame_group
        self.pt_input = pt_input
        self.pw_input = pw_input
        self.cb_pt = cb_pt
        self.cb_pw = cb_pw
        self.cb_mode = cb_mode
        self.pt_label = pt_label
        self.pw_label = pw_label

        self.change_mode(True)

    def change_mode(self, need_remain=True):
        """
        改变修剪模式
        :param need_remain:
        :return:
        """
        if need_remain:
            self.cb_pt["text"] = ' 剪片头 '
            self.cb_pw["text"] = ' 剪片尾 '
            self.cb_mode["text"] = " 修剪-倒数模式 "
            self.pt_label["text"] = '秒 这之前的会被剪掉'
            self.pw_label["text"] = '秒 倒数后的会被剪掉'
        else:
            self.cb_pt["text"] = ' 开始时间 '
            self.cb_pw["text"] = ' 结束时间 '
            self.cb_mode["text"] = " 修剪-起止模式 "
            self.pt_label["text"] = '秒'
            self.pw_label["text"] = '秒'

    def enable(self):
        pass

    def get_frame(self):
        return self.frame

    def get_mode(self):
        """是否为倒计时模式"""
        need_remain = True if self.cb_mode_var.get() else False
        return need_remain

    def cb_fast_call(self):
        fast_select = True if self.cb_fast_var.get() else False
        if fast_select:
            utils.showinfo('请注意：\n修剪的速度会变得很快，但首尾可能会有些空白！！！\n码率选项需勾选“智能”方能生效！')

    def cb_mode_call(self):
        need_remain = True if self.cb_mode_var.get() else False
        self.change_mode(need_remain)

    def start_check(self):
        r_arr = [False, False, False, 0, False, 0, True]
        pt_select = True if self.cb_pt_var1.get() else False
        pw_select = True if self.cb_pw_var2.get() else False
        fast_select = True if self.cb_fast_var.get() else False
        need_remain = True if self.cb_mode_var.get() else False
        # if not pt_select and not pw_select:
        #     utils.showinfo('请选一个修剪任务')
        #     return r_arr

        pt_second = self.pt_input.get(1.0, tk.END)
        pw_second = self.pw_input.get(1.0, tk.END)
        try:
            pt_second = float(pt_second) * 1000
            pt_second = int(pt_second)
        except:
            if pt_select:
                utils.showinfo('请检查 剪片头 输入框的秒数')
                r_arr[0] = False
                return r_arr
            pt_second = 0

        try:
            pw_second = float(pw_second) * 1000
            pw_second = int(pw_second)
        except:
            if pw_select:
                utils.showinfo('请检查 剪片尾 输入框的秒数')
                r_arr[0] = False
                return r_arr
            pw_second = 0

        r_arr[0] = True
        r_arr[1] = fast_select
        r_arr[2] = pt_select
        r_arr[3] = pt_second
        r_arr[4] = pw_select
        r_arr[5] = pw_second
        r_arr[6] = need_remain
        return r_arr


class MySizeOption:

    def __init__(self, parent):
        frame = tk.LabelFrame(parent, text=' 特殊处理 ', padx=2, pady=4, width=200)

        # 1080p裁剪
        self.cv_size_cut = tk.IntVar()
        cb_size_cut = tk.Checkbutton(frame, text="尺寸为 1920x1083 的裁剪成 1920x1080", variable=self.cv_size_cut)
        cb_size_cut.grid(column=3, row=4, sticky=tk.W)

        self.frame = frame

    def get_checked_bool(self):
        return True if self.cv_size_cut.get() else False

    def get_frame(self):
        return self.frame
