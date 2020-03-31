#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import util_theme
import utils
from atool import setting_atool, util_atool
from fftool.m_widget import IPanel


# pp = str(Path(utils.py_parent).parent)
# if utils.is_windows:
#     cur_pp = str(Path(utils.exe_parent).parent)
#     ff = "D:\FFmpeg"
#     sys.path.append(pp + os.sep + "shared")  # 父目录共享文件夹
#     sys.path.append(cur_pp + os.sep + "shared")  # 父目录共享文件夹
#     sys.path.append(ff + os.sep + "shared")  # 环境变量目录 shared目录
# else:
#     tool = os.path.expanduser('~/mytool/tool')  # 环境变量目录
#     sys.path.append(pp + os.sep + "shared")  # 父目录共享文件夹
#     sys.path.append(tool + os.sep + "shared")  # 环境变量目录 shared目录
# print(pp)
# print(sys.path)


class Main:
    destroy_arr = []
    apk_file = ''
    rename_str1 = ''
    rename_str2 = ''
    rename_str3 = ''

    data = None

    def __init__(self, apk):
        top_win = tk.Toplevel(utils.win)
        top_win.title('apk信息查看器')
        # top_win.geometry('200x200')
        # top_win.bind("<Destroy>", self.destroyed)

        color = util_theme.COLOR_BLACK

        frame_top = tk.Frame(top_win, padx=2, pady=2)
        frame_content = tk.Frame(top_win, padx=2, pady=2)

        bind = utils.bind
        btn_browse = tk.Button(frame_top, text='选择apk', fg=color, width=10)
        bind(btn_browse, self.btn_call)
        bind(btn_browse, self.btn_call, True)
        utils.tooltip(btn_browse, "左键点击 选择一个apk文件\n右键点击 读取剪贴板中的文件")

        frame_rename = tk.Frame(frame_top)
        btn_rename1 = tk.Button(frame_rename, text='应用名', width=6, fg=color)
        btn_rename2 = tk.Button(frame_rename, text='包名', width=6, fg=color)
        btn_rename3 = tk.Button(frame_rename, text='渠道名', width=6, fg=color)
        bind(btn_rename1, self.rename_call)
        bind(btn_rename2, self.rename_call)
        bind(btn_rename3, self.rename_call)
        bind(btn_rename1, self.rename_right_call, True)
        bind(btn_rename2, self.rename_right_call, True)
        bind(btn_rename3, self.rename_right_call, True)

        # labelframe
        label_frame_base = tk.LabelFrame(frame_content, text=' 基本 ', borderwidth=1)
        label_frame_sign = tk.LabelFrame(frame_content, text=' 签名、文件 ', borderwidth=1)
        label_frame_per = tk.LabelFrame(frame_content, text=' 权限 ', borderwidth=1)

        icon_frame = tk.Frame(label_frame_base, padx=0, pady=0)
        icon_left = tk.Frame(icon_frame, padx=0, pady=0)
        icon_right = tk.Frame(icon_frame, padx=0, pady=0)

        # label item
        config = [
            [icon_left, "名称", 0, 30, 1, 1],
            [icon_left, "包名", 0, 30, 1, 2],
            [icon_left, "版本号", 0, 30, 1, 3],
            [icon_left, "内部版本号", 0, 30, 1, 4],
            [icon_left, "友盟渠道", 0, 30, 1, 5],
            [icon_left, "友盟appkey", 0, 30, 1, 6],

            [label_frame_base, "min_sdk", 0, 55, 1, 2],
            [label_frame_base, "target_sdk", 0, 55, 1, 3],

            [label_frame_sign, "签名MD5", 0, 55, 1, 1],
            [label_frame_sign, "签名SHA1", 0, 55, 1, 2],
            [label_frame_sign, "签名SHA256", 0, 55, 1, 3],

            [label_frame_sign, "文件地址", 0, 55, 1, 4],
            [label_frame_sign, "文件大小", 0, 55, 1, 5],
            [label_frame_sign, "文件MD5", 0, 55, 1, 6],
        ]
        obj_arr = []
        for arr in config:
            col = arr[4]
            row = arr[5]
            obj = LabelItem(arr[0], name=arr[1], value_width=arr[3])
            obj.grid(column=col, row=row, sticky=tk.NW)
            obj_arr.append(obj)

        # icon
        m_icon = IconItem(icon_right)

        # 权限文本框
        m_entry = tk.Text(
            label_frame_per,
            height=9,
            width=65,
            fg=color,
            bd=1,
            wrap=tk.WORD,
            highlightthickness=1,
            highlightcolor=util_theme.COLOR_GRAY,
            font=util_theme.get_small_format()
        )

        btn_browse.grid(column=1, row=1)
        tk.Label(frame_top, width=19).grid(column=2, row=1)
        frame_rename.grid(column=3, row=1)

        btn_rename1.grid(column=2, row=1)
        btn_rename2.grid(column=3, row=1)
        btn_rename3.grid(column=4, row=1)

        label_frame_base.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        label_frame_sign.grid(column=1, row=2, sticky=tk.N + tk.S + tk.W)
        label_frame_per.grid(column=1, row=4, sticky=tk.N + tk.S + tk.W)
        m_icon.grid(column=1, row=1)
        m_entry.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)

        icon_left.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        icon_right.grid(column=2, row=1, sticky=tk.N + tk.S + tk.W)
        icon_frame.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)

        frame_top.grid(column=1, row=1, sticky=tk.W)
        frame_content.grid(column=1, row=2)

        self.m_name = obj_arr[0]
        self.m_package = obj_arr[1]
        self.m_ver = obj_arr[2]
        self.m_ver_inner = obj_arr[3]
        self.m_um_channel = obj_arr[4]
        self.m_um_key = obj_arr[5]
        self.m_min_sdk = obj_arr[6]
        self.m_target_sdk = obj_arr[7]

        self.m_sign_md5 = obj_arr[8]
        self.m_sign_sha1 = obj_arr[9]
        self.m_sign_sha256 = obj_arr[10]

        self.m_apk_path = obj_arr[11]
        self.m_apk_size = obj_arr[12]
        self.m_apk_md5 = obj_arr[13]

        self.m_entry = m_entry

        utils.set_groove((btn_browse, btn_rename1, btn_rename2, btn_rename3))

        self.m_icon = m_icon
        self.top_win = top_win
        self.btn_browse = btn_browse
        self.btn_rename1 = btn_rename1
        self.btn_rename2 = btn_rename2
        self.btn_rename3 = btn_rename3
        self.destroy_arr = [frame_top, frame_content, btn_browse]

        self.__update_tips()

        #  如果定义了 apk 地址
        if os.path.exists(apk):
            self.__show_info(apk)

    def __show_info(self, apk_file):
        self.apk_file = apk_file

        data = InfoData(apk_file)
        self.data = data

        v_app_name = data.app_name
        v_ver_name = data.ver_name
        v_package = data.package
        v_ver_code = data.ver_code
        v_um_channel = data.um_channel
        v_um_appkey = data.um_key
        v_min_sdk = data.min_sdk
        v_target_sdk = data.target_sdk
        icon_zip_path = data.icon_zip_path

        # 文件信息
        v_apk_file = apk_file
        v_apk_size = data.get_file_size()
        v_apk_md5 = data.get_file_md5()

        # 权限
        data.get_permission()
        v_permission = data.permission

        # 签名
        tup = self.get_sign_info(apk_file, utils.is_windows)
        v_rsa_md5 = tup[0]
        v_rsa_sha1 = tup[1]
        v_rsa_sha256 = tup[2]

        # icon
        if icon_zip_path:
            icon_url = self.extract_icon(apk_file, icon_zip_path)
            self.m_icon.set_icon(icon_url)
            self.m_icon.set_tips(icon_zip_path)

            t_path = setting_atool.output_dir + os.sep + "icon"
            utils.make_dir(t_path)

            save_path = "{dir}/{name}_v{ver}".format(dir=t_path, name=v_app_name, ver=v_ver_name)
            self.m_icon.icon_save_path = save_path

        if v_permission:
            self.m_entry.delete(1.0, tk.END)
            self.m_entry.insert(tk.INSERT, v_permission)

        #  更新组件值
        config = [
            [self.m_name, v_app_name],
            [self.m_package, v_package],
            [self.m_ver, v_ver_name],
            [self.m_ver_inner, v_ver_code],
            [self.m_um_channel, v_um_channel],
            [self.m_um_key, v_um_appkey],
            [self.m_min_sdk, v_min_sdk],
            [self.m_target_sdk, v_target_sdk],

            [self.m_sign_md5, v_rsa_md5],
            [self.m_sign_sha1, v_rsa_sha1],
            [self.m_sign_sha256, v_rsa_sha256],

            [self.m_apk_path, v_apk_file],
            [self.m_apk_size, v_apk_size],
            [self.m_apk_md5, v_apk_md5]
        ]
        for arr in config:
            arr[0].set_value(arr[1])

        self.__update_name_case()

    def btn_call(self, event):
        """点击按钮"""
        # 鼠标单击
        if not utils.is_right_click(event.num):
            types = [("apk文件", "*.apk")]
            init_dir = ''
            # init_dir = str( Path(init_dir).parent )
            f = filedialog.askopenfilename(filetypes=types, title='选择文件', initialdir=init_dir)
            if f:
                self.__show_info(str(f))

        # 鼠标右键点击
        else:
            arr = utils.clipboard_get_files()
            if len(arr):
                f = arr[0]
                self.__show_info(f)

    def rename_call(self, event):
        """点击重命名按钮"""
        if not self.apk_file:
            utils.showinfo('请选择一个apk文件')
            return

        w = event.widget
        s = ''
        msg = ''
        s1 = self.rename_str1
        s2 = self.rename_str2
        s3 = self.rename_str3
        if w == self.btn_rename1:
            s = s1 if s1 else ''
            msg = "命名失败！无法读取应用名称"

        elif w == self.btn_rename2:
            s = s2 if s2 else ''
            msg = "命名失败！无法读取应用包名"

        elif w == self.btn_rename3:
            s = s3 if s3 else ''
            msg = "命名失败！无法读取应用渠道名"

        if s:
            self.rename(self.apk_file, s)
        else:
            utils.showinfo(msg)

    def rename_right_call(self, event):
        w = event.widget
        index = 0
        if w == self.btn_rename1:
            index = 0
        elif w == self.btn_rename2:
            index = 1
        elif w == self.btn_rename3:
            index = 2

        files = utils.clipboard_get_files()
        arr = []
        for f in files:
            if str(Path(f).suffix) == ".apk":
                arr.append(f)
        for f in arr:
            d = InfoData(f)
            arr_new = self.__name_case(d.app_name, d.ver_name, d.package, d.um_channel)
            s = arr_new[index]
            if s:
                self.rename(f, "{}.apk".format(s))

    def __update_name_case(self):
        """ 更新命名方案 """
        if not self.apk_file:
            self.rename_str1 = ""
            self.rename_str2 = ""
            self.rename_str3 = ""
            self.__update_tips()
            return

        a_name = self.data.app_name
        a_ver = self.data.ver_name
        a_package = self.data.package
        a_channel = self.data.um_channel
        arr = self.__name_case(a_name, a_ver, a_package, a_channel)
        s1 = arr[0]
        s2 = arr[1]
        s3 = arr[2]

        self.rename_str1 = '{}.apk'.format(s1) if s1 else ''
        self.rename_str2 = '{}.apk'.format(s2) if s2 else ''
        self.rename_str3 = '{}.apk'.format(s3) if s3 else ''
        self.__update_tips()

    @staticmethod
    def __name_case(a_name, a_ver, a_package, a_channel):
        s = a_channel.replace("\t", "-").replace("     ", "-")
        s = s.replace("(", "").replace(")", "")
        s = s.replace("（", "").replace("）", "")
        a_channel = s

        s1 = ''
        s2 = ''
        s3 = ''
        # 应用名
        if a_name:
            if a_channel:
                s1 = "{0}-{1}-{2}".format(a_name, a_ver, a_channel)
            else:
                s1 = "{0}-{1}".format(a_name, a_ver)

        # 包名
        if a_package:
            if a_channel:
                s2 = "{0}-{1}-{2}".format(a_package, a_ver, a_channel)
            else:
                s2 = "{0}-{1}".format(a_package, a_ver)

        # 渠道名
        if a_channel:
            mark = "qb_"
            if a_channel.startswith("qb_"):
                s3 = a_channel.replace(mark, "")
            else:
                s3 = a_channel

        return s1, s2, s3

    def __update_tips(self):
        s1 = "左键点击以 应用名称 命名\n{}\n\n右键点击 可批量命名剪贴板中的apk".format(self.rename_str1)
        s2 = "左键点击以 应用包名 命名\n{}\n\n右键点击 可批量命名剪贴板中的apk".format(self.rename_str2)
        s3 = "左键点击以 渠道名称 命名\n{}\n\n右键点击 可批量命名剪贴板中的apk".format(self.rename_str3)
        utils.tooltip(self.btn_rename1, s1)
        utils.tooltip(self.btn_rename2, s2)
        utils.tooltip(self.btn_rename3, s3)

    def rename(self, apk, new_name=''):
        if not new_name:
            return

        a_path = Path(apk)
        new_path_str = str(Path(a_path.with_name(new_name)))
        if apk == new_path_str:
            utils.showinfo("命名的名称与当前相同，无需命名！")
            return

        if not os.path.exists(apk):
            utils.showinfo("此apk已不存在")
            return

        if not os.path.exists(new_path_str):
            try:
                print("正尝试重命名")
                os.rename(apk, new_path_str)
            except FileExistsError:
                s = "失败！\n文件已存在!!"
            except IOError:
                s = "失败！\n权限不足!"
            else:
                s = "成功！\n已改为:{}".format(new_name)
                self.apk_file = new_path_str
                self.m_apk_path.set_value(self.apk_file)
        else:
            s = "失败！\n存在同名文件!"
        utils.showinfo(s)

    @staticmethod
    def get_sign_info(apk_file, is_windows=False):
        """获得签名信息
        return (md5,sha1,sha256,result)
        """
        # reg_group = utils.reg_group

        # 查找、释放 rsa 文件
        rsa_out = setting_atool.temp_dir
        m_zip = util_atool.Unzip(apk_file)
        rsa = m_zip.find_rsa()
        m_zip.extract(rsa, rsa_out)
        m_zip.destroy()

        url = rsa_out + os.sep + rsa
        if not os.path.exists(url):
            print('rsa文件释放失败 {}'.format(url))
            return '', '', ''

        url_pem = str(Path(url).with_suffix(".pem"))
        c_trans_cert = '{openssl} pkcs7 -inform DER -in {rsa} -out {pem} -outform PEM -print_certs'
        c_print_cert = '{openssl} x509 -inform pem -in {pem} -fingerprint -{hash_type} -noout'
        openssl = util_atool.openssl_path if is_windows else 'openssl'
        index = len('openssl')

        # 转换RSA文件为PEM
        s = c_trans_cert.format(openssl=openssl, rsa=url, pem=url_pem)
        utils.execute(s)

        c_print = c_print_cert.format(openssl=openssl, rsa=url, pem=url_pem, hash_type="{hash_type}")
        s = c_print.format(hash_type="md5")
        result = utils.pipe(s)
        arr = result.split("Fingerprint=")
        # MD5 Fingerprint=EF:43:77:9C:15:7C:69:5E:25:BD:2D:6C:D3:49:FC:DD
        if len(arr) > 1:
            md5 = arr[1].replace(":", "")
        else:
            md5 = "计算出错"

        s = c_print.format(hash_type="SHA1")
        result = utils.pipe(s)
        arr = result.split("Fingerprint=")
        sha1 = arr[1] if len(arr) > 1 else "计算出错"

        s = c_print.format(hash_type="SHA256")
        result = utils.pipe(s)
        arr = result.split("Fingerprint=")
        sha256 = arr[1] if len(arr) > 1 else "计算出错"

        md5 = md5.replace("\\n'", "")
        sha1 = sha1.replace("\\n'", "")
        sha256 = sha256.replace("\\n'", "")
        return md5, sha1, sha256

    @staticmethod
    def extract_icon(apk_file, icon_zip_path):
        """释放 icon 文件
        """
        # 查找、释放 rsa 文件
        png_out = setting_atool.temp_dir
        m_zip = util_atool.Unzip(apk_file)
        m_zip.extract(icon_zip_path, png_out)
        m_zip.destroy()

        final_icon = png_out + os.sep + icon_zip_path
        return final_icon

    def destroy(self):
        for w in self.destroy_arr:
            w.grid_forget()
            w.destroy()
        del self.destroy_arr


