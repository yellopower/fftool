#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from subprocess import call
from subprocess import check_output
from subprocess import getoutput
from tkinter import messagebox

import tttk

#
# 判断系统
#
is_windows = True if platform.system() == "Windows" else False
is_mac = True if platform.system() == "Darwin" else False

# py文件所在目录，如果由外部调用请对本变量进行赋值
py_parent = ''

exe_parent = os.path.dirname(__file__)


# 路径兼容
def pathlib_path(path_str, tk_windows_fix=False):
    """统一 mac 和 windows 路径字符串
    返回 字符串
    """
    new_str = str(Path(path_str))
    if tk_windows_fix and is_windows:
        new_str = new_str
    return new_str


def pathlib_paths(path_arr, tk_windows_fix=False):
    """统一 mac 和 windows 路径字符串
    返回 字符串数组
    """
    narr = []
    for p in path_arr:
        pstr = str(pathlib_path(p, tk_windows_fix))
        narr.append(pstr)
    return narr


def pathlib_path_tup(path_tup, tk_windows_fix=False):
    """统一 mac 和 windows 路径字符串
    返回 字符串元组
    """
    narr = []
    for p in path_tup:
        pstr = pathlib_path(p, tk_windows_fix)
        narr.append(pstr)
    return tuple(narr)


def pathlib_parent(path_str):
    p = Path(path_str)
    return p.parent


def fix_wrap(_str):
    if is_windows:
        _str = _str.replace("\r\n", "\n")
        _str = _str.replace("\r", "\n")
        return _str
    else:
        return _str


def fix_cmd_wrap(_str):
    if is_windows:
        return _str.replace('\\', '^')
    else:
        return _str


def fix_tk_smb_url(path_str):
    return path_str.replace('\\\\', '\\')


def fix_tk_smb_urls(arr):
    """
    \\\\192.168.0.10\\公共文件\\1.mp4 给 tk的listbox，获取到的路径是
    \\\\\\\\192.168.0.10\\\\公共文件\\\\1.mp4
    本方法用于修复该种情况
    """
    narr = []
    for pathStr in arr:
        narr.append(fix_tk_smb_url(pathStr))
    return narr


def fix_windows_tk_url(path_str):
    """
    将
    \\\\192.168.0.10\\公共文件
    转成
    //192.168.0.10/公共文件
    """
    if is_windows:
        path_str = path_str.replace("\\", "/")
    return path_str


#
# 系统工具
#
def _check_out_put(pstr):
    _exc = check_output(pstr, shell=True)
    return _exc


def _get_out_put(pstr):
    _exc = getoutput(pstr)
    return _exc


def pipe(pstr, is_adb=False):
    p = subprocess.Popen(pstr, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    if is_adb:
        if is_windows:
            _exc = p.stdout.read()
            if type(_exc) is bytes:
                try:
                    _exc = _exc.decode('utf-8', 'ignore')
                except UnicodeDecodeError:
                    print('utf UnicodeDecodeError ')
                else:
                    pass

            if type(_exc) is not str:
                try:
                    _exc = _exc.decode("gb2312", 'ignore')
                except UnicodeDecodeError:
                    print('gb2312 UnicodeDecodeError ')
                    pass
        else:
            _exc = str(p.stdout.read())
    else:
        _exc = str(p.stdout.read())
    return _exc


def hide_file(path_str, is_hide=True):
    p = Path(path_str)
    if not p.exists():
        return

    if is_windows:
        s_hide = 'attrib +h +r +s "{}"'
        s_show = 'attrib -r -s -h "{}"'
        if is_hide:
            s = s_hide
        else:
            s = s_show
        s = s.format(p)
        os.system(s)

    if is_mac:
        s_hide = 'chflags hidden "{}"'
        s_show = 'chflags nohidden "{}"'
        if is_hide:
            s = s_hide
        else:
            s = s_show
        s = s.format(p)
        pipe(s)


def execute(pstr):
    """执行命令行命名
    参数:
        cmd_str {[ string]} --  脚本内容
    """
    if is_windows:
        return _check_out_put(pstr)
    else:
        return _get_out_put(pstr)


def make_dir(_path):
    """ 新建文件夹
    """
    if _path and not os.path.exists(_path):
        os.makedirs(_path)


def open_dir(dir_path):
    """ 打开文件夹
    """
    if not os.path.exists(dir_path):
        return False

    if is_windows:
        fix_path = pathlib_path(dir_path)
        s = 'start explorer "' + fix_path + '"'
        # os.system(s)
        _check_out_put(s)
    elif is_mac:
        s = 'open "{0}"'.format(dir_path)
        _check_out_put(s)
    return True


def open_file(file_path, select_file=False):
    """ 打开文件 """
    if not os.path.exists(file_path):
        return

    if is_windows:
        fix_path = pathlib_path(file_path)
        if select_file:
            s = 'explorer /select,"{}"'.format(fix_path)
            os.system(s)
        else:
            # s = 'start explorer "'+fix_path+'"'
            s = 'start explorer "{}"'.format(fix_path)
            _check_out_put(s)
    elif is_mac:
        if select_file:
            s = 'open -R "{0}"'.format(file_path)
        else:
            s = 'open "{0}"'.format(file_path)
        _check_out_put(s)


def remove_file(file_path, is_file=True):
    if os.path.exists(file_path):
        try:
            if is_file:
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)
        except IOError:
            print("没能删除 " + IOError.filename)


