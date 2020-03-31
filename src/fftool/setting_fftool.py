#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

import utils

# 返回当前文件所在的目录
# __pyParent = os.path.dirname(__file__)
# 返回当前文件所在的上上一级目录
# __pyGrandParent = os.path.dirname(__pyParent) + os.sep
# __pyParent = __pyParent + os.sep

# 需要先初始化 tk，才能创建字体信息
font_default = ''

# 记忆导入按钮的最后打开记录
last_folder = ''
# 转码时 会标记该变量
has_query = False

# 获取默认目录 和 配置保存路径
# 配置保存在我的文档的”转码工具箱“目录下
sep = os.sep
if utils.is_windows:
    output_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), '转码工具箱') + sep + 'output'
    document = os.path.join(os.path.join(os.environ['USERPROFILE']), '转码工具箱')
else:
    output_dir = os.path.expanduser('~/Documents/转码工具箱/output')
    document = os.path.expanduser('~/Documents/转码工具箱')

list_file = document + sep + "_py__list.txt"
setting_file = document + sep + "_py__setting.json"
utils.make_dir(output_dir)
utils.make_dir(document)


def read_setting():
    """从 json 文件中读取设置
    """
    seq = ('output_dir', 'tab_index',
           'pt_file', 'pw_file', 'frame_file', 'watermark_file', 'number_file',
           'pt_select', 'pw_select', 'frame_select', 'watermark_select', 'number_select',
           'number_15_select'
           )
    if os.path.exists(setting_file):
        f = open(setting_file, 'rb')
        jf = json.load(f)

        # 同步键值
        dc = jf.copy()
        for s in seq:
            if s not in jf:
                dc.setdefault(s, "")
    else:
        dc = dict.fromkeys(seq, "")

    # 旧版创建的 json 可能没有这些字段
    tup1 = ('number_15_select',
            'number_file', 'number_file_2', 'number_file_3',
            'number_select', 'number_select_2', 'number_select_3',
            'uninumber_file', 'uninumber_select'
            )
    tup2 = ('0',
            '', '', '',
            '0', '0', '0',
            '', '0'
            )
    for i in range(len(tup1)):
        key = tup1[i]
        value = tup2[i]
        if key not in dc:
            dc.setdefault(key, value)
    return dc


def save_setting(dc):
    """保存设置到json文件
    bool 类型用字符串 1 或 0来表示
    """
    s = json.dumps(dc, ensure_ascii=False, indent=2)
    utils.write_txt(setting_file, s)


def modify_setting(_dc):
    """修改json文件
    """
    rdc = read_setting()
    rdc.update(_dc)
    save_setting(rdc)


def read_tab_index():
    """返回tab的索引值
    返回 字符串
    """
    dc = read_setting()
    index_str = dc["tab_index"]
    return index_str


def save_tab_index(_index):
    """保存当前打开 tab索引值到 json 文件
    """
    dc = read_setting()
    dc["tab_index"] = str(_index)
    save_setting(dc)


def get_output_dir():
    jf = read_setting()
    p = jf["output_dir"]
    if not os.path.exists(p):
        p = output_dir
    if not os.path.exists(p):
        p = ""
    return p


if __name__ == "__main__":
    pass