class LabelItem(IPanel):
    """单项显示对象"""

    def __init__(self, _parent, **kw):
        IPanel.__init__(self, _parent)
        # **kw
        key = 'name'
        txt_name = kw[key] if key in kw else ""
        key = 'name_width'
        name_width = kw[key] if key in kw else 10
        key = 'value_width'
        value_width = kw[key] if key in kw else 100

        frame = self.frame
        tf = util_theme.get_small_format()

        txt_name = tk.Label(
            frame,
            text=txt_name + ":",
            width=name_width,
            fg=util_theme.COLOR_BLACK,
            font=tf,
            anchor=tk.N + tk.E
        )
        txt_value = tk.Text(
            frame,
            height=1,
            width=value_width,
            fg=util_theme.COLOR_BLACK,
            bd=0,
            wrap=tk.WORD,
            highlightthickness=1,
            highlightcolor=util_theme.COLOR_GRAY,
            font=tf
        )
        txt_name.grid(column=1, row=1, sticky=tk.NW)
        txt_value.grid(column=3, row=1, sticky=tk.N + tk.S + tk.W)

        utils.set_groove((txt_value,))

        self.txt_name = txt_name
        self.txt_value = txt_value

    def set_name(self, _name):
        self.txt_name['text'] = _name

    def set_value(self, _value):
        # self.txt_value['text'] = str(_value)
        self.txt_value.delete(1.0, tk.END)
        self.txt_value.insert(tk.INSERT, str(_value))


