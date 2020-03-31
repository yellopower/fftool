#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sched
import stat
import time
import zipfile

import utils
from atool import setting_atool, win_remote

"""
adb辅助类
"""

# adb 路径
adb_path = ""


def execute(cmd_str, has_adb_path=False):
    """执行 adb 或 appt 命令
    例如：adb device_list
    """
    result = ''
    if not has_adb_path:
        mark = 'adb'
        if not has_adb_path and not cmd_str.startswith(mark + ' '):
            print('adb命令行调用错误！\n' + cmd_str)
            return ''
        p_str = cmd_str.replace(mark, adb_path, 1)
    else:
        p_str = cmd_str

    if utils.is_mac:
        # 设置aapt为可执行
        if os.access(adb_path, os.X_OK) is not True:
            os.chmod(adb_path, stat.S_IRWXU)
        result = utils.execute(p_str)
    if utils.is_windows:
        result = utils.pipe(p_str, True)
        # result = result.replace('\r\n', '\n')
        result = utils.fix_wrap(result)
    return result


def screen_capture(_serial, auto_open=False):
    """截图
    """
    _arr = get_current_activity(_serial)
    activity_name = _arr[1]

    if activity_name:
        activity_name = activity_name.replace('.', '-')
        prefix = activity_name
    else:
        # 'adb -s {} shell getprop ro.product.model'.format(device)
        # getprop ro.product.name
        # s1 = 'adb -s {serial} shell getprop ro.product.name'.format(serial=_serial)
        d = device_data_find(_serial)
        ss = d.getprop('ro.product.name')
        device_name = ss.replace(' ', '_').replace('\n', '')

        ss = d.getprop('ro.build.id')
        build_id = ss.replace(' ', '_').replace('\n', '')
        prefix = device_name + '-' + build_id

    # s1 = 'adb -s {serial} shell getprop ro.product.name'.format(serial=_serial)
    # device_name = execute(s1).replace(' ', '_').replace('\r\n', '')
    # need_fix = True if device_name == 'lineage_m2note' else False

    png = '{prefix}-{now}.png'.format(prefix=prefix, now=__get_now())
    # s = 'cd {outdir} && \\'
    s = '{adb} -s {serial} shell screencap -p /sdcard/{png} && \\'
    s += '{adb} -s {serial} pull /sdcard/{png} {outdir} && \\'
    s += '{adb} -s {serial} shell rm /sdcard/{png}'
    s = utils.fix_cmd_wrap(s)
    final_png = setting_atool.output_dir + os.sep + png
    s = s.format(adb=adb_path, outdir=final_png, serial=_serial, png=png)
    print(no_xuhangfu(s))
    utils.pipe(s)

    show_msg("已截屏 " + png)
    if auto_open:
        utils.open_file(final_png)

    setting_atool.last_screen_shot = final_png


def screen_record(_serial, second=180):
    """录屏
    """
    # 'adb -s {} shell getprop ro.product.model'.format(device)
    # s2 = 'adb -s {serial} shell getprop ro.build.id'.format(serial=serial)
    # buildId = execute(s2).replace(' ', '_')
    # 部分手机不支持录屏
    d = device_data_find(_serial)
    # if not d.can_record:
    #     utils.showinfo("当前设备不能录屏")
    #     return

    device_name = d.getprop('ro.product.model')
    prefix = utils.legal_file_name(device_name)

    mp4 = '{prefix}-{now}.mp4'.format(prefix=prefix, now=__get_now())
    show_msg('正在录屏，倒计时{}s。录屏文件名：'.format(second) + mp4)

    # s = 'cd {outdir} && \\'
    s = '{adb} -s {serial} shell screenrecord --time-limit {second} /sdcard/{mp4} && \\'
    s += '{adb} -s {serial} pull /sdcard/{mp4} {outdir} && \\'
    s += '{adb} -s {serial} shell rm /sdcard/{mp4}'
    s = utils.fix_cmd_wrap(s)
    final_mp4 = setting_atool.output_dir + os.sep + mp4
    s = s.format(adb=adb_path, outdir=final_mp4, serial=_serial, mp4=mp4, second=second)
    print(no_xuhangfu(s))
    utils.pipe(s)
    if setting_atool.need_auto_open() == '1':
        utils.open_file(final_mp4)
    show_msg("已录屏 " + mp4)

    setting_atool.last_screen_shot = final_mp4
    print('已录屏 ' + mp4)


def open_wifi_debug(_serial):
    """开启wifi调试"""
    s = '{adb} -s {serial} shell setprop service.adb.tcp.port 5555 && \\'
    s += '{adb} -s {serial} tcpip 5555'
    s = utils.fix_cmd_wrap(s)
    s = s.format(adb=adb_path, serial=_serial)
    print(s.replace(" && \\", "\n"))
    result = utils.pipe(s)
    print(result)
    return result


