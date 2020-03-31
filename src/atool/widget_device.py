# -*- coding: utf-8 -*-


import os
import re
import threading
import tkinter as tk
import tkinter.font as tk_font
from pathlib import Path
from tkinter import filedialog
from tkinter import ttk

import util_theme
import utils
from atool import util_atool
from atool import win_remote
from atool import setting_atool as setting
from fftool.m_widget import IPanel


class DeviceItem(IPanel):
    serial = ''
    data = None

    def __init__(self, _parent):
        IPanel.__init__(self, _parent)
        # cb_text = kw['cb_text'] if 'cb_text' in kw else ''
        frame = self.frame
        color = util_theme.COLOR_BLACK

        font_name = '微软雅黑' if utils.is_windows else 'Yuanti SC'
        font_size = 16 if utils.is_windows else 20
        tf = tk_font.Font(size=font_size, family=font_name)

        txt = tk.LabelFrame(frame, fg=color, font=tf, relief='groove', borderwidth=2)
        txt.grid(column=1, row=1, sticky=tk.NE)

        am = ActionControl(txt)
        am.grid(column=2, row=2)

        self.am = am
        self.txt = txt

    def set_serial(self, _serial):
        """设置设备的序列号"""
        d = DeviceData(_serial)
        d.getprop()
        util_atool.device_data_append(d)

        if d.is_device:
            n = d.product_name
        else:
            n = "{0}  ({1})".format(d.product_name, d.ip)

        self.serial = _serial
        self.txt['text'] = n

        self.am.set_serial(d)

    def destroy(self):
        tup = (self.frame, self.txt, self.am)
        for w in tup:
            w.destroy()
        del tup