def move_file(file1, file2):
    try:
        shutil.move(file1, file2)
    except (FileNotFoundError, OSError) as err:
        print("移动文件错误", file1, file2, err)


def get_hms():
    time_local = time.localtime()
    return time.strftime("%H:%M:%S", time_local)


def shutdown():
    """关机
    """
    if is_windows:
        os.system('shutdown -s -f -t 10')
        # os.system(pStr)
        # call(pStr)
    elif is_mac:
        call(['osascript', '-e', 'tell app "System Events" to shut down'])
        # os.system("poweroff")
        # pStr = "sudo shutdown -h +1"
        # sudo kill 1746


def set_title(title):
    """设置 终端/命令行 标题
    """
    # 终端
    if is_mac:
        sys.stdout.write('\33]0;' + title + '\a')
        sys.stdout.flush()
    # windows command
    if is_windows:
        os.system("title " + title)
    # ctypes.windll.kernel32.SetConsoleTitleW(titleStr)
    return


def read_txt(txt_file, strip_comma=True):
    """
    读取txt并处理成数组
        :param txt_file:
        :param strip_comma: 是否去掉首尾的空白字符
    """
    fopen = open(txt_file, 'r', encoding='utf-8')
    lines = fopen.readlines()
    fopen.close()
    # 读取出不含空行的内容
    # 空白符包含：空格、制表符(\t)、换行(\n)、回车等(\r）
    lists = []
    for line in lines:
        line = line.replace("\n", "")
        if strip_comma:
            line = line.strip('"')
            line = line.strip("'")
        if not line or line.isspace():
            continue
        lists.append(line)
    return lists


def split_str(str_content, no_duplicate=False):
    """
    是否去掉首尾的空白字符
    :return:
    """
    ss = str_content
    ss = ss.replace("\r", "")  # 兼容 windows 的 /r/n
    lines = ss.split("\n")

    # 读取出不含空行的内容
    # 空白符包含：空格、制表符(\t)、换行(\n)、回车等(\r）
    lists = []
    strip_comma = True
    for line in lines:
        if strip_comma:
            line = line.strip('"')
            line = line.strip("'")
        if not line or line.isspace():
            continue
        if no_duplicate:
            if lists.count(line) == 0:
                lists.append(line)
        else:
            lists.append(line)
    return lists


def write_txt(_txt, save_str):
    if len(save_str):
        f1 = open(_txt, 'w', encoding='utf-8')
        f1.writelines(save_str)
        f1.close()


def write_txt_by_arr(_txt, _arr):
    for i in range(len(_arr)):
        _arr[i] = _arr[i] + "\n"
    if len(_arr):
        write_txt(_txt, _arr)


def write_log(log_file, save_str, is_reverse=True):
    fpath = log_file
    is_exists = os.path.exists(fpath)
    if not is_exists:
        write_txt(fpath, save_str)
    else:
        if is_reverse:
            rf = open(fpath, "r+", encoding='utf-8')
            rs = rf.read()
            rf.close()
            save_str += "\n" + rs
            write_txt(fpath, save_str)
        else:
            rf = open(fpath, "r+", encoding='utf-8')
            rf.seek(0, 2)
            rf.write("\n" + save_str)
            rf.close()