def install(_serial, _apk_file, action_type=0):
    """安装 apk 到对应设备
    action_type=2 测试应用
    """
    if action_type == 2:
        # s = 'adb -s {serial} install -t -r "{apk}"'.format(serial=_serial, apk=_apk_file)
        # result = execute(s)
        s = '{adb} -s {serial} push "{apk}" /data/local/tmp/{a_apk} && \\'
        s += '{adb} -s {serial} shell pm install -t -r /data/local/tmp/{a_apk}'
        s = utils.fix_cmd_wrap(s)
        a_apk = 'apk-{now}.apk'.format(now=__get_now())
        s = s.format(adb=adb_path, serial=_serial, apk=_apk_file, a_apk=a_apk)
        print(no_xuhangfu(s))
        result = utils.pipe(s, True)

    else:
        # s = 'adb -s {serial} install -t -r "{apk}"'.format(serial=_serial, apk=_apk_file)
        # result = execute(s)
        s = '{adb} -s {serial} push "{apk}" /data/local/tmp/{a_apk} && \\'
        s += '{adb} -s {serial} shell pm install -r /data/local/tmp/{a_apk}'
        s = utils.fix_cmd_wrap(s)
        a_apk = 'apk-{now}.apk'.format(now=__get_now())
        s = s.format(adb=adb_path, serial=_serial, apk=_apk_file, a_apk=a_apk)
        print(no_xuhangfu(s))
        result = utils.pipe(s, True)

    result_lower = result.lower()

    if result_lower.count('success'):
        paa = get_package_and_activity(_apk_file)
        am_start_activity(_serial, paa)
        dc = get_apk_info(_apk_file)
        app_name = dc['app_name']
        show_msg("《{0}》安装成功！正在启动：{1}".format(app_name, paa))

    else:
        r_str = "安装受限，请在设备上开启“允许 usb 安装“\n 魅族:打开手机管家--点击权限管理--点击USB安装管理--关闭USB安装管理"
        # 错误代码, 错误描述, 操作类型
        # 操作类型
        #   0   仅提示
        #   1   需要重新安装
        #   2   testonly
        # ('[INSTALL_PARSE_FAILED_NO_CERTIFICATES]', '签名冲突', 1),
        _arr = [
            ('[INSTALL_FAILED_VERSION_DOWNGRADE]', '已存在更高版', 1),
            ('INSTALL_FAILED_ALREADY_EXISTS]', '程序已经存在', 1),
            ('INSTALL_FAILED_DUPLICATE_PACKAGE]', '已存在同名程序', 1),
            ('INSTALL_FAILED_UPDATE_INCOMPATIBLE]', '版本不能共存', 1),
            ('INSTALL_PARSE_FAILED_INCONSISTENT_CERTIFICATES', '签名不一致', 1),

            ('failed to copy', "apk路径中含有中文", 2),

            ('[INSTALL_FAILED_TEST_ONLY]', '测试apk', 2),

            ('[INSTALL_FAILED_USER_RESTRICTED]', r_str, 0),
            ('INSTALL_FAILED_INVALID_APK]', '无效的APK', 0),
            ('INSTALL_FAILED_INVALID_URI]', '无效的链接', 0),
            ('INSTALL_FAILED_INSUFFICIENT_STORAGE]', '没有足够的存储空间', 0),
            ('INSTALL_FAILED_NO_SHARED_USER]', '要求的共享用户不存在', 0),
            ('INSTALL_FAILED_SHARED_USER_INCOMPATIBLE]', '需求的共享用户签名错误', 0),
            ('INSTALL_FAILED_MISSING_SHARED_LIBRARY]', '需求的共享库已丢失', 0),
            ('INSTALL_FAILED_REPLACE_COULDNT_DELETE]', '需求的共享库无效', 0),
            ('INSTALL_FAILED_DEXOPT]', 'DEX优化验证失败', 0),
            ('INSTALL_FAILED_OLDER_SDK]', '系统版本过旧', 0),
            ('INSTALL_FAILED_NEWER_SDK]', '系统版本过新', 0),
            ('INSTALL_FAILED_CONFLICTING_PROVIDER]', '存在同名的内容提供者', 0),
            ('INSTALL_FAILED_CPU_ABI_INCOMPATIBLE]', '包含的本机代码不兼容', 0),
            ('CPU_ABIINSTALL_FAILED_MISSING_FEATURE]', '使用了一个无效的特性', 0),
            ('INSTALL_FAILED_CONTAINER_ERROR]', 'SD卡访问失败', 0),
            ('INSTALL_FAILED_MEDIA_UNAVAILABLE]', 'SD卡不存在', 0),
            ('INSTALL_FAILED_INVALID_INSTALL_LOCATION]', '无效的安装路径', 0),
            ('INSTALL_FAILED_INTERNAL_ERROR]', '系统问题导致安装失败', 0),
            ('INSTALL_PARSE_FAILED_NO_CERTIFICATES', 'apk签名问题', 0),
            ('DEFAULT]', '未知错误', 0)
        ]
        index = -1
        count = 0
        for item in _arr:
            code = item[0].lower()
            if result_lower.count(code):
                index = count
                break
            else:
                count += 1
        if index != -1:
            f_err = _arr[index][0]
            f_dec = _arr[index][1]
            f_ext = _arr[index][2]
            if f_ext == 1:
                params = [_serial, _apk_file]
                s = "{0}，是否卸载并重新安装！\n错误代码：{1}".format(f_dec, f_err)
                utils.alert(s, reinstall, params)
            elif f_ext == 2:
                params = [_serial, _apk_file, 2]
                s = "{0}，是否坚持安装！\n提示代码：{1}\n注意：本apk不能提交给市场审核！"
                s = s.format(f_dec, f_err)
                utils.alert(s, install, params)
            elif f_ext == 100:
                params = [_serial, _apk_file, 100]
                s = "{0}，是否尝试另一种安装方法！"
                s = s.format(f_dec, f_err)
                utils.alert(s, install, params)
            else:
                s = "安装失败{0}\n错误代码：{1}".format(f_dec, f_err)
                utils.showinfo(s)
        else:
            s = "安装失败\n" + result[-200:]
            utils.showinfo(s)