class ActionControl(IPanel):
    """应用管理 小部件"""
    serial = ''
    p_list = []
    n_list = []

    t1 = ''
    t2 = ''
    _data = None
    last_apk = ''

    def __init__(self, _parent):
        IPanel.__init__(self, _parent)
        frame = self.frame

        self.th = utils.thread_func
        self.msg = util_atool.show_msg

        # frame = tk.LabelFrame(_parent, text=' 指令列表 ', fg=util_theme.COLOR_GRAP2, borderwidth=1, padx=4, pady=4)

        # 包名下拉框
        btn_frame = tk.Frame(frame)
        cbb_item = PackageCombobox(frame)

        cbb = ttk.Combobox(btn_frame, width=18, state='readonly', height=20, justify='center')
        cbb.bind("<<ComboboxSelected>>", self.cbb_call)
        # utils.tooltip(cbb, '选择下拉项即执行操作')
        utils.tooltip(cbb, '选择下拉项改变按钮功能')

        btn = tk.Button(btn_frame, text="Go", width=12, fg=util_theme.COLOR_BLACK)
        utils.bind(btn, self.btn_call)
        utils.bind(btn, self.btn_call, True)

        frame_btn_group = tk.Frame(btn_frame)
        # btn_am = tk.Button(frame_btn_group, text="应用管理", width=6)
        btn_screen = tk.Button(frame_btn_group, text="截屏", width=6)
        btn_install = tk.Button(frame_btn_group, text="安装", width=6)
        btn_log = tk.Button(frame_btn_group, text="日志", width=6)
        # utils.bind(btn_am, self.btn_group_call)
        # utils.bind(btn_am, self.btn_group_call, True)
        utils.bind(btn_screen, self.btn_group_call)
        utils.bind(btn_screen, self.btn_group_call, True)
        utils.bind(btn_install, self.btn_group_call)
        utils.bind(btn_install, self.btn_group_call, True)
        utils.bind(btn_log, self.btn_group_call)
        utils.bind(btn_log, self.btn_group_call, True)

        utils.tooltip(btn_screen, "左键截屏并自动打开图片\n右键截屏不自动打开图片", 800)
        utils.tooltip(btn_install, "左键点击 安装\n右键点击 安装剪贴板里的apk", 800)
        utils.tooltip(btn_log, "左键获取日志\n右键清除日志", 800)

        utils.set_groove((btn, btn_screen, btn_install, btn_log))

        # btn_am.grid(column=1, row=1, sticky=tk.NW)
        btn_screen.grid(column=2, row=1, sticky=tk.NW)
        btn_install.grid(column=3, row=1, sticky=tk.NW)
        btn_log.grid(column=4, row=1, sticky=tk.NW)

        cbb.grid(column=1, row=1, sticky=tk.NW)
        btn.grid(column=2, row=1, sticky=tk.NW)
        tk.Label(btn_frame, width='4').grid(column=3, row=1, sticky=tk.NW)
        frame_btn_group.grid(column=4, row=1)

        # cbb_item.grid(1, 2, tk.NW)
        btn_frame.grid(column=1, row=1, sticky=tk.NW)

        self.btn = btn
        self.cbb_item = cbb_item
        self.cbb = cbb
        self.cbb_ops = None
        # self.btn_am = btn_am
        self.btn_screen = btn_screen
        self.btn_install = btn_install
        self.btn_log = btn_log

    def set_serial(self, _data):
        self.serial = _data.serial
        self._data = _data

        c = [
             ['启动', OP.RUN],
             ['退出', OP.STOP],

             ['', OP.SEPARATOR],
             ['卸载', OP.UNINSTALL],
             ['清除数据', OP.CLEAR],
             ['前台运行', OP.ACTIVITY_CUR_RUN],
             ['输入文本', OP.SEND_Text],
             ['Clipper', OP.CLIPPER],
             ['遥控器', OP.REMOTER],

             ['', OP.SEPARATOR],
             ['应用列表', OP.AM_LIST],
             ['下载apk', OP.PULL_APK],

             ['', OP.SEPARATOR],
             ['录屏 1分钟', OP.REC_60],
             ['录屏 3分钟', OP.REC_180],
             ['录屏 5分钟', OP.REC_300],

             ['', OP.SEPARATOR],
             ['Scrcpy', OP.SCRCPY],
             # ['华为一键解锁', OP.HUAWEI_UNLOCK],
             ['系统设置', OP.OPEN_SETTINGS],
             ['布局边界', OP.DEBUG_LAYOUT],

             ['', OP.SEPARATOR],
             ['分辨率 自定义', OP.SIZE_CUSTOM],
             ['分辨率 还原', OP.SIZE_ORIGINAL],

             ['', OP.SEPARATOR],
             ['adb命令', OP.COPY_CMD],
             ['设备信息', OP.DEVICE_INFO]]
        if self._data.is_device:
            c.append(["开启 wifi调试", OP.WIFI_DEBUG])
        else:
            c.append(["断开连接", OP.DISCONNECT])
        # c.append(["----------", OP.SEPARATOR])

        values = []
        types = []
        i = 0
        for arr in c:
            op = arr[1]
            values.append(arr[0])
            types.append(op)
            i += 1
        cbb = self.cbb
        cbb['values'] = tuple(values)
        self.cbb_ops = types
        self.cbb_current(0)
        self.cbb_call('')

    def cbb_current(self, _index):
        """选中一个下拉项"""
        self.cbb.current(_index)
        s = self.cbb.get()
        utils.tooltip(self.btn, "点击执行 " + s, 800)

    def cbb_call(self, _):
        index = self.cbb.current()
        op = self.cbb_ops[index]
        if op == OP.SEPARATOR:
            s = ''
        else:
            s = self.cbb.get()

        tips = "点击执行 " + s

        if op == OP.INSTALL:
            tips = "左键点击 " + s
            tips += "\n右键点击 安装剪贴板里的apk"

        elif op == OP.AM_LIST:
            tips = "成功后将拷贝到剪贴板, 请粘贴后使用！\n" \
                   "左键点击 读取用户安装的应用信息，" + s
            tips += "\n右键点击 获取全部的应用信息"

        elif op == OP.CLEAR:
            tips = "左键点击 " + s
            tips += "\n右键点击 清除数据并启动应用"

        elif op == OP.SCREEN_SHOT:
            tips = "左键点击 " + s
            tips += "\n右键点击 截图 不自动打开截图文件"

        elif op == OP.SIZE_CUSTOM:
            tips = "左键点击 更改至自定义的分辨率" \
                   "\n右键点击 查询当前配置信息" \
                   "\n前往设置界面单独设置 宽x高 和 DPI 信息"

        elif op == OP.SIZE_SCALE:
            tips = "左键点击 2倍"
            tips += "\n右键点击 3倍"

        elif op == OP.SIZE_ORIGINAL:
            tips = "左键点击 " + s
            tips += "\n右键点击 查询当前分辨率信息"

        elif op == OP.DEBUG_LAYOUT:
            tips = "左键点击 显示布局边界"
            tips += "\n右键点击 关闭布局边界"

        elif op == OP.ACTIVITY_CUR_RUN:
            tips = "左键点击 " + s
            tips += "\n右键点击 仅获取前台运行程序的包名"

        elif op == OP.CLIPPER:
            tips = "左键点击 发送文本到安卓剪贴板" \
                   "\n右键点击 获取安卓剪贴板的文本" \
                   "\n备注：1.支持输入中文，但不支持空格等特殊符号" \
                   "\n2.’此功能需要设备上安装 Clipper 才能使用" \
                   "\nhttps://github.com/majido/clipper/releases"

        elif op == OP.STOP:
            tips = "左键点击 {} （指定包名的)".format(s)
            tips += "\n右键点击 {} (正在运行的)".format(s)

        elif op == OP.PULL_APK:
            # 下载apk
            tips = "左键点击 {} （指定包名的)".format(s)
            tips += "\n右键点击 {} （正在运行的)".format(s)

        elif op == OP.UNINSTALL:
            # 卸载应用
            tips = "左键点击 {}".format(s)
            tips += "\n右键点击 {} (保留数据)".format(s)

        elif op == OP.RUN:
            # 启动应用
            tips = "左键点击 {}".format(s)
            tips += "\n右键点击 重启正在运行的应用".format(s)

        elif op == OP.SCRCPY:
            arr_win = [
                "设备 BACK 键 Ctrl+B | 鼠标右键",
                "设备 HOME 键 Ctrl+H | 鼠标中键",
                "设备 任务管理 键 (切换APP) Ctrl+S",
                "设备 菜单 键 Ctrl+M",
                "设备音量+键 Ctrl+↑",
                "设备音量-键 Ctrl+↓",
                "设备电源键 Ctrl+P",
                "复制内容到设备 Ctrl+V",
                "点亮手机屏幕 鼠标右键",
                "安装APK 将 apk 文件拖入投屏",
                "传输文件到设备 将文件拖入投屏（非apk）"
            ]
            arr_mac = [
                "设备 BACK 键 ⌘+B | 鼠标右键",
                "设备 HOME 键 Ctrl+H | 鼠标中键",
                "设备 任务管理 键 (切换APP) ⌘+S",
                "设备 菜单 键 Ctrl+M",
                "设备音量+键 ⌘+↑",
                "设备音量-键 ⌘+↓",
                "设备电源键 ⌘+P",
                "复制内容到设备 ⌘+V",
                "点亮手机屏幕 鼠标右键",
                "安装APK 将 apk 文件拖入投屏",
                "传输文件到设备 将文件拖入投屏（非apk）"
            ]
            arr = arr_win if utils.is_windows else arr_mac
            tips = "左键点击 " + s
            tips += "\n\nscrcpy操作说明：\n" + "\n".join(arr)

        utils.tooltip(self.btn, tips, 800)
        if op[0:6] == "_need_":
            self.grid_cbb_package()
        else:
            self.grid_cbb_package(False)

        # self.btn['text'] = s
        # self.process()

    def find_op_index(self, op_str):
        # 查找op字符在下拉列表的索引值
        i = 0
        for op in self.cbb_ops:
            if op == op_str:
                return i
            i += 1
        return -1

    def btn_call(self, event):
        is_right = utils.is_right_click(event.num)
        self.process(is_right)

    def btn_group_call(self, event):
        is_right = utils.is_right_click(event.num)
        op = ''
        if event.widget == self.btn_screen:
            op = OP.SCREEN_SHOT
        elif event.widget == self.btn_install:
            op = OP.INSTALL
        elif event.widget == self.btn_log:
            if is_right:
                op = OP.LOG_CLEAR
                is_right = False
            else:
                op = OP.LOG_FAST
        if op:
            self.process(is_right, op)

    def process(self, is_right_click=False, op=''):
        if not op:
            index = self.cbb.current()
            op = self.cbb_ops[index]

        if op == OP.SEPARATOR:
            return

        if op[0:6] == "_need_":
            need_cbb = True
        else:
            need_cbb = False
        # 需要包名时，判断包名
        # 合格的包名添加到下拉列表
        package = self.cbb_item.get_package()
        if need_cbb:
            if not package:
                utils.showinfo('请 选择/输入 包名')
                return
            if package.count('.') < 2:
                utils.showinfo('包名无效')
                return
            self.cbb_item.append(package)

        # 检查设备断开情况
        serial = self.serial
        d_list = util_atool.devices(False)['device']
        if not OP.DISCONNECT and not d_list.count(serial):
            utils.showinfo('此设备已断开连接')
            return

        rec_second = 0

        # 启动应用
        if op == OP.RUN:
            self.op_run(is_right_click)

        # 退出应用
        elif op == OP.STOP:
            self.op_am_stop(is_right_click)

        # 清除数据
        elif op == OP.CLEAR:
            self.op_pm_clear(package, is_right_click)

        # 当前正在运行
        elif op == OP.ACTIVITY_CUR_RUN:
            self.op_am_cur(is_right_click)

        # 卸载应用
        elif op == OP.UNINSTALL:
            self.op_uninstall(is_right_click)

        # 应用列表
        elif op == OP.AM_LIST:
            self.op_am_list(is_right_click)

        # 下载apk
        elif op == OP.PULL_APK:
            self.op_pull_apk(is_right_click)

        # 设备信息
        elif op == OP.DEVICE_INFO:
            self.op_device_info()

        # 命令行
        elif op == OP.COPY_CMD:
            self.op_copy_cmd()

        # 发送文本
        elif op == OP.SEND_Text:
            self.op_send_text()

        # 发送文本，配合 clipper
        elif op == OP.CLIPPER:
            self.op_clipper(is_right_click)

        # log
        elif op == OP.LOG_CLEAR:
            self.op_log_clear()
        elif op == OP.LOG_FAST:
            self.op_log_fast()

        # 布局边界
        elif op == OP.DEBUG_LAYOUT:
            self.op_layout(is_right_click)

        # 断开连接
        elif op == OP.DISCONNECT:
            self.op_disconnect()

        # 开启wifi调试
        elif op == OP.WIFI_DEBUG:
            self.op_wifi_debug()

        # 显示遥控器
        elif op == OP.REMOTER:
            self.op_remote()

        # 安装
        elif op == OP.INSTALL:
            self.op_install(is_right_click)

        # scrcpy
        elif op == OP.SCRCPY:
            self.op_scrcpy()

        # 更改分辨率
        elif op == OP.SIZE_CUSTOM:
            self.op_size(op, is_right_click)
        elif op == OP.SIZE_SCALE:
            self.op_size(op, is_right_click)
        elif op == OP.SIZE_ORIGINAL:
            self.op_size(op, is_right_click)

        # 华为手机一键解锁
        elif op == OP.HUAWEI_UNLOCK:
            self.op_huawei_unlock()

        # 打开设置
        elif op == OP.OPEN_SETTINGS:
            self.op_open_settings()

        # 截屏
        elif op == OP.SCREEN_SHOT:
            self.op_screen_shot(is_right_click)

        # 录屏
        elif op == OP.REC_30:
            rec_second = 30
        elif op == OP.REC_60:
            rec_second = 60
        elif op == OP.REC_120:
            rec_second = 130
        elif op == OP.REC_180:
            rec_second = 180
        elif op == OP.REC_300:
            rec_second = 300
        if rec_second:
            self.op_record(rec_second)

    def op_run(self, is_right=False):
        """启动应用"""
        serial = self.serial
        if not is_right:
            package = self.cbb_item.get_package()
            self.msg("正在启动应用...")
            self.th(util_atool.am_start, (serial, package))
        else:
            self.msg("正在重启正在运行的应用...")
            self.th(util_atool.run_current_again, (serial, ))

    def op_uninstall(self, is_right=False):
        """卸载"""
        serial = self.serial
        package = self.cbb_item.get_package()
        if not is_right:
            s = "是否卸载" + package
            utils.alert(s, self.uninstall, [package, False, serial])
        else:
            self.msg("卸载一个应用，但保留此应用的数据...")
            s = "是否卸载" + package
            utils.alert(s, self.uninstall, [package, True, serial])

    def op_pm_clear(self, package, is_right=False):
        """ 清除数据 """
        s = util_atool.pm_clear(self.serial, package)
        utils.showinfo(s)
        if is_right:
            self.msg("清除数据{0},正在启动 {1}...".format(s, package))
            util_atool.am_start(self.serial, package)
        else:
            utils.showinfo(s)

    def op_am_cur(self, is_right=False):
        """查看前台运行"""
        self.th(self.p_am_cur, (is_right, ))

    def p_am_cur(self, is_right=False):
        self.msg("正在查询 前台运行...")
        s = util_atool.activity_current(self.serial, is_right)
        utils.clipboard_set(s)
        if is_right:
            if s and len(s.split(" ")) == 1:
                self.cbb_item.append(s)
                self.cbb_item.set(s)
                self.grid_cbb_package()
                self.msg("前台正在运行：{}，已加入包名下拉框并复制到剪贴板中".format(s))
            else:
                self.msg("找不到 前台正在运行".format(s))

        else:
            self.msg("前台正在运行：{}，已拷贝到剪贴板".format(s))

    def op_am_stop(self, is_right=False):
        """退出"""
        if not is_right:
            package = self.cbb_item.get_package()
            self.msg("正在停止应用...")
            self.th(util_atool.am_force_stop, (self.serial, package))
        else:
            self.msg("正在退出 前台运行...")
            self.th(util_atool.stop_current, (self.serial,))

    def op_am_list(self, is_right=False):
        """获取应用列表"""
        self.th(self.am_list, (self.serial, is_right))

    def op_pull_apk(self, is_right=False):
        """下载apk"""
        serial = self.serial
        if is_right:
            # 前台运行
            self.msg("正在查询 前台运行...")
            s = util_atool.activity_current(serial, True)
            if len(s.split(" ")) == 1:
                self.th(self.pull_apk, (serial, s))
            else:
                self.msg("找不到包名！！！")
        else:
            # 指定包名
            package = self.cbb_item.get_package()
            self.th(self.pull_apk, (serial, package))

    def op_device_info(self):
        """显示设备信息窗口"""
        self.th(self.show_info, (self._data,))

    def op_copy_cmd(self):
        """拷贝命令行"""
        s = util_atool.get_cmd_with_serial(self.serial)
        utils.clipboard_set(s)
        desc = '命令行' if utils.is_windows else '终端'
        self.msg("已复制到剪贴板，请粘贴到{0}上使用\n{1}".format(desc, s))

    def op_send_text(self):
        """发送文本 仅限字母和数字"""
        self.th(self.send_input, (self.serial,))

    def op_clipper(self, is_right_click):
        """发送文本，配合 clipper"""
        self.th(self.send_input_clipper, (self.serial, is_right_click))

    def op_log_clear(self):
        """清除日志"""
        self.th(util_atool.log_clear, (self.serial,))
        self.msg("日志已清除！")
        i = self.find_op_index(OP.LOG_FAST)
        if i > -1:
            self.cbb.current(i)

    def op_log_fast(self):
        """获取日志"""
        self.th(self.log_fast, (self.serial,))

    def op_layout(self, is_right_click):
        """布局边界"""
        enable = not is_right_click
        if enable:
            s = "显示 布局边界"
        else:
            s = "关闭 布局边界"

        self.msg(s)
        self.th(util_atool.debug_layout, (self.serial, enable))

    def op_disconnect(self):
        """断开wifi调试"""
        serial = self.serial
        if not len(utils.find_ip(serial)):
            self.msg("仅对wifi连接的设备有效\n此设备为{}".format(serial))
        else:
            self.msg("正在断开 {}".format(serial))
            util_atool.disconnect(serial)
        if utils.main is not None:
            utils.main.show_devices()

    def op_wifi_debug(self):
        """开启wifi调试"""
        ip = self._data.ip
        if not ip:
            utils.showinfo('没有找到ip地址')
            return
        self.msg("正在开启wifi调试, 此设备的ip为 {}".format(ip))
        self.th(self.open_wifi_debug, (self.serial, ip))

    def op_remote(self):
        """显示遥控器"""
        self.show_remote(self._data)
        self.msg("遥控器已瞄准 " + self._data.product_name)
        # if utils.main is not None:
        #     utils.main.show_devices()

    def op_screen_shot(self, is_right_click=False):
        """截屏"""
        if is_right_click:
            msg_str = "正在截屏(不自动打开截图文件)..."
            auto_open = False
        else:
            msg_str = "正在截屏..."
            if setting.need_auto_open() == '1':
                auto_open = True
            else:
                auto_open = False
        self.msg(msg_str)
        self.th(util_atool.screen_capture, (self.serial, auto_open))

    def op_install(self, is_right_click=False):
        """安装apk"""
        if is_right_click:  # 从剪贴板中安装
            func = self.install_by_clipboard
        else:
            func = self.install_by_select
        self.th(func, (self.serial,))

    def op_scrcpy(self):
        """启动scrcpy投屏"""
        if self._data.can_i_scrcpy():
            self.th(util_atool.scrcpy, (self.serial,))

    def op_size(self, op, is_right_click=False):
        """ 更改分辨率和屏幕密度操作 """
        serial = self.serial
        size_str = ''
        density_str = ''

        # 还原
        if op == OP.SIZE_ORIGINAL:
            size_arr = util_atool.get_resolution(serial)
            density_arr = util_atool.get_density(serial)
            size_str = size_arr[0]
            density_str = density_arr[0]

            # 右键只进行查询
            if is_right_click:
                s = "分辨率信息为：\n宽x高：{0}，DPI:{1}".format(size_str, density_str)
                s += "\nsize：{0}，density:{1}".format(size_arr, density_arr)
                utils.showinfo(s)
                return
            else:
                s = "分辨率 还原，size：{0}\tdensity：{1}".format(size_arr, density_arr)
                print(s)
                self.msg(s)

        # 等比缩放
        elif op == OP.SIZE_SCALE:
            scale = 3 if is_right_click else 2

            size_arr = util_atool.get_resolution(serial)
            s = size_arr[0]
            arr = s.split("x")
            w = int(arr[0])
            h = int(arr[1])
            # density_str = density_arr[0]
            size_str = "{0}x{1}".format(w * scale, h * scale)

            ps = "分辨率 等比缩放{0}倍, 仅更改宽x高".format(scale)
            ps += "\nsize：{0}\t{1}".format(size_arr, size_str)
            print(ps)
            self.msg(ps)

        # 自定义
        elif op == OP.SIZE_CUSTOM:
            jf = setting.read_setting()
            if utils.str_to_bool(jf["size_on"]):
                size_str = jf["size"]
            if utils.str_to_bool(jf["density_on"]):
                density_str = jf['density']

            if is_right_click:
                arr = ["分辨率 自定义配置信息：",
                       "\n宽x高：{0}, 是否启用：{1}".format(jf["size"], jf["size_on"]),
                       "\nDPI：{0}, 是否启用：{1}".format(jf["density"], jf["density_on"]),
                       ]
                utils.showinfo("".join(arr))
                return
            else:
                s = "设置为 自定义分辨率，size：{0}，density:{1}".format(size_str, density_str)
                print(s)
                self.msg(s)

        if size_str:
            self.th(util_atool.set_resolution, (serial, size_str, density_str))

    def op_huawei_unlock(self):
        self.th(util_atool.huawei_unlock, (self.serial,))

    def op_open_settings(self):
        self.th(util_atool.open_setting, (self.serial,))

    def op_start(self):
        """ op 启动应用 待回顾"""
        self.msg("正在启动应用...")
        s = self.serial
        p = ''
        self.th(util_atool.am_start, (s, p))

    def op_record(self, second=180):
        """ op 录屏"""
        self.th(self.record, (self.serial, second))

    @staticmethod
    def pull_apk(serial, package):
        util_atool.show_msg("正将{}相关的apk拷贝到本机".format(package))
        apk = util_atool.pull_apk(serial, package)
        if apk:
            s = "已保存至：\n{}\n是否前往?".format(apk)
            utils.alert(s, utils.open_file, [apk, True])

    @staticmethod
    def uninstall(_package, keep_data, _serial):
        util_atool.uninstall(_package, keep_data, _serial)

    def grid_cbb_package(self, is_grid=True):
        if is_grid:
            self.cbb_item.grid(column=1, row=2, sticky=tk.NW)
        else:
            self.cbb_item.grid_forget()

    @staticmethod
    def am_list(serial, is_system=False):
        """获得应用列表"""

        if not is_system:
            _boo = False
            desc_type = "用户应用"
            desc = "获取 {0} 信息成功！\n已复制到剪贴板，请粘贴后使用"
            msg_desc = "正在获取用户安装的应用列表信息"
        else:
            _boo = True
            desc_type = "全部应用"
            desc = "获取 {0} 信息成功！\n已复制到剪贴板，请粘贴后使用"
            msg_desc = "正在获取全部的应用列表信息"
        util_atool.show_msg(msg_desc)

        # 执行命令行
        s = util_atool.pm_list_f(serial, _boo)
        # 复制到剪贴板
        desc_add = '以下是{desc}信息，如需 拷贝 apk 到本机可使用:\n\t{adb} -s {serial} pull "[/data/app/xx.apk]"\n\n'
        desc_add = desc_add.format(desc=desc_type, adb=util_atool.adb_path, serial=serial)
        s = desc_add + s
        utils.clipboard_set(s)

        # 提示
        desc = desc.format(desc_type)
        utils.showinfo(desc)

    @staticmethod
    def open_wifi_debug(serial, ip):
        s = util_atool.open_wifi_debug(serial)
        if s.count('restarting in TCP mode port: 5555'):
            utils.showinfo("正在开启wifi调试...")
        else:
            utils.showinfo("开启失败！")

        utils.showinfo("此设备的ip为：{}".format(ip))

    def show_install(self, apk_file):
        """显示安装的的应用包名"""
        self.grid_cbb_package()
        dc = util_atool.get_apk_info(apk_file)
        p = dc['package_name']
        n = dc['app_name']
        self.cbb_item.append(p, n)
        self.cbb_item.set(p)

    @staticmethod
    def show_info(_data):
        """设备信息"""
        DeviceInfoWindow(_data)

    @staticmethod
    def send_input(serial):
        """发送文本"""
        s = utils.clipboard_get()
        if s:
            util_atool.send_input(serial, s)
            util_atool.show_msg('正发送文本 {0} 到 {1} 设备上'.format(s, serial))
        else:
            utils.showinfo("请先复制字符到剪贴板（仅英文字母和数字）")

    @staticmethod
    def send_input_clipper(serial, is_get=False):
        """发送文本"""
        if not is_get:
            s = utils.clipboard_get()
            if s:
                util_atool.send_input_clipper_set(serial, s)
                util_atool.show_msg('正发送文本 {0} 到 {1} 设备上'.format(s, serial))
            else:
                utils.showinfo("请先复制字符到剪贴板")
        else:
            s = util_atool.send_input_clipper_get(serial)
            utils.clipboard_set(s)
            util_atool.show_msg("安卓设备的剪贴板发现“{0}”\n已复制到本机的剪贴板".format(s))

    @staticmethod
    def show_remote(_data):
        """显示遥控器界面"""
        # import atool.remote_control as vremote
        # w = win_remote.RemoteControl()
        # w.set_data(_data)
        util_atool.show_remote(_data)

    @staticmethod
    def log_fast(_serial):
        txt_path = util_atool.log_fast(_serial)
        s = "logcat日志已保存至：\n{}\n是否前往?".format(txt_path)
        utils.alert(s, utils.open_file, [txt_path, True])

    def install_by_select(self, serial):
        """安装 弹出文件选择框"""
        f = [("apk文件", "*.apk")]
        init_dir = ''
        if len(f):
            f = filedialog.askopenfilename(filetypes=f, title='选择文件', initialdir=init_dir)
            self.install_handle(serial, f)

    def install_by_clipboard(self, _serial):
        """安卓 自动获取剪贴板中的地址"""
        p = utils.clipboard_get()
        p = p.replace("\r", "")
        arr = p.split("\n")
        if os.path.exists(arr[0]):
            f = arr[0]
            util_atool.show_msg('从剪贴板中安装apk\n{}'.format(f))
            self.install_handle(_serial, f)
        else:
            util_atool.show_msg("剪贴板里没有apk：{}".format(utils.clipboard_get()))

    def install_handle(self, serial, apk_file):
        """安装 apk"""
        if apk_file:
            self.last_apk = apk_file
            self.show_install(apk_file)
            util_atool.show_msg("安装 {0} 到 {1}".format(apk_file, serial))

            # 执行操作
            self.t1 = threading.Thread(target=self.install_apk, args=(serial, apk_file))
            self.t1.setDaemon(True)
            self.t1.start()

    def install_apk(self, serial, apk_file):
        util_atool.install(serial, apk_file)
        self.t1 = ""

    def record(self, _serial, _second=180):
        can_record = self._data.can_i_record()
        if not can_record:
            self.remove_record_item()
            utils.showinfo("当前设备不能录屏")
        else:
            # utils.showinfo('即将开始录屏{}s'.format(_second))
            util_atool.screen_record(_serial, _second)
            self.t2 = ""

    def remove_record_item(self):
        values = list(self.cbb['values'])
        types = self.cbb_ops

        ops = [OP.REC_30, OP.REC_60, OP.REC_180, OP.REC_300]
        i_arr = []
        for i in range(len(types)):
            op = types[i]
            if ops.count(op):
                i_arr.append(i)

        while len(i_arr):
            i = i_arr.pop()
            values.pop(i)
            types.pop(i)

        self.cbb['values'] = tuple(values)
        self.cbb_ops = types
        self.cbb_current(0)

    def destroy(self):
        self.cbb = None
        tup = (self.frame, self.cbb_item)
        for w in tup:
            w.destroy()
        del tup


