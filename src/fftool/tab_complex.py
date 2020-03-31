#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from pathlib import Path

import util_theme
import utils
from fftool import util_ff as ff, setting_fftool
from fftool.m_widget import FileChooser
from fftool.m_widget import NumberGroup
from fftool.m_widget import RadiobuttonOption
from fftool.m_widget import Shutdown
from fftool.m_widget import Start
from fftool.m_widget import TreeViewNew


class Main:
    """小胶水 界面"""
    shutdown_select = False
    has_shut_down = False
    is_manual_int = False
    t1 = ''
    titlePrefix = ''

    cb_fix = None
    cb_fast = None
    cb_30m = None
    fc_pt = None
    fc_pw = None
    fc_frame = None
    fc_watermark = None
    fc_number = None
    fc_out = None
    txt_smart_paste = None
    start_btn = None
    cb_shutdown = None
    file_chooser = None
    fps_option = None
    bit_rate_option = None
    final_video = ''

    def __init__(self, win):
        self.win = win
        self.var_fix = tk.IntVar()
        self.var_fast = tk.IntVar()
        self.var_30m = tk.IntVar()

    def manual_int(self):
        if self.is_manual_int:
            return
        self.is_manual_int = True
        win = self.win

        # 颜色
        color = util_theme.COLOR_BLACK

        # 导入文件 / ↑ / ↓ / - /+
        frame_top = tk.Frame(win)
        frame_center = tk.Frame(win)
        frame_file = tk.Frame(win)
        frame_group = tk.Frame(win)
        frame_bottom = tk.Frame(win)

        if utils.is_windows:
            w_arr = [30, 60 + 20, 192 + 30, 150 + 240 - 20 - 30, 70]
        else:
            w_arr = [50, 60 + 20, 220 + 30, 240 + 240 - 20 - 30, 70]
        file_chooser = TreeViewNew(frame_file,
                                   tree_num=10,
                                   file_types=[("视频文件", "*.mp4"),
                                               ("QuickTime", "*.mov"),
                                               ("avi", "*.avi"),
                                               ("mkv", "*.mkv"),
                                               ("mpg", "*.mpg")
                                               ],
                                   paste_notice=';-) 右键点我 粘贴视频文件，支持mp4、mov、avi、mkv、mpg格式',
                                   tree_widths=w_arr,
                                   has_list_btn=True
                                   )

        # listbox 和 scrollBar

        # 加片头/加片尾/加幕布/加水印 /输出目录
        f_mp4 = [("视频文件", "*.mp4")]
        f_png = [("图片文件", "*.png")]
        fc_pt = FileChooser(frame_group, cb_text="加片头　", filetypes=f_mp4, action_btn_text='浏览…', hasGROOVE=True)
        fc_pw = FileChooser(frame_group, cb_text="加片尾　", filetypes=f_mp4, action_btn_text='浏览…', hasGROOVE=False)
        fc_fr = FileChooser(frame_group, cb_text="加幕布　", filetypes=f_png, action_btn_text='浏览…', hasGROOVE=True)
        fc_wm = FileChooser(frame_group, cb_text="加水印　", filetypes=f_png, action_btn_text='浏览…', hasGROOVE=False)

        # 备案号 选择对象
        fc_number = NumberGroup(frame_group, text_width=79)

        fc_out = FileChooser(frame_group,
                             btn_text=" 输出目录 ",
                             action_btn_text='浏览…',
                             isFolder=True,
                             hasGROOVE=True,
                             btn_call=self.goto_out_dir,
                             text_width=80
                             )

        # frame_notes = tk.Frame(frame_group, padx=8, pady=-1)

        # 选项
        frame_option = tk.Frame(frame_group)

        # 帧率/码率
        fps_option = RadiobuttonOption(
            frame_option,
            title=" 帧率（FPS） ",
            options=['保持', '24', '25', '30'],
            set=1
        )
        bit_option = RadiobuttonOption(
            frame_option,
            title=" 码率（Bitrate） ",
            options=["保持", '智能', '≥4m', '≥6m', '≥8m', '≥10m'],
            set=1
        )
        tips = "爱奇艺备案号生成的视频码率固定为8m\n" \
               "有时码率可能达不到，请注意检查！（视频原码率低或画面较简单时)"

        utils.tooltip(bit_option.get_frame(), tips, 500, 5000)

        frame_option_cb = tk.Frame(frame_group)
        cb_fix = tk.Checkbutton(frame_option_cb, text="双倍时长修正", fg=color, variable=self.var_fix)
        cb_fast = tk.Checkbutton(frame_option_cb, text="极速模式", fg=color, variable=self.var_fast)
        cb_30m = tk.Checkbutton(frame_option_cb, text="30m(MPG)", fg=color, variable=self.var_30m,
                                command=self.cb_30m_call)
        cb_shutdown = Shutdown(frame_option_cb)

        tips = "输出格式为“mpg”，且码率为30m\n" \
               "爱奇艺备案号也受此选项控制"
        utils.tooltip(cb_30m, tips, 500, 5000)

        # 开始按钮
        start_btn = Start(frame_bottom, text='开始\n合成', command=self.start_check, width=80)

        # grid
        cb_fix.grid(column=2, row=2, sticky=tk.W)
        cb_30m.grid(column=3, row=2, sticky=tk.W)
        cb_shutdown.grid(column=4, row=2, sticky=tk.W)

        fps_option.grid(column=2, row=1, sticky=tk.W)
        bit_option.grid(column=3, row=1, sticky=tk.W)

        fc_pt.grid(column=1, row=1, sticky=tk.W)
        fc_pw.grid(column=1, row=2, sticky=tk.W)
        fc_fr.grid(column=1, row=3, sticky=tk.NW)
        fc_wm.grid(column=1, row=4, sticky=tk.NW)

        fc_number.grid(column=1, row=6, sticky=tk.NW)
        frame_option.grid(column=1, row=21, sticky=tk.NW)
        frame_option_cb.grid(column=1, row=22, sticky=tk.NW)
        fc_out.grid(column=1, row=25, sticky=tk.NW)

        start_btn.grid(column=1, row=1, sticky=tk.W)

        frame_top.grid(column=1, row=1, sticky=tk.NW)
        frame_center.grid(column=1, row=2, sticky=tk.NW)
        frame_file.grid(column=1, row=3, sticky=tk.NW)
        frame_group.grid(column=1, row=4, sticky=tk.NW)
        frame_bottom.grid(column=1, row=5, sticky=tk.NW)

        self.cb_fix = cb_fix
        self.cb_fast = cb_fast
        self.cb_30m = cb_30m
        self.fc_pt = fc_pt
        self.fc_pw = fc_pw
        self.fc_frame = fc_fr
        self.fc_watermark = fc_wm
        self.fc_number = fc_number
        self.fc_out = fc_out
        self.start_btn = start_btn
        self.cb_shutdown = cb_shutdown
        self.file_chooser = file_chooser
        self.fps_option = fps_option
        self.bit_rate_option = bit_option
        self.auto_select()

    def auto_select(self):
        """读取配置文件设置 ui 状态
        """
        jf = setting_fftool.read_setting()
        keys = ("pt_file", "pw_file",
                "frame_file", "watermark_file",
                "number_file", "number_file_2", "number_file_3"
                )
        keys2 = ("pt_select", "pw_select",
                 "frame_select", "watermark_select",
                 "number_select", "number_select_2", "number_select_3"
                 )

        fc_number = self.fc_number
        objs = (
            self.fc_pt, self.fc_pw,
            self.fc_frame, self.fc_watermark,
            fc_number, fc_number, fc_number
        )
        for i in range(len(objs)):
            key = keys[i]
            text = jf[key] if key in jf else ''
            if text:
                text = utils.pathlib_path(text)
            key = keys2[i]
            select_str = jf[key] if key in jf else '0'

            key = keys[i]
            if key == 'number_file':
                fc_number.set_select_and_text(1, select_str, text)
            elif key == 'number_file_2':
                fc_number.set_select_and_text(2, select_str, text)
            elif key == 'number_file_3':
                fc_number.set_select_and_text(3, select_str, text)
            else:
                objs[i].set_select_and_text(select_str, text)

        key = "number_15_select"
        select_str = jf[key] if key in jf else '0'
        self.fc_number.set_select_15(select_str)
        self.fc_out.set_text(setting_fftool.output_dir)

    def sync_status(self):
        self.manual_int()
        self.fc_out.set_text(setting_fftool.output_dir)

    def start_check(self):
        """点击 开始转码按钮
        """
        if setting_fftool.has_query:
            utils.showinfo('已经有转码任务了')
            return

        file_list = self.file_chooser.get_lists()
        if not len(file_list):
            utils.showinfo("还没有导入文件")
            return

        fc_pt = self.fc_pt
        fc_pw = self.fc_pw
        fc_frame = self.fc_frame
        fc_watermark = self.fc_watermark
        fc_number = self.fc_number
        fc_out = self.fc_out

        # 路径检查
        # 路径检查
        if not fc_pt.is_ready("片头路径设置不对"):
            return
        if not fc_pw.is_ready("片尾路径设置不对"):
            return
        if not fc_frame.is_ready("幕布路径设置不对"):
            return
        if not fc_watermark.is_ready("水印路径设置不对"):
            return
        if not fc_number.is_ready(1, "备案号图片路径设置不对"):
            return
        if not fc_number.is_ready(2, "爱奇艺 备案号设置不对"):
            return
        if not fc_number.is_ready(3, "腾讯 备案号设置不对"):
            return
        if not fc_out.is_ready("输出路径设置不对"):
            return

        select_double_fix = utils.int_var_to_str(self.var_fix)
        select_30m = utils.int_var_to_str(self.var_30m)
        fps = self.fps_option.get()
        bit = self.bit_rate_option.get()

        # 文件列表
        utils.write_txt_by_arr(setting_fftool.list_file, file_list.copy())

        # 记忆操作
        set_dc = setting_fftool.read_setting()
        # 选中状态
        set_dc["pt_select"] = fc_pt.get_select_str()
        set_dc["pw_select"] = fc_pw.get_select_str()
        set_dc["frame_select"] = fc_frame.get_select_str()
        set_dc["watermark_select"] = fc_watermark.get_select_str()
        set_dc["number_select"] = fc_number.get_select_str(1)
        set_dc["number_select_2"] = fc_number.get_select_str(2)
        set_dc["number_select_3"] = fc_number.get_select_str(3)
        set_dc["number_15_select"] = fc_number.get_select_15()
        # 片头等文件地址
        set_dc["pt_file"] = fc_pt.get_text()
        set_dc["pw_file"] = fc_pw.get_text()
        set_dc["frame_file"] = fc_frame.get_text()
        set_dc["watermark_file"] = fc_watermark.get_text()
        set_dc["number_file"] = fc_number.get_text(1)
        set_dc["number_file_2"] = fc_number.get_text(2)
        set_dc["number_file_3"] = fc_number.get_text(3)
        set_dc["output_dir"] = fc_out.get_text()
        setting_fftool.save_setting(set_dc)

        # 准备运行参数
        pt_select = fc_pt.has_select()
        pw_select = fc_pw.has_select()
        need_frame = fc_frame.has_select()
        need_watermark = fc_watermark.has_select()
        need_number = fc_number.has_select(1)
        need_number_2 = fc_number.has_select(2)
        need_number_3 = fc_number.has_select(3)

        if not pt_select and \
                not pw_select and \
                not need_frame and \
                not need_watermark and \
                not need_number and \
                not need_number_2 and \
                not need_number_3 and \
                not select_double_fix:
            utils.showinfo("没有任何合成操作，请检查！")
            return

        if self.var_30m.get():
            for mp4 in file_list:
                video_info_dc = ff.get_video_info(mp4)
                size_4m = 4 * 1024 * 1024
                bit_rate_int = int(video_info_dc["v_bit_rate"])
                if bit_rate_int < size_4m:
                    v_kb = '%.2f' % (bit_rate_int/1024)
                    utils.showinfo("30m转码方案要求视频在4m以上\n此文件码率未达标：\n{0} ({1}k)".format(mp4, v_kb))
                    # return

        # --------------------------------------------------
        # 取出参数并执行转码操作
        # 复选框 状态
        dc = dict.fromkeys(self.seq, "")
        # 选中状态
        dc["pt_select"] = pt_select
        dc["pw_select"] = pw_select
        dc["frame_select"] = need_frame
        dc["watermark_select"] = need_watermark
        dc["number_select"] = need_number
        dc["number_select_2"] = need_number_2
        dc["number_select_3"] = need_number_3
        dc["select_double_fix"] = select_double_fix
        dc["select_30m"] = select_30m
        # dc["fast_mode_select"] = fast_mode_select

        # 片头等文件地址
        dc["pt_file"] = fc_pt.get_text()
        dc["pw_file"] = fc_pw.get_text()
        dc["frame_file"] = fc_frame.get_text()
        dc["watermark_file"] = fc_watermark.get_text()
        dc["number_file"] = fc_number.get_text(1)
        dc["number_file_2"] = fc_number.get_text(2)
        dc["number_file_3"] = fc_number.get_text(3)
        dc["output_dir"] = fc_out.get_text()
        dc["fps"] = fps
        dc["bit"] = bit
        # 要处理的视频文件
        dc["number_second"] = '15' if fc_number.get_select_15() == '1' else '-1'
        dc["input_files"] = file_list

        # 禁用开始按钮
        self.start_btn.clear_query()
        # self.lock_btn(True)

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

    def lock_btn(self, is_lock):
        setting_fftool.has_query = is_lock
        enable = False if is_lock else True
        self.start_btn.set_state(enable)
        # utils.set_states(self.btn_import, self.btn_list, enable)
        # utils.set_states(self.btn_up, self.btn_down, enable)
        # utils.set_states(self.btn_remove, self.btn_add, enable)

    def update_status(self, index, status):
        self.file_chooser.update_status(index, status)

    def cb_30m_call(self):
        need = True if self.var_30m.get() else False
        if need:
            utils.showinfo('30m 转码方案 说明：\n'
                           '1、输出视频格式为 MPG；\n'
                           '2、码率恒定为30M，爱奇艺备案号的码率也将变为30M；\n'
                           '3、如果启用3个备案号，将输出3份 MPG；\n'
                           '4、原视频码率要超过4m才能转码；')

    seq = ('input_files', 'output_dir', 'number_second',
           'pt_file', 'pw_file', 'frame_file', 'watermark_file',
           'pt_select', 'pw_select', 'frame_select', 'watermark_select',
           'number_file', 'number_file_2', 'number_file_3',
           'number_select', 'number_select_2', 'number_select_3',
           'select_double_fix', 'select_30m', 'fast_mode_select', 'fps', 'bit'
           )

    def process(self, dc, _):
        set_title = self.start_btn.update_query

        lists = dc["input_files"]
        output_dir = dc["output_dir"] + os.sep
        output_dir = str(Path(output_dir)) + os.sep
        temp_dir = output_dir + 'tempDir' + os.sep
        utils.make_dir(temp_dir)
        utils.hide_file(temp_dir)

        pt_file = dc["pt_file"]
        pw_file = dc["pw_file"]
        frame_file = dc["frame_file"]
        watermark_file = dc["watermark_file"]
        number_file = dc["number_file"]
        number_file_2 = dc["number_file_2"]
        number_file_3 = dc["number_file_3"]

        pt_select = dc['pt_select']
        pw_select = dc['pw_select']
        need_frame = dc["frame_select"]
        need_watermark = dc["watermark_select"]
        need_number = dc['number_select']
        need_number_2 = dc['number_select_2']
        need_number_3 = dc['number_select_3']

        # double_fix_select = dc["double_fix_select"]
        # fast_mode_select = False
        # fast_mode_select = dc['fast_mode_select']
        rad_var = dc['fps']
        if rad_var == 2:
            fps = '24'
        elif rad_var == 3:
            fps = '25'
        elif rad_var == 4:
            fps = '30'
        else:
            fps = '0'

        # 30m方案特殊处理
        select_30m = utils.str_to_bool(dc["select_30m"])
        if select_30m:
            pt_out_file = temp_dir + "--pt.mpg"
            pw_out_file = temp_dir + "--pw.mpg"
        else:
            pt_out_file = temp_dir + "--pt.mp4"
            pw_out_file = temp_dir + "--pw.mp4"

        pf = ''
        if pt_select:
            pf = "加片头"
        if pw_select:
            pf += "加片尾"
        if need_frame:
            pf += ",加幕布"
        if need_watermark:
            pf += ",加水印"
        if need_number:
            pf += ",加备案号"
        pf = pf.strip(', ')
        self.titlePrefix = pf

        frame_size = '0x0'
        water_size = '0x0'
        number_size = '0x0'
        number_size_2 = '0x0'
        number_size_3 = '0x0'
        if need_frame and frame_file:
            frame_size = utils.get_image_size2(frame_file)

        if need_watermark and watermark_file:
            water_size = utils.get_image_size2(watermark_file)

        if need_number and number_file:
            number_size = utils.get_image_size2(number_file)
        if need_number_2 and number_file_2:
            number_size_2 = utils.get_image_size2(number_file_2)
        if need_number_3 and number_file_3:
            number_size_3 = utils.get_image_size2(number_file_3)

        # 片头持续时间
        pt_second = 0
        if pt_select and pt_file:
            print(pt_file)
            tdc = ff.get_video_info(pt_file, False)  # 匹配 尺寸和fps
            pt_second = tdc['duration'] if tdc["duration"] else '0'
            pt_second = float(pt_second)

        # 片尾持续时间
        pw_second = 0
        if pw_select and pw_file:
            tdc = ff.get_video_info(pw_file, False)  # 匹配 尺寸和fps
            pw_second = tdc['duration'] if tdc["duration"] else '0'
            pw_second = float(pw_second)

        seq = (
            ['index', -1],
            ['total', 0],
            ['rawMP4', ''],
            ['output_dir', ''],
            ['temp_dir', ''],
            ['pt_second', 0],
            ['pw_second', 0],
            ['pt_out_file', ''],
            ['pw_out_file', ''],
            ['frame_size', ''],
            ['water_size', ''],
            ['need_number', False],
            ['number_file', ''],
            ['number_size', ''],
            ['number_join_str', ''],
            ['number_join_short_str', ''],
            ['fps', 24]
        )
        # one_dc = dict.fromkeys(seq, "")
        one_dc = {}
        for key_value in seq:
            one_dc.setdefault(key_value[0], key_value[1])
        one_dc['total'] = len(lists)
        one_dc['output_dir'] = output_dir
        one_dc['temp_dir'] = temp_dir
        one_dc['pt_second'] = pt_second
        one_dc['pw_second'] = pw_second
        one_dc['pt_second'] = pt_second
        one_dc['pt_out_file'] = pt_out_file
        one_dc['pw_out_file'] = pw_out_file
        one_dc['fps'] = fps
        if need_frame and frame_file:
            one_dc['frame_size'] = frame_size
        if need_watermark and watermark_file:
            one_dc['water_size'] = water_size

        for i in range(len(lists)):
            one_dc['index'] = i
            one_dc['rawMP4'] = lists[i]

            if need_number:
                one_dc['number_join_str'] = ''
                one_dc['number_join_short_str'] = ''
                one_dc['need_number'] = need_number
                one_dc['number_file'] = number_file
                one_dc['number_size'] = number_size
                self.once_complex(dc, one_dc)

            if need_number_2:
                one_dc['number_join_str'] = '爱奇艺备案号'
                one_dc['number_join_short_str'] = '爱奇艺'
                one_dc['need_number'] = need_number_2
                one_dc['number_file'] = number_file_2
                one_dc['number_size'] = number_size_2
                self.once_complex(dc, one_dc)

            if need_number_3:
                one_dc['number_join_str'] = '腾讯备案号'
                one_dc['number_join_short_str'] = '腾讯'
                one_dc['need_number'] = need_number_3
                one_dc['number_file'] = number_file_3
                one_dc['number_size'] = number_size_3
                self.once_complex(dc, one_dc)

            # 没有备案号任务 只执行一次
            if not need_number and \
                    not need_number_2 and \
                    not need_number_3:
                one_dc['need_number'] = False
                # one_dc['number_file'] = number_file
                # one_dc['number_size'] = number_size
                # one_dc['number_join_str'] = ''
                # one_dc['number_join_short_str'] = ''
                self.once_complex(dc, one_dc)

        # 删除临时文件
        utils.remove_file(pt_out_file)
        utils.remove_file(pw_out_file)

        print("完成！\n输出目录：" + output_dir)
        set_title("操作结束！")
        set_title("")

        # 自动打开目录
        if self.final_video and os.path.exists(self.final_video):
            utils.open_file(self.final_video, True)
        else:
            utils.open_dir(output_dir)

        self.t1 = ""
        self.lock_btn(False)

        # 检查并执行关机
        self.cb_shutdown.shutdown()

    def once_complex(self, dc, one_dc):
        set_title = self.start_btn.update_query
        update_status = self.update_status

        need_number = one_dc['need_number']
        num_file = one_dc["number_file"]
        num_size = one_dc['number_size']
        num_join_str = one_dc['number_join_str']
        num_join_short_str = one_dc['number_join_short_str']
        if not num_join_short_str:
            num_join_short_str = ''
        else:
            num_join_short_str = " " + num_join_short_str

        num_second = 0
        is_iqy = True if num_join_str == '爱奇艺备案号' else False
        raw_mp4 = one_dc['rawMP4']
        i = one_dc['index']
        number_second = int(dc["number_second"])
        total = one_dc['total']

        out_dir = one_dc['output_dir']
        temp_dir = one_dc['temp_dir']
        pt_second = one_dc['pt_second']
        pw_second = one_dc['pw_second']
        pt_out_file = one_dc['pt_out_file']
        pw_out_file = one_dc['pw_out_file']
        frame_size = one_dc['frame_size']
        water_size = one_dc['water_size']

        rad_var = dc['fps']
        if rad_var == 2:
            fps = '24'
        elif rad_var == 3:
            fps = '25'
        elif rad_var == 4:
            fps = '30'
        else:
            fps = '0'
        target_fps = fps
        radio_select_var = dc["bit"]

        pt_file = dc["pt_file"]
        pw_file = dc["pw_file"]
        frame_file = dc["frame_file"]
        watermark_file = dc["watermark_file"]

        pt_select = dc['pt_select']
        pw_select = dc['pw_select']
        need_frame = dc["frame_select"]
        need_watermark = dc["watermark_select"]

        double_fix_select = utils.str_to_bool(dc["select_double_fix"])
        select_30m = utils.str_to_bool(dc["select_30m"])
        fast_mode_select = False
        # fast_mode_select = dc['fast_mode_select']

        # skip_content_mp4 = False
        count = i + 1

        set_title("")
        format_str = "(%d/%d)" % (count, total) + ' %s'

        arr = utils.get_file_names(raw_mp4)
        f_name = arr[1]
        f_type = arr[2]
        f_full_name = f_name + f_type

        out_file_type = ".mpg" if select_30m else ".mp4"
        temp_video = temp_dir + "-" + f_name + out_file_type
        final_video = out_dir + f_name + out_file_type

        if need_number and num_join_str:
            temp_path = Path(out_dir) / num_join_str
            temp_path = str(temp_path) + os.sep
            utils.make_dir(temp_path)
            final_video = temp_path + f_name + out_file_type

        vb_str = ""
        need_same_bit_rate = False
        # 1) 转正片视频
        set_title(format_str % f_full_name)
        update_status(i, '10%' + num_join_short_str)

        # 匹配 尺寸和fps
        tdc = ff.get_video_info(raw_mp4, False)
        v_size = tdc["v_size"] if tdc["v_size"] else "1920x1080"
        tdc["v_size"] = v_size
        fps = tdc["fps"] if tdc["fps"] else "24"
        tdc["fps"] = fps if target_fps == '0' else target_fps
        duration = tdc['duration'] if tdc["duration"] else '0'
        duration = float(duration)

        if is_iqy:
            vb_str = "8M"
        else:
            # 码率 部分
            if radio_select_var == 1:  # 保持
                need_same_bit_rate = True
                # tdc["crf"] = 1
                vb_str = ''

            elif radio_select_var == 2:  # 自动
                tdc["crf"] = 18
                vb_str = ''

            if radio_select_var == 3:
                vb_str = "4M"

            elif radio_select_var == 4:
                vb_str = "6M"

            elif radio_select_var == 5:
                vb_str = "8M"

            elif radio_select_var == 6:
                vb_str = "10M"

            elif radio_select_var == 7:
                vb_str = "30M"

        obj = ff.create_obj()
        obj.input_file = raw_mp4
        obj.output_file = temp_video
        obj.need_same_bit_rate = need_same_bit_rate
        obj.need_30m = select_30m
        # obj.set_video_info(tdc)
        # obj.fps = fps
        # obj.size = v_size
        obj.set_video_info(tdc, vb_str)

        if need_number:
            if number_second == -1:
                num_second = duration + pt_second + pw_second
            else:
                num_second = number_second

        if double_fix_select and duration:
            obj.time_start = 0
            obj.time_to = duration
            duration_string = ff.millisecond_to_str(int(duration * 1000))
            set_title(format_str % ("*[双倍时长修正]该视频时长：" + duration_string))

        png_list = []
        msg_str = '正在转换 正片('
        if need_frame:
            png_list.append(["加幕布", frame_file, frame_size, 0])
        if need_watermark:
            png_list.append([" 加水印", watermark_file, water_size, 0])
        if need_number:
            t = num_second - pt_second
            png_list.append([" 加备案号", num_file, num_size, t])
        if len(png_list):
            sizes = []
            times = []
            npngs = []
            for p in png_list:
                msg_str += p[0]
                npngs.append(p[1])
                sizes.append(p[2])
                times.append(p[3])
            png_list = npngs
            obj.set_overlay(png_list, sizes, times)

            msg_str += ')……'
            msg_str = msg_str.replace('()', '')
            set_title(format_str % msg_str)

        # 可以不转换片头的情况
        # 没有选择任何合成功能时，会对正片进行一次转码操作，后面会进行处理
        if not need_frame and not need_watermark and not need_number and not double_fix_select:
            skip_content_mp4 = True
        else:
            skip_content_mp4 = False
            update_status(i, '20%' + num_join_short_str)
            obj.execute()

        # 2) 有片头或片尾需要合成
        if pt_select or pw_select:
            # 生成concat.txt, 并转换片头/片尾
            subs = []
            # 1
            if pt_select:
                nobj = ff.create_obj()
                nobj.input_file = pt_file
                nobj.output_file = pt_out_file
                nobj.need_30m = select_30m
                nobj.need_same_bit_rate = need_same_bit_rate
                # nobj.fps = fps
                # nobj.size = v_size
                nobj.set_video_info(tdc, vb_str)
                # 需要添加备案号
                msg_str = "正在转换 片头"
                if need_number and num_second:
                    msg_str += '(加备案号)'
                    if pt_second < num_second:
                        nobj.set_overlay([num_file], [num_size])
                    else:
                        nobj.set_overlay([num_file], [num_size], [pt_second])

                msg_str += '……'
                set_title(format_str % msg_str)
                update_status(i, '40%' + num_join_short_str)
                nobj.execute()
                subs.append(pt_out_file)
            # 2
            if skip_content_mp4:
                if fast_mode_select and ff.compare_video(raw_mp4, pt_out_file):
                    subs.append(raw_mp4)  # 让正片参与最后的拼接，但不能删除正片
                    msg_str = "没有水印等，不转换正片，直接进行合并"
                    set_title(format_str % msg_str)
                else:
                    # 和片头的视频参数不一致，进行一次转码
                    obj.set_video_info(tdc, vb_str)  # 此操作能恢复之前的大多数参数
                    msg_str = "正在转换 正片"
                    msg_str += '……'
                    set_title(format_str % msg_str)
                    update_status(i, '50%' + num_join_short_str)
                    obj.execute()
                    subs.append(temp_video)
            else:
                subs.append(temp_video)

            # 3
            if pw_select:
                nobj = ff.create_obj()
                nobj.input_file = pw_file
                nobj.output_file = pw_out_file
                nobj.need_same_bit_rate = need_same_bit_rate
                nobj.need_30m = select_30m
                # nobj.fps = fps
                # nobj.size = v_size
                nobj.set_video_info(tdc, vb_str)

                # 需要添加备案号
                msg_str = "正在转换 片尾"
                t = pt_second + duration
                if need_number and t < num_second:
                    msg_str += '(加备案号)'
                    new_t = num_second - t
                    nobj.set_overlay([num_file], [num_size], [new_t])
                msg_str += "……"
                set_title(format_str % msg_str)
                update_status(i, '60%' + num_join_short_str)
                nobj.execute()
                subs.append(pw_out_file)

            # 拼接视频
            set_title(format_str % "拼接中……")
            update_status(i, '90%' + num_join_short_str)
            sub_txt = temp_dir + "concat_" + f_name + ".txt"
            ff.concat(subs, final_video, sub_txt)
            # 移除 concat.txt 和 mp4
            utils.remove_file(sub_txt)
            if not skip_content_mp4:
                utils.remove_file(temp_video)
        else:
            # 没有任何选项 仅对正片进行一次转码操作
            if skip_content_mp4:
                obj.execute()
                utils.move_file(temp_video, final_video)
            else:
                utils.move_file(temp_video, final_video)
        self.final_video = final_video
        update_status(i, 'OK')


if __name__ == "__main__":
    pass
