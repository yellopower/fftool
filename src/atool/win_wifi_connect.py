# -*- coding: utf-8 -*-

import socket
import threading
import tkinter as tk
from tkinter import ttk

import atool.widget_device as device
import util_theme as theme
import utils
from atool import setting_atool, util_atool

# 窗口最后的位置
_win_pos = ''


def __show_result(serial):
    """连接mumu模拟器 显示结果"""
    list1 = serial.split(":")
    ip = list1[0]
    port = list1[1] if len(list1) > 1 else ""

    list1 = util_atool.devices(False)['device']
    serial = ''
    for ss in list1:
        if ss.find(ip) != -1:
            serial = ss
            break
    if serial:
        d = device.DeviceData(serial)
        d.getprop()
        setting_atool.update_recent(d.product_name, ip, port)
        utils.showinfo('已连接至 {0} {1}'.format(d.product_name, ip))
    else:
        utils.showinfo('连接失败！\n请先启动mumu模拟器')

    if utils.main is not None:
        utils.main.show_devices()


def connect_one():
    """连接mumu模拟器"""
    port = "7555" if utils.is_windows else "5555"
    serial = "127.0.0.1:{0}".format(port)
    util_atool.connect(serial)
    __show_result(serial)


class WifiConnect:
    """ wifi连接 """
    EVEN = 'even'
    ODD = 'odd'

    def __init__(self):
        top_win = tk.Toplevel(utils.win)
        top_win.title('wifi连接')
        top_win.geometry(_win_pos)

        frame_top = tk.Frame(top_win)
        frame_top2 = tk.Frame(top_win)
        frame_list = tk.Frame(top_win)

        # 顶部输入框
        var_entry = tk.StringVar()
        var_entry2 = tk.StringVar()

        # 模拟器端口
        port = "7555" if utils.is_windows else "5555"
        serial1 = "127.0.0.1:{0}".format(port)
        serial2 = "127.0.0.1:{0}".format("62001")
        desc1 = "mumu模拟器"

        txt1 = tk.Label(frame_top, text='请输入设备的 IP 地址:')
        txt2 = tk.Label(frame_top, text='最近连接:', fg=theme.COLOR_GRAY)
        entry = tk.Entry(frame_top, textvariable=var_entry, width=28)
        entry.select_adjust(15)
        entry.focus()
        btn_connect = tk.Button(frame_top, text='连接', width=8)
        btn_serial1 = tk.Button(frame_top, text=desc1, width=40)
        btn_scan = tk.Button(frame_top, text='网络发现', width=8)

        entry.bind('<Return>', self.entry_call)
        btn_connect.bind('<Button-1>', self.connect_call)
        utils.bind(btn_serial1, self.emulator_call, False)
        utils.bind(btn_serial1, self.emulator_call, True)
        utils.tooltip(btn_serial1,  "左键 mumu模拟器 {0}\n右键 夜神模拟器 {1}".format(serial1, serial2))
        utils.bind(btn_scan, self.scan_call, False)
        utils.bind(btn_scan, self.scan_call, True)
        utils.tooltip(btn_scan, "左键扫描 开放5555端口的ip\n"
                                "右键扫描 开放7555端口的ip")

        # tree 配置
        # 列号，宽度，对齐，列名称
        config = [
            ["1", 140, "center", "名称"],
            ["2", 120, "nw", "IP"],
            ["3", 80, "center", "端口号"]
        ]
        names = []
        for c in config:
            names.append(c[0])
        tree = ttk.Treeview(frame_list, show="headings", selectmode=tk.EXTENDED, columns=names)
        tree.config(height=10)
        for c in config:
            tree.column(c[0], width=c[1], anchor=c[2])
            tree.heading(c[0], text=c[3])
        tree.tag_configure(self.ODD, background='#f5f5f5')
        tree.bind('<Button-1>', self.tree_call)
        tree.bind('<Double-1>', self.tree_double_call)

        y_scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=tree.yview)
        tree.config(yscrollcommand=y_scrollbar.set)
        self.i_name = 0
        self.i_ip = 1
        self.i_port = 2

        entry2 = tk.Entry(frame_top2, textvariable=var_entry2, width=28)
        rename = tk.Button(frame_top2, text='✏', width=2, command=self.rename_call)
        up = tk.Button(frame_top2, text='↑', width=2, command=self.up_call)
        down = tk.Button(frame_top2, text='↓', width=2, command=self.down_call)
        remove_btn = tk.Button(frame_top2, text='-', width=2, command=self.remove_call)
        entry2.bind('<Return>', self.entry2_call)

        utils.tooltip(rename, "更改设备名称\n支持输入框按enter键")

        txt1.grid(column=1, row=1, sticky=tk.NW)
        entry.grid(column=1, row=2, sticky=tk.E + tk.W)
        btn_serial1.grid(column=1, row=3, sticky=tk.NW)
        txt2.grid(column=1, row=4, sticky=tk.NW)

        btn_connect.grid(column=2, row=2)
        btn_scan.grid(column=2, row=3)

        tree.grid(column=1, row=2)
        y_scrollbar.grid(column=2, row=2, sticky=tk.N + tk.S)

        entry2.grid(column=2, row=3)
        rename.grid(column=3, row=3)
        up.grid(column=4, row=3)
        down.grid(column=5, row=3)
        remove_btn.grid(column=6, row=3)

        frame_top.grid(column=1, row=1)
        frame_list.grid(column=1, row=2, sticky=tk.NW)
        frame_top2.grid(column=1, row=3, sticky=tk.EW)

        utils.set_groove((btn_connect, btn_serial1, btn_scan, up, down, remove_btn))
        # utils.win.call('focus', '-force', entry)

        top_win.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.top_win = top_win
        self.frame_top = frame_top
        self.entry = entry
        self.var_entry = var_entry
        self.var_entry2 = var_entry2
        self.btn_connect = btn_connect
        self.btn_emulator1 = btn_serial1
        self.widget_arr = []
        self.serial1 = serial1
        self.serial2 = serial2
        self.tree = tree
        self.auto_select()

    def auto_select(self):
        list1 = setting_atool.get_recent()

        # 显示最近连接
        self.show_recent()

        # 输入框显示最后连接的ip serial
        list2 = list1.copy()
        list2.reverse()
        for obj in list2:
            if 'name' not in obj or 'ip' not in obj:
                continue

            ip = obj["ip"]
            key = "port"
            port = obj[key] if key in obj else ""
            if port:
                serial = "{0}:{1}".format(ip, port)
            else:
                serial = ip
            self.show_one_serial(serial)
            break

    def show_recent(self):
        """ 显示最近连接 """
        self.clear()
        arr = setting_atool.get_recent()
        i = 0
        for obj in arr:
            if 'name' not in obj or 'ip' not in obj:
                continue
            desc = obj["name"]
            ip = obj["ip"]
            key = "port"
            port = obj[key] if key in obj else ""
            if i % 2 == 0:
                tag = self.EVEN
            else:
                tag = self.ODD
            self.tree.insert('', 'end', tags=tag, values=[desc, ip, port])
            i += 1

    def clear(self):
        """清空内容
        """
        tree = self.tree
        x = tree.get_children()
        for item in x:
            tree.delete(item)

    def remove_call(self):
        self.remove_selection()

    def up_call(self):
        self.adjust(True)

    def down_call(self):
        self.adjust(False)

    def remove_selection(self):
        """ 删除选中 """
        tree = self.tree
        for item in tree.selection():
            tree.delete(item)
        self.save_recent()

    def adjust(self, is_up):
        """ 顺序调整 """
        tree = self.tree
        items = tree.selection()
        if len(items) > 1:
            utils.showinfo("只支持单个的顺序调整")
            return
        if not len(items):
            return

        item = items[0]
        i = tree.index(item)

        if is_up:
            i = i - 1 if i > 0 else 0
            tree.move(item, '', i)
        elif not is_up:
            total = len(tree.get_children())
            i = i + 1 if i < total else 0
            tree.move(item, '', i)

        # 重新设置标签以匹配单双行颜色
        items = tree.get_children()
        for i in range(len(items)):
            item = items[i]
            if i % 2 == 0:
                tag = self.EVEN
            else:
                tag = self.ODD
            text = tree.item(item, "values")
            li = list(text)
            # li[self.i_id] = str(i + 1)
            tree.item(item, tags=tag, values=li)

        self.save_recent()

    def save_recent(self):
        """
        更新全部
        :return:
        """
        tree = self.tree

        ips = []
        items = tree.get_children()
        for i in range(len(items)):
            item = items[i]
            text = tree.item(item, "values")
            li = list(text)
            obj = {
                "name": li[self.i_name],
                "ip": li[self.i_ip],
                "port": li[self.i_port]
                }
            # 端口号为空时则不写入
            key = "port"
            if not obj[key]:
                obj.pop(key)
            ips.append(obj)
        setting_atool.set_recent(ips)

    def rename_call(self):
        self.entry2_call("")

    def show_one_serial(self, ip_str):
        self.var_entry.set(ip_str)
        self.entry.select_adjust(len(ip_str))
        self.entry.focus()

    def connect(self, serial):
        utils.thread_func(self.thread_connect, (serial,))

    def thread_connect(self, serial):
        self.show_one_serial(serial)
        util_atool.connect(serial)
        self.show_connect_result(serial)

    def show_connect_result(self, serial):
        list1 = serial.split(":")
        ip = list1[0]
        port = list1[1] if len(list1) > 1 else ""

        list1 = util_atool.devices(False)['device']
        serial = ''
        for ss in list1:
            if ss.find(ip) != -1:
                serial = ss
                break
        if serial:
            d = device.DeviceData(serial)
            d.getprop()
            setting_atool.update_recent(d.product_name, ip, port)
            self.show_recent()
            utils.showinfo('已连接至 {0} {1}'.format(d.product_name, ip))
            # self.top_win.destroy()
        else:
            utils.showinfo('连接失败！\n1.可能IP不正确；\n'
                           '2.对应设备未开启 adb 调试；\n'
                           '3.有些设备仅允许一个adb连接，关开一次adb调试设置可解决重置连接；')

        if utils.main is not None:
            utils.main.show_devices()

    def connect_call(self, _):
        """ 点击连接按钮 """
        entry_str = self.var_entry.get()
        if len(utils.find_ip(entry_str)) == 0:
            utils.showinfo('ip输入不正确')
            return
        print("正在连接 {}".format(entry_str))
        self.connect(entry_str)

    def entry_call(self, _):
        self.connect_call("")

    def entry2_call(self, _):
        entry_str = self.var_entry2.get()
        if len(entry_str) == 0:
            utils.showinfo('设备名称不能为空!')
            return

        tree = self.tree
        items = tree.selection()
        if not len(items):
            utils.showinfo('请选中列表中的一行!')
            return
        item = items[0]
        i = tree.index(item)
        # arr = tree.item(i, "values")
        # ip = arr[self.i_ip]
        # port = arr[self.i_port]
        # desc = arr[self.i_name]
        # print(desc)
        if i % 2 == 0:
            tag = self.EVEN
        else:
            tag = self.ODD

        text = tree.item(item, "values")
        li = list(text)
        li[self.i_name] = entry_str
        # li[self.i_id] = str(i + 1)
        tree.item(item, tags=tag, values=li)
        self.save_recent()

    def tree_call(self, event):
        """ 点击 tree 一行 """
        tree = self.tree
        row = tree.identify_row(event.y)
        if not row:
            return

        arr = tree.item(row, "values")
        ip = arr[self.i_ip]
        port = arr[self.i_port]
        desc = arr[self.i_name]

        if port:
            serial = "{0}:{1}".format(ip, port)
        else:
            serial = ip
        # self.connect(serial)
        self.var_entry2.set(desc)
        self.show_one_serial(serial)

    def tree_double_call(self, event):
        """ 双击 tree 一行 """
        tree = self.tree
        row = tree.identify_row(event.y)
        if not row:
            return
        self.connect_call("")

    @staticmethod
    def scan_call(event):
        """ 点击 网络发现 按钮 """
        is_right = utils.is_right_click(event.num)
        port = "7555" if is_right else "5555"
        ScanPort(port).search_routers()

        # s = ScanPort2()
        # s.port_scan('192.168.1.207', [5555, 7555])

    def emulator_call(self, event):
        """ 点击 模拟器 按钮 """
        is_right = utils.is_right_click(event.num)
        if is_right:
            serial = self.serial2
        else:
            serial = self.serial1
        utils.thread_func(self.thread_emulator, args=(serial, ""))

    def thread_emulator(self, serial, _):
        result = util_atool.connect(serial)
        util_atool.show_msg(result)
        self.show_connect_result(serial)

    def on_closing(self):
        self.destroy()

    def destroy(self):
        tup = (self.entry, )
        for w in tup:
            w.destroy()
        del tup

        global _win_pos
        _win_pos = self.top_win.geometry()
        self.top_win.destroy()
        self.top_win = None