class PackageCombobox(IPanel):
    """包名下拉框"""
    list_package = []
    list_name = []
    list_path = []
    list_device = []
    C_MARK = " | "

    def __init__(self, _parent):
        IPanel.__init__(self, _parent)
        frame = self.frame

        w = 46 if utils.is_windows else 40
        cbb = ttk.Combobox(frame, width=w, height=40)
        cbb.bind("<<ComboboxSelected>>", self.cbb_call)
        cbb.grid(column=1, row=1, sticky=tk.NW)

        # 字体格式
        f_name = '微软雅黑' if utils.is_windows else ''
        f_size = 9 if utils.is_windows else 11
        w = 30 if utils.is_windows else 38
        tf = tk_font.Font(size=f_size, family=f_name)
        txt = tk.Label(frame, width=w, fg=util_theme.COLOR_BLACK, font=tf, anchor='w')
        self.cbb = cbb
        self.txt = txt

        self.init_package()
        self.select_first()
        # cbb.current(0)
        # index = cbb.current(0)
        # cbb['values']
        # cbb.get()

    def cbb_call(self, _):
        p = self.list_package[self.cbb.current()]
        self.set(p)

    def set(self, package):
        self.cbb.set(package)
        if not self.list_package.count(package):
            return

        # 更新简介框
        index = self.list_package.index(package)
        n = self.list_name[index]
        path = self.list_path[index]
        if n and path:
            s = "{0}    {1}".format(n, path)
        elif path:
            s = path
        else:
            s = n
        self.txt['text'] = s
        self.txt.grid(column=1, row=2, sticky=tk.W)
        utils.tooltip(self.txt, s, 300, 3000)

    def init_package(self):
        """读取配置"""
        setting.init_package()
        arr = setting.get_package()
        for obj in arr:
            kp = 'package'
            kn = 'name'
            if kp not in obj or kn not in obj:
                continue
            p = obj[kp]
            n = obj[kn]
            self.data_append(p, n)

        # 更新下拉列表
        self.data_to_value()

        # 选中最后一项
        # self.select_last()

    def get_package_list(self, serial, is_ful=False):
        result = util_atool.pm_list_f(serial, is_ful)
        if utils.is_windows:
            result = result.replace('\r', '')
        if not result:
            utils.showinfo("获取失败")
            return

        self.clear_device_package()

        arr = result.split("\n")
        n = ''
        is_device = True
        for item in arr:
            if not item.count("="):
                continue
            i = item.rindex("=")
            p = item[i + 1:]
            path = item[0:i].replace("package:", "")
            self.data_append(p, n, path, is_device)

        self.data_to_value()
        self.select_last()
        utils.showinfo("获取完成，请查看下拉框！")

    def clear_device_package(self):
        i_list = []
        for i in range(len(self.list_device)):
            if self.list_device[i]:
                i_list.append(i)
        while len(i_list):
            i = i_list.pop()
            self.list_package.pop(i)
            self.list_name.pop(i)
            self.list_path.pop(i)
            self.list_device.pop(i)

    def append(self, package, _app_name=''):
        """添加至下拉列表"""
        arr = self.cbb['values']
        if not self.list_package.count(package):
            if _app_name:
                s = "{0} | {1}".format(_app_name, package)
            else:
                s = package
            self.cbb['values'] = arr + (s,)
            self.data_append(package, _app_name)
        else:
            # 补充本地记录中缺省的名称
            i = self.list_package.index(package)
            n = self.list_name[i]
            if not _app_name:
                _app_name = n

        setting.update_package(_app_name, package)

    def data_append(self, package, name, path='', is_device=False):
        self.list_package.append(package)
        self.list_name.append(name)
        self.list_path.append(path)
        self.list_device.append(is_device)

    def data_len(self):
        return len(self.list_package)

    def data_to_value(self):
        list_len = len(self.list_package)
        values = []
        for i in range(list_len):
            p = self.list_package[i]
            n = self.list_name[i]
            if n:
                s = "{0} | {1}".format(n, p)
            else:
                s = p
            values.append(s)

        self.cbb['values'] = tuple(values)

    def select_last(self):
        p_len = self.data_len()
        if p_len:
            p = self.list_package[p_len - 1]
            self.cbb.set(p)

    def select_first(self):
        p = self.list_package[0]
        self.cbb.set(p)

    def get_package(self):
        s = self.cbb.get()
        arr = s.split(self.C_MARK)
        if len(arr) == 2:
            return arr[1]
        else:
            return arr[0]

    def destroy(self):
        pass


