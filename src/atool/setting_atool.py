#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path

import utils
from atool import util_atool, widget_device

py_parent = ''
last_screen_shot = ''

# 设备信息数据
device_datas = []

# 获取默认目录 和 配置保存路径
# 配置保存在我的文档的对应目录下```
sep = os.sep
if utils.is_windows:
    output_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), '安卓工具箱') + sep + 'AndroidTool'
    document = os.path.join(os.path.join(os.environ['USERPROFILE']), '安卓工具箱')
else:
    output_dir = os.path.expanduser('~/Documents/安卓工具箱/AndroidTool')
    document = os.path.expanduser('~/Documents/安卓工具箱')
utils.make_dir(output_dir)

temp_dir = output_dir + sep + "temp"
utils.make_dir(temp_dir)
utils.hide_file(temp_dir)

setting_file = document + sep + "setting.json"
permission_json = document + sep + "config_permission.json"
channel_json = document + sep + "config_channel.json"
android_api_json = document + sep + "config_android_api.json"


def read_setting():
    """从 json 文件中读取设置"""
    seq = ('recent_ip', 'auto_open', 'output_dir')
    if os.path.exists(setting_file):
        f = open(setting_file, 'rb')
        jf = json.load(f)
        f.close()

        # 同步键值
        dc = jf.copy()
        for s in seq:
            if s not in jf:
                dc.setdefault(s, "")
    else:
        dc = dict.fromkeys(seq, "")

    key = 'auto_open'
    if not dc[key]:
        dc[key] = '1'
    key = 'output_dir'
    if not dc[key]:
        dc[key] = output_dir

    # 自定义分辨率
    dc_config = [
        ["size", "1280x720"], ["size_on", "1"],
        ["density", "240"], ["density_on", "1"]
    ]
    for arr in dc_config:
        key = arr[0]
        value = arr[1]
        if key not in dc:
            dc.setdefault(key, value)

    return dc


def save_to_json(dc):
    """保存设置到json文件"""
    s = json.dumps(dc, ensure_ascii=False, indent=2)
    utils.write_txt(setting_file, s)


def modify_setting(dc):
    """修改json文件"""
    rdc = read_setting()
    rdc.update(dc)
    save_to_json(rdc)


def modify_one(key, value):
    """ 更新一条设置 """
    jf = read_setting()
    jf[key] = value
    save_to_json(jf)


def read_one(key):
    """ 读取一条设置 """
    jf = read_setting()
    if key in jf:
        return jf[key]
    else:
        return ""


def need_auto_open():
    return read_one('auto_open')


def get_data_by_serial(_serial):
    for d in device_datas:
        if d.serial == _serial:
            return d

    d = widget_device.DeviceData(_serial)
    return d


def _get_output_dir():
    p = read_one("output_dir")
    if os.path.exists(p):
        return p
    else:
        return ''


def init_tool():
    """初始化工具"""
    _dir = _get_output_dir()
    if _dir:
        global output_dir
        output_dir = _dir

    pp = str(Path(py_parent).parent)
    if utils.is_windows:
        # ff = 'D:\\FFmpeg'
        # arr = [
        #     py_parent,
        #     utils.exe_parent,  # exe 释放路径
        #     pp + sep + "shared",  # 父目录共享文件夹
        #     ff,  # 环境变量目录
        #     "{}/_pack/win".format(pp),  # 打包地址
        #     ff + sep + "shared"  # 环境变量目录 shared目录
        # ]
        arr = [str(Path(utils.ffmpeg_path).parent)]
        util_atool.adb_path = __find_file(arr, "adb.exe")
        util_atool.aapt_path = __find_file(arr, "aapt.exe")
        util_atool.openssl_path = __find_file(arr, "openssl.exe")

        if not util_atool.openssl_path:
            utils.showinfo("找不到openssl路径！！！")

    elif utils.is_mac:
        arr = [
            "/usr/local/bin",  # homebrew安装的android-platform-tools
            py_parent,
            pp + sep + "shared",  # 父目录共享文件夹
            os.path.expanduser('~/mytool/tool')  # 环境变量目录
        ]
        util_atool.adb_path = __find_file(arr, "adb")
        util_atool.aapt_path = __find_file(arr, "aapt")

    if not util_atool.adb_path:
        utils.showinfo("找不到 adb 路径")
    else:
        print("adb：{}".format(util_atool.adb_path))
    if not util_atool.aapt_path:
        utils.showinfo("找不到 aapt 路径")

    # 创建配置文件
    touch_permission_json()
    touch_channel_json()
    touch_api_json()


