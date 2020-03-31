#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import util_theme
import utils
from atool import setting_atool, util_atool, widget_device, win_apkinfo, win_preferences, win_wifi_connect


class Main:
    """安卓工具箱 主 ui"""
    is_manual_int = False
    btn_refresh = None
    btn_wifi = None
    btn_apk = None
    btn_folder = None
    btn_remote = None
    btn_setting = None
    frame_wifi = None
    frame_device = None
    win_wifi = None
    win_pref = None
    win_remote = None
    device_list = []

    replace_txt = None

    cbb = None
    cbb_ops = []

    OP_B64_IMG = 'op_b64_img'
    OP_IMG_B64 = 'op_img_b64'

    def __init__(self, parent):
        self.win = parent

    def manual_int(self):
        if self.is_manual_int:
            return
        self.is_manual_int = True
        win = self.win

        self.win = None

        frame_btn = tk.Frame(win, bd=1)
        frame_msg = tk.Frame(win)
        frame_content = tk.Frame(win)

        frame_device = tk.Frame(frame_content)

        color = util_theme.COLOR_BLACK

        def init_btn(text, width=8):
            btn = tk.Button(frame_btn, text=text, width=width, fg=color)
            btn.bind("<Button-1>", self.btn_click)
            utils.set_groove((btn,))
            return btn

        btn_refresh = init_btn('刷新设备列表', 10)
        btn_wifi = init_btn('Wifi调试')
        btn_apk = init_btn('apkinfo')
        btn_folder = init_btn('定位截图')
        btn_remote = init_btn('遥控器')
        btn_setting = init_btn('✿设置')

        utils.bind(btn_refresh, self.btn_click, True)
        utils.bind(btn_wifi, self.btn_click, True)
        utils.bind(btn_apk, self.btn_click, True)

        # 设置tooltip
        utils.tooltip(btn_refresh, "右键单击可强制刷新", 300, 3000)

        cbb = ttk.Combobox(frame_btn, width=10, justify='center')
        cbb.bind("<<ComboboxSelected>>", self.cbb_call)
        utils.tooltip(cbb, '选择下拉项即执行操作')
        # 配置下拉项
        c = [
            ['base64 转图片', self.OP_B64_IMG],
            ['图片转 base64', self.OP_IMG_B64]
        ]
        values = []
        types = []
        for arr in c:
            values.append(arr[0])
            types.append(arr[1])
        cbb['values'] = tuple(values)
        cbb.current(0)
        self.cbb = cbb
        self.cbb_ops = types

        # 提示框
        w = 70 if utils.is_windows else 60
        label_msg = tk.Label(frame_msg, width=w, fg=color, justify='left', anchor="nw")
        utils.label_msg = label_msg

        btn_wifi.grid(column=1, row=1)
        btn_refresh.grid(column=2, row=1)
        btn_apk.grid(column=3, row=1)
        btn_folder.grid(column=4, row=1)
        btn_remote.grid(column=5, row=1)
        # cbb.grid(column=5, row=1)
        btn_setting.grid(column=6, row=1)

        label_msg.grid(column=1, row=2, sticky=tk.NW)

        frame_device.grid(column=2, row=1, sticky=tk.NW)

        frame_btn.grid(column=1, row=1, sticky=tk.NW)
        frame_msg.grid(column=1, row=2, sticky=tk.NW)
        frame_content.grid(column=1, row=3, sticky=tk.NW)

        # menu = tk.Menu(win)
        # for i in ('One', 'Two', 'Three'):
        #     menu.add_command(label=i)
        # if (win.tk.call('tk', 'windowingsystem') == 'aqua'):
        #     win.bind('<2>', lambda e: menu.post(e.x_root, e.y_root))
        #     print('<2>')
        #     win.bind('<Control-1>', lambda e: menu.post(e.x_root, e.y_root))
        # else:
        #     win.bind('<3>', lambda e: menu.post(e.x_root, e.y_root))
        #     print('<3>')

        utils.main = self

        self.btn_refresh = btn_refresh
        self.btn_wifi = btn_wifi
        self.btn_apk = btn_apk
        self.btn_folder = btn_folder
        self.btn_remote = btn_remote
        self.btn_setting = btn_setting
        self.frame_device = frame_device
        self.show_devices()

    def sync_status(self):
        self.manual_int()

    def btn_click(self, event):
        """点击按钮"""
        w = event.widget
        if utils.is_right_click(event.num):
            # 鼠标右键键
            if w == self.btn_refresh:
                self.show_devices_force()
            elif w == self.btn_apk:
                self.show_apk_info(utils.clipboard_get(), True)
            elif w == self.btn_wifi:
                win_wifi_connect.connect_one()

        else:
            # 鼠标左键
            if w == self.btn_refresh:
                self.show_devices()

            elif w == self.btn_apk:
                self.show_apk_info()

            elif w == self.btn_folder:
                f = setting_atool.last_screen_shot
                s = str(f)

                if os.path.exists(f):
                    utils.open_file(f, True)    # 如果有文件记录 则定位到文件
                else:
                    s = str(setting_atool.output_dir)
                    success = utils.open_dir(s)
                    if not success:
                        utils.showinfo("文件夹不存在，请查看设置")
                utils.clipboard_set(s)  # 将路径拷贝到剪贴板中

            # wifi链接
            elif w == self.btn_wifi:
                if not utils.lift_and_check(self.win_wifi):
                    self.win_wifi = win_wifi_connect.WifiConnect()
            # 遥控器
            elif w == self.btn_remote:
                util_atool.show_remote()
            # 设置
            elif w == self.btn_setting:
                if not utils.lift_and_check(self.win_pref):
                    self.win_pref = win_preferences.Main()

    # def start_check_device_info(self):
    #     global timer
    #     timer = threading.Timer(5, self.check_device_info)
    #     timer.start()

    def show_devices(self):
        """刷新设备列表"""
        win = self.frame_device
        widgets = self.device_list
        serials = self.get_serials()

        # 找出消失的对象索引值
        dc = util_atool.devices(True)
        serials_new = dc['device']
        index_list = []
        for i in range(len(serials)):
            s = serials[i]
            if not serials_new.count(s):
                index_list.append(i)
        # 销毁对象
        while len(index_list):
            i = index_list.pop()
            w = widgets[i]
            w.grid_forget()
            # w.destroy()
            widgets.pop(i)
            serials.pop(i)

        # 创建新添加的
        for s in serials_new:
            if not serials.count(s):
                w = widget_device.DeviceItem(win)
                w.set_serial(s)
                widgets.append(w)
                serials.append(s)

        count = 0
        for w in widgets:
            w.grid(column=0, row=count, sticky=tk.NW)
            count += 1

        if not len(widgets):
            txt = self.replace_txt
            if txt is None:
                txt = tk.Label(win)
            txt.grid(column=0, row=0)

        self.device_list = widgets

        # 提示需要授权的设备
        serials_unauthorized = dc['unauthorized']
        if len(serials_unauthorized):
            utils.showinfo("下列设备需要授权（允许USB调试）\n（强制“刷新设备列表”将重新弹出授权提示）：\n"
                           + "\n".join(serials_unauthorized))
        # utils.win.update()

    def get_serials(self):
        _list = []
        for w in self.device_list:
            _list.append(w.serial)
        return _list

    def show_devices_force(self):
        """强制刷新设备列表
        """
        dc = util_atool.devices(True)
        arr = dc['device']
        util_atool.kill_server()

        ips = []
        for s in arr:
            if s.find('192.168.') != -1:
                ip = s.split(':')[0]
                ips.append(ip)
        for ip in ips:
            util_atool.connect(ip)

        self.show_devices()

        # serials_unauthorized = dc['unauthorized']
        # if len(serials_unauthorized):
        #     utils.showinfo("下列设备需要授权调试权限才能操作：\n" + "\n".join(serials_unauthorized))

    @staticmethod
    def show_apk_info(apk='', is_group=False):
        """显示 apk信息界面 """
        if not is_group:
            win_apkinfo.Main(apk)
        else:
            apk = apk.replace("\r", "")
            arr = apk.split("\n")
            opened_count = 0
            for apk in arr:
                apk = apk.strip("'")
                apk = apk.strip('"')
                apk = apk.strip(' ')
                if apk:
                    if os.path.exists(apk):
                        opened_count += 1
                        win_apkinfo.Main(apk)
            # 没有符合的地址，则打开一个空的界面
            if opened_count == 0:
                win_apkinfo.Main('')

    def cbb_call(self, _):
        """下拉框选择"""
        # s = self.cbb.get()
        self.process()

    def process(self):
        """处理命令"""
        index = self.cbb.current()
        if index == -1 or index >= len(self.cbb_ops):
            return

        s = self.cbb_ops[index]
        if s == self.OP_B64_IMG:
            c = utils.clipboard_get()
            save_path = setting_atool.output_dir + os.sep + "base64"
            utils.make_dir(save_path)
            img_path = '{0}/img-{1}.png'.format(save_path, self.__get_now())
            utils.base64_img(c, img_path)
        elif s == self.OP_IMG_B64:
            self.image_to_base64()

    @staticmethod
    def image_to_base64():
        types = [
                    ("png", "*.png"),
                    ("jpg", "*.jpg")
                ],
        f = filedialog.askopenfilename(filetypes=types, title='选择文件')
        if f:
            utils.base64_img(f)

    @staticmethod
    def __get_now():
        cur_time = time.localtime(time.time())
        return time.strftime('%Y%m%d%H%M%S', cur_time)


if __name__ == "__main__":
    pass