class DeviceInfoWindow:
    """设备信息 查看窗口"""
    _data = None

    def __init__(self, _data):
        serial = _data.serial
        self._data = _data

        top_win = tk.Toplevel(utils.win)
        # top_win.geometry('200x200')
        top_win.title('设备信息查看器')

        # top_win.bind("<Destroy>", self.destroyed)

        frame_a = tk.Frame(top_win, padx=2, pady=2)
        frame_b = tk.Frame(top_win, padx=2, pady=2)

        browse_label = tk.Label(
            frame_a,
            text='',
            fg='#515556',
            font=tk_font.Font(size=9)
        )
        browse_label.grid(column=2, row=1)

        if utils.is_windows:
            font_name = ''
            size = 14
        else:
            font_name = '微软雅黑'
            size = 12
        tf = tk_font.Font(size=size, family=font_name)

        info_text = tk.Text(
            frame_b,
            height=40,
            width=100,
            fg=util_theme.COLOR_BLACK,
            bd=1,
            wrap=tk.WORD,
            highlightthickness=1,
            highlightcolor=util_theme.COLOR_GRAY,
            font=tf
        )
        info_text.grid(column=1, row=1)

        frame_a.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        frame_b.grid(column=1, row=2)

        self.top_win = top_win
        self.browse_label = browse_label
        self.info_text = info_text
        # self.auto_select()
        self.destroy_arr = [frame_a, frame_b, info_text, browse_label]

        if serial:
            self.showinfo(serial)

    def auto_select(self):
        pass

    def showinfo(self, serial):
        # self.browse_label['text']=apk_file
        # reg_one = self.reg_group_one
        # get_api_desc = setting.get_api_desc

        # result = util_atool.dump(apk_file)
        # print(result)
        # wifi.interface.mac    dhcp.wlan0.ip
        """adb shell dumpsys battery"""
        # ('处理器型号', 'ro.product.board'),
        arr = [
            ('厂商', 'ro.product.manufacturer'),
            ('品牌', 'ro.product.brand'),
            ('型号', 'ro.product.model'),
            ('SDK 版本', 'ro.build.version.sdk'),
            ('Android版本', 'ro.build.version.release'),
            ('Android 安全补丁程序级别', 'ro.build.version.security_patch'),
            ('设备名', 'ro.product.name'),
            ('屏幕密度', 'ro.sf.lcd_density'),

            ('版本号', 'ro.build.display.id'),
            ('MAC 地址', 'wifi.interface.mac'),
            ('序列号', 'ro.serialno'),
            ('IMEI', 'ril.gsm1.deviceid'),
            ('', 'ril.gsm2.deviceid'),
            ('', 'ril.gsm.imei'),
        ]
        s_arr = []
        prop = util_atool.getprop(serial)
        for t in arr:
            s = t[0]
            key = t[1]
            value = util_atool.search_in_prop(prop, key)
            s_arr.append(s + "\t\t" + value)

        value = util_atool.get_resolution(serial)[0]
        s_arr.append("分辨率\t\t" + value)
        # value = util_adb.get_density(serial)
        # s_arr.append("屏幕密度\t\t" + value)

        s_arr.append("IP地址\t\t" + self._data.ip)

        mac_address = util_atool.get_mac_address(serial)
        s_arr.append("MAC 地址\t\t" + mac_address)

        mem_info = util_atool.get_mem_info(serial)
        s_arr.append(mem_info)

        cpu_info = util_atool.get_cpu_info(serial)
        s_arr.append(cpu_info)

        final_str = "\n".join(s_arr)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.INSERT, final_str)
        # ss = info_text.get(1.0, tk.END)

    @staticmethod
    def reg_group(search_str, reg):
        """匹配结果输出至 tup
        """
        m = re.search(reg, search_str, re.M | re.I)
        if m:
            return m.groups()
        else:
            return tuple([])

    def reg_group_one(self, search_str, reg):
        """匹配其中一个结果
        若不匹配 返回空字符 ""
        """
        tup = self.reg_group(search_str, reg)
        if len(tup) > 0:
            return tup[0]
        else:
            return ""

    def destroy(self):
        for w in self.destroy_arr:
            w.grid_forget()
            w.destroy()
        del self.destroy_arr