def __find_file(dir_list, file_name):
    """在多个目录下查找文件，返回第一个匹配"""
    for p in dir_list:
        f = p + os.sep + file_name
        if os.path.exists(f):
            return f
    return ""


def get_permission_desc(permission_name=''):
    """获得权限描述
    """
    checked = touch_permission_json()
    if not checked:
        return ''

    f = open(permission_json, 'rb')
    jf = json.load(f)
    f.close()

    pname = permission_name.replace("android.permission.", "")
    desc = ''
    key = 'config'
    arr = jf[key] if key in jf else []
    for item in arr:
        kname = 'name'
        kdesc = 'desc'
        if kname in item and \
                kdesc in item and \
                item[kname] == pname:
            desc = item['desc']
    return desc


def get_channel_desc(channel_name=''):
    """获得权限描述
    """
    checked = touch_channel_json()
    if not checked:
        return ''

    f = open(channel_json, 'rb')
    jf = json.load(f)
    f.close()

    desc = ''
    key = 'config'
    arr = jf[key] if key in jf else []
    for item in arr:
        kname = 'name'
        kdesc = 'desc'
        if kname in item and \
                kdesc in item and \
                item[kname] == channel_name:
            desc = item['desc']
    return desc


def get_api_desc(api_id=''):
    """获得权限描述
    """
    checked = touch_api_json()
    if not checked:
        return ''

    f = open(android_api_json, 'rb')
    jf = json.load(f)
    f.close()

    api_id = str(api_id)
    desc = ''
    key = 'config'
    arr = jf[key] if key in jf else []
    for item in arr:
        if 'name' in item and \
                'desc' in item and \
                item['name'] == api_id:
            desc = item['desc']
    return desc


def touch_permission_json():
    json_file = permission_json
    ver = ver_permission
    gen_func = gen_permission
    checked = touch_json(json_file, ver, gen_func)
    return checked


def touch_channel_json():
    json_file = channel_json
    ver = ver_channel
    gen_func = gen_channel
    checked = touch_json(json_file, ver, gen_func)
    return checked


def touch_api_json():
    json_file = android_api_json
    ver = ver_api
    gen_func = gen_api
    checked = touch_json(json_file, ver, gen_func)
    return checked


def touch_json(json_file, ver, gen_func):
    """
    创建 并 比对 json，如果 json 版本较低则更新
    :param json_file:
    :param gen_func:
    :param ver:
    :return:
    """
    # json_file = android_api_json
    # gen_func = setting_json.gen_api
    # ver = setting_json.ver_api
    if not os.path.exists(json_file):
        gen_func(json_file)
    if not os.path.exists(json_file):
        return False

    f = open(json_file, 'rb')
    jf = json.load(f)
    f.close()

    key = 'version'
    if key in jf:
        if int(jf['version']) < ver:
            gen_func(json_file)
            if not os.path.exists(json_file):
                return False
    else:
        gen_func(json_file)

    return True


def get_recent():
    dc = read_setting()
    ips = dc['recent_ip']
    if ips == '':
        ips = []
    return ips


def set_recent(ips_arr):
    """
    设置最近连接，数组是一个个json对象
    例如：
        { "name": "FamilyKtv", "ip": "192.168.0.118" }
    :param ips_arr:
    :return:
    """
    dc = read_setting()
    dc['recent_ip'] = ips_arr
    save_to_json(dc)