class IconItem(IPanel):
    """图标显示对象"""

    icon_size = 96
    max_width = 144

    # image = None
    # im = None

    def __init__(self, _parent):
        IPanel.__init__(self, _parent)

        frame = self.frame
        canvas = tk.Canvas(
            frame,
            width=self.icon_size,
            height=self.icon_size
        )
        # bg=util_theme.COLOR_GRAP2,
        # frame.create_rectangle(0, 0, 72, 72, fill=util_theme.COLOR_GRAP2)
        # image = self.canvas.create_image(50, 50, anchor=tk.N + tk.E, image=filename) # only gif
        # , outline = util_theme.COLOR_GRAY
        # canvas.create_rectangle(2, 2, 96, 96)
        canvas.grid(columns=1, row=1)

        color = util_theme.COLOR_BLACK
        color2 = util_theme.COLOR_GRAY
        btn_save = tk.Button(frame, text='保存', width=8, fg=color)
        btn_save.bind("<Button-1>", self.btn_click)

        txt = tk.Label(frame, fg=color2, font=util_theme.get_small_format())

        utils.set_groove((btn_save,))

        self.canvas = canvas
        self.pre_img = None
        self.btn_save = btn_save
        self.icon_path = ""
        self.icon_save_path = ""
        self.txt = txt

    def set_icon(self, icon_path):
        if self.pre_img is not None:
            self.pre_img.image = None
            self.pre_img.forget()
            self.txt['text'] = ""

        self.btn_save.forget()
        if not os.path.exists(icon_path):
            return
        ext = str(Path(icon_path).suffix)
        fys = ['.png', '.jpg', '.gif']
        if fys.count(ext) == 0:
            print("xml类型的 icon，暂不支持显示")
            return

        # global image
        # global im
        # image = Image.open(icon_path)
        # im = ImageTk.PhotoImage(image)
        # size = self.icon_size
        # self.canvas.create_image(0, 0, anchor=tk.NW, image=im)

        # pip3 install pillow
        try:
            from PIL import Image, ImageTk, ImageFilter
        except ImportError:
            can_i_use_pil = False
            print("PIL包导入错误, 无法显示apk图标！！！")
        else:
            can_i_use_pil = True

        if can_i_use_pil:
            img_size = ""
            load = Image.open(icon_path)
            try:
                load = load.filter(ImageFilter.SMOOTH_MORE)
            except ValueError:
                print("图标平滑显示miss\n{}".format(icon_path))
            else:
                pass

            try:
                img_size = utils.get_image_size2(icon_path)
                # 1920x1080
            except ValueError:
                print("获取图标尺寸失败\n{}".format(icon_path))
            else:
                pass

            if img_size:
                split_arr = img_size.split("x")
                w = int(split_arr[0])
                h = int(split_arr[1])
                scale_value = min(self.max_width / w, self.icon_size / h)
                w = int(w * scale_value)
                h = int(h * scale_value)
            else:
                w = self.icon_size
                h = self.icon_size
            size = (w, h)
            render = ImageTk.PhotoImage(load.resize(size))
            img = tk.Label(self.frame, image=render, anchor=tk.N + tk.E)
            img.image = render
            img.grid(columns=1, row=1, sticky=tk.NW)
            self.txt['text'] = img_size
            self.txt.grid(columns=1, row=3, sticky=tk.NW)
            self.btn_save.grid(columns=1, row=2, sticky=tk.NW)

            self.pre_img = img
            self.icon_path = icon_path

    def set_tips(self, tips):
        if self.pre_img is not None:
            utils.tooltip(self.pre_img, tips)

    def btn_click(self, event):
        if not os.path.exists(self.icon_path):
            return
        ext = str(Path(self.icon_path).suffix)
        save_path = self.icon_save_path + ext
        shutil.copy(self.icon_path, save_path)
        utils.open_file(save_path, True)