class DeviceData(object):
    """一台设备的数据"""
    serial = ''

    product_name = ''
    ip = ''

    size = '1920x1080'
    density = 240
    details = ''
    is_device = True
    bin_files = []
    can_record = False
    prop = ''

    def __init__(self, serial):
        self.serial = serial
        self.is_device = False if len(utils.find_ip(serial)) else True

    def getprop(self, prop_name=''):
        """
        获得属性
        :param prop_name:
        :return:
        """
        serial = self.serial
        if serial.count("127.0.0.1"):
            self.ip = "127.0.0.1"

        if not self.prop:
            self.prop = util_atool.getprop(serial)

        # 设备名称
        if not self.product_name:
            self.product_name = util_atool.getprop_product_name(self.prop)

        # ip 地址
        if not self.ip:
            self.ip = util_atool.getprop_ip(self.prop)
            if not self.ip:
                # 另一种读取ip的方法
                self.ip = util_atool.get_ip(serial)
                # print(serial, self.ip)

        if prop_name:
            return util_atool.search_in_prop(self.prop, prop_name)

        # tup = ('ro.hardware',
        #     'ro.build.version.sdk',
        #     'sys.display-size'
        # )
        # for p in tup:
        #     s = util_adb.search_in_prop(prop,p)
        #     print(p,s)

    def can_i_record(self):
        if not len(self.bin_files):
            # 是否支持录制屏幕
            "ls /system/bin/"
            "adb shell screenrecord"
            url = "/system/bin"
            mark = "screenrecord"
            s = util_atool.ls_path(self.serial, url)
            self.bin_files = s.split("\n")
            self.can_record = True if self.bin_files.count(mark) else False
        return self.can_record

    def can_i_scrcpy(self):
        if not self.can_i_record():
            util_atool.show_msg(self.product_name + " 不支持scrcpy")
            return False

        s_name = "scrcpy.exe" if utils.is_windows else "scrcpy"
        p = Path(util_atool.adb_path).with_name(s_name)
        if p.exists():
            return True
        else:
            print("{0}  {1}".format(p, p.exists()))
            if utils.is_windows:
                s = "请先安装scrcpy。将scrcpy.exe放在 “D:\\FFmpeg”目录下"
            else:
                s = "请先安装scrcpy。brew install scrcpy"
            util_atool.show_msg(s)
            return False

    # @property
    # def serial(self):
    #     return self.__serial
    # @serial.setter
    # def serial(self, value):
    #     """设备序列号
    #     """
    #     self.__serial = value