def reinstall(_serial, _apk_file):
    """卸载重新安装
    """
    dc = get_apk_info(_apk_file)
    p = dc['package_name']
    uninstall(p, False, _serial)
    install(_serial, _apk_file)


def uninstall(package_name, keep_data, _serial):
    """卸载应用
    """
    # uninstall -k ..would keep cache and data files
    if keep_data:
        s = 'adb -s {0} shell pm uninstall -k {1}'.format(_serial, package_name)
    else:
        s = 'adb -s {0} uninstall {1}'.format(_serial, package_name)
    s = execute(s)
    if s == 'Success':
        utils.showinfo("卸载完成")
    else:
        utils.showinfo(s)


def set_resolution(_serial, _size="", _density=""):
    """ 设置屏幕分辨率和屏幕密度, 支持单独设置 """
    if _size and _density:
        s = '{adb} -s {serial} shell wm size {size} && \\'
        s += '{adb} -s {serial} shell wm density {density}'
        # s += '{adb} -s {serial} shell am kill com.android.settings'
        s = utils.fix_cmd_wrap(s)
        s = s.format(adb=adb_path, serial=_serial, size=_size, density=_density)
    elif _size:
        s = '{adb} -s {serial} shell wm size {size}'
        s = utils.fix_cmd_wrap(s)
        s = s.format(adb=adb_path, serial=_serial, size=_size)
    elif _density:
        s = '{adb} -s {serial} shell wm density {density}'
        s = utils.fix_cmd_wrap(s)
        s = s.format(adb=adb_path, serial=_serial, density=_density)
    else:
        s = ""

    if s:
        result = utils.pipe(s)
        print(result)
        return result
    else:
        print("set_resolution方法 传参错误！！")
        return ""


def get_resolution(_serial):
    """获得分辨率
    """
    s = 'adb -s {serial} shell wm size'.format(serial=_serial)
    result = execute(s)
    # Physical size: 720x1280
    # Override density: 320
    reg = "Physical size: (.*)"
    p_str = reg_one(result, reg)

    reg = "Override size: (.*)"
    o_str = reg_one(result, reg)

    return [p_str, o_str]


def get_density(_serial):
    """获得屏幕密度
    """
    s = 'adb -s {serial} shell wm density'.format(serial=_serial)
    result = execute(s)

    # Physical size: 720x1280
    # Override density: 320
    reg = "Physical density: (.*)"
    p_str = reg_one(result, reg)

    reg = "Override density: (.*)"
    o_str = reg_one(result, reg)

    return [p_str, o_str]


def get_orientation(_serial):
    """旋转方向
    """
    s = 'adb -s {serial} shell dumpsys input'.format(serial=_serial)
    result = execute(s)
    reg = "SurfaceOrientation: (.*)"
    return reg_one(result, reg)


def get_current_activity(_serial):
    """获得当前运行的 activity
    """
    s = 'adb -s {serial} shell dumpsys activity recents'.format(serial=_serial)
    result = execute(s)
    reg = "realActivity=(.*)/(.*)"
    m = re.search(reg, result, re.M | re.I)
    if m:
        _arr = list(m.groups())

        arr2 = _arr[1].split('.')
        if len(arr2) >= 2:
            if arr2[0]:
                _arr[1] = arr2[0] + '-' + arr2[1]
            else:
                _arr[1] = arr2[1]
        else:
            _arr[1] = arr2[1]
    else:
        _arr = ('', '')
    return _arr


def get_cmd_with_serial(_serial):
    return '{adb} -s {serial} '.format(adb=adb_path, serial=_serial)


def log_clear(_serial):
    s = '{adb} -s {serial} logcat -c'.format(adb=adb_path, serial=_serial)
    utils.pipe(s, True)


def log_fast(_serial):
    txt_path = 'logcat-{now}.txt'.format(now=__get_now())

    save_dir = setting_atool.output_dir + os.sep + "logcat"
    final_txt = save_dir + os.sep + txt_path
    utils.make_dir(save_dir)

    s = '{adb} -s {serial} logcat -d -v time > "{final_txt}"'
    s = s.format(adb=adb_path, serial=_serial, final_txt=final_txt)
    print(s)
    utils.pipe(s)

    # 替换日志中多余的换行
    if utils.is_windows:
        _replace_empty_line(final_txt)

    return final_txt