def thread_func(func, args=()):
    t2 = threading.Thread(target=func, args=args)
    t2.setDaemon(True)
    t2.start()


#
# 字符处理和数据类型逻辑处理
#


def get_file_names(filename):
    """
    获取文件路径、文件名、后缀名
        :param filename:
    """
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension


def get_file_full_name(filename):
    arr = get_file_names(filename)
    n = arr[1]
    ext = arr[2]
    return n + ext


def get_file_name(filename):
    return get_file_names(filename)[1]


def get_file_type(filename):
    return get_file_names(filename)[2]


def list_dir(path, list_name):
    """
    传入存储的list
    :param path:
    :param list_name:
    :return:
    """
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            list_dir(file_path, list_name)
        else:
            list_name.append(file_path)


# def setBinPath(_parentPath, _str):
#     """绝对路径 转 相对路径
#     """
#     # tup的长度需为1
#     if not len(_str):
#         return ""
#     s = str(_str)
#     # s = s.replace(_parentPath, "./")
#     s = os.path.relpath(s)

#     return s
# def transBinPath(_parentPath, _str):
#     """相对路径转绝对路径
#     """
#     # ss = _str[0:2]
#     # if ss == "./":
#     #     return _parentPath + _str[2:len(_str)]
#     # else:
#     #     return _str
#     return os.path.abspath(_str)


def append_tup(tub1, tub2):
    """
    取 两个tup的合集（tup去重添加）
        :param tub1:
        :param tub2:
    """
    arr = list(tub2)
    narr = []
    for item in arr:
        if tub1.count(item) == 0:
            narr.append(item)
    if len(narr):
        return tub1 + tuple(narr)
    else:
        return tub1


