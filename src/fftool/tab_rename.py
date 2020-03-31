#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量命名
功能：
  支持批量重命名 文件或文件夹

基本用法：
  界面有两个粘贴框，左边粘贴文件路径，右边粘贴文件名
  工具可以将左侧文件的文件名命名为右侧的文件名。

  也可以在右边输入文件名，输入完一个后按下 enter 键，完成输入后，移动鼠标到粘贴框之外。

  对照式快速命名：
    如果一个文件夹下的文件，要命名成另一个文件夹的样子，只需在左右两边 ctrl+c和 ctrl+v对应文件即可

粘贴框用法：
  选中文件或文件夹，并按下ctrl+c，此时单击粘贴框，执行 ctrl+v，可获得文件路径
"""

import os
import tkinter as tk
from pathlib import Path

from tttk import StringVar
import utils
from fftool import setting_fftool


class Main:
    """批量重命名
    """
    is_manual_int = False

    def __init__(self, _parent):
        self.win = _parent

    def manual_int(self):
        if self.is_manual_int:
            return
        self.is_manual_int = True
        win = self.win
        self.hasQuery = False
        self.LeftIsReverse = False
        self.RightIsReverse = False
        self.sortDesc = ('排序↕', "升序a-z", '降序z-a')

        """组装 ui
        """
        # 颜色
        GRAP = "#515556"
        # GRAP2 = "#B9BFC1"
        # TXT_BG = "#ECECEC"
        LIST_BG = "#EFEFEF"
        LIST_WIDTH = 91 + 10
        # TXT_WIDTH = 80+7
        # FILE_GAP = 65+10
        # WRAP_LENGTH = 780

        frame = tk.Frame(win, padx=8, pady=2)
        frame.grid(column=1, row=0, sticky=tk.N + tk.S + tk.W)

        self.svL = StringVar()
        self.svC = StringVar()
        self.svR = StringVar()
        varL = self.svL.get_object()
        varC = self.svC.get_object()
        varR = self.svR.get_object()
        self.list_l = tk.Listbox(
            frame,
            selectmode=tk.EXTENDED,
            fg=GRAP,
            background=LIST_BG,
            height=20,
            setgrid=1,
            activestyle='none'
        )
        self.list_c = utils.clone(self.list_l)
        self.list_r = utils.clone(self.list_l)
        self.list_l.config(yscrollcommand=self.yscroll1, listvariable=varL)
        self.list_c.config(yscrollcommand=self.yscroll2, listvariable=varC)
        self.list_r.config(yscrollcommand=self.yscroll3, listvariable=varR)
        self.list_l.config(bd=1, justify=tk.RIGHT, width=LIST_WIDTH - 35)
        self.list_c.config(bd=0, justify=tk.CENTER, width=7)
        self.list_r.config(bd=1, justify=tk.LEFT, width=25)
        self.list_l.grid(column=1, row=10, sticky=tk.E)
        self.list_c.grid(column=2, row=10, sticky=tk.W)
        self.list_r.grid(column=3, row=10, sticky=tk.W)

        self.scrollbar = tk.Scrollbar(frame, orient='vertical', command=self.yview)
        self.scrollbar.grid(column=4, row=10, sticky=tk.N + tk.S + tk.W)

        # test
        # for x in range(30):
        #     self.list_l.insert('end', x)
        #     self.list_r.insert('end', x)

        self.msgLeft = " ;-) 点我 粘贴 需命名的文件"
        self.paste_l = tk.Text(
            frame,
            height=1,
            width=LIST_WIDTH - 30,
            fg=GRAP,
            wrap=tk.WORD,
            font=setting_fftool.font_default
        )
        self.paste_l.bind("<Leave>", self.paste_leave_left)
        self.paste_l.bind("<Button-1>", self.pasteClick)
        self.paste_l.tag_config("right", justify=tk.RIGHT)
        self.paste_l.insert(tk.INSERT, self.msgLeft, "right")

        self.msg_right = " ;-) 粘贴 文件名 或 文件"
        self.paste_r = tk.Text(
            frame,
            height=1,
            width=25,
            fg=GRAP,
            wrap=tk.WORD,
            font=setting_fftool.font_default
        )
        self.paste_r.bind("<Leave>", self.leave_right)
        self.paste_r.bind("<Button-1>", self.pasteClick)
        self.paste_r.insert(tk.INSERT, self.msg_right)

        self.paste_l.grid(column=1, row=0, sticky=tk.NE)
        self.paste_r.grid(column=3, row=0, sticky=tk.NW)

        # 左右排序按钮
        fleft = tk.Frame(frame, padx=8, pady=2)
        fRight = tk.Frame(frame, padx=8, pady=2)

        desc = self.sortDesc
        self.sortLS = tk.Button(fleft, text=desc[0], width=7)
        self.sortLU = tk.Button(fleft, text='↑', width=2)
        self.sortLD = tk.Button(fleft, text='↓', width=2)

        self.sortRS = tk.Button(fRight, text=desc[0], width=7)
        self.sortRU = tk.Button(fRight, text='↑', width=2)
        self.sortRD = tk.Button(fRight, text='↓', width=2)

        widgets = (self.sortLS, self.sortLU, self.sortLD,
                   self.sortRS, self.sortRU, self.sortRD)
        for w in widgets:
            utils.bind(w, self.sortCall)

        fleft.grid(column=1, row=5, sticky=tk.NE)
        self.sortLS.grid(column=4, row=1)
        self.sortLU.grid(column=2, row=1)
        self.sortLD.grid(column=3, row=1)

        fRight.grid(column=3, row=5, sticky=tk.NE)
        self.sortRS.grid(column=1, row=1)
        self.sortRU.grid(column=2, row=1)
        self.sortRD.grid(column=3, row=1)
        start_btn = tk.Button(
            frame,
            text='开始\n命名',
            width=6,
            height=3,
            command=self.start_check,
            relief=tk.GROOVE
        )
        undo_btn = tk.Button(
            frame,
            text='↺撤销',
            width=6,
            height=1,
            command=self.start_check,
            relief=tk.GROOVE
        )
        start_btn.grid(column=2, row=20)
        undo_btn.grid(column=2, row=21)
        utils.set_state(start_btn, False)
        utils.set_state(undo_btn, False)

        # 统一设置样式
        tub1 = (self.list_l, self.list_r, start_btn, undo_btn)
        tub = widgets + tub1
        utils.set_groove(tub)

        self.undo_btn = undo_btn
        self.start_btn = start_btn

        # 测试用
        # if utils.is_mac:
        # self.test_func()

    def sync_status(self):
        self.manual_int()

    def test_func(self):
        """
        临时用的测试方法
        :return:
        """
        left_arr = [
            "/Users/qinbaomac-mini/Desktop/output/test-rename/1111/1234234321423/1.mov",
            "/Users/qinbaomac-mini/Desktop/output/test-rename/1111/1234234321423/2.mov",
            "/Users/qinbaomac-mini/Desktop/output/test-rename/1111/1234234321423/3.mov",
            "/Users/qinbaomac-mini/Desktop/output/test-rename/1111/1234234321423/4.mov",
            "/Users/qinbaomac-mini/Desktop/output/test-rename/1111/1234234321423/5.mov",
            "/Users/qinbaomac-mini/Desktop/output/test-rename/1111/1234234321423/6.mov"
        ]
        # left_arr = ["/Users/qinbaomac-mini/Desktop/output/111/1111/1234234321423/yw_d21_d6.mp3",
        #             "/Users/qinbaomac-mini/Desktop/output/111/1111/1234234321423/yw_d21_d4.mp3",
        #             "/Users/qinbaomac-mini/Desktop/output/111/1111/1234234321423/yw_d21_d5.mp3",
        #             "/Users/qinbaomac-mini/Desktop/output/111/1111/1234234321423/yw_d21_d1.mp3",
        #             "/Users/qinbaomac-mini/Desktop/output/111/1111/1234234321423/yw_d21_d2.mp3",
        #             "/Users/qinbaomac-mini/Desktop/output/111/1111/1234234321423/yw_d21_d3.mp3"
        #             ]
        right_arr = [
            "d21_d1",
            "d21_d2.mp3",
            "d21_d3.mp3",
            "d21_d4.mp3",
            "d21_d5.mp3",
            "d21_d6.mp3"
        ]
        self.svL.set(left_arr)
        self.svR.set(right_arr)
        utils.set_state(self.start_btn, True)

    def yscroll1(self, *args):
        if self.list_c.yview() != self.list_l.yview():
            self.list_c.yview_moveto(args[0])
        if self.list_r.yview() != self.list_l.yview():
            self.list_r.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yscroll2(self, *args):
        if self.list_l.yview() != self.list_c.yview():
            self.list_l.yview_moveto(args[0])
        if self.list_r.yview() != self.list_c.yview():
            self.list_r.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yscroll3(self, *args):
        if self.list_l.yview() != self.list_r.yview():
            self.list_l.yview_moveto(args[0])
        if self.list_c.yview() != self.list_r.yview():
            self.list_c.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yview(self, *args):
        self.list_l.yview(*args)
        self.list_c.yview(*args)
        self.list_r.yview(*args)

    def sortCall(self, event):
        """点击排序按钮
        """
        w = event.widget
        if w == self.sortLS or w == self.sortLU or w == self.sortLD:
            listbox = self.list_l
            rawVar = self.svL
        elif w == self.sortRS or w == self.sortRU or w == self.sortRD:
            listbox = self.list_r
            rawVar = self.svR
        else:
            return

        # vstr = rawVar.get()
        # varr = util.stringVartoList(vstr)
        varr = rawVar.get()
        # 单列排序
        if not len(varr):
            return
        isReverse = False
        if w == self.sortLS:
            self.LeftIsReverse = False if self.LeftIsReverse else True
            isReverse = self.LeftIsReverse
        elif w == self.sortRS:
            self.RightIsReverse = False if self.RightIsReverse else True
            isReverse = self.RightIsReverse
        if w == self.sortLS or w == self.sortRS:
            desc = self.sortDesc
            w['text'] = desc[2] if isReverse else desc[1]
            varr.sort(reverse=isReverse)
            rawVar.set(varr)

        # 清空中间列表内容
        # self.varC.set(tuple([]))
        self.svC.set([])

        # 单个排序
        indexs = listbox.curselection()
        snum = len(indexs)
        if snum == 0:
            return
        if snum > 1:
            utils.showinfo("只支持单个的顺序调整")
            return

        i = indexs[0]
        # 向上调整
        if w == self.sortLU or w == self.sortRU:
            if i > 0 and i < len(varr) and len(varr) > 0:
                obj = varr[i]
                del varr[i]
                varr.insert(i - 1, obj)
                rawVar.set(varr)
                listbox.selection_clear(i)
                listbox.select_set(i - 1)
        # 向下调整
        elif w == self.sortLD or w == self.sortRD:
            if i < len(varr) - 1 and len(varr) > 0:
                obj = varr[i]
                del varr[i]
                varr.insert(i + 1, obj)
                rawVar.set(varr)
                listbox.selection_clear(i)
                listbox.select_set(i + 1)

    def pasteClick(self, event):
        """点击粘贴框
        """
        event.widget.delete(1.0, tk.END)

    def paste_leave_left(self, event):
        """移出左侧粘贴框
        """
        if self.hasQuery:
            return
        ss = self.paste_l.get(1.0, tk.END)
        arr = utils.split_str(ss, False)
        if len(arr) and arr[0] == self.msgLeft:
            # print("默认")
            return

        # 检查文件/文件夹是否存在
        narr = []
        no_exists_arr = []
        for i in range(len(arr)):
            arr[i] = utils.pathlib_path(arr[i])
            item = arr[i]
            if len(item) < 3:
                continue
            if os.path.exists(item):
                narr.append(item)
            else:
                no_exists_arr.append(item)

        if not len(narr):
            self.paste_l.delete(1.0, tk.END)
            self.paste_l.insert(tk.INSERT, self.msgLeft, "right")
            return

        # 去重
        tarr = []
        for item in narr:
            if not tarr.count(item):
                tarr.append(item)
        narr = tarr

        # self.varL.set(tuple(narr))
        # self.varC.set(tuple([]))
        self.svL.set(narr)
        self.svC.set([])
        self.sortLS['text'] = self.sortDesc[0]
        self.LeftIsReverse = False
        self.list_l.xview_moveto(1.0)

        # vlstr = self.varL.get()
        # vrstr = self.varR.get()
        # validL = False if util.stringVarisN(vlstr) else True
        # validR = False if util.stringVarisN(vrstr) else True
        validL = False if self.svL.is_null() else True
        validR = False if self.svR.is_null() else True
        if validL and validR:
            utils.set_state(self.start_btn, True)

        self.paste_l.delete(1.0, tk.END)
        self.paste_l.insert(tk.INSERT, self.msgLeft, "right")

        num1 = len(no_exists_arr)
        if num1:
            file_name_str = "\n".join(str(item) for item in no_exists_arr)
            utils.showinfo('{0}个文件不存在，将不参与重命名：{1}\n'.format(num1, file_name_str))

    def leave_right(self, event):
        """移出右侧粘贴框
        """
        if self.hasQuery:
            return
        ss = self.paste_r.get(1.0, tk.END)
        arr = utils.split_str(ss, False)
        if len(arr) and arr[0] == self.msg_right:
            # print("默认")
            return

        # 如果是文件路径，则取出文件名和扩展名 / 文件夹名
        narr = []
        for i in range(len(arr)):
            arr[i] = utils.pathlib_path(arr[i])
            item = arr[i]
            item = item.strip("\t").strip(" ")
            item = item.strip("\t").strip(" ")
            item = item.strip('"').strip("'")
            p = Path(item)
            if p.name:
                narr.append(p.name)

        if not len(narr):
            self.paste_r.delete(1.0, tk.END)
            self.paste_r.insert(tk.INSERT, self.msg_right)
            return

        # self.varR.set(tuple(narr))
        # self.varC.set(tuple([]))
        self.svR.set(narr)
        self.svC.set([])
        self.sortRS['text'] = self.sortDesc[0]
        self.RightIsReverse = False

        # vlstr = self.varL.get()
        # vrstr = self.varR.get()
        # varIsN = util.stringVarisN
        # if varIsN(vlstr) or varIsN(vrstr):
        validL = self.svL.is_null()
        validR = self.svR.is_null()
        if not validL or not validR:
            utils.set_state(self.start_btn, True)

        self.paste_r.delete(1.0, tk.END)
        self.paste_r.insert(tk.INSERT, self.msg_right)

    def lock_btn(self, is_lock):
        """锁定按钮
        有任务正在执行时
        """
        self.hasQuery = is_lock
        enable = False if is_lock else True
        utils.set_states(self.sortLS, self.sortRS, enable)
        utils.set_states(self.sortLU, self.sortRU, enable)
        utils.set_states(self.sortLD, self.sortRD, enable)
        utils.set_states(self.paste_l, self.paste_r, enable)

    def clear_query(self):
        """清空中间列表内容
        """
        # self.varC.set(tuple(['']))
        self.svC.set([])

    def update_query(self, arr):
        """显示任务进度
        """
        # tup = tuple(arr)
        # self.varC.set(tup)
        self.svC.set(arr)
        # self.list_c.see(len(tup))
        l = len(arr)
        self.list_l.see(l)
        self.list_c.see(l)
        self.list_r.see(l)

    def start_check(self):
        """点击开始按钮
        """
        if self.hasQuery:
            utils.showinfo("有任务正在执行，请稍后")
            return

        # vlstr = self.varL.get()
        # vrstr = self.varR.get()
        # vlarr = util.stringVartoList_smb_url(vlstr)
        # vrarr = util.stringVartoList_smb_url(vrstr)
        vlarr = self.svL.get()
        vrarr = self.svR.get()

        # # 禁用开始按钮
        self.clear_query()
        self.lock_btn(True)

        # 保持长度一致
        # vrarr = vrarr[0:len(vlstr)]
        vrarr = vrarr[0:len(vlarr)]

        # # 执行操作
        import threading
        self.t1 = threading.Thread(target=self.process, args=(vlarr, vrarr))
        self.t1.setDaemon(True)
        self.t1.start()

    def process(self, list1, list2):
        """执行重命名操作

        Arguments:
            list1 {[type]} -- [description]
            list2 {[type]} -- [description]
        """
        status = []
        failure_count = 0
        for i in range(len(list1)):
            if i >= len(list2):
                continue
            raw_name = list1[i]
            new_name = list2[i]
            if not os.path.exists(raw_name):
                status.append("文件不存在!")
                failure_count += 1
                self.update_query(status.copy())
                continue

            if os.path.isdir(raw_name):
                status.append("暂不支持文件夹重命名!")
                failure_count += 1
                self.update_query(status.copy())
                continue

            raw_path = Path(raw_name)
            temp_path = Path(new_name)
            new_path = Path(raw_path.with_name(temp_path.name))
            new_path_str = str(new_path)

            print(raw_name, "  ===> ", new_path_str)
            if not os.path.exists(new_path_str):
                try:
                    print("正尝试重命名")
                    os.rename(raw_name, new_path_str)
                except FileExistsError:
                    status.append("文件已存在!")
                    failure_count += 1
                except IOError:
                    status.append("权限不足!")
                    failure_count += 1
                else:
                    status.append("成功")
            else:
                status.append("文件已存在!")
                failure_count += 1
            self.update_query(status.copy())

        self.t1 = ""
        self.lock_btn(False)

        # 提示失败结果
        show_str = '命名完成！'
        if failure_count > 0:
            arr = []
            nums = []
            failure_str = ''
            for s in status:
                if c == '成功':
                    continue
                c = arr.count(s)
                if c == 0:
                    arr.push(s)
                    nums.push(1)
                else:
                    index = arr.count(s)
                    nums[index] += 1

            for i in range(len(arr)):
                s = arr[i]
                failure_str += "\n{0} {1} 个".format(s, nums[i])
            show_str += failure_str
        else:
            show_str += "\n成功命名 {0} 个".format(len(status))
        utils.showinfo(show_str)


if __name__ == "__main__":
    g = Main()