def update_recent(device_name, ip, port=""):
    ips = get_recent()
    need_add = True
    for obj in ips:
        if 'name' not in obj or 'ip' not in obj:
            continue
        if obj['ip'] == ip:
            need_add = False
            # 更新设备名
            if device_name:
                obj.setdefault("name", device_name)
            # 更新端口号
            if port:
                obj.setdefault("port", port)
            break

    if need_add:
        obj = {"ip": ip}
        if device_name:
            obj.setdefault("name", device_name)
        if port:
            obj.setdefault("port", port)
        ips.append(obj)

    dc = read_setting()
    dc['recent_ip'] = ips
    save_to_json(dc)


def remove_recent(ip_str):
    dc = read_setting()
    arr = dc['recent_ip']
    i = 0
    index = -1
    for obj in arr:
        if "ip" in obj and obj["ip"] == ip_str:
            index = i
        i += 1
    arr.pop(index)
    save_to_json(dc)


def get_package():
    dc = read_setting()
    key = 'package'
    if key not in dc:
        return []
    else:
        return dc[key]


def update_package(_app_name, _package):
    dc = read_setting()
    key = 'package'
    if key not in dc:
        arr = []
    else:
        arr = dc[key]

    need_add = True
    for obj in arr:
        if 'package' not in obj or 'name' not in obj:
            continue
        if obj['package'] == _package:
            need_add = False
            if _app_name:
                obj['name'] = _app_name
            break

    if need_add:
        dc[key].append({'package': _package, 'name': _app_name})
        save_to_json(dc)


def remove_package(_package):
    dc = read_setting()
    arr = dc['package']
    i = 0
    index = -1
    for obj in arr:
        if 'package' in obj:
            if obj['package'] == _package:
                index = i
        i += 1
    arr.pop(index)
    save_to_json(dc)


def init_package():
    tup = (
        ['亲宝乐园', 'com.guliguli.tv.babyland'],
        ['果果乐园', 'com.lutongnet.ott.ggly'],
        ['亲宝儿歌', 'com.iqinbao.android.songs'],
        ['亲宝儿歌TV', 'com.iqinbao.android.songsTV'],
        ['幼升小全课程', 'com.guliguli.youxiao'],
        ['幼升小全课程 华为', 'com.guliguli.youxiao.huawei'],
        ['幼升小全课程 OPPO', 'com.guliguli.youxiao.nearme.gamecenter'],
        ['成长乐园', 'com.jrsoft.cqczlyedu']
    )
    cur_ver = 1

    dc = read_setting()
    kp = 'package'
    kv = 'package_version'
    ver = int(dc[kv]) if kv in dc else 0
    if kp not in dc or ver < cur_ver:
        dc[kp] = []
        dc[kv] = '1'
        for s in tup:
            p_name = s[0]
            p_package = s[1]
            dc[kp].append({'package': p_package, 'name': p_name})
        save_to_json(dc)


pyParent = os.path.dirname(__file__)
sep = os.sep


# def read_json():
#     channel_json = py_parent + sep + "shared" + sep + "config_permission.json"
#     f = open(channel_json, 'rb')
#     jf = json.load(f)
#     f.close()

#     key = 'config'
#     arr = jf[key] if key in jf else []
#     for item in arr:
#         jname = item['name']
#         jdesc = item['desc']
#         s = '"{0}", "{1}",'
#         print(s.format(jname,jdesc))


def gen_channel(json_file):
    """生成 channel.json
    """
    __gen_json(json_file, channel_arr, ver_channel)


def gen_api(json_file):
    """生成 android_api.json
    """
    __gen_json(json_file, api_arr, ver_api)


def gen_permission(json_file):
    """生成 permission.json
    """
    __gen_json(json_file, permission_arr, ver_permission)