def get_image_size(_img):
    """
    获得图片的尺寸
        :param _img:   图片地址
        :return [width,height]
    """
    import struct
    import imghdr

    with open(_img, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return [0, 0]
        if imghdr.what(_img) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return [0, 0]
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(_img) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(_img) == 'jpeg':
            try:
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception:  # IGNORE:W0703
                return [0, 0]
        else:
            return [0, 0]
        return [width, height]


def get_image_size2(_img):
    arr = get_image_size(_img)
    return "{0}x{1}".format(arr[0], arr[1])


def get_file_md5(file_path):
    """
    获取文件md5值
    :param file_path: 文件路径名
    :return: 文件md5值
    """
    with open(str(file_path), 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        _hash = md5obj.hexdigest()
    return str(_hash).upper()


# tk 相关
def showinfo(msg, title=""):
    messagebox.showinfo(message=msg, title=title, icon='info')


def tooltip(obj, msg, delay=500, duration=3000):
    tttk.Tooltip(obj, msg, delay=delay, duration=duration)


def alert(msg, func, params, title=""):
    result = messagebox.askokcancel(message=msg, title=title)
    if result:
        len_param = len(params)
        if len_param == 3:
            func(params[0], params[1], params[2])
        elif len_param == 2:
            func(params[0], params[1])
        else:
            func(params[0])


def set_state(btn, enable=True):
    btn['state'] = tk.NORMAL if enable else tk.DISABLED


def set_states(btn1, btn2, enable=True):
    btn1['state'] = tk.NORMAL if enable else tk.DISABLED
    btn2['state'] = tk.NORMAL if enable else tk.DISABLED


def clone(widget):
    parent = widget.nametowidget(widget.winfo_parent())
    cls = widget.__class__

    new_widget = cls(parent)
    for key in widget.configure():
        new_widget.configure({key: widget.cget(key)})
    return new_widget


def bind(widget, func, is_right=False):
    """
    绑定点击事件
    :param widget:  按钮
    :param func:    点击执行
    :param is_right: 是否右键单击，windows（<Button-3>） 和 mac（<Button-2>）
    :return:
    """
    if is_right:
        if is_windows:
            s = "<Button-3>"  # win 右键
        else:
            s = "<Button-2>"  # mac 右键
    else:
        s = "<Button-1>"  # 左键
    widget.bind(s, func)


def is_right_click(event_num):
    """ 判断是否是右击，请传入 event.num """
    if is_windows and event_num == 3:
        return True
    if is_mac and event_num == 2:
        return True
    return False


def var_to_list(_str):
    # print('_str', _str)
    _str = _str.strip(",)")  # 只有一条记录时，结尾出现,)字符
    arr = _str.strip("(").strip(")").split(",")
    for i in range(len(arr)):
        arr[i] = arr[i].strip(" ").strip("'").strip('"')
    return arr


def var_to_list_smb(_str):
    arr = var_to_list(_str)
    return fix_tk_smb_urls(arr)


def var_is_empty(var_str):
    return True if var_str == "('',)" else False


def bool_to_str(bool_value):
    if bool_value:
        return '1'
    else:
        return '0'


def str_to_bool(str_value):
    """
    字符串转 bool 类型
    :param str_value:    '1', 'True', 'true' 返回 True
    :return:
    """
    l1 = ['1', 'True', 'true']
    if l1.count(str_value):
        return True
    else:
        return False


def int_var_to_bool(_var):
    """int_var转 bool类型"""
    if _var.get():
        return True
    else:
        return False


def int_var_to_str(_var):
    """int_var转 bool类型"""
    return str(_var.get())


def set_groove(_tup):
    for w in _tup:
        w.configure(relief=tk.GROOVE)


def clipboard_append(text):
    if win is not None:
        win.clipboard_append(text)


def clipboard_clear():
    if win is not None:
        win.clipboard_clear()


def lift_win(widget):
    """窗口前置"""
    widget.attributes("-topmost", True)
    widget.after_idle(widget.attributes, '-topmost', False)
    widget.focus()


def lift_and_check(con):
    """将对象中的top_win窗口前置，如果对象为空时返回false"""
    if con is None or con.top_win is None:
        return False
    else:
        lift_win(con.top_win)
        return True


def clipboard_get():
    """Retrieve data from the clipboard on window's display.

    The window keyword defaults to the root window of the Tkinter
    application.

    The type keyword specifies the form in which the data is
    to be returned and should be an atom name such as STRING
    or FILE_NAME.  Type defaults to STRING.

    This command is equivalent to:

    selection_get(CLIPBOARD)
    """
    if win:
        return win.call(('clipboard', 'get'))
    else:
        return ""


def clipboard_set(text):
    clipboard_clear()
    clipboard_append(text)


def clipboard_get_files(check_valid=True):
    p = clipboard_get()
    p = p.replace("\r", "")
    arr = p.split("\n")
    if check_valid:
        arr_new = []
        for f in arr:
            if os.path.exists(f):
                arr_new.append(f)
        return arr_new
    else:
        return arr


def reg_group(search_str, reg):
    """匹配结果输出至 tup
    """
    m = re.search(reg, search_str, re.M | re.I)
    if m:
        return m.groups()
    else:
        return tuple([])


def find_ip(string_ip):
    result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", string_ip)
    if result:
        return result
    else:
        return []


def legal_file_name(_str):
    _str = _str.replace(" ", "-")
    _str = _str.replace("\t", "    ")
    _str = _str.replace("\r", "")
    _str = _str.replace("\n", "")
    return _str


def base64_img(str_or_path, img_save_path=''):
    # base64和图片互转
    if img_save_path:
        # 字符串 转 图片文件
        # str = "iVBORw0KGgoAAAANSUhEUgAAANwAAAAoCAIAAAAaOwPZAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAQuSURBVHhe7ZptmoMgDIR7rh6o5+lpvEwP01XUGshAokgX+8z+7PKRTF6SoN7e/KMCnSlw68wemkMF3oSSEHSnAKHsLiQ0iFCSge4UIJTdhYQGEUoy0J0ChLK7kNAgQkkGulOAUHYXEhpEKMlAdwpcG8rhcRv/HkN3stIgW4F88DYoX89nObjmANuOc0eMXpHHcyX9+mowhgHKmdlChM0BZzvzet6DSSW7xjEWk8Hu+/O1x7zF1237/Uu4t/O46V6sZuARoZb9KqbO7On4rJlykqcYYnNAjSbx3Gmrj6WTzxirVlA+90F82G+nm4fX3zOxgqyKqRaUU7b8FpRDOeyjJa7k5oByT1yWse4mxfDC3NrrprnQtQeUMuUXoURmCGHdKfl/oTS8MElxu2mudO0BXUCZL8efVGU0EmsQjkGpM2H8y/CwGtW1C3el8ywxhHKWxgOlaPNj0VcRRW+OoiKvCXF0o6YeXWLQDaNQyMf1Clhsi22D9HUNXOBCVZamaBmiO5BxRdRQOt3M3oFUAD4/HDolSChx7AvXzRIJQtgsUfMu6HB+HglNLc5d5KiwpcAqTH7Idk/lvLD9Z0rUx4vYWL2UJ4WY6XbdL91ML57+EjsRNEMnw/LCrKklN9NNkbuLvKsdabjM/ZMByh+PDWuuw6kDEYXPzeSfzGARlNG1M1ENRCfGLlUuJ5MVTg+UyxGzC+1+KN/DkDyuTSVbqo7vNnagfKPTrH9b8pQtgQ/PRCifDTaUJaIWw8adUycklLrcppkyCZfkJ5cYlSZnQTkmsYf58OYAlMpg6JnlhYlC9uxhIdWvbr1NS8Ahc9pgQlkkai3fOorVUK4JGeYTJIgVTm+mnCqrmSfOgDJ0mOlOlhcmClk3M0KmPzeF0mnDGVB6LjqbmKB8p5GRQ34DStRCdpEpp5MRNWRNocwsjk9i7nyqugzPYTWUSZuqe0qVucAT5tgH9ITmxEdCdihjpcCVAgfI8uJ4pgx3K3UhgBeRQ9dtbJmjp1TnYmsKoSH1UGqKE23mxlrsri4yKsuAFnZ5BrAugypw0/IdSvHmxHJbEI6lREzj0asuOc7TR8BONdd9pNKCo4LRNY9CdgCEXjqObDhQvsFpy7z7DsqHP9khxp9DzNeKbSR+Iy3/n31tqVFYe17xFUZkTu507+4px4USFwBRm32lbzFyXphgRMtn3cwqqaef8a0UrMHlaJYM8RC1Iq2DeOXvKUdVjALmzromST8+4N+Egm9rrwzl/DpAVlddnE9su36Jyx6ECtkUxufaUMJOzfwQsxldUbnTLyO/ckCcNsS112yDmkkGF/4xKL8rHndrowChbKMrV61QgFBWiMepbRQglG105aoVChDKCvE4tY0ChLKNrly1QgFCWSEep7ZRgFC20ZWrVihAKCvE49Q2ChDKNrpy1QoF/gDXIhmWmc+CSAAAAABJRU5ErkJggg=="
        try:
            img_data = base64.b64decode(str_or_path)
            file = open(img_save_path, 'wb')
            file.write(img_data)
            file.close()
        except FileExistsError:
            s = "失败！\n文件已存在!!"
        except IOError:
            s = "失败！\n权限不足!"
        else:
            s = "保存成功:\n{}".format(img_save_path)
        showinfo(s)

    else:
        # 文件转 base64
        f = open(str_or_path, 'rb')
        base64_data = base64.b64encode(f.read())  # 使用base64进行加密
        f.close()
        clipboard_set(base64_data)


# ffmpeg对象持有
ffmpeg = ''
serial = ''
last_screen_shot = ''
label_msg = None
ffmpeg_path = ""

main = None  # main.py的持有
win = None  # tk win
remote_control_parent = None

if __name__ == "__main__":
    if not py_parent:
        py_parent = os.path.dirname(__file__)

    # 测试读取剪切板
    win = tk.Tk()
    win.mainloop()

    # ffmpeg=os.path.expanduser('~/mytool/tool/ffmpeg')
    # arr=["/Users/hf/Desktop/output/1/020010386--3.mp4"]
    # for mp4 in arr:
    #     print(dc,"\n")
    # file1='/Users/qinbaomac-mini/Desktop/output/tempDir/-138大马路宽又宽.mp4'
    # file2='/Users/qinbaomac-mini/Desktop/output/138大马路宽又宽.mp4'
    # move_file(file1,file2)