class MRecent:
    """最近记录显示项
    """
    ip = ''
    port = ''
    desc = ''
    parentObj = None

    def __init__(self, _parent):
        frame = tk.Frame(_parent, padx=2, pady=1)
        btn = tk.Button(frame, text='', width=40, command=self.btn_call)
        btn_close = tk.Button(frame, text='移除', fg=theme.COLOR_GRAY, width=4, command=self.close_call)
        btn.grid(column=1, row=1, sticky=tk.W)
        btn_close.grid(column=2, row=1)

        utils.set_groove((btn, btn_close))

        self.frame = frame
        self.btn = btn
        self.btn_close = btn_close

    def get_frame(self):
        return self.frame

    def set_ip(self, ip_str, desc, port=""):
        self.ip = ip_str
        self.port = port
        if port:
            name_str = '{0}  {1}:{2}'.format(desc, ip_str, port)
        else:
            name_str = '{0}  {1}'.format(desc, ip_str)
        self.btn['text'] = name_str

    def set_parent_class(self, obj):
        self.parentObj = obj

    def btn_call(self):
        obj = self.parentObj
        print(self.ip)
        if self.ip and obj is not None:
            if self.port:
                serial = "{0}:{1}".format(self.ip, self.port)
            else:
                serial = self.ip
            obj.connect(serial)

    def close_call(self):
        setting_atool.remove_recent(self.ip)
        self.destroy()

    def destroy(self):
        self.frame.grid_forget()
        tup = (self.frame, self.btn, self.btn_close)
        for w in tup:
            w.destroy()
        del tup