class InfoData:
    """
    apk信息数据对象
    """
    file_size = ''
    apk_md5 = ''
    permission = ''

    def __init__(self, apk_file):
        self.apk_file = apk_file
        reg_one = self.reg_group_one
        comment_str = self.comment_str

        dc = util_atool.get_apk_info(apk_file)
        v_ver_name = dc['version_name']
        v_ver_code = dc['version_code']
        v_package = dc['package_name']
        v_app_name = dc['app_name']
        icon_zip_path = dc['icon_path']
        v_target_sdk = comment_str(dc['target_sdk_version'])
        v_min_sdk = comment_str(dc['sdk_version'])

        # 读取友盟渠道 ==================================================================
        result = util_atool.get_apk_xmlstrings(apk_file)
        lines = result.split('\n')
        key = 'UMENG_CHANNEL'
        value = ''
        v_um_channel = ''
        for i in range(len(lines)):
            line = lines[i]
            if line.count(key):
                value = lines[i + 1]
                break
        if value:
            reg = 'A: android:value.*=.*Raw: \"(.*)\"'
            v = reg_one(value, reg)
            v_um_channel = comment_str(v, 2)
            # reg = "A: android:value.*=\(type .*\)(.*)"
            # tup = reg_group(value,reg)
            # if len(tup)>0:
            #     print(tup[0])
            #     print('case2',tup[0])
            #     a = tup[0]
        # A: android:value(0x01010024)="qb_1" (Raw: "qb_1")
        #  A: android:value(0x01010024)=(type 0x4)0x40200000
        # A: android:value(0x01010024)=(type 0x10)0x8

        key = 'UMENG_APPKEY'
        value = ''
        v_um_appkey = ''
        for i in range(len(lines)):
            line = lines[i]
            if line.count(key):
                value = lines[i + 1]
                break
        if value:
            reg = 'A: android:value.*=.*Raw: \"(.*)\"'
            v = reg_one(value, reg)
            v_um_appkey = v if v else ''

        self.app_name = v_app_name
        self.ver_name = v_ver_name
        self.ver_code = v_ver_code
        self.package = v_package
        self.um_key = v_um_appkey
        self.um_channel = v_um_channel
        self.icon_zip_path = icon_zip_path
        self.min_sdk = v_min_sdk
        self.target_sdk = v_target_sdk

    @staticmethod
    def comment_str(v, comment_type=1):
        if v is None:
            return ""

        a = v
        if comment_type == 2:
            b = setting_atool.get_channel_desc(v)
        elif comment_type == 3:
            b = setting_atool.get_permission_desc(v)
        else:
            b = setting_atool.get_api_desc(v)

        if b:
            return '{0}     ({1})'.format(a, b)
        else:
            return a

    def get_file_size(self):
        if not self.file_size:
            file_path = self.apk_file
            if not os.path.exists(file_path):
                return ''
            size = os.path.getsize(file_path)
            size_str = '{:,}'.format(size)
            mb_str = '%.2f' % (size / 1024 / 1024)
            self.file_size = '{0}字节（{1}MB）'.format(size_str, mb_str)
        return self.file_size

    def get_file_md5(self):
        if not self.apk_md5:
            self.apk_md5 = utils.get_file_md5(self.apk_file)
        return self.apk_md5

    def get_permission(self):
        result = util_atool.get_permissions(self.apk_file)
        reg = 'uses-permission: name=\'(.*)\''
        p = re.compile(reg, re.M | re.I)
        m = p.findall(result)
        # v_permission = ''
        # 兼容旧版aapt
        if not len(m):
            reg = 'uses-permission: (.*)'
            p = re.compile(reg, re.M | re.I)
            m = p.findall(result)
        if m:
            p = []
            arr = list(m)
            for item in arr:
                s1 = setting_atool.get_permission_desc(item)
                if s1:
                    s = item + "\n" + s1 + "\n\n"
                else:
                    s = item + "\n"
                p.append(s)
            self.permission = "".join(p)

    @staticmethod
    def reg_group_one(search_str, reg):
        """匹配其中一个结果
        若不匹配 返回空字符 ""
        """
        tup = utils.reg_group(search_str, reg)
        if len(tup) > 0:
            return tup[0]
        else:
            return ""


if __name__ == "__main__":
    pass