def __gen_json(json_file, arr, version=0):
    """生成 json

    Arguments:
        json_file {[type]} -- 完整的 json 文件路径
        arr {[type]} -- ["28","9.0", "27","8.0"]
    """
    if version:
        dc = {"config": [], "version": version}
    else:
        dc = {"config": []}
    for i in range(len(arr)):
        if i % 2 != 0:
            continue
        jname = arr[i]
        jdesc = arr[i + 1]
        obj = {"name": jname, "desc": jdesc}
        dc['config'].append(obj)
    # 保存到 json 文件
    s = json.dumps(dc, ensure_ascii=False, indent=2)
    utils.write_txt(json_file, s)


ver_channel = 5
ver_permission = 4
ver_api = 4

channel_arr = [
    "1", "360",
    "2", "百度",
    "3", "91",
    "4", "安卓市场",
    "5", "应用宝",
    "6", "小米",
    "7", "魅族",
    "8", "华为",
    "9", "联想",
    "10", "oppo",
    "11", "vivo",
    "12", "乐视",
    "13", "豌豆荚",
    "14", "pp助手",
    "15", "搜狗",
    "16", "木蚂蚁",
    "17", "安智市场",
    "18", "应用汇",
    "19", "优亿",
    "20", "阿里云",
    "21", "googleplay",
    "22", "iqinbao",
    "23", "锤子",
    "24", "葡萄科技平台",
    "25", "金立",
    "26", "三星",
    "100", "备用渠道",
    "101", "备用渠道",
    "102", "备用渠道",
    "103", "备用渠道",
    "104", "备用渠道",
    "105", "备用渠道",
    "qb_1", "360",
    "qb_2", "百度",
    "qb_3", "91",
    "qb_4", "安卓市场",
    "qb_5", "应用宝",
    "qb_6", "小米",
    "qb_7", "魅族",
    "qb_8", "华为",
    "qb_9", "联想",
    "qb_10", "oppo",
    "qb_11", "vivo",
    "qb_12", "乐视",
    "qb_13", "豌豆荚",
    "qb_14", "pp助手",
    "qb_15", "搜狗",
    "qb_16", "木蚂蚁",
    "qb_17", "安智市场",
    "qb_18", "应用汇",
    "qb_19", "优亿",
    "qb_20", "阿里云",
    "qb_21", "googleplay",
    "qb_22", "iqinbao",
    "qb_23", "锤子",
    "qb_24", "葡萄",
    "qb_25", "金立",
    "qb_26", "三星",
    "qb_100", "步步高家教机",
    "qb_101", "移动mm",
    "qb_102", "优学派",
    "qb_103", "备用渠道",
    "qb_104", "读书郎",
    "qb_105", "备用渠道",
    "tv1", "小米TV",
    "tv2", "乐视电视",
    "tv3", "阿里TV",
    "tv4", "当贝市场",
    "tv5", "沙发管家",
    "tv6", "爱家TV",
    "tv7", "奇珀市场",
    "tv8", "悦me盒子",
    "tv9", "联通OTT",
    "tv10", "大麦盒子",
    "tv11", "卓影TV",
    "tv12", "欢网",
    "tv13", "网讯",
    "tv14", "屁颠虫",
    "tv15", "海信电视",
    "tv16", "TCL电视",
    "tv17", "重庆移动",
    "tv18", "华为",
    "tv19", "中国电信",
    "tv20", "四川移动",
    "tv21", "未来应用"
]

api_arr = [
    "28", "10.0 Android Q",
    "28", "9.0  Pie 果馅饼",
    "27", "8.1  Oreo 奥利奥",
    "26", "8.0  Oreo 奥利奥",
    "25", "7.1  Nougat 牛轧糖",
    "24", "7.0  Nougat 牛轧糖",
    "23", "6.0  Marshmallow 棉花糖",
    "22", "5.1  LOLLIPOP_MR1 棒棒糖",
    "21", "5.0  LOLLIPOP 棒棒糖",
    "20", "4.4W",
    "19", "4.4",
    "18", "4.3",
    "17", "4.2 4.2.2",
    "16", "4.1 4.1.1",
    "15", "4.0.3 4.0.4",
    "14", "4.0 4.0.1 4.0.2",
    "13", "3.2",
    "12", "3.1.x",
    "11", "3.0.x",
    "10", "2.3.4 2.3.3",
    "9", "2.3.2 2.3.1 2.3",
    "8", "2.2.x",
    "7", "2.1.x",
    "6", "2.0.1",
    "5", "2.0",
    "4", "1.6",
    "3", "1.5",
    "2", "1.1",
    "1", "1.0"
]