class ScanPort:
    """
    扫描开放指定端口的ip地址
    参考 https://blog.csdn.net/qq_30656253/article/details/79801368
    """

    # 创建接收路由列表
    routers = []

    # 创建互斥锁
    lock = threading.Lock()

    # 设置需要扫描的端口号列表
    # port_list = ['5555', '7555']

    search_result = "扫描结果："

    def __init__(self, port):
        self.port_list = [port]

    # 定义查询路由函数
    def search_routers(self):
        print("正在扫描..., 请稍等...")

        # 获取本地ip地址列表
        local_ips = socket.gethostbyname_ex(socket.gethostname())[2]
        # print("{}本地ip".format(local_ips))
        # 存放线程列表池
        all_threads = []
        # 循环本地网卡IP列表
        for ip in local_ips:
            for i in range(1, 255):
                # 把网卡IP"."进行分割,生成每一个可用地址的列表
                array = ip.split('.')
                # 获取分割后的第四位数字，生成该网段所有可用IP地址
                array[3] = str(i)
                # 把分割后的每一可用地址列表，用"."连接起来，生成新的ip
                new_ip = '.'.join(array)
                # print(new_ip)
                # 遍历需要扫描的端口号列表
                for port in self.port_list:
                    dst_port = int(port)
                    # 循环创建线程去链接该地址
                    t = threading.Thread(target=self.check_ip, args=(new_ip, dst_port))
                    t.start()
                    # 把新建的线程放到线程池
                    all_threads.append(t)
        # 循环阻塞主线程，等待每一字子线程执行完，程序再退出
        for t in all_threads:
            t.join()
        util_atool.show_msg(self.search_result)

    def check_ip(self, new_ip, port):
        """创建访问IP列表方法"""
        # 创建TCP套接字，链接新的ip列表
        scan_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 链接地址(通过指定我们 构造的主机地址，和扫描指定端口)
        result = scan_link.connect_ex((new_ip, port))
        # 设置链接超时时间
        scan_link.settimeout(1)
        scan_link.close()
        # print(result)
        # 判断链接结果
        if result == 0:
            # 加锁
            self.lock.acquire()

            ss = '{0}\t\t端口号 {1} 开放'.format(new_ip, port)
            print(ss)
            self.search_result += "\n" + ss
            # utils.showinfo(ss)

            self.routers.append((new_ip, port))
            # 释放锁
            self.lock.release()
        # print(routers)


if __name__ == '__main__':
    pass
