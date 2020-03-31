#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import tkinter as tk
import tkinter.font as tk_font
from pathlib import Path
from tkinter import filedialog
from tkinter import ttk

import util_theme
import utils
from fftool import setting_fftool


class IPanel:
    """
    面板容器对象 接口类
    """

    def __init__(self, _parent):
        self.frame = tk.Frame(_parent)

    def get_frame(self):
        return self.frame

    def grid(self, **kw):
        self.frame.grid(kw)

    def grid_forget(self):
        self.frame.grid_forget()


class Start(IPanel):
    """
    界面底部的开始按钮 和 输出活动显示框
    """

    def __init__(self, _parent, **kw):
        IPanel.__init__(self, _parent)
        frame = self.frame

        if 'text' in kw:
            btn_text = kw['text']
        else:
            btn_text = "开始"

        btn_call = kw['command'] if 'command' in kw else ''

        # frame = tk.Frame(_parent, bd=1, padx=0, pady=2)
        # frame.grid(column=1, row=1, sticky=tk.W)

        # 颜色
        c_black = util_theme.COLOR_BLACK
        c_list_bg = util_theme.COLOR_LIST_BG
        txt_width = 80 + 6

        # 开始转码 按钮
        btn = tk.Button(frame, text=btn_text, command=btn_call)
        btn.config(height=5, width=12)

        # listbox 和 scrollBar
        self.v2 = tk.StringVar()
        w = kw['width'] if 'width' in kw else txt_width
        list_box = tk.Listbox(frame,
                              selectmode=tk.EXTENDED,
                              listvariable=self.v2,
                              width=w,
                              height=5,
                              fg=c_black,
                              bd=0,
                              background=c_list_bg,
                              setgrid=1,
                              activestyle='none'
                              )
        scroll_bar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        # self.scrollBar.set(0.5,1)

        list_box.config(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=list_box.yview)

        btn.grid(column=1, row=1, sticky=tk.N + tk.W)
        list_box.grid(column=2, row=1, sticky=tk.W)
        scroll_bar.grid(column=3, row=1, sticky=tk.N + tk.S)

        utils.set_groove((btn,))

        self.frame = frame
        self.start_btn = btn
        self.list_box = list_box

    def set_state(self, boo):
        utils.set_state(self.start_btn, boo)

    def see(self, num):
        self.list_box.see(num)

    def get_string_var(self):
        return self.v2.get()

    def set_string_var(self, tup):
        self.v2.set(tup)
        self.see(len(tup))

    def update_query(self, q_str, warning=False):
        q_str = utils.get_hms() + " " + q_str
        utils.set_title(q_str)
        if warning:
            ""
        # self.logTxt['fg'] = "#ff5643" if warning else "#0096FF"
        # self.logTxt['text'] = qStr
        tup = tuple([q_str])
        var_str = self.get_string_var()
        if utils.var_is_empty(var_str):
            new_tup = tup
        else:
            v = utils.var_to_list(var_str)
            if len(v):
                new_tup = utils.append_tup(tuple(v), tup)
            else:
                new_tup = tup
        new_arr = list(new_tup)
        tmp_arr = []
        for item in new_arr:
            if item:
                tmp_arr.append(item)
        tup = tuple(tmp_arr)
        self.set_string_var(tup)

    def clear_query(self):
        tup = tuple([''])
        self.set_string_var(tup)


