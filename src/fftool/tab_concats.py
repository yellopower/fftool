#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import filedialog

import utils
from fftool import util_ff as ff, setting_fftool
from fftool.m_widget import Start
from fftool.m_widget import FileChooser


class VideoConcats():

    def __init__(self):
        self.dc = dict.fromkeys(self.seqConcats, "")
        self.titlePrefix = ''
        self.isMG = False
        self.hasClick = False
        self.groupInfos = ()

    def setup(self, tkwin):
        """组装 ui
        """
        win = tkwin

        # 颜色
        GRAP = "#515556"
        LIST_BG = "#EFEFEF"
        LIST_WIDTH = 91 + 10

        # 列布局
        # 0, 1,5,10, 11
        # 左边距，左，中，右，右边距

        # 导入文件 / ↑ / ↓ / - /+
        frame_top = tk.Frame(win, padx=8, pady=8)
        frame_top.grid(column=5, row=0, sticky=tk.NW)

        self.importBtn = tk.Button(frame_top, text='导入文件', width=14)
        self.importBtn.bind("<Button-1>", self.importCall)
        self.importBtn.grid(column=1, row=0)

        self.importListBtn = tk.Button(frame_top, text='↺', width=2)
        # self.import_list_btn.bind("<Button-1>", self.import_call)
        # self.import_list_btn.grid(column=2, row=0)

        self.smartNotice = " ;-) 点我 粘贴视频文件 或 多组合并配置信息"
        self.smartPaste = tk.Text(frame_top, height=1, width=LIST_WIDTH - 33, fg=GRAP, wrap=tk.WORD,
                                  font=setting_fftool.font_default)
        self.smartPaste.grid(column=5, row=0)
        self.smartPaste.bind("<Leave>", self.smartPasteLeave)
        self.smartPaste.bind("<Button-1>", self.smartPasteClick)
        self.smartPaste.insert(tk.INSERT, self.smartNotice)

        self.upBtn = tk.Button(frame_top, text='↑', width=2)
        self.downBtn = tk.Button(frame_top, text='↓', width=2)
        self.removeBtn = tk.Button(frame_top, text='-', width=2, command=self.removeCall)
        self.addBtn = tk.Button(frame_top, text='+', width=2, command=self.addCall)
        self.upBtn.bind("<Button-1>", self.adjustCall)
        self.downBtn.bind("<Button-1>", self.adjustCall)

        self.upBtn.grid(column=10, row=0, sticky=tk.NE)
        self.downBtn.grid(column=11, row=0, sticky=tk.NE)
        self.removeBtn.grid(column=12, row=0, sticky=tk.NE)
        self.addBtn.grid(column=13, row=0, sticky=tk.NE)

        # listbox 和 scrollBar
        frameLB = tk.Frame(win, padx=8)
        frameLB.grid(column=5, row=11, sticky=tk.NW)

        self.varL = tk.StringVar()
        self.varC = tk.StringVar()
        self.varR = tk.StringVar()
        self.listL = tk.Listbox(frameLB, selectmode=tk.EXTENDED, fg=GRAP, background=LIST_BG, height=20, setgrid=1,
                                activestyle='none')
        self.listC = utils.clone(self.listL)
        self.listR = utils.clone(self.listL)
        self.listL.config(yscrollcommand=self.yscroll1, listvariable=self.varL)
        self.listC.config(yscrollcommand=self.yscroll2, listvariable=self.varC)
        self.listR.config(yscrollcommand=self.yscroll3, listvariable=self.varR)
        self.listL.config(bd=1, justify=tk.RIGHT, width=LIST_WIDTH - 30)
        self.listC.config(bd=0, justify=tk.CENTER, width=7)
        self.listR.config(bd=1, justify=tk.LEFT, width=20)
        self.listL.grid(column=1, row=11, sticky=tk.E)
        self.listC.grid(column=2, row=11, sticky=tk.W)
        self.listR.grid(column=3, row=11, sticky=tk.W)

        self.scrollbar = tk.Scrollbar(frameLB, orient=tk.VERTICAL, command=self.yview)
        self.scrollbar.grid(column=10, row=11, sticky=tk.N + tk.S)

        frame_out = tk.Frame(win, padx=8)
        frame_out.grid(column=5, row=71, sticky=tk.NW)
        self.fc_out = FileChooser(frame_out, btn_text="　输出目录 ", action_btn_text='选择目录', btn_call=self.gotoOutDir,
                                     isFolder=True, hasGROOVE=True, text_width=80)
        frame_out = self.fc_out.get_frame()
        frame_out.grid(column=5, row=71, sticky=tk.NW)

        frameCB = tk.Frame(win, bd=0, padx=8)
        frameCB.grid(column=5, row=81, sticky=tk.NW)

        self.CheckVar1 = tk.IntVar()
        self.cb1 = tk.Checkbutton(frameCB, text="极速模式", variable=self.CheckVar1)
        self.cb1.grid(column=1, row=86, sticky=tk.W)

        # self.msgTxt = tk.Label(frameCB, text='', )
        # self.msgTxt.config(fg=GRAP2, wraplength=WRAP_LENGTH, justify='left',
        #                    anchor='w', width=TXT_WIDTH, height=1, padx=3)
        # self.msgTxt.grid(column=5, row=86)
        # self.msgTxt['text'] = ""

        frameS = tk.Frame(win, bd=1, padx=8)
        frameS.grid(column=5, row=87, sticky=tk.N + tk.S + tk.W)

        # 开始转码 按钮
        self.start_btn = Start(frameS, text='开始\n合并', command=self.startCheck)
        self.start_btn.grid(column=1, row=1, sticky=tk.W)
        self.start_btn.set_state(False)

        tup = (self.importBtn, self.importListBtn,
               self.upBtn, self.downBtn, self.removeBtn, self.addBtn,
               self.listL, self.listR
               )
        utils.set_groove(tup)
        self.autoSelect()

    def autoSelect(self):
        """读取配置
        """
        # 默认勾选 极速模式
        # self.cb1.select()
        self.fc_out.set_text(setting_fftool.output_dir)

    def sync_status(self):
        self.fc_out.set_text(setting_fftool.output_dir)

    def yscroll1(self, *args):
        """列表滚动1
        """
        if self.listC.yview() != self.listL.yview():
            self.listC.yview_moveto(args[0])
        if self.listR.yview() != self.listL.yview():
            self.listR.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yscroll2(self, *args):
        """列表滚动2
        """
        if self.listL.yview() != self.listC.yview():
            self.listL.yview_moveto(args[0])
        if self.listR.yview() != self.listC.yview():
            self.listR.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yscroll3(self, *args):
        """列表滚动3
        """
        if self.listL.yview() != self.listR.yview():
            self.listL.yview_moveto(args[0])
        if self.listC.yview() != self.listR.yview():
            self.listC.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yview(self, *args):
        """列表滚动
        """
        self.listL.yview(*args)
        self.listC.yview(*args)
        self.listR.yview(*args)

    def lockBtn(self, isLock):
        """锁定按钮
        """
        setting_fftool.has_query = isLock
        enable = False if isLock else True
        utils.set_state(self.importBtn, enable)
        utils.set_states(self.upBtn, self.downBtn, enable)
        utils.set_states(self.removeBtn, self.addBtn, enable)

    def gotoOutDir(self):
        """打开输出目录
        """
        # p5 = self.outTxt['text']
        p5 = self.fc_out.get_text()
        if not p5 or not os.path.exists(p5):
            utils.showinfo("输出路径设置不对")
        else:
            utils.open_dir(p5)

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

    def importCall(self, event):
        """点击导入按钮
        """
        tup = tuple([])
        if event.widget == self.importBtn:
            ft = [("视频文件", "*.mp4"), ("QuickTime", "*.mov"),
                  ("avi", "*.avi"), ("mkv", "*.mkv"), ("mpg", "*.mpg")]
            tup = filedialog.askopenfilenames(filetypes=ft,
                                              title='导入视频 (两个以上文件)',
                                              initialdir=setting_fftool.last_folder)
        # elif event.widget == self.import_list_btn:
        #     if os.path.exists(setting.list_file):
        #         arr = util.read_txt(setting.list_file)
        #         if not len(arr):
        #             return
        #         tup = tuple(arr)
        if len(tup):
            self.isMG = False
            tup = utils.pathlib_path_tup(tup, True)
            self.varL.set(tup)
            self.start_btn.set_state(True)
            self.varC = tk.StringVar()
            self.varR = tk.StringVar()
            setting_fftool.last_folder = utils.pathlib_parent(tup[0])
            # self.clear_query()

    def addCall(self):
        """追加文件到列表中
        """
        if self.isMG:
            utils.showinfo("处于多组合并模式，请使用粘贴框进行操作！")
            return

        ft = [("视频文件", "*.mp4"), ("QuickTime", "*.mov"),
              ("avi", "*.avi"), ("mkv", "*.mkv"), ("mpg", "*.mpg")]
        tup = filedialog.askopenfilenames(filetypes=ft)
        if len(tup):
            vStr = self.varL.get()
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
            tup = utils.pathlib_path_tup(tup, True)
            self.varL.set(tup)
            self.start_btn.set_state(bool(len(nnArr)))
            setting_fftool.last_folder = utils.pathlib_parent(tup[0])
            # self.clear_query()

    def removeCall(self):
        """移除列表中的一项
        """
        indexs = self.listL.curselection()
        if len(indexs):
            indexArr = list(indexs)
            indexArr.sort(reverse=True)

            vStr = self.varL.get()
            v = utils.var_to_list(vStr)
            for i in indexArr:
                del v[i]
            self.varL.set(tuple(v))
            # vStr = self.varL.get()

            vStr = self.varR.get()
            v = utils.var_to_list(vStr)
            for i in indexArr:
                del v[i]
            self.varR.set(tuple(v))
            vStr = self.varR.get()

            enbale = False if utils.var_is_empty(vStr) else True
            self.start_btn.set_state(enbale)

            if not enbale:
                self.isMG = False

    def adjustCall(self, event):
        """上下调整列表
        """
        if self.isMG:
            utils.showinfo("处于多组合并模式，请使用粘贴框进行操作！")
            return
        indexs = self.listL.curselection()
        snum = len(indexs)
        if not snum:
            return
        if snum > 1:
            utils.showinfo("只支持单个的顺序调整")
            return

        vStr = self.varL.get()
        v = utils.var_to_list(vStr)
        i = indexs[0]
        if event.widget == self.upBtn:
            if i > 0 and i < len(v) and len(v) > 0:
                obj = v[i]
                del v[i]
                v.insert(i - 1, obj)
                self.varL.set(tuple(v))
                self.listL.selection_clear(i)
                self.listL.select_set(i - 1)

        if event.widget == self.downBtn:
            if i < len(v) - 1 and len(v) > 0:
                obj = v[i]
                del v[i]
                v.insert(i + 1, obj)
                self.varL.set(tuple(v))
                self.listL.selection_clear(i)
                self.listL.select_set(i + 1)

    def smartPasteLeave(self, event):
        """粘贴框离开
        """
        if not self.hasClick:
            return
        else:
            self.hasClick = False

        if setting_fftool.has_query:
            utils.showinfo("有任务正在执行，请稍后")
            return
        ss = self.smartPaste.get(1.0, tk.END)
        arr = utils.split_str(ss, False)
        if len(arr) and arr[0] == self.smartNotice:
            return
        # 检查文件是否存在 /指定格式
        ft = (".mp4", ".mov", ".avi", ".mkv", ".mpg")

        # 多组合并
        self.isMG = False
        imp4s = []
        inames = []
        for item in arr:
            iarr = item.split("\t")
            if len(iarr) > 1:
                imp4 = iarr[0]
                imp4 = imp4.strip('"')  # windows复制的路径有可能带有 双引号
                iname = iarr[1]
                if not iname:
                    continue
                if not os.path.isfile(imp4):
                    continue
                typestr = utils.get_file_type(imp4).lower()
                if not ft.count(typestr):
                    continue
                imp4s.append(imp4)
                inames.append(iname)
                self.isMG = True

        if not self.isMG:
            imp4s = []
            for item in arr:
                typestr = utils.get_file_type(item).lower()
                if not ft.count(typestr) or not os.path.isfile(item):
                    continue
                imp4s.append(item)

            if len(imp4s):
                tup = tuple(imp4s)
                tup = utils.pathlib_path_tup(tup, True)
                self.varL.set(tup)
                self.start_btn.set_state(True)

                self.varC = tk.StringVar()
                self.varR = tk.StringVar()
            else:
                if ss == '':
                    utils.showinfo('粘贴的文件路径 不正确，请检查！')
                # self.clear_query()
        else:
            # Z = zip(inames,imp4s)
            # Z = sorted(Z,reverse=True)

            # imp4s,inames = zip(*Z)
            tup = self.removeInvalid(imp4s, inames)
            mp4tup = utils.pathlib_path_tup(tup[0], True)
            nametup = utils.pathlib_path_tup(tup[1], True)
            marktup = utils.pathlib_path_tup(tup[2], True)
            self.groupInfos = tup[3]

            self.varL.set(mp4tup)
            self.varC.set(marktup)
            self.varR.set(nametup)

            self.start_btn.set_state(True)

            if len(imp4s) == 0 and ss == '':
                utils.showinfo('粘贴的文件路径 不正确，请检查！')

        self.smartPaste.delete(1.0, tk.END)
        self.smartPaste.insert(tk.INSERT, self.smartNotice)

    def smartPasteClick(self, event):
        """点击粘贴框
        """
        self.smartPaste.delete(1.0, tk.END)
        self.hasClick = True

    def startCheck(self):
        """点击开始按钮
        """
        dc = self.dc

        if setting_fftool.has_query:
            utils.showinfo("有任务正在执行，请稍后")
            return

        vlstr = self.varL.get()
        vlarr = utils.var_to_list_smb(vlstr)
        if utils.var_is_empty(vlstr):
            utils.showinfo("还没有导入文件")
            return

        if len(vlarr) < 2:
            utils.showinfo("不能少于2个文件")
            return

        # p5 = self.outTxt['text']
        p5 = self.fc_out.get_text()
        fast_mode_select = True if self.CheckVar1.get() else False

        dc["output_dir"] = p5
        dc["input_files"] = vlarr
        dc["fast_mode_select"] = fast_mode_select

        # 记忆操作
        setdc = setting_fftool.read_setting()
        setdc["output_dir"] = p5
        setting_fftool.save_setting(setdc)

        # 禁用开始按钮
        # self.clear_query()
        self.lockBtn(True)

        # 执行操作
        if not self.isMG:
            func = self.processConcats
        else:
            func = self.processConcatsGroup
            dc["group_infos"] = self.groupInfos
        import threading
        self.t1 = threading.Thread(target=func, args=(dc, ''))
        self.t1.setDaemon(True)
        self.t1.start()

    def processConcats(self, dc, astr=''):
        """合并多个 mp4成一个文件
        """
        self.concat(dc, "")

        # 结束后的操作
        self.processAfter()

    def processConcatsGroup(self, dc, astr=''):
        """多个合并组 合并多个文件
        """
        infos = dc["group_infos"]
        ndc = dc.copy()
        total = len(infos)
        count = 0
        msgStr = "【{0}/{1}】【{2}】"
        for info in infos:
            finalName = info['name']
            ndc["input_files"] = info['files']

            count = count + 1
            prefix = msgStr.format(count, total, finalName + '.mp4')

            self.concat(ndc, finalName, prefix)

        # 结束后的操作
        self.processAfter()

    def processAfter(self):
        """结束后的操作
        """
        self.setTitle2("操作结束！")
        # 自动打开目录
        if self.finalMP4:
            utils.open_dir(self.outputDir)
        # 重置多线程
        self.t1 = ""
        self.lockBtn(False)

    seqConcats = ('input_files', 'group_infos'  'output_dir', 'fast_mode_select')

    def concat(self, dc, finalName='', titlePrefix=''):
        """执行合并操作
        """
        setTitle = self.setTitle2

        files = dc["input_files"]
        fast_mode_select = dc["fast_mode_select"]
        outputDir = dc["output_dir"] + os.sep
        tempDir = outputDir + 'tempDir' + os.sep

        finalMP4 = ""
        pStr = ""

        # set param=-c:v libx264 -s 1920x1080 -r 24 -b:v 6144k -b:a 128k -ar 44100 -ac 2 -preset slower -threads 8
        FFStr = '''ffmpeg -y -i "{input}" -c:v libx264 -s {v_size} -crf 18 -r {fps} -b:a 128k -ar 44100 -ac 2 -threads 8 "{output}"'''
        FFConcat = '''ffmpeg -y -f concat -safe 0 -i "{0}" -c copy "{1}"'''

        total = len(files)
        fpath = files[0]
        arr = utils.get_file_names(fpath)
        fname = arr[1]
        if total > 2:
            fullName = fname + '__{0}__等' + str(total) + '个合并'
        else:
            fullName = fname + '__{0}'

        subs = []
        sub = "file '{0}'\n"

        # 读取第一个视频的 尺寸和帧频作为基准
        # ！！！所有的视频都会进行一次转码
        seq = ('input', 'output', 'v_size', 'fps')
        dc = dict.fromkeys(seq, "")
        dcinfo = ff.get_video_info(fpath, False)
        dc['fps'] = dcinfo['fps'] if dcinfo['fps'] else '24'
        dc['v_size'] = dcinfo['v_size'] if dcinfo['v_size'] else '1920x1080'

        # 逐个转换视频
        utils.make_dir(tempDir)
        utils.hide_file(tempDir)
        count = 0
        msgStr = " ({0}/{1}) {2}"
        files_temp = []
        for i in range(total):
            count = count + 1

            fpath = files[i]
            arr = utils.get_file_names(fpath)
            fname = arr[1]
            ftemp = tempDir + "-" + fname + ".mp4"
            files_temp.append(ftemp)

            if i == 1:
                fullName = fullName.format(fname)

            # 极速模式 跳过转码步骤
            if fast_mode_select:
                continue

            mstr = msgStr.format(count, total, "转换 " + fname + " ……")
            setTitle(titlePrefix + mstr)
            dc['input'] = fpath
            dc['output'] = ftemp
            pStr = FFStr.format(**dc)
            ff.execute(pStr)

        # 检查文件 并 写入 concat 文件
        for i in range(total):
            fpath = files[i]
            ftemp = files_temp[i]

            ffpath = fpath if fast_mode_select else ftemp

            if os.path.exists(ffpath):
                subs.append(sub.format(ffpath))
            else:
                mstr = ffpath + "转码失败"
                setTitle(titlePrefix + mstr)

        # 写入concat文件 并 拼接视频
        subTxt = tempDir + "concat_" + fullName + ".txt"
        utils.write_txt(subTxt, subs)

        mstr = "正在拼接所有视频……"
        setTitle(titlePrefix + mstr)
        if finalName:
            finalMP4 = outputDir + finalName + ".mp4"
        else:
            finalMP4 = outputDir + fullName + ".mp4"
        pStr = FFConcat.format(subTxt, finalMP4)
        ff.execute(pStr)
        setTitle("")

        # 移除 concat.txt 和 临时mp4
        utils.remove_file(subTxt)
        for i in range(total):
            ftemp = files_temp[i]
            utils.remove_file(ftemp)

        self.finalMP4 = finalMP4
        self.outputDir = outputDir

    def setTitle2(self, title, warning=False):
        ntitle = utils.get_hms() + " " + title
        utils.set_title(self.titlePrefix + "-" + ntitle)
        self.updateQuery(ntitle, warning)
        print(ntitle)

    def removeInvalid(self, imp4s, inames):
        """移除无效数据
        
        Arguments:
            imp4s {[string]} -- mp4路径
            inames {[string]} -- 合并组组名
        
        Returns:
            (imp4s,inames,infos)
        """
        lista = imp4s
        listb = inames
        listc = []

        seq = ("name", "files")
        info = dict.fromkeys(seq)
        infos = []
        names = []
        for i in range(len(listb)):
            fname = lista[i]
            item = listb[i]
            count = names.count(item)
            if count > 0:
                index = names.index(item)
                info = infos[index]
                info['files'].append(fname)
            else:
                info = dict.fromkeys(seq)
                info['name'] = item
                info['files'] = [fname]

                infos.append(info)
                names.append(item)

        # 合并必须两个文件以上
        ninfos = []
        for info in infos:
            files = info['files']
            if len(files) > 1:
                ninfos.append(info)
        infos = ninfos

        lista.clear()
        listb.clear()
        mark1 = '︷'
        mark2 = '۰'
        mark3 = '︸'

        for info in infos:
            mp4s = info['files']
            fname = info['name']
            count = 0
            for mp4 in mp4s:
                lista.append(mp4)
                listb.append(fname)
                count = count + 1
                if count == 1:
                    listc.append(mark1)
                elif count == len(mp4s):
                    listc.append(mark3)
                else:
                    listc.append(mark2)

        imp4s = lista
        inames = listb
        imarks = listc

        return (imp4s, inames, imarks, infos)


if __name__ == "__main__":
    pass