def _replace_empty_line(_txt):
    f = open(_txt, 'r', encoding='utf-8')
    lines = f.read()
    f.close()

    lines = lines.replace("\n\n", "\n")
    utils.write_txt(_txt, lines)


def debug_layout(_serial, is_on=False):
    """
    打开/关闭 布局边界
    adb shell setprop debug.layout true
    adb shell am start com.android.settings/.DevelopmentSettings
    """
    on_str = 'true' if is_on else 'false'
    s = '{adb} -s {serial} shell setprop debug.layout {on_str} && \\'
    s += '{adb} -s {serial} shell am start com.android.settings/.DevelopmentSettings'
    # s += '{adb} -s {serial} shell am kill com.android.settings'

    s = utils.fix_cmd_wrap(s)
    s = s.format(adb=adb_path, serial=_serial, on_str=on_str)
    return utils.pipe(s)


def huawei_unlock(_serial):
    """华为解锁"""
    # 先按电源键, 再滑动
    s = '{adb} -s {serial} shell input keyevent {keycode} && \\'
    s += "{adb} -s {serial} shell input swipe 250 250 600 600"
    s = utils.fix_cmd_wrap(s)
    s = s.format(adb=adb_path, serial=_serial, keycode=26)
    return utils.pipe(s)


def open_setting(_serial):
    """打开设置"""
    # 先按电源键, 再滑动
    s = 'adb -s {serial} shell am start -n com.android.settings/.Settings$ManageApplicationsActivitadb'
    s = s.format(serial=_serial)
    print(s)
    return execute(s)


###
# 获得设备属性
###
def getprop(_serial):
    """获得设备属性
        dhcp.wlan0.ip    ip地址
        ro.product.model        设备名称
        ro.product.name         设备名称（model 更为可靠）
        ro.hardware
        ro.build.id
        ro.build.version.sdk
        sys.display-size        显示尺寸
    """
    s = 'adb -s "{serial}" shell getprop'.format(serial=_serial)
    s = execute(s)
    # print(s)
    return s


def getprop_product_name(prop_result):
    """设备名称"""
    p = 'ro.product.model'
    return search_in_prop(prop_result, p)


def search_in_prop(details, prop_name):
    """在 getprop结果中搜索某个属性"""
    reg = r"\[{}\]: \[(.*)\]".format(prop_name)
    return reg_one(details, reg)


def getprop_ip(prop_result):
    """ip 地址"""
    p = 'dhcp.wlan0.ip'
    return search_in_prop(prop_result, p)


def get_ip(_serial):
    s = 'adb -s "{serial}" shell ifconfig wlan0'
    s = s.format(serial=_serial)
    result = execute(s)
    if result == 'ifconfig: wlan0: No such device':
        pass
        # print('读取不到ip地址，adb shell ifconfig wlan0')
    else:
        ip_list = utils.find_ip(result)
        if len(ip_list):
            return ip_list[0]
        else:
            pass
            # print('没有匹配到ip ' + result)
    return ''


def get_mac_address(_serial):
    s = 'adb -s "{serial}" shell cat /sys/class/net/wlan0/address'
    s = s.format(serial=_serial)
    result = execute(s)
    # result = result.replace('\r', '').replace('\n', '')
    return result


def get_mem_info(_serial):
    s = 'adb -s "{serial}" shell cat /proc/meminfo'
    s = s.format(serial=_serial)
    result = execute(s)
    result = utils.fix_wrap(result)

    # 截取前面两行信息
    lines = result.split("\n")
    new_str = ''
    for i in range(len(lines)):
        if i > 1:
            break
        new_str += lines[i] + "\n"
    # 替换多余的换行
    if utils.is_windows:
        new_str = new_str.replace("\n\n", "\n")
    return new_str


def get_cpu_info(_serial):
    s = 'adb -s "{serial}" shell cat /proc/cpuinfo'
    s = s.format(serial=_serial)
    result = execute(s)
    # 替换多余的换行
    if utils.is_windows:
        result = result.replace("\n\n", "\n")
    return result


def am_force_stop(_serial, package):
    """停止应用"""
    s = 'adb -s {serial} shell am force-stop {package}'
    s = s.format(serial=_serial, package=package)
    execute(s)


def am_start(_serial, package):
    """通过包名启动应用"""
    s = 'adb -s {serial} shell monkey -p {package} -c android.intent.category.LAUNCHER 1'
    s = s.format(serial=_serial, package=package)
    execute(s)


def am_restart(_serial, package):
    """通过包名重启应用"""
    s = 'adb -s {serial} shell am force-stop {package} && \
    adb -s {serial} shell monkey -p {package} -c android.intent.category.LAUNCHER 1'
    s = s.format(serial=_serial, package=package)
    execute(s)


def am_start_activity(_serial, package_and_activity):
    """
    启动应用
    :param _serial:
    :param package_and_activity:
    :return:
    """
    _arr = package_and_activity.split('/')
    if len(_arr) < 3:
        s = 'adb -s {serial} shell monkey -p {package} -c android.intent.category.LAUNCHER 1'
        s = s.format(serial=_serial, package=_arr[0])
    else:
        s = 'adb -s {serial} shell am start {paa}'
        s = s.format(serial=_serial, paa=package_and_activity)
    print(s)
    execute(s)


