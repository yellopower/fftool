#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk

import utils

# 颜色
COLOR_BLACK = "#000000"
COLOR_GRAY = "#B9BFC1"
COLOR_GREEN = '#009051'
COLOR_RED = '#ff5643'
COLOR_TXT_BG = "#ECECEC"
COLOR_LIST_BG = "#EFEFEF"

img_win_icon = utils.exe_parent + '/icon.ico'
img_mac_icon = utils.exe_parent + '/icon.icns'


def get_small_format():
    families = tk.font.families()
    font_name = '微软雅黑' if utils.is_windows else ''
    font_size = 8 if utils.is_windows else 10
    if families.count(font_name):
        txt_format = tk.font.Font(size=font_size, family=font_name)
    else:
        txt_format = tk.font.Font(size=font_size)
    return txt_format


def get_big_title():
    families = tk.font.families()
    font_name = '微软雅黑' if utils.is_windows else ''
    font_size = 16 if utils.is_windows else 14
    if families.count(font_name):
        txt_format = tk.font.Font(size=font_size, family=font_name)
    else:
        txt_format = tk.font.Font(size=font_size)
    return txt_format

# LIST_WIDTH = 91+10
# TXT_WIDTH = 78
# FILE_GAP = 65+10
# WRAP_LENGTH = 780
