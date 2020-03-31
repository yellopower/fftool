#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from pathlib import Path

import util_theme
import utils
from fftool import util_ff as ff, setting_fftool
from fftool.m_widget import FileChooser
from fftool.m_widget import Shutdown
from fftool.m_widget import Start
from fftool.m_widget import TreeViewNew


class Main:
    """app转码
    """

    is_manual_int = False
    concatList = []
    titlePrefix = ''
    fc_out = None
    cb_size1 = None
    cb_size2 = None
    cb_tune1 = None
    cb_tune2 = None
    cb_format1 = None
    cb_format2 = None
    cb_format3 = None
    cb_format4 = None
    cb_format5 = None
    file_chooser = None
    item_shutdown = None
    start_btn = None
    fc_number = None

    keep_ratio_var = tk.IntVar()
    var_fix = tk.IntVar()
    keep_parent_var = tk.IntVar()
    cb_size_var1 = tk.IntVar()
    cb_size_var2 = tk.IntVar()
    cb_tune_var1 = tk.IntVar()
    cb_tune_var2 = tk.IntVar()
    cb_format_var1 = tk.IntVar()
    cb_format_var2 = tk.IntVar()
    cb_format_var3 = tk.IntVar()
    cb_format_var4 = tk.IntVar()
    cb_format_var5 = tk.IntVar()
    t1 = ""

    def __init__(self, parent):
        self.win = parent

        self.seq = (
            "list", "output_dir",
            "size1_select", "size2_select",
            "tune1_select", "tune2_select",
            "format1_select", "format2_select", "format3_select", "format4_select", "format5_select",
            "keep_parent_select", "keep_ratio_select", "double_fix_select",
            "number_select", "number_file"
        )
        self.dc = dict.fromkeys(self.seq, "")

    def manual_int(self):
        if self.is_manual_int:
            return
        self.is_manual_int = True
        win = self.win

        # 颜色
        color = util_theme.COLOR_BLACK

        frame_file = tk.Frame(win)
        frame_group = tk.Frame(win)
        frame_check = tk.Frame(win)
        frame_wm = tk.Frame(win)
        frame_out = tk.Frame(win)
        frame_start = tk.Frame(win)

        if utils.is_windows:
            w_arr = [30, 60, 192, 150 + 240, 70]
        else:
            w_arr = [50, 60, 220, 240 + 240, 70]
        file_chooser = TreeViewNew(
            frame_file,
            tree_num=15,
            file_types=[("视频文件", "*.mp4"),
                ("QuickTime", "*.mov"),
                ("avi", "*.avi"),
                ("mkv", "*.mkv"),
                ("mpg", "*.mpg"),
                ("ts", "*.ts")
            ],
            paste_notice=';-) 点我 粘贴媒体文件, 支持mp4、mov、avi、mkv、mpg、ts格式',
            tree_widths=w_arr,
            has_list_btn=True
        )
        # 选项
        lf_size = tk.LabelFrame(frame_group, padx=8, pady=4, text=' 分辨率 ', width=300, borderwidth=1)
        lf_tune = tk.LabelFrame(frame_group, padx=8, pady=4, text=' 画面优化 ', borderwidth=1)
        lf_format = tk.LabelFrame(frame_group, padx=8, pady=4, text=' 输出格式 ', width=200, borderwidth=1)

        cb_size1 = tk.Checkbutton(lf_size, text="流畅 (640x360)", variable=self.cb_size_var1)
        cb_size2 = tk.Checkbutton(lf_size, text="高清 (1280x720)", variable=self.cb_size_var2)
        cb_size1.select()
        cb_size2.select()

        cb_tune1 = tk.Checkbutton(lf_tune, text="动画类 (亲宝儿歌)", variable=self.cb_tune_var1)
        cb_tune2 = tk.Checkbutton(lf_tune, text="实拍类 (舞蹈学堂)", variable=self.cb_tune_var2)
        cb_tune1.select()
        cb_tune1.bind("<Button-1>", self.tune_cb_call)
        cb_tune2.bind("<Button-1>", self.tune_cb_call)

        cb_format1 = tk.Checkbutton(lf_format, text=" mp4  ", variable=self.cb_format_var1)
        cb_format2 = tk.Checkbutton(lf_format, text=" flv ", variable=self.cb_format_var2)
        cb_format3 = tk.Checkbutton(lf_format, text=" m3u8 ", variable=self.cb_format_var3)
        cb_format4 = tk.Checkbutton(lf_format, text=" ts(电信) ", variable=self.cb_format_var4)
        cb_format5 = tk.Checkbutton(lf_format, text=" ts(移动) ", variable=self.cb_format_var5)
        cb_format1.select()
        cb_format3.bind("<Button-1>", self.format_cb_call)
        cb_format4.bind("<Button-1>", self.format_cb_call)
        cb_format5.bind("<Button-1>", self.format_cb_call)

        utils.tooltip(cb_format4, "电信渠道的ts文件，分辨率统一为 1280x720", 100, 2000)
        utils.tooltip(cb_format5, "移动渠道的ts文件，分辨率统一为 1280x720", 100, 2000)

        fc_number = FileChooser(
            frame_wm,
            cb_text="加备案号",
            filetypes=[("图片文件", "*.png")],
            action_btn_text='浏览…',
            hasGROOVE=False
        )

        cb_fix = tk.Checkbutton(frame_check, text="双倍时长修正", fg=color, variable=self.var_fix)
        cb_ratio = tk.Checkbutton(frame_check, text="黑边视频", fg=color, variable=self.keep_ratio_var)
        cb = tk.Checkbutton(frame_check, text="保留上层目录", fg=color, variable=self.keep_parent_var)

        fc_number.set_cb_tooltip("目前仅支持 ts(电信)和ts(移动)转码方案", 100, 2000)
        utils.tooltip(cb_fix, "目前仅支持 ts(电信)和ts(移动)转码方案", 100, 2000)
        utils.tooltip(cb_ratio, "目前仅支持 ts(电信)和ts(移动)转码方案", 100, 2000)

        # 自动关机
        self.item_shutdown = Shutdown(frame_check)

        # 输出目录
        self.fc_out = FileChooser(
            frame_out,
            label_text="输出:",
            action_btn_text='浏览…',
            isFolder=True,
            hasGROOVE=True,
            text_width=86
        )

        # 开始转码 按钮
        self.start_btn = Start(frame_start, text='转码', command=self.start_check)
        self.start_btn.grid(column=1, row=1, sticky=tk.W)

        cb_size1.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        cb_size2.grid(column=1, row=2, sticky=tk.N + tk.S + tk.W)
        cb_tune1.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        cb_tune2.grid(column=1, row=2, sticky=tk.N + tk.S + tk.W)
        cb_format1.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        cb_format2.grid(column=2, row=1, sticky=tk.N + tk.S + tk.W)
        cb_format3.grid(column=3, row=1, sticky=tk.N + tk.S + tk.W)
        cb_format4.grid(column=1, row=2, sticky=tk.N + tk.S + tk.W)
        cb_format5.grid(column=2, row=2, sticky=tk.N + tk.S + tk.W)

        lf_size.grid(column=2, row=1)
        lf_tune.grid(column=3, row=1)
        lf_format.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)

        fc_number.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)

        cb_fix.grid(column=1, row=2, sticky=tk.W)
        cb_ratio.grid(column=2, row=2, sticky=tk.W)
        cb.grid(column=3, row=2, sticky=tk.W)
        self.item_shutdown.grid(column=4, row=2, sticky=tk.W)

        self.fc_out.grid(column=0, row=0, sticky=tk.NW)

        frame_file.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        frame_group.grid(column=1, row=2, sticky=tk.N + tk.S + tk.W)
        frame_wm.grid(column=1, row=3, sticky=tk.N + tk.S + tk.W)
        frame_check.grid(column=1, row=4, sticky=tk.N + tk.S + tk.W)
        frame_out.grid(column=1, row=5, sticky=tk.N + tk.S + tk.W)
        frame_start.grid(column=1, row=6, sticky=tk.N + tk.S + tk.W)

        self.cb_size1 = cb_size1
        self.cb_size2 = cb_size2
        self.cb_tune1 = cb_tune1
        self.cb_tune2 = cb_tune2
        self.cb_format1 = cb_format1
        self.cb_format2 = cb_format2
        self.cb_format3 = cb_format3
        self.cb_format4 = cb_format4
        self.cb_format5 = cb_format5
        self.file_chooser = file_chooser
        self.fc_number = fc_number
        self.auto_select()

    def auto_select(self):
        # 读取上次的备案号地址
        jf = setting_fftool.read_setting()
        key = "number_file"
        text = jf[key] if key in jf else ''
        if text:
            text = utils.pathlib_path(text)
            self.fc_number.set_select_and_text(0, text)

        self.fc_out.set_text(setting_fftool.output_dir)

    def sync_status(self):
        self.manual_int()
        self.fc_out.set_text(setting_fftool.output_dir)

    def start_check(self):
        dc = self.dc

        if setting_fftool.has_query:
            utils.showinfo("转码中，请稍后")
            return

        arr = self.file_chooser.get_lists()
        if not len(arr):
            utils.showinfo("还没有导入要转码的文件")
            return

        var2b = utils.int_var_to_bool
        b2str = utils.bool_to_str

        size1_select = var2b(self.cb_size_var1)
        size2_select = var2b(self.cb_size_var2)
        has_size = True if size1_select or size2_select else False
        if not has_size:
            utils.showinfo('请勾选一个分辨率')
            return

        tune1_select = var2b(self.cb_tune_var1)
        tune2_select = var2b(self.cb_tune_var2)
        format1_select = var2b(self.cb_format_var1)
        format2_select = var2b(self.cb_format_var2)
        format3_select = var2b(self.cb_format_var3)
        format4_select = var2b(self.cb_format_var4)
        format5_select = var2b(self.cb_format_var5)
        if format1_select \
                or format2_select \
                or format3_select \
                or format4_select \
                or format5_select:
            pass
        else:
            utils.showinfo('请勾选一种输出格式')
            return

        double_fix_select = var2b(self.var_fix)
        keep_parent_select = var2b(self.keep_parent_var)
        keep_ratio_select = var2b(self.keep_ratio_var)
        # # 禁用开始按钮
        self.start_btn.clear_query()
        self.lock_btn(True)

        p5 = self.fc_out.get_text()

        dc["list"] = arr
        dc["output_dir"] = p5

        dc["size1_select"] = b2str(size1_select)
        dc["size2_select"] = b2str(size2_select)
        dc["tune1_select"] = b2str(tune1_select)
        dc["tune2_select"] = b2str(tune2_select)
        dc["format1_select"] = b2str(format1_select)
        dc["format2_select"] = b2str(format2_select)
        dc["format3_select"] = b2str(format3_select)
        dc["format4_select"] = b2str(format4_select)
        dc["format5_select"] = b2str(format5_select)
        dc["keep_parent_select"] = b2str(keep_parent_select)
        dc["keep_ratio_select"] = b2str(keep_ratio_select)
        dc["double_fix_select"] = b2str(double_fix_select)

        # 水印检查处理
        if format4_select or format5_select:
            if not self.fc_number.is_ready("备案号图片路径设置不对"):
                return
        dc["number_select"] = self.fc_number.get_select_str()
        dc["number_file"] = self.fc_number.get_text()

        # 记忆操作
        set_dc = setting_fftool.read_setting()
        set_dc["output_dir"] = p5
        set_dc["number_file"] = dc["number_file"]
        setting_fftool.save_setting(set_dc)

        # 保留上次转码列表
        utils.write_txt_by_arr(setting_fftool.list_file, arr.copy())

        # 禁用开始按钮
        self.start_btn.clear_query()
        self.lock_btn(True)

        # 执行操作
        import threading
        self.t1 = threading.Thread(target=self.process, args=(dc, ''))
        self.t1.setDaemon(True)
        self.t1.start()

    def tune_cb_call(self, event):
        if event.widget == self.cb_tune1:
            self.cb_tune_var2.set(0)
        elif event.widget == self.cb_tune2:
            self.cb_tune_var1.set(0)

    def format_cb_call(self, event):
        if event.widget == self.cb_format3:
            self.cb_format_var4.set(0)
        elif event.widget == self.cb_format4:
            self.cb_format_var1.set(0)
            self.cb_format_var2.set(0)
            self.cb_format_var3.set(0)
            self.cb_format_var5.set(0)
            self.cb_size_var1.set(0)
        elif event.widget == self.cb_format5:
            self.cb_format_var1.set(0)
            self.cb_format_var2.set(0)
            self.cb_format_var3.set(0)
            self.cb_format_var4.set(0)
            self.cb_size_var1.set(0)

    @staticmethod
    def lock_btn(is_lock):
        setting_fftool.has_query = is_lock
        # enable = False if is_lock else True
        # utils.setState(self.importBtn, enable)

    def process(self, dc, add_str=''):
        set_title = self.start_btn.update_query
        write_log = utils.write_log

        input_list = dc["list"]
        output_dir_raw = dc["output_dir"] + os.sep
        temp_dir = output_dir_raw + 'tempDir' + os.sep
        utils.make_dir(temp_dir)
        utils.hide_file(temp_dir)

        log_txt = output_dir_raw + "log.txt"
        log_txt_str = log_txt.replace('\\', '/')

        s2bool = utils.str_to_bool
        size1_select = s2bool(dc["size1_select"])
        size2_select = s2bool(dc["size2_select"])
        # tune1_select = s2bool(dc["tune1_select"])
        tune2_select = s2bool(dc["tune2_select"])
        format1_select = s2bool(dc["format1_select"])
        format2_select = s2bool(dc["format2_select"])
        format3_select = s2bool(dc["format3_select"])
        format4_select = s2bool(dc["format4_select"])
        format5_select = s2bool(dc["format5_select"])
        keep_parent_select = s2bool(dc["keep_parent_select"])
        keep_ratio_select = s2bool(dc["keep_ratio_select"])
        double_fix_select = s2bool(dc["double_fix_select"])
        number_select = s2bool(dc["number_select"])
        number_file = dc["number_file"]
        if not number_select:
            number_file = ''

        final_mp4 = ""
        output_file = ""

        total = len(input_list)
        count = 0
        for i in range(total):
            count = count + 1
            input_file = input_list[i]
            p = Path(input_file)

            # 保留上层目录结构
            # 排除根目录
            path_root = "{0}{1}".format(p.drive, os.sep)
            path_parent = str(Path(p.parent).name)
            if keep_parent_select and not path_root == path_parent:
                output_dir = "{0}{1}{2}".format(output_dir_raw, path_parent, os.sep)
                utils.make_dir(output_dir)
                # output_file = "{0}{1}{2}".format(output_sub_dir, p.stem, ".mp3")
            else:
                output_dir = output_dir_raw
                # output_file = "{0}{1}{2}".format(output_dir, p.stem, ".mp3")

            # 任务信息
            if count < 2:
                set_title("本次转码将记录到日志：" + log_txt_str)

            msg_str_default = "  ({0}/{1})  {2}"
            msg_str = msg_str_default.format(count, total, '{}')
            ss = msg_str.format(p.stem)
            set_title(ss)

            # 写入日志
            ss = msg_str.format(p)
            log_str = '{0}	{1}'.format(utils.get_hms(), ss)
            write_log(log_txt, log_str)

            # 640
            # ffmpeg -i input -y -c:v libx264 -s 640x360 -crf 26 -r 15 -b:a 96k -ar 44100 -ac 2 -preset slower
            # -threads 8 -tune film output
            # ffmpeg -i input -y -c:v libx264 -s 1280x720 -crf 26 -r 24 -b:a 96k -ar 44100 -ac 2 -preset slower
            # -threads 8 -tune film output
            # -tune film
            # -tune animation
            if tune2_select:
                tune_str = 'film'
            else:
                tune_str = 'animation'

            obj = ff.create_obj()
            obj.input_file = input_file
            # obj.output_file = output_file
            # obj.size = size_str
            obj.crf = 26
            # obj.fps = fps
            obj.audio_bitrate = '96k'
            obj.other_param = '-ar 44100 -ac 2 -preset slower -threads 8'
            if tune_str:
                obj.tune = tune_str

            if size1_select:
                output_file = output_dir + p.stem + "_640.mp4"
                obj.size = '640x360'
                obj.fps = 24
                # mp4格式
                if format1_select:
                    set_title(msg_str.format('  正在生成 640 视频'))
                    obj.output_file = output_file
                    obj.execute()
                # flv格式
                if format2_select:
                    set_title(msg_str.format('  正在生成 640 视频（flv）'))
                    new_path = Path(output_file)
                    obj.output_file = Path.with_suffix(new_path, '.flv')
                    obj.execute()
                # m3u8 格式
                if format3_select:
                    set_title(msg_str.format('  正在生成 640 视频（m3u8）'))
                    save_dir = self.encode_m3u8(input_file, output_dir, True, tune_str)
                    output_file = save_dir

            if size2_select:
                output_file = output_dir + p.stem + "_1280.mp4"
                obj.size = '1280x720'
                obj.fps = 24
                # mp4格式
                if format1_select:
                    set_title(msg_str.format('  正在生成 1280 视频'))
                    obj.output_file = output_file
                    obj.execute()
                # flv格式
                if format2_select:
                    set_title(msg_str.format('  正在生成 1280 视频（flv）'))
                    new_path = Path(output_file)
                    obj.output_file = Path.with_suffix(new_path, '.flv')
                    obj.execute()

                # m3u8 格式
                if format3_select:
                    set_title(msg_str.format('  正在生成 1280 视频（m3u8）'))
                    save_dir = self.encode_m3u8(input_file, output_dir, False, tune_str)
                    output_file = save_dir

            # 电信 ts
            if format4_select:
                ss = msg_str.format('  正在生成 电信 ts ')
                if count < 2:
                    ss += '分辨率统一为 1280x720'
                set_title(ss)
                output_file = self.encode_teleconm_ts(
                    input_file,
                    output_dir,
                    tune_str,
                    number_select,
                    number_file,
                    '1920x1080',
                    15,
                    keep_ratio_select,
                    double_fix_select
                )

            # 移动 ts
            if format5_select:
                ss = msg_str.format('  正在生成 移动 ts ')
                if count < 2:
                    ss += '分辨率统一为 1280x720 (可以在输出目录的 "移动"文件夹下找到) '
                set_title(ss)
                output_file = self.encode_china_mobile_ts(
                    input_file,
                    output_dir,
                    tune_str,
                    number_select,
                    number_file,
                    '1920x1080',
                    15,
                    keep_ratio_select,
                    double_fix_select
                )
                # obj.full_param = arr[0]
                # obj.execute()
                # output_file = arr[1]

            final_mp4 = output_file
            obj.destroy()

        set_title("操作结束！")
        set_title("")

        # 自动打开目录
        if final_mp4:
            utils.open_file(final_mp4, True)

        self.t1 = ""
        self.lock_btn(False)

        # 检查并执行关机
        self.item_shutdown.shutdown()

    @staticmethod
    def encode_m3u8(input_file, output_dir, is_640=False, tune_str='animation'):
        s = 'ffmpeg -hide_banner -re -y -i "{in_file}" {param} "{out_ts}" "{out_m3u8}"'

        param_640 = "-c:v libx264 " \
                    "-s 640x360 " \
                    "-crf 28 " \
                    "-r 15 " \
                    "-g 60 " \
                    "-b:a 96k " \
                    "-ar 44100 " \
                    "-ac 2 " \
                    "-preset slower " \
                    "-threads 8"

        param_1280 = "-c:v libx264 " \
                     "-s 1280x720 " \
                     "-crf 26 " \
                     "-r 24 " \
                     "-g 48 " \
                     "-b:a 128k " \
                     "-ar 44100 " \
                     "-ac 2 " \
                     "-preset slower " \
                     "-threads 8"

        # param_hls = "-map 0 -f hls -hls_time 10 -hls_list_size 0 -use_localtime_mkdir 1 -hls_segment_filename"
        param_segment = '-map 0 ' \
                        '-f hls ' \
                        '-bsf:v h264_mp4toannexb ' \
                        '-hls_time 10 ' \
                        '-hls_flags split_by_time ' \
                        '-hls_list_size 0 ' \
                        '-hls_allow_cache 1 ' \
                        '-hls_segment_filename'

        # 创建输出目录
        p = Path(input_file)
        save_dir = output_dir + str(p.stem)
        save_dir += '_640' if is_640 else '_1280'
        save_dir += '_m3u8' + os.sep
        utils.remove_file(save_dir, False)
        utils.make_dir(save_dir)

        # 输出文件名
        m3u8_file = save_dir + 'playlist.m3u8'
        ts_file = save_dir + '%06d.ts'

        # 拼接参数
        param_video = param_640 if is_640 else param_1280
        param_final = '{param_video} -tune {tune} {param_segment}'
        param_final = param_final.format(param_video=param_video, tune=tune_str, param_segment=param_segment)
        s = s.format(in_file=input_file, param=param_final, out_m3u8=m3u8_file, out_ts=ts_file)
        ff.execute(s)

        return save_dir

    def encode_teleconm_ts(self, input_file, output_dir, tune_str='animation', png_select=False, png_path='',
                           size='1920x1080', t=15, keep_ratio=False, double_fix_select=False):
        format_str = 'ffmpeg -hide_banner -y -i "{in_file}" {param} "{out_ts}"'

        param = "-c:v libx264 " \
                "-x264-params nal-hrd=cbr:force-cfr=1:keyint_min=25:keyint=250:b-pyramid=2:bframes=3:qcomp=0.00 " \
                "-b:v 6000k " \
                "-minrate 6000k " \
                "-maxrate 6000k " \
                "-bufsize 3000k " \
                "-muxrate 6384k " \
                "-profile:v main -level 4.0 " \
                "-r 25 " \
                "-s 1280x720 " \
                "-aspect 16:9 " \
                "-pix_fmt yuv420p " \
                "-refs:v 3 " \
                "-threads 8 " \
                "-map_metadata -1 " \
                "-ab 192k " \
                "-ar 48000 " \
                "-ac 2"

        # 创建输出目录
        p = Path(input_file)
        # save_dir = output_dir + str(p.stem)
        # save_dir += os.sep
        # utils.remove_file(save_dir, False)
        # utils.make_dir(save_dir)

        # 双倍时长修正
        if double_fix_select:
            tdc = ff.get_video_info(input_file, False)  # 匹配 尺寸和fps
            duration = tdc['duration'] if tdc["duration"] else '0'
            duration = float(duration)
            if duration:
                ss = duration
                if isinstance(ss, int) or isinstance(ss, float):
                    ss = ss * 1000
                    ss = int(ss)
                    ss = ff.millisecond_to_str(ss)
                    param += ' -to {}'.format(ss)

                    set_title = self.start_btn.update_query
                    duration_string = ff.millisecond_to_str(int(duration * 1000))
                    set_title("*[双倍时长修正]该视频时长：" + duration_string)

        # 输出文件名
        ts_file = output_dir + p.stem + ".ts"

        if keep_ratio:
            w = 1280
            h = 720
            # 获取当前视频的分辨率和缩放比
            v_dc = ff.get_video_info(input_file)
            v_size = v_dc['v_size']
            v_arr = v_size.split("x")
            vw = int(v_arr[0])
            vh = int(v_arr[1])
            scale = min(w / vw, h / vh)
            w_real = round(vw * scale)
            h_real = round(vh * scale)
            x = round((w - w_real) / 2)
            y = round((h - h_real) / 2)
            con_vf = 'scale={w_real}:{h_real},pad={w}:{h}:{x}:{y}:black'
            con_vf = con_vf.format(w=w, h=h, x=x, y=y, w_real=w_real, h_real=h_real)
        else:
            con_vf = ''

        # 拼接参数
        param_final = '{param} -tune {tune}'.format(param=param, tune=tune_str)

        # 添加水印参数 水印图片作为输入管道 需参数之前 pngs = ['/Users/qinbaomac-mini/Library/Mobile
        # Documents/com~apple~CloudDocs/Dev/python/py_pack/res/备案号-爱奇艺.png'] sizes = ["1920x1080"] times = [15]
        if png_select:
            if os.path.exists(png_path):
                param_final = ' -i "{0}" {1}'.format(png_path, param_final)
                param_overlay = ff.get_overlay([png_path], [size], [t], [], True)
                if con_vf:
                    param_overlay = param_overlay.replace('-filter_complex "', '-filter_complex "' + con_vf + ',')
                    con_vf = ''
                param_final = '{0} {1} '.format(param_final, param_overlay)
            else:
                print('水印图片地址不正确 "{}"'.format(png_path))
        # 黑边视频参数
        if con_vf:
            con_vf = '-filter_complex "{}"'.format(con_vf)
            param_final = '{0} {1} '.format(param_final, con_vf)

        final_str = format_str.format(in_file=input_file, param=param_final, out_ts=ts_file)
        print(final_str)
        ff.execute(final_str)

        return ts_file

    def encode_china_mobile_ts(self, input_file, output_dir, tune_str='animation', png_select=False, png_path='',
                               size='1920x1080', t=15, keep_ratio=False, double_fix_select=False):
        format_str = 'ffmpeg -hide_banner -y -i "{in_file}" {param} "{out_ts}"'

        param = "-c:v libx264 " \
                "-b:v 3.8m " \
                "-minrate 2.5m " \
                "-maxrate 4m " \
                "-profile:v high -level 4.1 " \
                "-s 1280x720 " \
                "-r 25 " \
                "-coder cabac " \
                "-refs:v 3 " \
                "-x264opts b-pyramid=0 " \
                "-c:a aac " \
                "-profile:a aac_low " \
                "-b:a 128k " \
                "-ar 48000 " \
                "-ac 2 " \
                "-map_metadata -1 " \
                "-preset slower"

        # 创建输出目录
        p = Path(input_file)
        # save_dir = output_dir + str(p.stem)
        # save_dir += os.sep
        # utils.remove_file(save_dir, False)
        # utils.make_dir(save_dir)

        # 双倍时长修正
        if double_fix_select:
            tdc = ff.get_video_info(input_file, False)  # 匹配 尺寸和fps
            duration = tdc['duration'] if tdc["duration"] else '0'
            duration = float(duration)
            if duration:
                ss = duration
                if isinstance(ss, int) or isinstance(ss, float):
                    ss = ss * 1000
                    ss = int(ss)
                    ss = ff.millisecond_to_str(ss)
                    param += ' -to {}'.format(ss)

                    set_title = self.start_btn.update_query
                    duration_string = ff.millisecond_to_str(int(duration * 1000))
                    set_title("*[双倍时长修正]该视频时长：" + duration_string)

        # 输出文件名
        save_dir = output_dir + "移动/"
        ts_file = save_dir + p.stem + ".ts"
        utils.make_dir(save_dir)

        if keep_ratio:
            w = 1280
            h = 720
            # 获取当前视频的分辨率和缩放比
            v_dc = ff.get_video_info(input_file)
            v_size = v_dc['v_size']
            v_arr = v_size.split("x")
            vw = int(v_arr[0])
            vh = int(v_arr[1])
            scale = min(w / vw, h / vh)
            w_real = round(vw * scale)
            h_real = round(vh * scale)
            x = round((w - w_real) / 2)
            y = round((h - h_real) / 2)
            con_vf = 'scale={w_real}:{h_real},pad={w}:{h}:{x}:{y}:black'
            con_vf = con_vf.format(w=w, h=h, x=x, y=y, w_real=w_real, h_real=h_real)
        else:
            con_vf = ''

        # 拼接参数
        param_final = '{param} -tune {tune}'.format(param=param, tune=tune_str)

        # 添加水印参数 水印图片作为输入管道 需参数之前 pngs = ['/Users/qinbaomac-mini/Library/Mobile
        # Documents/com~apple~CloudDocs/Dev/python/py_pack/res/备案号-爱奇艺.png'] sizes = ["1920x1080"] times = [15]
        if png_select:
            if os.path.exists(png_path):
                param_final = ' -i "{0}" {1}'.format(png_path, param_final)
                param_overlay = ff.get_overlay([png_path], [size], [t], [], True)
                if con_vf:
                    param_overlay = param_overlay.replace('-filter_complex "', '-filter_complex "' + con_vf + ',')
                    con_vf = ''
                param_final = '{0} {1} '.format(param_final, param_overlay)
            else:
                if png_path:
                    print('水印图片地址不正确 "{}"'.format(png_path))
        # 黑边视频参数
        if con_vf:
            con_vf = '-filter_complex "{}"'.format(con_vf)
            param_final = '{0} {1} '.format(param_final, con_vf)

        final_str = format_str.format(in_file=input_file, param=param_final, out_ts=ts_file)
        print(final_str)
        ff.execute(final_str)

        return ts_file


if __name__ == "__main__":
    pass