def pm_clear(_serial, package):
    """清除应用的数据"""
    s = 'adb -s {serial} shell pm clear {package}'
    s = s.format(serial=_serial, package=package)
    s = execute(s)
    return s


def pm_path(_serial, package):
    """查看应用安装路径"""
    s = 'adb -s {serial} shell pm path {package}'
    s = s.format(serial=_serial, package=package)
    s = execute(s)

    # 成功的话提取出apk
    # 获取成功返回：package:/data/app/xx.apk=com.xx.xx
    # 获取失败返回空
    s = s.replace('\r', '').replace('\n', '')
    mark = 'package:'
    device_apk = s[len(mark):] if s.count(mark) else ""
    if device_apk:
        return device_apk
    else:
        print("找不到此应用 {}".format(package))
        return ''


def pull_apk(_serial, package):
    """下载apk"""
    device_apk = pm_path(_serial, package)
    if not device_apk:
        utils.showinfo("找不到此应用")
        return ''

    apk_name = '{package}-{now}.apk'.format(package=package, now=__get_now())
    save_dir = setting_atool.output_dir + os.sep + "apk"
    utils.make_dir(save_dir)

    pc_apk = save_dir + os.sep + apk_name
    s = 'adb -s {serial} pull "{device_apk}" {pc_apk}'
    s = s.format(serial=_serial, device_apk=device_apk, pc_apk=pc_apk)
    print(s)
    # 'adb: error: remote object \'/data/app/com.bbk.personal-2/base.apk\' does not exist'
    result = execute(s)

    if result.count("error"):
        url = 'http://app.mi.com/details?id=com.estrongs.android.pop'
        utils.clipboard_set(url)
        utils.showinfo("可能权限不够，可使用 es文件浏览器 执行备份应用操作！\napk下载链接已拷贝到剪贴板\n" + result)
        return ''

    return pc_apk


def ls_path(_serial, _path):
    """列出文件夹下的文件"""
    s = 'adb -s {serial} shell ls "{path}"'
    s = s.format(serial=_serial, path=_path)
    s = execute(s)
    s = utils.fix_wrap(s)
    return s


def __get_now():
    cur_time = time.localtime(time.time())
    return time.strftime('%Y%m%d%H%M%S', cur_time)


def send_keyevent(_serial, keycode):
    """发送键盘事件
    """
    s = 'adb -s {serial} shell input keyevent {keycode}'
    s = s.format(serial=_serial, keycode=keycode)
    execute(s)


def send_input(_serial, text):
    """发送键盘事件
    """
    s = 'adb -s {serial} shell input text "{text}"'.format(serial=_serial, text=text)
    execute(s)


def send_input_clipper_get(_serial):
    """ Broadcasting: Intent { act=clipper.get flg=0x400000 }"""
    """ Broadcast completed: result=-1, data="安卓剪贴板内容" """
    """ Broadcast completed: result=0" """
    # 检查clipper
    check_clipper(_serial)

    package = 'ca.zgrs.clipper'
    # 启动 clipper
    s = '{adb} -s {serial} shell monkey -p {package} -c android.intent.category.LAUNCHER 1 && \\'
    # 获取文本
    s += '{adb} -s {serial} shell am broadcast -a clipper.get && \\'
    # 退出 clipper
    s += '{adb} -s {serial} shell am force-stop {package}'
    s = utils.fix_cmd_wrap(s)
    s = s.format(adb=adb_path, serial=_serial, package=package)
    print(s)
    result = execute(s, True)
    if result.count("data="):
        data_str = result.split("data=").pop().strip('"')
        data_str = data_str.strip("\r\n")
        return data_str
    else:
        return ''


def send_input_clipper_set(_serial, text):
    # https://github.com/majido/clipper/releases
    # 检查clipper
    check_clipper(_serial)
    package = 'ca.zgrs.clipper'
    # 启动 clipper
    s = '{adb} -s {serial} shell monkey -p {package} -c android.intent.category.LAUNCHER 1 && \\'
    # 发送文本
    s += '{adb} -s {serial} shell am broadcast -a clipper.set -e text "{text}" && \\'
    # 退出 clipper
    s += '{adb} -s {serial} shell am force-stop {package}'
    s = utils.fix_cmd_wrap(s)
    s = s.format(adb=adb_path, serial=_serial, text=text, package=package)
    print(s)
    return utils.pipe(s)


def check_clipper(_serial):
    package = 'ca.zgrs.clipper'
    device_apk = pm_path(_serial, package)
    if not device_apk:
        # utils.showinfo("此设备未安装 Clipper")
        params = [_serial]
        s = "此设备未安装 Clipper，是否进行安装？"
        utils.alert(s, install_clipper, params)
        return False
    else:
        return True


def install_clipper(_serial):
    base64_apk = "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"
    save_dir = setting_atool.output_dir + os.sep + "apk"
    utils.make_dir(save_dir)
    url = save_dir + os.sep + "clipper-1.1.apk"
    utils.base64_img(base64_apk, url)
    if os.path.exists(url):
        install(_serial, url)
    else:
        show_msg("释放 CLipper-1.1.apk 失败！！！")