class Shutdown(IPanel):
    # 关机小部件
    # 1. 调用本部件关机方法后，会出现60秒倒计时；
    # 2. 倒计时期间可以点击勾选框取消关机

    time_count = 0
    after_id = 0
    need_shutdown = False
    shutdown_select = False

    def __init__(self, _parent):
        IPanel.__init__(self, _parent)
        self.frame = tk.Frame(_parent, bd=1, padx=0, pady=0)

        c_black = util_theme.COLOR_BLACK
        c_red = util_theme.COLOR_RED

        self.var_cb = tk.IntVar()
        cb = tk.Checkbutton(self.frame, text="完成后关机", fg=c_black, variable=self.var_cb, command=self.shutdown_cancel)
        cb.grid(column=3, row=2, sticky=tk.W)
        self.txt = tk.Label(self.frame, text='', fg=c_red)
        self.txt.grid(column=4, row=2, sticky=tk.W)

    def has_select(self, _type=1):
        """勾选框是否选中"""
        foo = True if self.var_cb.get() else False
        return foo

    def shutdown(self):
        """关机
        """
        if not self.has_select():
            return

        self.time_count = 60
        self.need_shutdown = True
        self.shutdown_count()

    def shutdown_cancel(self):
        """取消关机
        """
        self.shutdown_select = True if self.var_cb.get() else False
        if self.after_id:
            utils.win.after_cancel(self.after_id)
        self.txt['text'] = "已取消关机" if self.need_shutdown else ""
        self.need_shutdown = False

    def shutdown_count(self):
        """关机倒计时
        """
        # update displayed time
        # self.now.set(current_iso8601())
        # schedule timer to call myself after 1 second
        self.time_count -= 1
        s = "{0}秒后关机 (点击勾选框可取消关机)"
        self.txt['text'] = s.format(self.time_count)
        self.after_id = utils.win.after(1000, self.shutdown_count)

        if self.time_count <= 0:
            utils.win.after_cancel(self.after_id)
            self.txt['text'] = ""
            if self.need_shutdown:
                self.need_shutdown = False
                utils.shutdown()


