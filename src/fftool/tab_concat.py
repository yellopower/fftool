#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import os
import random
import tkinter as tk
from tkinter import filedialog

import utils
from fftool import util_ff as ff, setting_fftool
from fftool.m_widget import FileChooser
from fftool.m_widget import Start


class Main:
    is_manual_int = False

    def __init__(self, parent):
        self.concatList = []
        self.titlePrefix = ''
        self.dc = dict.fromkeys(self.seq, "")
        self.win = parent

    def manual_int(self):
        if self.is_manual_int:
            return
        self.is_manual_int = True
        win = self.win

        # 颜色
        GRAP = "#515556"
        LIST_BG = "#EFEFEF"
        LIST_WIDTH = 91 + 10

        frameImport = tk.Frame(win, padx=8, pady=8)
        frame_file = tk.Frame(win, padx=8)
        frameList = tk.Frame(win, padx=8)
        frameOutDir = tk.Frame(win, padx=8)
        frameStart = tk.Frame(win, padx=8)
        frameCB = tk.Frame(win, padx=8)

        frameImport.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W)
        frame_file.grid(column=1, row=2, sticky=tk.N + tk.S + tk.W)
        frameList.grid(column=1, row=3, sticky=tk.N + tk.S + tk.W)
        frameOutDir.grid(column=1, row=4, sticky=tk.N + tk.S + tk.W)
        frameCB.grid(column=1, row=5, sticky=tk.N + tk.S + tk.W)
        frameStart.grid(column=1, row=6, sticky=tk.N + tk.S + tk.W)

        self.importBtn = tk.Button(frameImport, text='导入文件', width=14)
        self.importBtn.bind("<Button-1>", self.importCall)
        self.importBtn.grid(column=1, row=0)

        self.smartNotice = " ;-) 点我 粘贴视频文件"
        self.smartPaste = tk.Text(frameImport, height=1, width=LIST_WIDTH - 22, fg=GRAP, wrap=tk.WORD,
                                  font=setting_fftool.font_default)
        self.smartPaste.grid(column=2, row=0)
        self.smartPaste.bind("<Leave>", self.smartPasteLeave)
        self.smartPaste.bind("<Button-1>", self.smartPasteClick)
        self.smartPaste.insert(tk.INSERT, self.smartNotice)

        # tk.Label(frameImport, height=1, width=LIST_WIDTH-22).grid(column=2, row=0)   # 右边距

        self.randomBtn = tk.Button(frameImport, text='⇌随机', width=9)
        self.randomBtn.bind("<Button-1>", self.randomCall)
        self.randomBtn.grid(column=6, row=0)

        self.varL = tk.StringVar()
        self.varC = tk.StringVar()
        self.varR = tk.StringVar()
        self.listL = tk.Listbox(
            frameList,
            selectmode=tk.EXTENDED,
            fg=GRAP,
            background=LIST_BG,
            height=20,
            setgrid=1,
            activestyle='none')
        self.listC = utils.clone(self.listL)
        self.listR = utils.clone(self.listL)
        self.listL.config(yscrollcommand=self.yscrollL, listvariable=self.varL, bd=1, justify=tk.LEFT, width=48 - 2)
        self.listC.config(yscrollcommand=self.yscrollC, listvariable=self.varC, bd=0, justify=tk.CENTER, width=7)
        self.listR.config(yscrollcommand=self.yscrollR, listvariable=self.varR, bd=1, justify=tk.LEFT, width=48 - 2)
        self.listL.grid(column=1, row=10, sticky=tk.E)
        self.listC.grid(column=2, row=10, sticky=tk.W)
        self.listR.grid(column=3, row=10, sticky=tk.W)

        self.scrollbar = tk.Scrollbar(frameList, orient='vertical', command=self.yview)
        self.scrollbar.grid(column=4, row=10, sticky=tk.N + tk.S + tk.W)

        self.fc_out = FileChooser(frameOutDir, btn_text="　输出目录 ", action_btn_text='选择目录', btn_call=self.gotoOutDir,
                                  isFolder=True, hasGROOVE=True, text_width=84)
        frame_out = self.fc_out.get_frame()
        frame_out.grid(column=1, row=21, sticky=tk.NW)

        self.CheckVar1 = tk.IntVar()
        self.cb1 = tk.Checkbutton(frameCB, text="极速模式", variable=self.CheckVar1)
        self.cb1.grid(column=1, row=1, sticky=tk.W)

        # 开始转码 按钮
        self.start_btn = Start(frameStart, text='开始\n合并', command=self.startCheck)
        self.start_btn.grid(column=1, row=1, sticky=tk.W)
        self.start_btn.set_state(False)
        tup = (self.importBtn, self.randomBtn, self.listL, self.listR)
        utils.set_groove(tup)

        self.autoSelect()

    def autoSelect(self):
        # 默认勾选 极速模式
        # self.cb1.select()
        self.fc_out.set_text(setting_fftool.output_dir)
        # self.outTxt['text'] = output_dir

    def sync_status(self):
        self.manual_int()
        self.fc_out.set_text(setting_fftool.output_dir)

    def yscrollL(self, *args):
        if self.listC.yview() != self.listL.yview():
            self.listC.yview_moveto(args[0])
        if self.listR.yview() != self.listL.yview():
            self.listR.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yscrollC(self, *args):
        if self.listL.yview() != self.listC.yview():
            self.listL.yview_moveto(args[0])
        if self.listR.yview() != self.listC.yview():
            self.listR.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yscrollR(self, *args):
        if self.listL.yview() != self.listR.yview():
            self.listL.yview_moveto(args[0])
        if self.listC.yview() != self.listR.yview():
            self.listC.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yview(self, *args):
        self.listL.yview(*args)
        self.listC.yview(*args)
        self.listR.yview(*args)

    def lockBtn(self, isLock):
        setting_fftool.has_query = isLock
        enable = False if isLock else True
        utils.set_states(self.importBtn, self.randomBtn, enable)

    def clearQuery(self):
        # 清空中间列表内容
        self.varC.set(tuple(['']))

    def gotoOutDir(self):
        # p5 = self.outTxt['text']
        p5 = self.fc_out.get_text()
        if not p5 or not os.path.exists(p5):
            utils.showinfo("输出路径设置不对")
        else:
            utils.open_dir(p5)

    def importCall(self, event):
        tup = tuple([])
        if event.widget == self.importBtn:
            ft = [
                ("视频文件", "*.mp4"),
                ("QuickTime", "*.mov"),
                ("avi", "*.avi"),
                ("mkv", "*.mkv")
            ]
            tup = filedialog.askopenfilenames(
                filetypes=ft,
                title='导入视频 (两个以上文件)',
                initialdir=setting_fftool.last_folder
            )

        if not len(tup):
            return
        tup = utils.pathlib_path_tup(tup)
        self.concatList = list(tup)
        self.updateList(self.concatList)
        enable = bool(len(tup) > 1)
        self.start_btn.set_state(enable)
        self.clearQuery()
        setting_fftool.last_folder = utils.pathlib_parent(tup[0])

    def updateList(self, arr):
        count = math.floor(len(arr) / 2)
        if not count:
            return

        arrL = arr[0:count]
        arrR = arr[count:]

        self.varL.set(tuple(arrL))
        self.varC.set(tuple([]))
        self.varR.set(tuple(arrR))

    def randomCall(self, event):
        self.randomTuple(self.concatList)

    def randomTuple(self, arr):
        arr = arr.copy()
        random.shuffle(arr)
        self.updateList(arr)

    def updateQuery(self, qStr, warning=False):
        # self.logTxt['fg'] = "#ff5643" if warning else "#0096FF"
        # self.logTxt['text'] = qStr
        tup = tuple([qStr])
        vStr = self.start_btn.get_string_var()
        if utils.var_is_empty(vStr):
            ntup = tup
        else:
            v = utils.var_to_list(vStr)
            if len(v):
                ntup = utils.append_tup(tuple(v), tup)
            else:
                ntup = tup
        nArr = list(ntup)
        nnArr = []
        for item in nArr:
            if item:
                nnArr.append(item)
        tup = tuple(nnArr)
        self.start_btn.set_string_var(tup)

    def updateQueryCenter(self, arr):
        tup = tuple(arr)
        self.varC.set(tup)
        num = len(tup)
        self.listL.see(num)
        self.listC.see(num)
        self.listR.see(num)

    def startCheck(self):
        dc = self.dc

        if setting_fftool.has_query:
            utils.showinfo("有任务正在执行，请稍后")
            return

        vlstr = self.varL.get()
        vrstr = self.varR.get()
        vlarr = utils.var_to_list_smb(vlstr)
        vrarr = utils.var_to_list_smb(vrstr)
        if utils.var_is_empty(vlstr):
            utils.showinfo("还没有导入文件")
            return

        # # 禁用开始按钮
        self.clearQuery()
        self.lockBtn(True)

        # p5 = self.outTxt['text']
        p5 = self.fc_out.get_text()
        fast_mode_select = True if self.CheckVar1.get() else False

        dc["output_dir"] = p5
        dc["list1"] = vlarr
        dc["list2"] = vrarr
        dc["fast_mode_select"] = fast_mode_select

        # 记忆操作
        setdc = setting_fftool.read_setting()
        setdc["output_dir"] = p5
        setting_fftool.save_setting(setdc)

        # 禁用开始按钮
        self.clearQuery()
        self.lockBtn(True)

        # 执行操作
        import threading
        self.t1 = threading.Thread(target=self.processConcat, args=(dc, ''))
        self.t1.setDaemon(True)
        self.t1.start()

    def smartPasteLeave(self, event):
        if setting_fftool.has_query:
            return

        ss = self.smartPaste.get(1.0, tk.END)
        arr = utils.split_str(ss, False)
        if len(arr) and arr[0] == self.smartNotice:
            # print("默认")
            return

        # 检查文件是否存在 /指定格式
        narr = []
        ft = (".mp4", ".mov", ".avi", ".mkv", ".mpg")
        for item in arr:
            typestr = utils.get_file_type(item).lower()
            if not ft.count(typestr) or not os.path.isfile(item):
                continue
            narr.append(item)

        if len(narr):
            narr = utils.pathlib_paths(narr)
            self.updateList(narr)
            self.start_btn.set_state(True)
            self.clearQuery()

        self.smartPaste.delete(1.0, tk.END)
        self.smartPaste.insert(tk.INSERT, self.smartNotice)

    def smartPasteClick(self, event):
        self.smartPaste.delete(1.0, tk.END)

    def setTitle2(self, title, warning=False):
        ntitle = utils.get_hms() + " " + title
        utils.set_title(self.titlePrefix + "-" + ntitle)
        self.updateQuery(ntitle, warning)
        print(ntitle)

    seq = ('list1', 'list2', 'output_dir', 'fast_mode_select')

    def processConcat(self, dc, astr=''):
        setTitle = self.setTitle2

        list1 = dc["list1"]
        list2 = dc["list2"]
        fast_mode_select = dc["fast_mode_select"]
        outputDir = dc["output_dir"] + os.sep

        tempDir = outputDir + 'tempDir' + os.sep

        # 保持长度一致
        minLen = min(len(list1), len(list2))
        list1 = list1[0:minLen]
        list2 = list2[0:minLen]

        finalMP4 = ""
        pStr = ""

        # set param=-c:v libx264 -s 1920x1080 -r 24 -b:v 6144k -b:a 128k -ar 44100 -ac 2 -preset slower -threads 8
        FFStr = '''ffmpeg -y -i "{input}" -c:v libx264 -s {v_size} -crf 18 -r {fps} -b:a 128k -ar 44100 -ac 2 -threads 8 "{output}"'''
        FFConcat = '''ffmpeg -y -f concat -safe 0 -i "{0}" -c copy "{1}"'''
        seq = ('input', 'output', 'v_size', 'fps')

        utils.make_dir(tempDir)
        utils.hide_file(tempDir)
        total = len(list1)
        count = 0
        msgStr = " ({0}/{1}) {2}"
        print(list1)
        status = []
        for i in range(len(list1)):
            count = count + 1
            status.append('')

            fileA = list1[i]
            fileB = list2[i]

            arr = utils.get_file_names(fileA)
            fnameA = arr[1]
            # ftypeA = arr[2]
            ftempA = tempDir + "-" + fnameA + ".mp4"

            arr = utils.get_file_names(fileB)
            fnameB = arr[1]
            # ftypeB = arr[2]
            ftempB = tempDir + "-" + fnameB + ".mp4"

            fullName = fnameA + '__' + fnameB
            finalMP4 = outputDir + fullName + ".mp4"
            subTxt = tempDir + "concat_" + fullName + ".txt"

            # 任务信息
            mstr = msgStr.format(count, total, fullName)
            setTitle(mstr)

            # 读取第一个视频的 尺寸和帧频作为基准
            # ！！！所有的视频都会进行一次转码
            dc = dict.fromkeys(seq, "")
            dcinfo = ff.get_video_info(fileA, False)
            dc['fps'] = dcinfo['fps'] if dcinfo['fps'] else '24'
            dc['v_size'] = dcinfo['v_size'] if dcinfo['v_size'] else '1920x1080'

            # 检查视频参数是否相同
            isSame = False
            if fast_mode_select:
                isSame = ff.compare_video(fileA, fileB)
            # 生成concat.txt, 并转换片头/片尾
            subs = []
            sub = "file '{0}'\n"
            if not isSame:
                # 转第一个视频
                mstr = msgStr.format(count, total, "转换 第一个视频……")
                setTitle(mstr)
                status[i] = '10%'
                self.updateCenter(status)

                dc['input'] = fileA
                dc['output'] = ftempA
                pStr = FFStr.format(**dc)
                ff.execute(pStr)

                # 转第二个视频
                mstr = msgStr.format(count, total, "转换 第二个视频……")
                setTitle(mstr)
                status[i] = '50%'
                self.updateCenter(status)

                dc['input'] = fileB
                dc['output'] = ftempB
                pStr = FFStr.format(**dc)
                ff.execute(pStr)

                subs.append(sub.format(ftempA))
                subs.append(sub.format(ftempB))
            else:
                mstr = msgStr.format(count, total, "参数相同，跳过转换，直接拼接！")
                setTitle(mstr)

                subs.append(sub.format(fileA))
                subs.append(sub.format(fileB))

            # 写入concat文件
            utils.write_txt(subTxt, subs)

            # 拼接视频
            mstr = msgStr.format(count, total, "拼接中……")
            setTitle(mstr)
            status[i] = '90%'
            self.updateCenter(status)

            pStr = FFConcat.format(subTxt, finalMP4)
            ff.execute(pStr)
            # print(pStr)

            sstr = '成功' if os.path.exists(finalMP4) else '失败'
            status[i] = sstr
            self.updateCenter(status)

            # 移除 concat.txt 和 mp4
            utils.remove_file(subTxt)
            utils.remove_file(ftempA)
            utils.remove_file(ftempB)

        setTitle("操作结束！")
        setTitle("")

        # 自动打开目录
        if finalMP4:
            utils.open_dir(outputDir)

        self.t1 = ""
        self.lockBtn(False)

    def updateCenter(self, arr):
        self.updateQueryCenter(arr.copy())


if __name__ == "__main__":
    pass