def disconnect(_serial):
    """断开wifi连接"""
    s = 'adb disconnect {serial}'.format(serial=_serial)
    execute(s)


def pm_list_f(_serial, is_ful=False):
    """应用列表
    """
    if is_ful:
        s = 'adb -s {serial} shell pm list packages -f'
    else:
        s = 'adb -s {serial} shell pm list packages -f -3'
    s = s.format(serial=_serial)
    print(s)
    result = execute(s)
    # 替换日志中多余的换行
    if utils.is_windows:
        result = result.replace("\n\n", "\n")
    return result


# def pm_list(_serial, is_ful=False):
#     """应用列表"""
#     """adb shell pm path <PACKAGE>"""
#     if is_ful:
#         s = 'adb -s {serial} shell pm list packages'
#     else:
#         s = 'adb -s {serial} shell pm list packages -3'
#     s = s.format(serial=_serial)
#     return execute(s)


def activity_current(_serial, only_package=False):
    if utils.is_windows:
        s = 'adb -s {serial} shell "dumpsys activity activities | grep mResumedActivity"'
    else:
        s = "adb -s {serial} shell dumpsys activity activities | grep mResumedActivity"
    s = s.format(serial=_serial)
    result = execute(s)
    result = result.replace("    mResumedActivity", "mResumedActivity")
    print(result)
    # mResumedActivity: ActivityRecord{fdca91c u0 com.teamviewer.quicksupport.market/com.
    # teamviewer.quicksupport.ui.QSActivity t740}
    if only_package:
        package = result.split("/")[0].split(" ").pop()
        print(package)
        return package
    return result


def stop_current(_serial):
    # mResumedActivity: ActivityRecord{8079d7e u0 com.cyanogenmod.trebuchet/com.android.launcher3.Launcher t42}
    s = activity_current(_serial)
    arr = s.split("/")
    if len(arr) > 1:
        package = arr[0].split(" ").pop()
        am_force_stop(_serial, package)


def run_current_again(_serial):
    # mResumedActivity: ActivityRecord{8079d7e u0 com.cyanogenmod.trebuchet/com.android.launcher3.Launcher t42}
    package = activity_current(_serial, True)
    if package:
        s = '{adb} -s {serial} shell am force-stop {package} && \\'
        s += '{adb} -s {serial} shell monkey -p {package} -c android.intent.category.LAUNCHER 1'
        s = utils.fix_cmd_wrap(s)
        s = s.format(adb=adb_path, serial=_serial, package=package)
        execute(s, True)
        show_msg("正在重启：{}".format(package))
    else:
        show_msg("找不到包名：{}".format(package))


def devices(has_log=False):
    """
    获得当前连接的 serial
    :param has_log
    :return: 词典 {
        "device": arr,
        "unauthorized": arr,
        "offline": arr
    }

    emulator-5554 device
    98AFBNH23DFF	unauthorized
    device
    offline
    unauthorized
    device
    no device
    sideload
    recovery
    """
    # serial='emulator-5554'
    result = execute('adb devices')
    if has_log:
        print(result)

    # 已连接
    p = re.compile('(.*)\tdevice', re.M | re.I)
    d_arr = p.findall(result)

    # 未授权
    p = re.compile('(.*)\tunauthorized', re.M | re.I)
    u_arr = p.findall(result)
    # 离线
    p = re.compile('(.*)\toffline', re.M | re.I)
    o_arr = p.findall(result)

    dc = {
        "device": d_arr,
        "unauthorized": u_arr,
        "offline": o_arr
    }
    return dc


def kill_server():
    """停止 adb 服务"""
    s = 'adb kill-server'
    return execute(s)


def connect(ip):
    """连接到指定 IP"""
    # 是否带有端口号
    has_port = False
    list1 = ip.split(":")
    if list1.pop() and len(list1):
        has_port = True

    if has_port:
        s = 'adb connect {}'.format(ip)
    else:
        s = 'adb connect {}'.format(ip + ":5555")
    result = execute(s)
    return result


def scrcpy(_serial, _title=''):
    """
    启动scrcpy
    """
    if _title:
        s = """scrcpy -s {serial} --window-title '{title}'""".format(
            serial=_serial, title=_title
        )
    else:
        s = "scrcpy -s {serial}".format(serial=_serial)
    print(s)
    result = execute(s, True)
    print(result)
    return result


def reg_one(search_str, reg):
    """返回匹配的第一个结果
    """
    m = re.search(reg, search_str, re.M | re.I)
    if m:
        tup = m.groups()
        if len(tup):
            return tup[0]
    return ''


def no_xuhangfu(_str):
    if utils.is_windows:
        return _str.replace(" && ^", "\n\r")
    else:
        return _str.replace(" && \\", "\n")


# 消息框倒计时对象
sched_obj = sched.scheduler(time.time, time.sleep)


def show_msg(msg):
    txt = utils.label_msg
    if txt is not None:
        txt['text'] = msg
        utils.tooltip(txt, msg)

        # 一定时间后清楚显示
        # if msg:
        #     sched_obj.enter(12, 0.2, clear_msg)
        #     t = threading.Thread(target=sched_obj.run)
        #     t.start()