class OP:
    REC_30 = 'rec_30'
    REC_60 = 'rec_60'
    REC_120 = 'rec_120'
    REC_180 = 'rec_180'
    REC_300 = 'rec_300'

    SCREEN_SHOT = 'screen_cat'
    DEVICE_INFO = 'device_info'
    WIFI_DEBUG = 'wifi_debug'

    AM_LIST_USER = '_need_am_user'
    AM_LIST = '_need_am'

    SEND_Text = 'send_text'
    COPY_CMD = 'copy_cmd'
    LOG_FAST = 'log_fast'
    LOG_CLEAR = 'log_clear'
    LOG_CAT = 'log_cat'

    DISCONNECT = 'disconnect'
    REMOTER = 'remoter'
    DEBUG_LAYOUT = 'debug_layout'

    INSTALL = 'install'

    UNINSTALL = '_need_uninstall'
    UNINSTALL_KEEP = '_need_uninstall_keep'
    RUN = '_need_run'
    CLEAR = '_need_clear'
    STOP = '_need_stop'
    PULL_APK = '_need_pull_apk'
    PULL_CUR_APK = 'pull_CUR_apk'

    SCRCPY = 'scrcpy'
    CLIPPER = 'clipper'

    SIZE_ORIGINAL = 'size_Original'
    SIZE_CUSTOM = 'size_xtc'
    SIZE_SCALE = 'size_double'
    SIZE_TRIPLE = 'size_triple'
    SIZE_720 = 'size_720'
    HUAWEI_UNLOCK = 'huawei_unlock'
    OPEN_SETTINGS = 'open_settings'

    ACTIVITY_CUR_RUN = 'activity-current-runing'
    SEPARATOR = 'separator'
