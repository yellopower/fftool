#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from pathlib import Path

import util_theme
import utils
from fftool import util_ff as ff, setting_fftool
from fftool.m_widget import FileChooser
from fftool.m_widget import Start
from fftool.m_widget import TreeViewNew
from fftool.tab_bitrate import MyDurationOption


class Main:
    """转码为mp3
    """
    cb_format_var1 = tk.IntVar()
    cb_format_var2 = tk.IntVar()
    cb_format_var3 = tk.IntVar()

    def __init__(self, parent):
        self.concatList = []
        self.titlePrefix = ''
        self.dc = dict.fromkeys(self.seq, "")
        self.t1 = ''

        win = parent

        # 颜色
        color = util_theme.COLOR_BLACK

        frame_file = tk.Frame(win)
        frame_format = tk.Frame(win)
        frame_group = tk.Frame(win)
        frame_out = tk.Frame(win)
        frame_start = tk.Frame(win)

        file_chooser = TreeViewNew(
            frame_file,
            tree_num=15,
            file_types=[
                ("视频文件", "*.mp4"),
                ("QuickTime", "*.mov"),
                ("Windows Media Audio", "*.wma"),
                ("flv", "*.flv"),
                ("avi", "*.avi"),
                ("mpg", "*.mpg"),
                ("mkv", "*.mkv"),
                ("音频文件", "*.mp3"),
                ("wav", "*.wav"),
                ("m4a", "*.m4a"),
                ("ogg", "*.ogg"),
                ("aac", "*.aac")
            ],
            paste_notice=';-) 点我 粘贴媒体文件'
        )

        lf_format = tk.LabelFrame(frame_format, padx=8, pady=4, text=' 输出格式 ', width=200, borderwidth=1)
        cb_format1 = tk.Checkbutton(lf_format, text=" mp3  ", variable=self.cb_format_var1)
        cb_format2 = tk.Checkbutton(lf_format, text=" m4a ", variable=self.cb_format_var2)
        cb_format3 = tk.Checkbutton(lf_format, text=" wav ", variable=self.cb_format_var3)
        cb_format1.select()
        cb_format1.bind("<Button-1>", self.format_cb_call)
        cb_format2.bind("<Button-1>", self.format_cb_call)
        cb_format3.bind("<Button-1>", self.format_cb_call)

        duration_option = MyDurationOption(frame_format, True)

        var_parent = tk.IntVar()
        cb = tk.Checkbutton(frame_group, text="保留上层目录", fg=color, variable=var_parent)

        var_meta = tk.IntVar()
        cb_meta = tk.Checkbutton(frame_group, text="保留元数据", fg=color, variable=var_meta)

        fc_out = FileChooser(
            frame_out,
            btn_text="　输出目录 ",
            action_btn_text='选择目录',
            btn_call=self.goto_out_dir,
            isFolder=True,
            hasGROOVE=True,
            text_width=82
        )

        start = Start(frame_start, text='转码', command=self.start_check)
        start.grid(column=1, row=1, sticky=tk.W)

        cb_format1.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        cb_format2.grid(column=2, row=1, sticky=tk.N + tk.S + tk.W)
        cb_format3.grid(column=3, row=1, sticky=tk.N + tk.S + tk.W)
        lf_format.grid(column=1, row=3, sticky=tk.N + tk.S + tk.W)
        duration_option.get_frame().grid(column=2, row=3, sticky=tk.N + tk.S + tk.W)

        cb.grid(column=1, row=2, sticky=tk.W)
        cb_meta.grid(column=2, row=2, sticky=tk.W)
        fc_out.grid(column=1, row=3)

        frame_file.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        frame_format.grid(column=1, row=3, sticky=tk.N + tk.S + tk.W)
        frame_group.grid(column=1, row=4, sticky=tk.N + tk.S + tk.W)
        frame_out.grid(column=1, row=5, sticky=tk.N + tk.S + tk.W)
        frame_start.grid(column=1, row=6, sticky=tk.N + tk.S + tk.W)

        self.file_chooser = file_chooser
        self.var_parent = var_parent
        self.var_meta = var_meta
        self.fc_out = fc_out
        self.start = start
        self.cb_format1 = cb_format1
        self.cb_format2 = cb_format2
        self.cb_format3 = cb_format3
        self.duration_option = duration_option

        self.auto_select()

    def auto_select(self):
        self.fc_out.set_text(setting_fftool.output_dir)

    def sync_status(self):
        self.fc_out.set_text(setting_fftool.output_dir)

    def format_cb_call(self, event):
        if event.widget == self.cb_format1:
            self.cb_format_var2.set(0)
            self.cb_format_var3.set(0)
        elif event.widget == self.cb_format2:
            self.cb_format_var1.set(0)
            self.cb_format_var3.set(0)
        elif event.widget == self.cb_format3:
            self.cb_format_var1.set(0)
            self.cb_format_var2.set(0)

    def start_check(self):
        dc = self.dc

        if setting_fftool.has_query:
            utils.showinfo("有任务正在执行，请稍后")
            return

        file_arr = self.file_chooser.get_lists()
        if not len(file_arr):
            utils.showinfo("还没有导入文件")
            return

        var2b = utils.int_var_to_bool
        var2str = utils.int_var_to_str
        b2str = utils.bool_to_str
        format1_select = var2b(self.cb_format_var1)
        format2_select = var2b(self.cb_format_var2)
        format3_select = var2b(self.cb_format_var3)
        if format1_select \
                or format2_select \
                or format3_select:
            pass
        else:
            utils.showinfo('请勾选一种输出格式')
            return

        # 剪片头片尾 检查
        time_arr = self.duration_option.start_check()
        if bool(time_arr[0]):
            # fast_select = bool(time_arr[1])
            pt_select = time_arr[2]
            pt_second = time_arr[3]
            pw_select = time_arr[4]
            pw_second = time_arr[5]
            need_remain = time_arr[6]
        else:
            return

        # # 禁用开始按钮
        self.clear_query()
        self.lock_btn(True)

        # p5 = self.outTxt['text']
        p5 = self.fc_out.get_text()

        dc["list"] = file_arr
        dc["output_dir"] = p5
        dc["keep_parent_select"] = var2str(self.var_parent)
        dc["keep_meta_select"] = var2str(self.var_meta)
        dc["format1_select"] = b2str(format1_select)
        dc["format2_select"] = b2str(format2_select)
        dc["format3_select"] = b2str(format3_select)

        dc["pt_select"] = pt_select
        dc["pt_second"] = pt_second
        dc["pw_select"] = pw_select
        dc["pw_second"] = pw_second
        dc["need_remain"] = need_remain

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

    seq = ("list", "output_dir", "keep_parent_select", "keep_meta_select",
           "format1_select", "format2_select", "format3_select",
           'fast_select',
           'pt_select',
           'pt_second',
           'pw_select',
           'pw_second',
           'need_remain'
           )

    def process(self, dc, a_str=''):
        set_title = self.start.update_query

        input_list = dc["list"]
        output_dir = dc["output_dir"] + os.sep
        temp_dir = output_dir + 'tempDir' + os.sep
        utils.make_dir(temp_dir)
        utils.hide_file(temp_dir)

        s2bool = utils.str_to_bool
        keep_parent_select = s2bool(dc["keep_parent_select"])
        keep_meta_select = s2bool(dc["keep_meta_select"])

        # format1_select = s2bool(dc["format1_select"])
        format2_select = s2bool(dc["format2_select"])
        format3_select = s2bool(dc["format3_select"])

        pt_select = dc["pt_select"]
        pw_select = dc["pw_select"]
        pt_second = dc["pt_second"] / 1000
        pw_second = dc["pw_second"] / 1000
        need_remain = dc["need_remain"]

        if format2_select:
            ext = ".m4a"
            param_a = ""
        elif format3_select:
            ext = ".wav"
            param_a = ""
        else:
            ext = ".mp3"
            param_a = " -acodec libmp3lame -ac 2 -ar 44100 -b:a 128k"

        final_mp4 = ""

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
                output_file = "{0}{1}{2}".format(output_sub_dir, p.stem, ext)
            else:
                output_file = "{0}{1}{2}".format(output_dir, p.stem, ext)

            # 任务信息
            set_title(msg_str.format(count, total, p.name))

            # 读取视频参数
            tdc = ff.get_video_info(input_file, False)
            # v_size = tdc["v_size"] if tdc["v_size"] else "1920x1080"
            # fps = tdc["fps"] if tdc["fps"] else "24"
            # tdc["fps"] = fps

            duration = float(tdc['duration']) if tdc["duration"] else 0
            duration = float(duration)
            second = duration

            if not duration:
                set_title('读取视频参数失败，不处理该视频')
                continue

            need_execute = False
            time_start = 0
            time_to = 0
            if pt_select and pt_second != 0:
                if pt_second < second:
                    time_start = pt_second
                    need_execute = True
                else:
                    set_title('片头时长超过视频时长，不进行片头修剪！！！')

            if pw_select and pw_second != 0:
                if need_remain:
                    time_to = second - pw_second
                else:
                    time_to = pw_second

                if time_to > time_start:
                    need_execute = True
                else:
                    time_to = 0
                    set_title('片尾时长在起始时间之前，不进行片尾修剪！！！')

            if need_execute:
                set_title('正在转换 修剪部分……')

            if time_start != 0:
                ss = ' -ss {}'.format(time_start)
            else:
                ss = ''

            if time_to != 0:
                to = ' -to {}'.format(time_to)
            else:
                to = ''

            # 拼接 ffmpeg 参数
            if keep_meta_select:
                param = 'ffmpeg -y -i "{in_file}"{param_a}{ss}{to} ' \
                        '-vn -hide_banner "{out_file}"'
            else:
                param = 'ffmpeg -y -i "{in_file}"{param_a}{ss}{to} -map_metadata -1 ' \
                        '-vn -hide_banner "{out_file}"'
            param = param.format(in_file=input_file, out_file=output_file, param_a=param_a, ss=ss, to=to)
            ff.execute(param)
            final_mp4 = output_file

        set_title("操作结束！")

        # 自动打开目录
        if final_mp4:
            utils.open_dir(output_dir)

        self.t1 = ""
        self.lock_btn(False)


if __name__ == "__main__":
    pass