def clear_msg():
    txt = utils.label_msg
    if txt is not None:
        try:
            txt['text'] = ''
            utils.tooltip(txt, '')
        except RuntimeError:
            print('RuntimeError: main thread is not in main loop')


_data_list = []
_win_remote = None
_data_last = None


def device_data_append(_data):
    """
    全局存储设备数据
    :param _data:
    :return:
    """
    for d in _data_list:
        if d.serial == _data.serial:
            return
    _data_list.append(_data)


def device_data_find(_serial):
    """
    查找设备数据
    :param _serial:
    :return: 如果找不到则返回 None
    """
    for d in _data_list:
        if d.serial == _serial:
            return d
    return None


def device_data_first():
    """
    获得第一条数据，如果没有连接则返回 None
    """
    if len(_data_list):
        return _data_list[0]
    else:
        return None


def show_remote(_data=None):
    """ 显示遥控器 """
    global _win_remote, _data_last
    con = _win_remote

    if con is None or con.top_win is None:
        _win_remote = win_remote.RemoteControl()
        con = _win_remote
    else:
        utils.lift_win(con.top_win)

    # 记忆上次打开，如果没有上次记录则默认显示第一个
    if _data is None:
        if con.has_data():
            return

        if _data_last is None:
            _data = device_data_first()
        else:
            _data = _data_last

    if _data is None:
        return

    _data_last = _data
    con.set_data(_data)


#####################################################
"""
aapt 辅助类

aapt 命令行工具
参数格式
    strings          Print the contents of the resource table string pool in the APK.  //查询字符串
    badging          Print the label and icon for the app declared in APK.
    permissions      Print the permissions from the APK.  查询权限
    resources        Print the resource table from the APK. 查询资源
    configurations   Print the configurations in the APK. 查询配置
    xmltree          Print the compiled xmls in the given assets. 以树形结构输出的xml信息
    xmlstrings       Print the strings of the given compiled xml assets. 输出xml文件中所有的字符串信息

CONST = aapt+' d {0} "'+apkFile+'" AndroidManifest.xml'
CONST.format("permissions")
CONST.format("xmlstrings")
CONST.format("xmltree")
"""

# aapt 路径
aapt_path = ""

# openssl 路径，主要用来获得签名的md5
openssl_path = ""


def execute_aapt(command_str):
    """执行 appt 命令
    """
    mark = 'aapt'
    if not command_str.startswith(mark + ' '):
        print('aapt命令行调用错误！\n' + command_str)
        return ''
    result = ''
    s = command_str.replace(mark, aapt_path, 1)
    if utils.is_mac:
        # 设置aapt为可执行
        if os.access(aapt_path, os.X_OK) is not True:
            os.chmod(aapt_path, stat.S_IRWXU)
        result = utils.execute(s)
    if utils.is_windows:
        result = utils.pipe(s, True)
        result = result.replace('\r\n', '\n')
    return result


def version():
    return execute_aapt('aapt v')


def dump(file_path, values='badging'):
    """
    aapt dump badging "{apk}"
    aapt dump permissions "{apk}"
    """
    return execute_aapt('aapt dump {0} "{1}"'.format(values, file_path))


def get_permissions(file_path):
    """获得 apk xmlstrings 信息"""
    return dump(file_path, 'permissions')


def ls(file_path):
    return execute_aapt('aapt l "{}"'.format(file_path))


#
# def packagecmd(file_path, command):
#     return execute_aapt('p ' + command + ' ' + file_path)
#
#
# def remove(file_path, files):
#     return execute_aapt('aapt r "{0}" "{1}"'.format(file_path, files))
#
#
# def add(file_path, files):
#     return execute_aapt('aapt a "{0}" "{1}"'.format(file_path, files))
#
#
# def crunch(resource, output_folder):
#     return execute_aapt('aapt c -S "{0}" -C "{1}"'.format(resource, output_folder))
#
#
# def single_crunch(input_file, output_file):
#     return execute_aapt('aapt s -i "{0}" -o "{1}"'.format(input_file, output_file))