permission_arr = [
    "BATTERY_STATS", "获取电池状态信息的权限",
    "BLUETOOTH", "连接匹配的蓝牙设备的权限",
    "BLUETOOTH_ADMIN", "发现匹配的蓝牙设备的权限",
    "BROADCAST_SMS", "广播收到短信提醒的权限",
    "CALL_PHONE", "拨打电话的权限",
    "CHANGE_NETWORK_STATE", "改变网络连接状态的权限",
    "CHANGE_WIFI_STATE", "改变wifi网络连接状态的权限",
    "DELETE_CACHE_FILES", "删除缓存文件的权限",
    "DELETE_PACKAGES", "删除安装包的权限",
    "FLASHLIGHT", "访问闪光灯的权限",
    "MODIFY_AUDIO_SETTINGS", "修改全局声音设置的权限",
    "PROCESS_OUTGOING_CALLS", "监听、控制、取消呼出电话的权限",
    "READ_CONTACTS", "读取用户的联系人数据的权限",
    "READ_HISTORY_BOOKMARKS", "读取历史书签的权限",
    "READ_OWNER_DATA", "读取用户数据的权限",
    "READ_PHONE_SMS", "读取短信的权限",
    "REBOOT", "重启系统的权限",
    "RECEIVE_MMS", "接收、监控、处理彩信的权限",
    "RECEIVE_SMS", "接收、监控、处理短信的权限",
    "RECORD_AUDIO", "录音的权限",
    "SEND_SMS", "发送短信的权限",
    "SET_ORIENTATION", "旋转屏幕的权限",
    "SET_TIME", "设置时间的权限",
    "SET_TIME_ZONE", "设置时区的权限",
    "SET_WALLPAPER", "设置桌面壁纸的权限",
    "VIBRATE", "控制振动器的权限",
    "WRITE_CONTACTS", "写入用户联系人的权限",
    "WRITE_HISTORY_BOOKMARKS", "写历史书签的权限",
    "WRITE_OWNER_DATA", "写用户数据的权限",
    "WRITE_SMS", "写短信的权限",
    "GET_TASKS", "获取信息有关当前或最近运行的任务，一个缩略的任务状态，是否活动等等",

    "EXPAND_STATUS_BAR", "扩展收缩在状态栏,应该是一个类似Windows Mobile中的托盘程序",
    "FACTORY_TEST", "作为一个工厂测试程序，运行在root用户",
    "FLASHLIGHT", "访问闪光灯",
    "FORCE_BACK", "强行一个后退操作是否在顶层activities",
    "FOTA_UPDATE", "",
    "GET_ACCOUNTS", "访问一个帐户列表在Accounts Service中",
    "GET_PACKAGE_SIZE", "获取任何package占用空间容量",
    "GET_TASKS", "获取信息有关当前或最近运行的任务，一个缩略的任务状态，是否活动等等",
    "HARDWARE_TEST", "允许访问硬件",
    "INJECT_EVENTS", "截获用户事件如按键、触摸、轨迹球等等到一个时间流，android 开发网提醒算是hook技术吧",
    "INSTALL_PACKAGES", "安装packages",
    "INTERNAL_SYSTEM_WINDOW", "允许打开窗口使用系统用户界面",
    "ACCESS_CHECKIN_PROPERTIES", "允许读写访问“properties”表在checkin数据库中，改值可以修改上传。",
    "ACCESS_FINE_LOCATION", "允许访问精确的位置",
    "WRITE_CONTACTS", "写入但不读取用户联系人数据",
    "WRITE_GSERVICES", "修改Google服务地图",
    "WRITE_OWNER_DATA", "写入但不读取所有者数据",
    "WRITE_SMS", "写短信",
    "WRITE_SYNC_SETTINGS", "写入同步设置",
    "ACCESS_LOCATION_EXTRA_COMMANDS", "访问额外的位置提供命令",
    "ACCESS_MOCK_LOCATION", "创建模拟位置提供用于测试",
    "ACCESS_NETWORK_STATE", "访问有关GSM网络信息",
    "ACCESS_SURFACE_FLINGER", "使用SurfaceFlinger底层特性",
    "ACCESS_WIFI_STATE", "访问Wi-Fi网络状态信息",
    "ADD_SYSTEM_SERVICE", "发布系统级服务",
    "BATTERY_STATS", "更新手机电池统计信息",
    "BLUETOOTH", "连接到已配对的蓝牙设备",
    "BLUETOOTH_ADMIN", "发现和配对蓝牙设备",
    "BROADCAST_PACKAGE_REMOVED", "广播一个提示消息在一个应用程序包已经移除后",
    "BROADCAST_STICKY", "广播常用intents",
    "CALL_PHONE", "初始化一个电话拨号不需通过拨号用户界面需要用户确认",
    "DELETE_CACHE_FILES", "删除缓存文件",
    "DELETE_PACKAGES", "删除包",
    "DEVICE_POWER", "允许访问底层电源管理",
    "DIAGNOSTIC", "RW诊断资源",
    "DUMP", "返回状态抓取信息从系统服务",
    "CALL_PRIVILEGED", "拨打任何号码，包含紧急号码无需通过拨号用户界面需要用户确认",
    "CAMERA", "请求访问使用照相设备",
    "CHANGE_COMPONENT_ENABLED_STATE", "是否改变一个组件或其他的启用或禁用",
    "CHANGE_NETWORK_STATE", "改变网络连接状态",
    "CHANGE_WIFI_STATE", "改变Wi-Fi连接状态",
    "CLEAR_APP_CACHE", "清楚缓存从所有安装的程序在设备中",
    "CLEAR_APP_USER_DATA", "清除用户设置",
    "CONTROL_LOCATION_UPDATES", "允许启用禁止位置更新提示从无线模块",
    "REBOOT", "请求能够重新启动设备",
    "RECEIVE_BOOT_COMPLETED", "接收到 ACTION_BOOT_COMPLETED广播在系统完成启动",
    "RECEIVE_MMS", "监控将收到MMS彩信,记录或处理",
    "RECEIVE_SMS", "监控一个将收到短信息，记录或处理",
    "RECEIVE_WAP_PUSH", "监控将收到WAP PUSH信息",
    "RECORD_AUDIO", "录制音频",
    "REORDER_TASKS", "改变Z轴排列任务",
    "RESTART_PACKAGES", "重新启动其他程序",
    "SEND_SMS", "发送SMS短信",
    "INTERNET", "打开网络套接字",
    "MANAGE_APP_TOKENS", "管理(创建、催后、 z- order默认向z轴推移)程序引用在窗口管理器中",
    "MASTER_CLEAR", "可能是清除一切数据，类似硬格机",
    "MODIFY_AUDIO_SETTINGS", "修改全局音频设置",
    "MODIFY_PHONE_STATE", "允许修改话机状态，如电源，人机接口等",
    "PERSISTENT_ACTIVITY", "设置他的activities显示",
    "PROCESS_OUTGOING_CALLS", "监视、修改有关播出电话",
    "READ_CALENDAR", "读取用户日历数据",
    "READ_CONTACTS", "读取用户联系人数据",
    "READ_FRAME_BUFFER", "屏幕波或和更多常规的访问帧缓冲数据",
    "READ_INPUT_STATE", "返回当前按键状态",
    "READ_LOGS", "读取系统日志",
    "READ_OWNER_DATA", "读取所有者数据",
    "READ_SMS", "读取短信息",
    "READ_SYNC_SETTINGS", "读取同步设置",
    "READ_SYNC_STATS", "读取同步状态",
    "SET_ACTIVITY_WATCHER", "监控或控制activities已经启动全局系统中",
    "SET_ALWAYS_FINISH", "控制是否活动间接完成在处于后台时",
    "SET_ANIMATION_SCALE", "修改全局信息比例",
    "SET_DEBUG_APP", "配置一个程序用于调试",
    "SET_ORIENTATION", "允许底层访问设置屏幕方向和实际旋转",
    "SET_PREFERRED_APPLICATIONS",
    "修改列表参数PackageManager.addPackageToPreferred() 和PackageManager.removePackageFromPreferred()方法",
    "SET_PROCESS_FOREGROUND", "当前运行程序强行到前台",
    "SET_PROCESS_LIMIT", "允许设置最大的运行进程数量",
    "SET_TIME_ZONE", "设置时间区域",
    "SET_WALLPAPER", "设置壁纸",
    "SET_WALLPAPER_HINTS", "设置壁纸hits",
    "SIGNAL_PERSISTENT_PROCESSES", "请求发送信号到所有显示的进程中",
    "STATUS_BAR", "打开、关闭或禁用状态栏及图标",
    "SUBSCRIBED_FEEDS_READ", "访问订阅RSS Feed内容提供",
    "SUBSCRIBED_FEEDS_WRITE", "",
    "WRITE_APN_SETTINGS", "写入API设置",
    "WRITE_CALENDAR", "写入但不读取用户日历数据",

    "INTERNET", "允许访问网络",
    "ACCESS_COARSE_LOCATION", "粗略位置（基于网络的）",
    "ACCESS_FINE_LOCATION", "精准的(GPS)位置",
    "ACCESS_NETWORK_STATE", "查看网络状态（2G 还是 Wi-Fi)",
    "ACCESS_WIFI_STATE", "查看 Wi-Fi 状态",
    "SYSTEM_ALERT_WINDOW", "显示在其他应用上面",
    "VIBRATE", "允许访问振动设备",
    "com.android.vending.BILLING", "应用内购买结算",
    "RAISED_THREAD_PRIORITY", "改变线程优先级",

    "CHANGE_CONFIGURATION", "更改用户界面设置",
    "CAMERA", "拍摄照片和视频",
    "PHONE_STATE", "读取手机状态和身份",
    "READ_PHONE_STATE", "读取手机状态和身份",
    "WRITE_SETTINGS", "更改用户界面设置",
    "MOUNT_UNMOUNT_FILESYSTEMS", "装载和卸载文件系统",
    "DISABLE_KEYGUARD", "停用键盘锁",
    "WAKE_LOCK", "防止手机休眠",
    "KILL_BACKGROUND_PROCESSES", "结束后台进程",
    "READ_EXTERNAL_STORAGE", "允许读取外置存储卡",
    "WRITE_EXTERNAL_STORAGE", "允许写入外置存储卡",
    "RECEIVE_USER_PRESENT", "识别用户解锁了屏幕",
    # "BROADCAST_PACKAGE_ADDED", "",
    # "BROADCAST_PACKAGE_CHANGED", "",
    # "BROADCAST_PACKAGE_INSTALL", "",
    # "BROADCAST_PACKAGE_REPLACED", "",
    "REQUEST_INSTALL_PACKAGES", "允许安装应用",
]

if __name__ == "__main__":
    if not py_parent:
        py_parent = os.path.dirname(__file__)
    # dc = {}
    # arr = []
    # dc['recent_ip'] = arr
    # arr.append({'name': 'xxx', 'ip': '192.168.0.1'})
    # arr.append({'name': 'xx3x', 'ip': '192.168.0.3'})
    # arr.append({'name': 'xxx2', 'ip': '192.168.0.2'})
    # save_to_json(dc)
