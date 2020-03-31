#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
遥控器
"""

import tkinter as tk

import util_theme
import utils
from atool import setting_atool as setting
from atool import util_atool

# 窗口最后的位置
_win_pos = '180x200'


class RemoteControl:
    btn_up = None
    btn_down = None
    btn_left = None
    btn_right = None
    btn_enter = None
    btn_back = None
    btn_home = None
    btn_menu = None
    btn_vol_mute = None
    btn_vol_up = None
    btn_vol_down = None
    btn_screen = None
    btn_power = None
    btn_switch = None

    def __init__(self):
        top_win = tk.Toplevel(utils.win)
        # '180x200+1920+1080'
        top_win.geometry(_win_pos)
        top_win.title('TV遥控器')
        frame_btn = tk.Frame(top_win)
        frame_txt = tk.Frame(top_win)

        # 配置 并创建按钮
        config = (
            [self.btn_up, '▲', 2, 1, "btn_up", "快捷键：↑"],
            [self.btn_down, '▼', 2, 3, "btn_down", "快捷键：↓"],
            [self.btn_left, '◀', 1, 2, "btn_left", "快捷键：←"],
            [self.btn_right, '▶', 3, 2, "btn_right", "快捷键：→"],
            [self.btn_enter, '●', 2, 2, "btn_enter", "快捷键：回车键"],

            [self.btn_menu, '☰', 1, 4, "btn_menu", "可尝试 菜单键 或 右徽标键"],
            [self.btn_home, 'home', 2, 4, "btn_home", ""],
            [self.btn_back, '⇦', 3, 4, "btn_back", "可尝试 esc键 或 backspace键"],

            [self.btn_vol_down, '音量-', 1, 6, "btn_vol_down", ""],
            [self.btn_vol_mute, '静音', 2, 6, "btn_vol_mute", ""],
            [self.btn_vol_up, '音量+', 3, 6, "btn_vol_up", ""],

            [self.btn_power, '电源', 1, 7, "btn_power", "功能：电源键"],
            [self.btn_screen, '✄', 2, 7, "btn_screen", ""],
            [self.btn_switch, '切换', 3, 7, "btn_switch", "功能：切换应用"]
        )
        arr = []
        for c in config:
            text = c[1]
            column = c[2]
            row = c[3]
            name = c[4]
            tips = c[5]

            c[0] = tk.Button(frame_btn, text=text, width=4)
            btn = c[0]

            setattr(btn, "name", name)
            btn.bind("<Button-1>", self.btn_call)

            if tips:
                utils.tooltip(btn, tips)
            btn.grid(column=column, row=row)

            arr.append(btn)

        # 分割线
        tk.Label(frame_btn).grid(column=1, row=5, sticky=tk.W)

        t = tuple(arr)
        utils.set_groove(t)

        # 文本框
        txt = tk.Label(frame_txt, fg=util_theme.COLOR_GRAY, width=18)
        txt.grid(column=1, row=1)

        frame_btn.grid(column=1, row=1)
        frame_txt.grid(column=1, row=2)

        # frame_btn.focus()
        # frame_btn.bind("<Button-1>", self.refocus)
        top_win.bind('<Key>', self.btn_call)
        top_win.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.txt = txt
        self.serial = 'emulator-5554'
        self.data = None
        self.frame_btn = frame_btn
        self.top_win = top_win
        self.auto_select()

    def auto_select(self):
        pass

    # def set_serial(self, _serial):
    #     self.serial = _serial
    #     self.data = setting.get_data_by_serial(_serial)
    #     self.show_device_name()

    def set_data(self, data):
        self.data = data
        self.serial = data.serial
        self.show_device_name()

    def has_data(self):
        if self.data:
            return True
        else:
            return False

    def show_device_name(self):
        if self.data is None:
            return
        product_name = self.data.product_name
        # self.text['text'] = "已连接至 "+product_name
        self.txt['text'] = "已瞄准\n" + product_name
        self.top_win.title(product_name)
        d_list = util_atool.devices(False)['device']
        if d_list.count(self.serial) == 0:
            self.txt['text'] = "{}\n{已断开连接}" + product_name

    # def refocus(self, event):
    #     if not event.widget:
    #         return
    #     self.frame_btn.focus()

    def btn_call(self, event):
        """[summary]

        Arguments:
            event {[type]} -- [description]
        KEYCODE_BACK    返回键  4
        KEYCODE_ENTER	回车键	66
        KEYCODE_ESCAPE	ESC键	111

        KEYCODE_DPAD_CENTER	导航键 确定键	23
        KEYCODE_DPAD_UP	导航键 向上	19
        KEYCODE_DPAD_DOWN	导航键 向下	20
        KEYCODE_DPAD_LEFT	导航键 向左	21
        KEYCODE_DPAD_RIGHT	导航键 向右	22

        KEYCODE_MOVE_HOME	光标移动到开始键	122
        KEYCODE_MOVE_END	光标移动到末尾键	123
        KEYCODE_PAGE_UP	向上翻页键	92
        KEYCODE_PAGE_DOWN	向下翻页键	93
        KEYCODE_DEL	退格键	67
        KEYCODE_FORWARD_DEL	删除键	112
        KEYCODE_INSERT	插入键	124
        KEYCODE_TAB	Tab键	61
        KEYCODE_NUM_LOCK	小键盘锁	143
        KEYCODE_CAPS_LOCK	大写锁定键	115
        KEYCODE_BREAK	Break/Pause键	121
        KEYCODE_SCROLL_LOCK	滚动锁定键	116
        KEYCODE_ZOOM_IN	放大键	168
        KEYCODE_ZOOM_OUT	缩小键	169

        KEYCODE_HOME    3
        KEYCODE_MENU    82
        KEYCODE_SETTINGS    176
        KEYCODE_SEARCH  84
        """

        key_code = 0
        if event.widget:
            t = (
                ('btn_up', 19),
                ('btn_down', 20),
                ('btn_left', 21),
                ('btn_right', 22),
                ('btn_enter', 23),
                ('btn_back', 4),
                ('btn_menu', 82),
                ('btn_screen', -1),
                ('btn_vol_mute', 164),
                ('btn_vol_up', 24),
                ('btn_vol_down', 25),
                ('btn_home', 3),
                ('btn_power', 26),
                ('btn_search', 84),
                ('btn_switch', 187)
            )
            try:
                widget_name = event.widget.name if hasattr(event.widget, 'name') else ''
                for obj in t:
                    if obj[0] == widget_name:
                        key_code = obj[1]
                        break
            except AttributeError as e:
                # error: has not attribute
                print(e)

        if event.keycode:
            kc = event.keycode
            if kc != "??":
                util_atool.show_msg(kc)
                key_code = event.keycode

            if kc == 16:
                key_code = 82

        # 处理键盘事件
        if event.keysym:
            t = (
                'Up', 19,
                'Down', 20,
                'Left', 21,
                'Right', 22,
                'Return', 23,
                'BackSpace', 4,
                'Cancel', 4,

                # 'w', 19,
                # 's', 20,
                # 'a', 21,
                # 'd', 22,
                #
                # 'z', 82,
                # 'x', -1,
                # 'c', 4,

                # "a", "KEYCODE_A",
                # "b", "KEYCODE_B",
                # "c", "KEYCODE_C",
                # "d", "KEYCODE_D",
                # "e", "KEYCODE_E",
                # "f", "KEYCODE_F",
                # "g", "KEYCODE_G",
                # "h", "KEYCODE_H",
                # "i", "KEYCODE_I",
                # "j", "KEYCODE_J",
                # "k", "KEYCODE_K",
                # "l", "KEYCODE_L",
                # "m", "KEYCODE_M",
                # "n", "KEYCODE_N",
                # "o", "KEYCODE_O",
                # "p", "KEYCODE_P",
                # "q", "KEYCODE_Q",
                # "r", "KEYCODE_R",
                # "s", "KEYCODE_S",
                # "t", "KEYCODE_T",
                # "u", "KEYCODE_U",
                # "v", "KEYCODE_V",
                # "w", "KEYCODE_W",
                # "x", "KEYCODE_X",
                # "y", "KEYCODE_Y",
                # "z", "KEYCODE_Z",

                # "0", "KEYCODE_0",
                # "1", "KEYCODE_1",
                # "2", "KEYCODE_2",
                # "3", "KEYCODE_3",
                # "4", "KEYCODE_4",
                # "5", "KEYCODE_5",
                # "6", "KEYCODE_6",
                # "7", "KEYCODE_7",
                # "8", "KEYCODE_8",
                # "9", "KEYCODE_9",

                'F5', 82,
                'F6', -1,
                'F7', 4
            )

            sym = event.keysym
            if sym != "??":
                util_atool.show_msg(sym)
            if t.count(sym):
                index = t.index(sym)
                if index < len(t) - 2:
                    key_code = t[index + 1]

        if key_code == -1:
            self.screen_shot()
        elif key_code:
            serial = self.serial
            utils.thread_func(util_atool.send_keyevent, (serial, key_code))

    def screen_shot(self):
        if self.serial:
            if setting.need_auto_open() == '1':
                auto_open = True
            else:
                auto_open = False
            utils.thread_func(util_atool.screen_capture, (self.serial, auto_open))

    def on_closing(self):
        self.destroy()

    def destroy(self):
        # arr = self.__btn_arr
        # for w in arr:
        #     w.destroy()
        # del arr

        global _win_pos
        _win_pos = self.top_win.geometry()

        self.top_win.destroy()
        self.top_win = None


if __name__ == "__main__":
    pass