def get_apk_info(file_path):
    result = dump(file_path)

    # 找出匹配的哪一行
    # reg = "package: name=\'(.*)\' versionCode=\'(.*)\' versionName=\'(.*)\' platformBuildVersionName=\'(.*)\'"
    # reg = "package: name=\'(.*)\' versionCode=\'(.*)\' versionName=\'(.*)\'"
    reg = "package: name=(.*)"
    groups = utils.reg_group(result, reg)
    # print(groups)
    reged = groups[0] if len(groups) else ''
    arr = reged.split(' ')
    v_ver_name = ""
    v_ver_code = ""
    v_package = ""
    if len(arr) > 0:
        v_package = arr.pop(0).strip("'")
        for item in arr:
            c_mark = 'versionCode='
            n_mark = 'versionName='
            if item.count(c_mark):
                vc = item.replace(c_mark, '')
                v_ver_code = vc.strip("'")
            elif item.count(n_mark):
                vn = item.replace(n_mark, '')
                v_ver_name = vn.strip("'")

    reg = 'application-label:\'(.*)\''
    v_app_name = reg_one(result, reg)

    reg = 'application: .* icon=\'(.*)\''
    icon_zip_path = reg_one(result, reg)
    """'res/mipmap-hdpi-v4/app_icon.png' banner='res/drawable-xhdpi-v4/app_banner.png'"""
    if icon_zip_path.count("='") and icon_zip_path.count("' "):
        str_arr = icon_zip_path.split("' ")
        if len(str_arr):
            icon_zip_path = str_arr[0]
            icon_zip_path = icon_zip_path.replace("\\", "")

    reg = 'targetSdkVersion:\'(.*)\''
    v = reg_one(result, reg)
    v_target_sdk = comment_str(v)

    reg = 'sdkVersion:\'(.*)\''
    v = reg_one(result, reg)
    v_min_sdk = comment_str(v)

    return {
        'package_name': v_package,
        'version_code': v_ver_code,
        'version_name': v_ver_name,
        'app_name': v_app_name,
        'icon_path': icon_zip_path,
        'target_sdk_version': v_target_sdk,
        'sdk_version': v_min_sdk,
    }


def get_package_and_activity(apk_or_result, is_file=True):
    """获得 apk 中的可执行的 activity
    """
    package = ''
    run_activity = ''
    result = dump(apk_or_result) if is_file else apk_or_result

    reg = "package: name=(.*) versionCode=.*"
    m = re.search(reg, result, re.M | re.I)
    if m:
        tup = m.groups()
        s = tup[0]
        package = s.split(' ')[0].strip("'")

    reg = "launchable-activity:.*name=(.*)"
    m = re.search(reg, result, re.M | re.I)
    if m:
        tup = m.groups()
        s = tup[0]
        run_activity = s.split(' ')[0].strip("'")

    return package + '/' + run_activity


def get_apk_xmlstrings(file_path):
    """获得 apk xmlstrings 信息
    """
    s = 'aapt dump xmltree "{}" AndroidManifest.xml'.format(file_path)
    return execute_aapt(s)


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


# def __process_rsa(rsa_file):
#     # from Crypto.PublicKey import RSA
#     # f = open(rsa_file,'r')
#     # key = RSA.importKey(f.read())
#     # print(key)
#
#     # import OpenSSL
#     # openssl
#     decrypt(rsa_file, '123')


# def decrypt(rsa_file, encoded_text):
#     """解密 未成功
#     """
#     import base64
#     from Crypto.PublicKey import RSA
#
#     f = open(rsa_file, 'r')
#     priv_key = RSA.importKey(f)
#
#     encrypted_text = base64.b64decode(encoded_text)
#     plain_text = priv_key.decrypt(encrypted_text)
#
#     return plain_text
#
#
# def reg_group(search_str, reg):
#     """匹配结果输出至 tup
#     """
#     m = re.search(reg, search_str, re.M | re.I)
#     if m:
#         return m.groups()
#     else:
#         return tuple([])


class Unzip:

    def __init__(self, zip_file):
        try:
            self.m_zip = zipfile.ZipFile(zip_file, 'r')
        except Exception as err:
            print("apk解析错误：" + str(err))
            self.is_zip = False
        else:
            self.is_zip = True

    def extract(self, inner_file, out_file):
        if not self.is_zip:
            return

        try:
            self.m_zip.extract(inner_file, out_file)
        except KeyError as err:
            print("释放资源出错：" + str(err.args))

    def find_rsa(self):
        if not self.is_zip:
            return ''
        # 可能是 META-INF/CERT.RSA
        # 也可能是 META-INF/xx.RSA
        reg = 'META-INF/(.*).RSA'
        f_str = reg.replace("(.*)", "{}")
        arr = self.m_zip.namelist()
        for n in arr:
            m = re.search(reg, n, re.M)
            if m:
                return f_str.format(m.group(1))
        return ''

    def destroy(self):
        if not self.is_zip:
            return
        self.m_zip.close()
        self.m_zip = None


if __name__ == "__main__":
    toolDir = os.path.expanduser('~/mytool/tool')
    adb_path = toolDir + os.sep + "adb"
    aapt_path = toolDir + os.sep + "aapt"

    p_ic = os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs/')
    apk_file = p_ic + 'hf/mytool/1.apk'
    p_desktop = os.path.expanduser('~/Desktop/')

    # unzip
    # m_zip = Unzip(apk_file)
    # rsa_name = m_zip.find_rsa()
    # m_zip.extract(rsa_name, p_desktop)
    # m_zip.destroy()

    # openssl 转成 ssl
    # import ssl
    # import OpenSSL
    # url = os.path.expanduser('~/Documents/安卓工具箱/AndroidTool/temp/META-INF/CERT.RSA')
    # pkcs7 = OpenSSL.crypto.PKCS7()
    #
    # url = os.path.expanduser('~/Documents/安卓工具箱/AndroidTool/temp/META-INF/CERT.pem')
    # x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(url, 'rb+').read())
    # x509.digest('md5')

    # ========================
    # print(dump(apk_file))
    print(get_apk_info(apk_file))
    print("========================")
    # print(get_permissions(apk_file))