class TreeView(object):
    """TreeView
    """

    EVEN = 'even'
    ODD = 'odd'
    # EVEN_BG = "#EFEFEF"
    ODD_BG = '#f5f5f5'

    def __init__(self, parent, **kw):
        if utils.is_mac:
            w = [50, 100, 220, 420, 70]
        else:
            w = [30, 70, 192, 370, 70]

        status_anchor = kw['status_anchor'] if 'status_anchor' in kw else 'center'
        tree_num = kw['tree_num'] if 'tree_num' in kw else 10
        tree_widths = kw['tree_widths'] if 'tree_widths' in kw else w
        if len(tree_widths) < 4:
            tree_widths = w

        tree = ttk.Treeview(parent, columns=['1', '2', '3', '4', '5'], show='headings', selectmode=tk.EXTENDED)
        tree.config(height=tree_num)
        tree.column('1', width=tree_widths[0], anchor='center')
        tree.column('2', width=tree_widths[1], anchor=status_anchor)
        tree.column('3', width=tree_widths[2], anchor='nw')
        tree.column('4', width=tree_widths[3], anchor='nw')
        tree.column('5', width=tree_widths[4], anchor='nw')
        tree.heading('1', text='序号')
        tree.heading('2', text='状态')
        tree.heading('3', text='文件名')
        tree.heading('4', text='路径')
        tree.heading('5', text='完整路径')
        self.i_id = 0
        self.i_status = 1
        self.i_name = 2
        self.i_dir = 3
        self.i_full = 4
        self.tree_len = 5

        y_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        x_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
        y_scrollbar.grid(column=2, row=1, sticky=tk.N + tk.S)
        x_scrollbar.grid(column=1, row=2, sticky=tk.NW + tk.NE)

        tree.config(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        tree.grid(column=1, row=1, sticky=tk.NSEW)

        # tree.bind('<ButtonRelease-1>', treeviewClick)#绑定单击离开事件===========
        self.tree = tree

        # tree.tag_configure(self.EVEN, background=self.VEN_BG)
        tree.tag_configure(self.ODD, background=self.ODD_BG)
        # 双击左键复制内容
        tree.bind('<Double-1>', self.copy_to_clipboard)

    def copy_to_clipboard(self, event):
        tree = self.tree
        i_name = self.i_name
        i_dir = self.i_dir
        i_full = self.i_full
        i_status = self.i_status

        has_selection = True if len(tree.selection()) else False
        if has_selection:
            items = tree.selection()
        else:
            items = tree.get_children()

        if len(items) == 0:
            return

        # 点击是那一列
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        is_one_column = False if row else True
        copy_str = ''
        id_str = '#{}'
        if column == id_str.format(i_name + 1):
            index = i_name
            desc_str = '已拷贝 整列的 文件名' if is_one_column else '已拷贝 选中的 文件名'
        elif column == id_str.format(i_dir + 1):
            index = i_dir
            desc_str = '已拷贝 整列的 路径名' if is_one_column else '已拷贝 选中的 路径名'
        elif column == id_str.format(i_status + 1):
            index = i_status
            desc_str = '已拷贝 整列的 状态描述' if is_one_column else '已拷贝 选中的 状态描述'
        else:
            index = i_full
            desc_str = '已拷贝 整列的 完整路径名' if is_one_column else '已拷贝 选中的 完整路径名'

        if not is_one_column:
            tips = '(双击列头 可以复制整列内容)'
            desc_str += "\n" + tips
        else:
            items = tree.get_children()

        for item in items:
            text = tree.item(item, "values")
            if copy_str:
                copy_str += "\n" + text[index]
            else:
                copy_str = text[index]

        utils.clipboard_clear()
        utils.clipboard_append(copy_str)
        utils.showinfo(desc_str)

    def clear(self):
        """清空内容
        """
        tree = self.tree
        x = tree.get_children()
        for item in x:
            tree.delete(item)

    def update_status(self, index, status):
        tree = self.tree
        # i_name = self.i_name
        # i_dir = self.i_dir
        # i_full = self.i_full
        i_status = self.i_status

        items = tree.get_children()
        if index < 0 or index >= len(items):
            return

        item = items[index]
        text = list(tree.item(item, "values"))
        text[i_status] = status
        tree.item(item, values=text)
        tree.see(item)

    def set_list(self, arr):
        """设置文件列表
        """
        self.clear()
        tree = self.tree
        for i in range(len(arr)):
            item = arr[i]
            tag = self.EVEN if i % 2 == 0 else self.ODD

            p = Path(item)
            li = [""]*self.tree_len
            li[self.i_id] = str(i + 1)
            li[self.i_name] = str(p.name)
            li[self.i_dir] = str(p.parent)
            li[self.i_full] = str(p)
            tree.insert('', 'end', tags=tag, values=li)

    def get_lists(self):
        """获得文件列表
        """
        tree = self.tree
        # i_name = self.i_name
        # i_dir = self.i_dir
        i_full = self.i_full

        items = tree.get_children()
        arr = []
        for item in items:
            text = tree.item(item, "values")
            # f_name = text[i_name]
            # f_dir = text[i_dir]
            # arr.append(f_name + f_dir)
            arr.append(text[i_full])
        return arr

    def remove_selection(self):
        """删除选中
        """
        tree = self.tree
        for item in tree.selection():
            tree.delete(item)

    def adjust(self, is_up):
        """顺序调整
        """
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
            li[self.i_id] = str(i + 1)
            tree.item(item, tags=tag, values=li)

    def is_null(self):
        """是否为空
        """
        total = len(self.tree.get_children())
        if total:
            return False
        else:
            return True


class TreeViewNew:

    def __init__(self, parent, **kw):
        frame = parent
        color_black = util_theme.COLOR_BLACK

        # **kw
        key = 'file_types'
        self.file_types = kw[key] if key in kw else [("文件", "*.*"), ]

        key = 'tree_num'
        tree_num = kw[key] if key in kw else 20

        key = 'paste_notice'
        self.smart_notice = kw[key] if key in kw else ' ;-) 右键点我 粘贴文件'

        key = 'tree_widths'
        tree_widths = kw[key] if key in kw else []

        key = 'has_list_btn'
        has_list_btn = kw[key] if key in kw else False

        # 补齐格式
        arr = []
        for t in self.file_types:
            if len(t) >= 2:
                arr.append(t[1].replace("*", ""))
        self.file_types_tup = tuple(arr)

        # 补齐宽度
        if utils.is_mac:
            w_arr = [50, 100, 220, 420, 70]
        else:
            w_arr = [30, 70, 192, 370, 70]
        for i in range(len(w_arr)):
            if len(tree_widths) - 1 < i:
                tree_widths.append(w_arr[i])

        frame_top = tk.Frame(frame)
        frame_center = tk.Frame(frame)

        # 导入文件 / ↑ / ↓ / - /+
        import_btn = tk.Button(frame_top, text='导入文件', width=14)
        import_dir_btn = tk.Button(frame_top, text='导入目录', width=8)
        import_list_btn = tk.Button(frame_top, text='↺', width=2)

        import_btn.bind("<Button-1>", self.import_call)
        import_dir_btn.bind("<Button-1>", self.import_call)
        import_list_btn.bind("<Button-1>", self.import_call)

        w = 101 - 12 - 10 if utils.is_mac else 62
        tf = setting_fftool.font_default
        smart_paste = tk.Label(frame_top, padx=8, bd=0, height=1, width=w, fg=color_black, font=tf)
        smart_paste['text'] = self.smart_notice
        utils.bind(smart_paste, self.paste_right_click, True)
        tips = "右键单击此处可以粘贴哦！"
        utils.tooltip(smart_paste, tips, 100, 6000)

        up = tk.Button(frame_top, text='↑', width=2, command=self.up_call)
        down = tk.Button(frame_top, text='↓', width=2, command=self.down_call)
        remove_btn = tk.Button(frame_top, text='-', width=2, command=self.remove_call)
        add_btn = tk.Button(frame_top, text='+', width=2, command=self.add_call)

        import_btn.grid(column=1, row=0)
        import_dir_btn.grid(column=2, row=0)
        if has_list_btn:
            import_list_btn.grid(column=3, row=0)
        smart_paste.grid(column=4, row=0)
        up.grid(column=11, row=0)
        down.grid(column=12, row=0)
        remove_btn.grid(column=13, row=0)
        add_btn.grid(column=14, row=0)

        # 设置tooltip
        utils.tooltip(import_list_btn, "恢复上次的文件列表", 300, 3000)

        # treeview
        self.tree = TreeView(frame_center, tree_num=tree_num, tree_widths=tree_widths)

        w = (frame_top, frame_center,
             import_btn, import_list_btn, import_dir_btn,
             up, down, remove_btn, add_btn
             )
        utils.set_groove(w)

        frame_top.grid(column=1, row=1, sticky=tk.NW)
        frame_center.grid(column=1, row=2, sticky=tk.NW)

        self.paste = smart_paste
        self.import_btn = import_btn
        self.import_list_btn = import_list_btn
        self.import_dir_btn = import_dir_btn
        self.up = up
        self.down = down
        self.remove_btn = remove_btn
        self.add_btn = add_btn

    def import_call(self, e):
        if setting_fftool.has_query:
            utils.showinfo("有任务正在执行，请稍后")
            return

        tup = tuple([])
        ft = self.file_types
        ft_tup = self.file_types_tup
        if e.widget == self.import_btn:
            tup = filedialog.askopenfilenames(filetypes=ft,
                                              title='导入文件',
                                              initialdir=setting_fftool.last_folder
                                              )

        elif e.widget == self.import_list_btn:
            if os.path.exists(setting_fftool.list_file):
                arr = utils.read_txt(setting_fftool.list_file)
                new_arr = []
                for f in arr:
                    if os.path.exists(f):
                        new_arr.append(f)
                if not len(new_arr):
                    utils.showinfo('txt中的地址都不正确' + setting_fftool.list_file)
                    return
                tup = tuple(new_arr)

        elif e.widget == self.import_dir_btn:
            folder = filedialog.askdirectory(
                title='选择目录',
                initialdir=setting_fftool.last_folder)
            if folder:
                folder = utils.pathlib_path(folder)
                setting_fftool.last_folder = folder
                arr = []
                new_arr = []
                # 获得目录下所有文件
                utils.list_dir(folder, arr)
                # 过滤出指定格式的文件
                for f in arr:
                    suffix = str(Path(f).suffix)
                    for f_type in ft_tup:
                        if suffix == f_type:
                            new_arr.append(f)
                            break
                tup = tuple(new_arr)

        if len(tup):
            tup = utils.pathlib_path_tup(tup, True)
            self.tree.set_list(list(tup))
            # self.start.set_state(True)
            # self.clear_query()

            setting_fftool.last_folder = utils.pathlib_parent(tup[0])

    def add_call(self):
        if setting_fftool.has_query:
            utils.showinfo("有任务正在执行，请稍后")
            return

        tup = filedialog.askopenfilenames(
            title='添加文件',
            filetypes=self.file_types,
            initialdir=setting_fftool.last_folder)
        if not len(tup):
            return

        v = self.tree.get_lists()
        if len(v):
            new_tup = utils.append_tup(tuple(v), tup)
        else:
            new_tup = tup
        # 此处可以执行一次 去重操作
        new_arr = list(new_tup)
        final_arr = []
        for item in new_arr:
            if item:
                final_arr.append(item)
        tup = tuple(final_arr)
        tup = utils.pathlib_path_tup(tup, True)
        self.tree.set_list(list(tup))
        # self.start.set_state(bool(len(nnArr)))
        # self.clear_query()
        setting_fftool.last_folder = utils.pathlib_parent(tup[0])

    def remove_call(self):
        if setting_fftool.has_query:
            utils.showinfo("有任务正在执行，请稍后")
        else:
            self.tree.remove_selection()
            # if self.tree.is_null():
            #     self.start.set_state(False)

    def up_call(self):
        if setting_fftool.has_query:
            utils.showinfo("有任务正在执行，请稍后")
        else:
            self.tree.adjust(True)

    def down_call(self):
        if setting_fftool.has_query:
            utils.showinfo("有任务正在执行，请稍后")
        else:
            self.tree.adjust(False)

    def paste_right_click(self, _):
        ss = utils.clipboard_get()
        arr = utils.split_str(ss, True)
        if len(arr) and arr[0] == self.smart_notice:
            # print("默认")
            return

        # 检查文件是否存在 /指定格式
        new_arr = []
        t = self.file_types_tup
        for item in arr:
            s = utils.get_file_type(item).lower()
            if not t.count(s) or not os.path.isfile(item):
                continue
            new_arr.append(item)

        if len(new_arr):
            new_arr = utils.pathlib_paths(new_arr, True)
            self.tree.set_list(new_arr)
            # self.start.set_state(True)
            # self.clear_query()

        # self.paste.delete(1.0, tk.END)
        # self.paste.insert(tk.INSERT, self.smart_notice)

    def get_lists(self):
        """获得文件列表"""
        return self.tree.get_lists()

    def update_status(self, index, status):
        self.tree.update_status(index, status)


class FileChooser(IPanel):
    """文件选择器
    参数:
        cb_text {[string]} -- [勾选框上的文字]
        btn_text {[string]} -- [按钮上的文字]
        connect_call {[function]} -- [description]
        action_btn_text {[string]} -- [操作按钮上的文字（点击打开文件对话框）]
        filetypes {[list]} -- [文件类型，例如“[("图片文件", "*.png")]”]
        hasGROOVE {[Boolean]} -- [按钮是否有描边]
    """

    cb = None

    def __init__(self, _parent, **kw):
        IPanel.__init__(self, _parent)
        frame = self.frame

        label_text = kw['label_text'] if 'label_text' in kw else ''
        cb_text = kw['cb_text'] if 'cb_text' in kw else ''
        cb_call = kw['cb_call'] if 'cb_call' in kw else None
        btn_text = kw['btn_text'] if 'btn_text' in kw else ''
        btn_call = kw['connect_call'] if 'connect_call' in kw else None
        action_btn_text = kw['action_btn_text'] if 'action_btn_text' in kw else '...'
        action_btn_call = kw['action_btn_call'] if 'action_btn_call' in kw else None
        file_types = kw['filetypes'] if 'filetypes' in kw else []
        is_folder = kw['isFolder'] if 'isFolder' in kw else False
        text_width = kw['text_width'] if 'text_width' in kw else 80

        # 颜色
        color = util_theme.COLOR_BLACK
        wrap_length = 780

        font_name = '微软雅黑' if utils.is_windows else ''
        font_size = 7 if utils.is_windows else 12

        self.cb_call = cb_call
        has_check = False
        if label_text:
            self.label_txt = tk.Label(frame, text=label_text, fg=color)
            self.label_txt.grid(column=1, row=1, sticky=tk.W)

        # 勾选框 形式
        elif cb_text:
            self.var_cb = tk.IntVar()
            cb = tk.Checkbutton(
                frame,
                text=cb_text,
                variable=self.var_cb,
                fg=color,
                command=self.checkbox_call
            )
            cb.grid(column=1, row=1, sticky=tk.W)

            self.cb = cb
            has_check = True

        # 按钮 形式
        elif btn_text:
            btn = tk.Button(frame, text=btn_text, fg=color)
            if btn_call:
                btn.config(command=btn_call)
                utils.tooltip(btn, "点击打开目录", 100, 2000)
            btn.grid(column=1, row=1, sticky=tk.W)
            self.btn = btn
            utils.set_groove((btn,))

        # 文件路径
        txt = tk.Label(frame, text='')
        txt.config(
            width=text_width,
            height=1,
            bd=1,
            padx=3,
            fg=color,
            wraplength=wrap_length,
            justify='left',
            anchor='w'
        )
        txt.grid(column=2, row=1)

        # 选择文件按钮
        action_btn = tk.Button(
            frame,
            text=action_btn_text,
            fg=color,
            font=(font_name, font_size),
            state=tk.DISABLED
        )
        if len(file_types):
            action_btn.config(command=self.open_file_call)
            utils.bind(action_btn, self.right_click_call, True)
            self.filetypes = file_types
        self.action_btn_call = action_btn_call
        if is_folder:
            action_btn.config(command=self.open_folder_call, state=tk.NORMAL)
            utils.bind(action_btn, self.right_click_call, True)

        utils.tooltip(action_btn, "左键点击 选择文件/目录\n右键点击 前往对应文件/目录", 100, 2000)

        action_btn.grid(column=3, row=1)

        tup = (frame, action_btn)
        utils.set_groove(tup)

        self.txt = txt
        self.action_btn = action_btn
        self.hasCheck = has_check
        self.is_folder = is_folder

    def open_file_call(self):
        """打开文件对话框
        """
        f_type = self.filetypes
        init_dir = self.txt['text']
        init_dir = str(Path(init_dir).parent)
        if len(f_type):
            f = filedialog.askopenfilename(filetypes=f_type, title='选择文件', initialdir=init_dir)
            if f:
                self.txt['text'] = utils.pathlib_path(f)

        if self.action_btn_call is not None:
            self.action_btn_call()

    def open_folder_call(self):
        """打开文件夹对话框
        """
        init_dir = self.txt['text']
        folder = filedialog.askdirectory(title='选择目录', initialdir=init_dir)
        if folder:
            folder = utils.pathlib_path(folder)
            self.txt['text'] = folder
            setting_fftool.output_dir = folder

        if self.action_btn_call is not None:
            self.action_btn_call()

    def checkbox_call(self):
        """点击勾选框
        """
        state = tk.NORMAL if self.var_cb.get() else tk.DISABLED
        self.action_btn['state'] = self.txt['state'] = state
        if self.cb_call is not None:
            self.cb_call()

        # if self.var_cb.get() and self.open_file_call:
        #     self.open_file_call()

    def right_click_call(self, _):
        """
        右键点击 行动按钮
        """
        fp = self.txt['text']
        if not fp:
            utils.showinfo('你还没有选择文件/目录')
            return
        if not os.path.exists(fp):
            utils.showinfo('文件/目录 不存在 "{}"'.format(fp))
            return

        if self.is_folder:
            utils.open_dir(fp)
        else:
            utils.open_file(fp, True)

    def set_cb_tooltip(self, tips, delay=500, duration=3000):
        if self.cb is not None:
            utils.tooltip(self.cb, tips, delay, duration)

    def get_text(self):
        """获得文本框上的内容
        """
        return self.txt['text']

    def set_text(self, text):
        """设置文本框上的内容
        """
        self.txt['text'] = text
        tips = text if os.path.exists(text) else text + "\n*此文件不存在！"
        utils.tooltip(self.txt, tips)

    def set_select(self, value_str='0'):
        """设置是否选中,通过字符串的方式
        str='0' 不选中
        str='1' 选中
        """
        if not self.hasCheck:
            return
        enable = True if value_str == "1" else False
        self.cb.select() if enable else self.cb.deselect()
        self.checkbox_call()

    def set_select_and_text(self, value_str, text):
        """设置
            1.是否选中,通过字符串的方式
                str='0' 不选中
                str='1' 选中
            2.路径文本框文字
        """
        self.set_select(value_str)
        self.set_text(text)

    def has_select(self):
        """是否选中"""
        return utils.int_var_to_bool(self.var_cb)

    def get_select_str(self):
        """是否选中
        选中返回 字符串1，没选中返回 字符串0
        """
        value = '1' if self.var_cb.get() else '0'
        return value

    def is_ready(self, ng_show):
        """是否勾选，路径是否 ok
        """
        f = self.get_text()
        is_ng = False
        if self.hasCheck:
            if self.var_cb.get() and not os.path.exists(f):
                is_ng = True
        else:
            if not os.path.exists(f):
                is_ng = True
        if is_ng:
            utils.showinfo(ng_show)
        return not is_ng


class NumberGroup(IPanel):
    """
    备案号图片选择组
    """

    def __init__(self, _parent, **kw):
        IPanel.__init__(self, _parent)
        frame = self.frame

        text_width = kw['text_width'] if 'text_width' in kw else 80
        color = util_theme.COLOR_BLACK

        label_frame = tk.LabelFrame(frame, text=' 备案号 ', fg=color, borderwidth=2, padx=0, pady=0)

        types_png = [("图片文件", "*.png")]
        fca = FileChooser(label_frame,
                          cb_text="普通　　",
                          filetypes=types_png,
                          action_btn_text='浏览…',
                          cb_call=self.checkbox_call,
                          hasGROOVE=True,
                          text_width=text_width
                          )
        fcb = FileChooser(label_frame,
                          cb_text="爱奇艺　",
                          filetypes=types_png,
                          action_btn_text='浏览…',
                          cb_call=self.checkbox_call,
                          hasGROOVE=True,
                          text_width=text_width
                          )
        fcc = FileChooser(label_frame,
                          cb_text="腾讯　　",
                          filetypes=types_png,
                          action_btn_text='浏览…',
                          cb_call=self.checkbox_call,
                          hasGROOVE=True,
                          text_width=text_width
                          )

        # 15秒 勾选框
        frame_more = tk.Frame(label_frame)
        number_check_var = tk.IntVar()
        number_cb = tk.Checkbutton(frame_more, text="仅前15秒", fg=color, variable=number_check_var)

        tips_txt = tk.Label(frame_more,
                            width=80 + 7 - 2,
                            height=1,
                            bd=1,
                            padx=3,
                            fg=util_theme.COLOR_RED,
                            wraplength=780,
                            justify='left',
                            anchor='w'
                            )

        fca.grid(column=1, row=1, sticky=tk.W)
        fcb.grid(column=1, row=2, sticky=tk.W)
        fcc.grid(column=1, row=3, sticky=tk.W)

        frame_more.grid(column=1, row=4, sticky=tk.NW)

        number_cb.grid(column=1, row=1, sticky=tk.NW)
        tips_txt.grid(column=2, row=1, sticky=tk.NW)

        label_frame.grid(column=1, row=1, sticky=tk.NW)
        # number_notice_txt.grid(column=1, row=2, sticky=tk.NW)

        self.fca = fca
        self.fcb = fcb
        self.fcc = fcc
        self.number_cb = number_cb
        self.number_CheckVar = number_check_var
        # self.number_notice_txt = number_notice_txt
        self.tips_txt = tips_txt

    def __get_sc(self, _type=1):
        if _type == 2:
            return self.fcb
        elif _type == 3:
            return self.fcc
        else:
            return self.fca

    def is_ready(self, _type=1, ng_show=''):
        fc = self.__get_sc(_type)
        return fc.is_ready(ng_show)

    def get_select_str(self, _type=1):
        fc = self.__get_sc(_type)
        return fc.get_select_str()

    def get_text(self, _type=1):
        fc = self.__get_sc(_type)
        return fc.get_text()

    def has_select(self, _type=1):
        fc = self.__get_sc(_type)
        return fc.has_select()

    def set_select_and_text(self, _type=1, value_str='', text=''):
        fc = self.__get_sc(_type)
        fc.set_select_and_text(value_str, text)

    def set_select_15(self, value_str):
        enable = True if value_str == "1" else False
        self.number_cb.select() if enable else self.number_cb.deselect()

    def get_select_15(self):
        """15s勾选框是否选中
        选中返回 字符串1，没选中返回 字符串0
        """
        value = '1' if self.number_CheckVar.get() else '0'
        return value

    def checkbox_call(self):
        b1 = self.fca.has_select()
        b2 = self.fcb.has_select()
        b3 = self.fcc.has_select()
        if not b1 and \
                not b2 and \
                not b3:
            self.number_cb.deselect()

        if b1 or b2 or b3:
            self.number_cb.select()

        if b2 and b3:
            if b1:
                ss = '将额外生成两份视频，并对应保存到“爱奇艺备案号” 和 ”腾讯备案号“文件夹下'
            else:
                ss = '将生成两份视频，并对应保存到“爱奇艺备案号” 和 ”腾讯备案号“文件夹下'

        elif b2:
            if b1:
                ss = '爱奇艺 码率8m，将额外生成1份视频到“爱奇艺备案号”文件夹下'
            else:
                ss = '爱奇艺 码率8m，视频将保存到“爱奇艺备案号”文件夹下'
        elif b3:
            if b1:
                ss = '将额外生成1份视频到”腾讯备案号“文件夹下'
            else:
                ss = '视频将保存到”腾讯备案号“文件夹下'
        else:
            ss = ''

        self.tips_txt['text'] = ss


class RadiobuttonOption(IPanel):
    """单选按钮组
    """
    __rad = None

    def __init__(self, _parent, **kw):
        IPanel.__init__(self, _parent)
        frame = self.frame

        title = kw['title'] if 'title' in kw else ""
        options = kw['options'] if 'options' in kw else []
        rad_var_num = kw['set'] if 'set' in kw else 0
        style = kw['style'] if 'style' in kw else 1
        radio_call = kw['command'] if 'command' in kw else ""
        # w = kw['width'] if 'width' in kw else 200

        # 颜色
        color = util_theme.COLOR_BLACK

        # frame 容器
        if style == 2:
            label_frame = tk.Frame(frame, padx=2, pady=4)
        else:
            label_frame = tk.LabelFrame(frame, text=title, fg=color, padx=2, pady=4)

        rad_var = tk.IntVar()

        count = 0
        rad = None
        for item in options:
            text = item
            count += 1
            rad = tk.Radiobutton(label_frame,
                                 text=text,
                                 variable=rad_var,
                                 value=count,
                                 fg=color
                                 )
            if radio_call:
                rad.config(command=radio_call)
            rad.grid(column=count, row=0, sticky=tk.W)

        if rad_var_num > 0:
            rad_var.set(rad_var_num)
        label_frame.grid(column=1, row=1, sticky=tk.N + tk.W)
        self.rad_var = rad_var
        self.__rad = rad

    def get(self):
        return self.rad_var.get()

    def set(self, num):
        return self.rad_var.set(num)

    def config(self, **kw):
        radio_call = kw['command'] if 'command' in kw else ""
        self.__rad.config(command=radio_call)


if __name__ == "__main__":
    win = tk.Tk()
    font_default = tk_font.Font(family="微软雅黑", size=9)
    setting_fftool.font_default = font_default

    # file_chooser = MFileChooser(win,
    #                             tree_num=5,
    #                             file_types=[("视频文件", "*.mp4"),
    #                                         ("QuickTime", "*.mov"),
    #                                         ("avi", "*.avi"),
    #                                         ("mkv", "*.mkv"),
    #                                         ("mpg", "*.mpg")
    #                                         ],
    #                             paste_notice=';-) 点我 粘贴视频文件'
    #                             )
    file_chooser = TreeViewNew(
        win,
        tree_num=5,
        file_types=[
            ("音频文件", "*.mp3"),
            ("wav", "*.wav"),
            ("m4a", "*.m4a"),
            ("ogg", "*.ogg"),
            ("aac", "*.aac"),
            ("视频文件", "*.mp4"),
            ("QuickTime", "*.mov"),
            ("avi", "*.avi"),
            ("mpg", "*.mpg"),
            ("mkv", "*.mkv")
        ],
        paste_notice=';-) 点我 粘贴媒体文件'
    )
    win.mainloop()
