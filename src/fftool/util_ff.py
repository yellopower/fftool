# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path

import utils


class FF(object):
    """ffmpeg参数装饰器
    """
    input_file = ''
    input_files = []
    output_file = ''
    size = ''
    crf = 0
    fps = 0
    tune = ''
    video_codec = 'h264'
    video_bit_rate = '0'
    video_bit_rate_min = '0'
    video_bit_rate_max = '0'
    audio_codec = 'aac'
    audio_bit_rate = '128000'
    audio_sample_rate = '44100'
    audio_channel = '2'
    # 可以是字符串，可以是数字
    time_start = 0
    # time_start = '00:00:00'
    time_to = 0
    other_param = '-threads 8 -hide_banner'
    override = True
    __filter_complex = ''
    full_param = ''
    need_30m = False
    need_same_bit_rate = False

    def __init__(self, has_video=True, has_audio=True):
        """初始化
        Keyword Arguments:
            has_video {bool} -- 如果有，将自动设置部分视频参数 (default: {True})
            has_audio {bool} -- 如果有，将自动设置部分音频参数 (default: {True})
        """
        if has_video:
            self.crf = 18
            self.fps = 24

        if has_audio:
            self.audio_bit_rate = '128000'
            # self.other_param = '-ar 44100 -ac 2 ' + self.other_param

    def clear_default(self):
        self.video_codec = ''
        self.crf = 0
        self.fps = 0
        self.audio_bit_rate = ''
        self.other_param = '-hide_banner'

    def set_video_info(self, vdc, b_str=""):
        """
        :param vdc:
        :param b_str: 码率, 8m,以为这将输出视频的码率调整为8mb，为空是码率为自动
        :return:
        """
        # v_codec = "h264" # libx264
        # a_codec = 'aac'

        key = 'v_size'
        v_size = vdc[key] if key in vdc else "1920x1080"
        key = 'fps'
        fps = vdc[key] if key in vdc else "24"
        fps = float(fps)
        key = 'crf'
        crf = vdc[key] if key in vdc else "18"
        key = 'v_bit_rate'
        vb = vdc[key] if key in vdc else "8M"
        key = 'v_bit_rate_min'
        vb_min = vdc[key] if key in vdc else "8M"
        key = 'v_bit_rate_max'
        vb_max = vdc[key] if key in vdc else "9M"

        key = 'a_bit_rate'
        ab = vdc[key] if key in vdc else "128000"
        key = 'a_sample_rate'
        ar = vdc[key] if key in vdc else "44100"
        key = 'a_channels'
        ac = vdc[key] if key in vdc else "2"

        key = 'other_param'
        op = vdc[key] if key in vdc else '-threads 8 -hide_banner'
        key = 'other_param_add'
        re_op = vdc[key] if key in vdc else ''
        if re_op != '':
            op += " " + re_op

        if self.need_same_bit_rate:
            crf = 0
            vb_min = vb
            vb_max = vb
            op = op + " -max_muxing_queue_size 1024"

        # 特定码率处理
        # [target,min,max]
        b_dc = {
            "4m": ["4.5M", "4.5M", "5M"],
            "6m": ["6.5M", "6.5M", "7M"],
            "8m": ["8.5M", "8.5M", "9M"],
            "10m": ["10.5M", "10.5M", "11M"],
            "30m": ["30.5M", "30.5M", "31M"]
        }
        b_str = b_str.lower()
        if b_str in b_dc:
            b_arr = b_dc[b_str]
            crf = 0
            vb = b_arr[0]
            vb_min = b_arr[1]
            vb_max = b_arr[2]

        # self.video_codec = v_codec
        # self.audio_codec = a_codec
        self.size = v_size
        self.fps = fps
        self.crf = crf
        self.video_bit_rate = vb
        self.video_bit_rate_min = vb_min
        self.video_bit_rate_max = vb_max
        self.audio_bit_rate = ab
        self.audio_sample_rate = ar
        self.audio_channel = ac
        self.other_param = op

    def execute(self):
        """执行操作
        Returns:
            [type] -- 如果参数传入不正确 则返回 false
        """
        cstr = 'ffmpeg'
        if not self.full_param:
            if not self.input_file and len(self.input_files):
                print('input_file 不能为空')
                return False

            # 是否覆盖
            if self.override:
                cstr += ' -y'

            # 输入文件
            istr = ' -i "{}"'
            farr = [self.input_file] + self.input_files
            for f in farr:
                cstr += istr.format(f)

            # -ss
            ss = self.time_start
            if ss:
                if isinstance(ss, int) or isinstance(ss, float):
                    ss = ss * 1000
                    ss = int(ss)
                    ss = millisecond_to_str(ss)
                    cstr += ' -ss {}'.format(ss)

            # -to
            ss = self.time_to
            if ss:
                if isinstance(ss, int) or isinstance(ss, float):
                    ss = ss * 1000
                    ss = int(ss)
                    ss = millisecond_to_str(ss)
                    cstr += ' -to {}'.format(ss)

            # 30m fix
            if self.need_30m:
                self.video_codec = "mpeg2video"
                self.crf = 0
                self.video_bit_rate = "30720k"
                self.video_bit_rate_min = "30720k"
                self.video_bit_rate_max = "30720k"

                self.audio_codec = ""
                self.audio_bit_rate = "384k"
                self.audio_sample_rate = "48000"

                # "-timecode 00:00:00:00 " \
                add_param = "-bufsize 15360k " \
                            "-muxrate 31104k " \
                            "-profile:v 4 " \
                            "-level:v 4 " \
                            "-bf 2 " \
                            "-map_metadata -1"
                self.other_param = self.other_param + " " + add_param

            # 其它参数
            arr = [
                (self.video_codec, '-c:v {}'),
                (self.size, '-s {}'),
                (self.fps, '-r {}'),
                (self.__filter_complex, '-filter_complex {}'),
                (self.tune, '-tune {}'),

                (self.audio_codec, '-c:a {}'),
                (self.audio_bit_rate, '-b:a {}'),
                (self.audio_sample_rate, '-ar {}'),
                (self.audio_channel, '-ac {}'),

            ]
            if self.crf:
                arr.append([self.crf, '-crf {}'])
            else:
                arr.append([self.video_bit_rate, '-b:v {}'])
                arr.append([self.video_bit_rate_min, '-minrate {}'])
                arr.append([self.video_bit_rate_max, '-maxrate {}'])
                # arr.append([self.video_bit_rate_max, '-bufsize {}'])
                # arr.append([self.video_bit_rate_max, '-muxrate {}'])

            arr.append([self.other_param, '{}'])
            arr.append([self.output_file, '"{}"'])

            for tup in arr:
                key = tup[0]
                if key:
                    add_str = tup[1]
                    add_str = add_str.format(key)
                    cstr += ' ' + add_str

            # print('参数拼接ok:',cstr)
        else:
            cstr = self.full_param
        execute(cstr)
        return True

    # 设置水印
    def set_overlay(self, png_arr, size_arr, limit_time=[], pos_arr=[]):
        fstr = ''
        for i in range(len(png_arr)):
            size = size_arr[i]

            if i < len(pos_arr):
                p = pos_arr[i]
                arr = p.split(':')
                x = arr[0]
                y = arr[1]
            else:
                x = 0
                y = 0

            if i < len(limit_time):
                t = limit_time[i]
            else:
                t = 0

            if t:
                f1 = ",scale={0},overlay=x='if(lte(t,{3}),{1},NAN)':{2}"
                fstr += f1.format(size, x, y, t)
            else:
                f2 = ",scale={0},overlay={1}:{2}"
                fstr += f2.format(size, x, y)

        fstr = fstr.strip(',')
        self.__filter_complex = '"{}"'.format(fstr)
        self.input_files = png_arr.copy()

    def get_overlay(self, _x=0, _y=0):
        s = 'overlay={0}:{1}'
        return s.format(_x, _y)

    def get_overlay_with_size(self, _size, _x=0, _y=0):
        s = 'scale={0},overlay={1}:{2}'
        return s.format(_size, _x, _y)

    def destroy(self):
        self.input_file = None
        self.input_files.clear()
        self.output_file = None
        self.size = None
        self.crf = None
        self.fps = None
        self.tune = None
        self.video_codec = None
        self.video_bit_rate = None
        self.video_bit_rate_min = None
        self.video_bit_rate_max = None
        self.audio_codec = None
        self.audio_bit_rate = None
        self.audio_sample_rate = None
        self.audio_channel = None
        self.time_start = None
        self.time_to = None
        self.other_param = None
        self.override = None
        self.__filter_complex = None
        self.full_param = None


#####################################################
"""ffmpeg 辅助类
"""
__pyParent = os.path.dirname(__file__) + os.sep

# ffmpeg 路径
ffmpeg_path = ''
sep = os.sep


def init_ffmpeg():
    """
    ffmpeg 初始化，设定 ffmpeg 工具地址
        :param _parent: 脚本当前目录，可选参数，如果传入将优先使用
    """
    pp = str(Path(__pyParent).parent)
    ff = ''
    if utils.is_windows:
        ff = 'D:\\FFmpeg'
        ff_c = 'C:\\FFmpeg'
        arr = [
            __pyParent,
            __pyParent + sep + "shared",  # 父目录共享文件夹
            pp + sep + "shared",  # 父目录共享文件夹
            ff,  # 环境变量目录
            ff_c,
            "{}/_pack/win".format(pp),  # 打包地址
            ff + sep + "shared"  # 环境变量目录 shared目录
        ]
        tool_path = ff
        ff = __find_file(arr, "ffmpeg.exe")

        # c_driver_path = "C:\\FFmpeg\\ffmpeg.exe"
        # d_driver_path = "D:\\FFmpeg\\ffmpeg.exe"
        # parent_path = __pyParent + "ffmpeg.exe"
        #
        # if os.path.exists(d_driver_path):
        #     ff = d_driver_path
        # elif os.path.exists(c_driver_path):
        #     ff = c_driver_path
        # elif os.path.exists(parent_path):
        #     ff = parent_path
    elif utils.is_mac:
        tool_path = os.path.expanduser('~/mytool/tool/ffmpeg')
        parent_path = __pyParent + "ffmpeg"

        # app中本脚本位于 转码工具箱.app/Contents/Resources/lib/python37.zip/
        gParent = Path(__pyParent).parent
        gParent = Path(gParent).parent
        app_path = gParent / "ffmpeg"
        app_path = str(app_path)

        if os.path.exists(app_path):
            ff = app_path
        elif os.path.exists(parent_path):
            ff = parent_path
        elif os.path.exists(tool_path):
            ff = tool_path

    if not ff:
        print("找不到   " + tool_path)
        print("请检查对应文件，然后重新执行本脚本！！！")
    else:
        print("ffmpeg：{}".format(ff))
        # 检查 ffprobe
        if utils.is_windows:
            _ffprobe = Path(ff).with_name('ffprobe.exe')
        elif utils.is_mac:
            _ffprobe = Path(ff).with_name('ffprobe')
        _ffprobe = str(_ffprobe)

        if not os.path.exists(_ffprobe):
            print("找不到   " + _ffprobe)
            print("请检查对应文件，然后重新执行本脚本！！！")

    return ff


def __find_file(dir_list, file_name):
    """在多个目录下查找文件，返回第一个匹配"""
    for p in dir_list:
        f = p + os.sep + file_name
        if os.path.exists(f):
            return f
    return ""


def execute(command_str):
    """执行 ffmpeg 命令
    例如：ffmpeg -i input.mp4 output.mp4
    """
    s = ffmpeg_path + command_str[6:len(command_str)]
    print("执行命令行:", s)
    utils.execute(s)


def concat(files, out_mp4, concat_txt):
    """指定合并操作
    Arguments:
        concat_txt {[type]} -- concat.txt
        out_mp4 {[type]} -- 输出的mp4路径
    """
    # 创建 concat.txt
    __create_concat_txt(files, concat_txt)

    # concat 一般参数
    s = '''ffmpeg -y -f concat -safe 0 -i "{0}" -c copy "{1}"'''
    s = s.format(concat_txt, out_mp4)
    execute(s)


def merge_image(input_file1, input_file2, out_file, size):
    """2图并1图
    Arguments:
        input_file1 {[type]} -- [description]
        input_file2 {[type]} -- [description]
        out_file {[type]} -- [description]
        size {[type]} -- [description]
    """
    s = '''ffmpeg -y -i "{0}" -i "{1}" -filter_complex overlay=0:0 -s {2} "{3}"'''
    s = s.format(input_file1, input_file2, size, out_file)
    # print("mergeStr", mergeStr)
    execute(s)


def __create_concat_txt(files, subTxt):
    """生成 concat.txt

    Arguments:
        files {[string]} --  要合并的文件地址
        subTxt {[type]} --  concat.txt 的名称
    """
    subs = []
    sub = "file '{0}'\n"
    for f in files:
        subs.append(sub.format(f))
    utils.write_txt(subTxt, subs)


# 检测片头和水印环节中 出现的音画不同步的情况
def check_vcomplex_nosync(out_file):
    outdc = ffprobe_info(out_file)

    hasTag = False
    duration_video = 0.0
    duration_audio = 0.0
    duration_total = 0.0
    for tdc in outdc['streams']:
        codec_type = tdc['codec_type']

        # 视频部分参数
        if codec_type == 'video':
            duration_video = tdc['duration']  # "duration": "6.976000",

        # 音频部分参数
        if codec_type == 'audio':
            duration_audio = tdc['duration']  # "duration": "6.976000",

            key = 'tags'
            if key in tdc:
                tag_sub_json = tdc[key]
                key2 = 'handler_name'
                if key2 in tag_sub_json:
                    if tag_sub_json[key2] == "#Mainconcept MP4 Sound Media Handler":
                        hasTag = True
                        break
    if not hasTag:
        return '该视频似乎没被本工具处理过'

    tdc = outdc['format']
    duration_total = tdc['duration']  # "duration": "6.976000",
    # duration_video = float( duration_video )

    duration_audio = float(duration_audio)
    duration_total = float(duration_total)
    difference_second = duration_total - duration_audio
    difference_second = round(difference_second, 2)
    if difference_second > 5:
        ss = '不同步（音频少了{0}秒）'.format(difference_second)
    elif difference_second > 2:
        ss = '可能他不同步（音频少了{0}秒）'.format(difference_second)
    else:
        ss = '正常（相差{0}秒）'.format(difference_second)

    return ss


# 检测片头和水印环节中 出现的音画不同步的情况
def check_double_time(out_file):
    outdc = ffprobe_info(out_file)
    ss = "--"
    for tdc in outdc['streams']:
        codec_type = tdc['codec_type']

        # 视频部分参数
        if codec_type == 'video':
            key = 'profile'     # "profile": "Constrained Baseline",
            mark = "Constrained Baseline"
            if key in tdc and tdc[key].count(mark):
                ss = "有双倍时长问题"
                break

        # 音频部分参数
        if codec_type == 'audio':
            duration_audio = tdc['duration']  # "duration": "6.976000",

            key = 'tags'
            if key in tdc:
                tag_sub_json = tdc[key]
                key2 = 'handler_name'
                if key2 in tag_sub_json:
                    if tag_sub_json[key2] == "#Mainconcept MP4 Sound Media Handler":
                        ss += "请复查音画同步问题"
                        break
    return ss


def get_video_info(_mp4, has_log=False):
    """获得视频信息 返回一个词典
        :param _mp4:  视频文件地址
        :param hasLog=False:
    """
    _ffmpeg = ffmpeg_path
    infoStr = """
        *** 视频信息 ****
        文件：
            \t文件名：{file_name}
            \t路径：{file_parent}
        简述：
            \t时长：{duration}
            \t开始：{start}
            \t码率：{file_bit_rate} kb/s
        视频：
            \t编码：{v_codec}
            \t数据格式：{VDF}
            \t尺寸：{v_size}
            \t比特率：{v_bit_rate} kb/s
            \t帧率：{fps} fps
        音频：
            \t编码：{a_codec}
            \t采样：{a_sample_rate} Hz
            \t声道：{a_channels}
            \t码率：{a_bit_rate} kb/s
        *********
    """

    seq = ('file_name', 'file_parent', 'file_type',
           'duration', 'start', 'file_bit_rate',
           'v_codec', 'VDF', 'v_size', 'v_bit_rate', 'fps',
           'a_codec', 'a_sample_rate', 'a_channels', 'a_bit_rate',
           'v_profile', 'v_profile_level',
           'a_profile'
           )
    dc = dict.fromkeys(seq, "")

    # 文件名
    p = Path(_mp4)
    dc["file_parent"] = _mp4
    dc["file_name"] = str(p.name)
    dc["file_type"] = str(p.suffix)

    info_dc = ffprobe_info(_mp4)
    for tdc in info_dc['streams']:
        codec_type = tdc['codec_type']
        # 视频部分参数
        if codec_type == 'video':
            dc["v_profile"] = tdc['profile'] if 'profile' in tdc else ''  # "profile": "High",
            dc["v_profile_level"] = tdc['level']  # "level": 50,
            dc["v_codec"] = tdc['codec_name']  # "codec_name": "h264",
            dc["VDF"] = tdc['pix_fmt']  # "pix_fmt": "yuv420p",

            if 'bit_rate' in tdc:
                dc["v_bit_rate"] = tdc['bit_rate']  # "bit_rate": "3085817",
            else:
                dc["v_bit_rate"] = "0"

            # 分辨率
            w = tdc['width']  # "width": 1920,
            h = tdc['height']  # "height": 1080,
            dc["v_size"] = "{0}x{1}".format(w, h)

            # fps
            arr = tdc['r_frame_rate'].split('/')  # "r_frame_rate": "30000/1001",
            n1 = float(arr[0])
            n2 = float(arr[1])
            fps = n1 / n2
            dc["fps"] = str(fps)

        # 音频部分参数
        elif codec_type == 'audio':
            key = 'profile'
            if key in tdc:
                dc["a_profile"] = tdc[key]  # "profile": "LC",
            dc["a_codec"] = tdc['codec_name']  # "codec_name": "aac",
            dc["a_sample_rate"] = tdc['sample_rate']  # "sample_rate": "48000",
            dc["a_channels"] = str(tdc['channels'])  # "channels": 2,
            dc["a_bit_rate"] = tdc['bit_rate']  # "bit_rate": "143393"

    tdc = info_dc['format']
    dc["duration"] = tdc["duration"]  # "duration": "6.976000",
    dc["start"] = tdc["start_time"]  # "start_time": "0.000000",
    dc["file_bit_rate"] = tdc["bit_rate"]  # "bit_rate": "2969731",

    # 旧办法 ############################################################3
    # 通过 ffmpeg -i input.mp4 获得视频信息 再通过正则匹配信息
    # 实践中容易出现正则匹配到错误信息的情况，有时视频的参数情况比正常的要复杂的多
    # # Input #0, mov,mp4,m4a,3gp,3g2,mj2, from '020020998.mp4':
    # # Duration: 00: 02: 09.00, start: 0.000000, bitrate: 249 kb/s
    # # Stream #0:0(eng): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 640x360 [SAR 1:1 DAR 16:9], 147 kb/s, 15 fps, 15 tbr, 15360 tbn, 30 tbc (default)
    # # Stream #0:1(eng): Video: h264 (Baseline) (avc1 / 0x31637661), yuv420p(tv, unknown/bt470bg/unknown), 720x1280, 364 kb/s, SAR 1:1 DAR 9:16, 8.28 fps, 90k tbr, 90k tbn, 180k tbc (default)
    # # Stream #0:1(eng): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 98 kb/s (default)
    # mStr = exc
    # # regexDuration = "(.*) Duration: (.*?), start: (.*?), bitrate: (\\d*) kb\\/s"
    # # regexVideo = "(.*) Video: (.*?), (.*?), (.*?)[,\\s].*, (.*?) kb/s, (.*?) fps"
    # # regexAudio = "(.*) Audio: (.*?), (\\d*) Hz, (.*?), (.*?), (.*?) kb/s"

    # regexDuration = "Duration: (.*?), start: (.*?), bitrate: (\\d*) kb\\/s"
    # regexVideo = "Video: (.*?), (.*?), (.*?)[,\\s].*, (.*?) kb/s, (.*?) fps"
    # regexAudio = "Audio: (.*?), (\\d*) Hz, (.*?), (.*?), (.*?) kb/s"

    # # 时长信息
    # m = re.search(regexDuration, mStr, re.M|re.I)
    # if m:
    #     dc["duration"] = m.group(1)
    #     dc["start"] = m.group(2)
    #     dc["file_bit_rate"] = m.group(3)

    # # 视频信息
    # m = re.search(regexVideo, mStr, re.M|re.I)
    # if m:
    #     dc["v_codec"] = m.group(1)
    #     dc["VDF"] = m.group(2)
    #     dc["v_size"] = m.group(3)
    #     dc["v_bit_rate"] = m.group(4)
    #     dc["fps"] = m.group(5)

    # # 音频信息
    # m = re.search(regexAudio, mStr, re.M|re.I)
    # if m:
    #     dc["a_codec"] = m.group(1)
    #     dc["a_sample_rate"] = m.group(2)
    #     dc["a_channels"] = m.group(3)
    #     dc["a_bit_rate"] = m.group(5)
    # 旧办法 ############################################################3

    if has_log:
        print(infoStr.format(**dc))
    return dc


def ffprobe_info(_mp4):
    """调用 ffprobe 获得视频信息json
     参数:
        _mp4 {[ string]} -- 完整的文件路径
    返回:
        [词典] -- [description]
    """
    os.path.exists(_mp4)
    if not Path(_mp4).exists():
        print('此文件不存在', _mp4)
        return []

    _ffprobe = Path(ffmpeg_path).with_name('ffprobe')
    _ffprobe = str(_ffprobe)

    pStr = _ffprobe + ' -v quiet -print_format json -show_format -show_streams "%s"' % (_mp4)
    exc = utils.execute(pStr)
    if utils.is_windows:
        exc = exc.decode('utf-8')
    try:
        json_dc = json.loads(str(exc))
    except json.JSONDecodeError as e:
        print('获取视频信息失败! ', e)
        return []
    return json_dc


def get_overlay(png_arr, size_arr, limit_time=[], pos_arr=[], is_full=False):
    """
    :param png_arr:
    :param size_arr: 水印图片的尺寸
    :param limit_time: 限制时间
    :param pos_arr: 位置
    :param is_full:
    :return:
    """
    f_str = ''
    for i in range(len(png_arr)):
        size = size_arr[i]

        if i < len(pos_arr):
            p = pos_arr[i]
            arr = p.split(':')
            x = arr[0]
            y = arr[1]
        else:
            x = 0
            y = 0

        if i < len(limit_time):
            t = limit_time[i]
        else:
            t = 0

        if t:
            f1 = ",scale={0},overlay=x='if(lte(t,{3}),{1},NAN)':{2}"
            f_str += f1.format(size, x, y, t)
        else:
            f2 = ",scale={0},overlay={1}:{2}"
            f_str += f2.format(size, x, y)

    f_str = f_str.strip(',')
    if is_full:
        f_str = '-filter_complex "{}"'.format(f_str)
    else:
        f_str = '"{}"'.format(f_str)
    return f_str

def compare_video(fileA, fileB):
    """检查视频参数是否一致
    Returns:
        [type] -- [description]
    """
    dca = get_video_info(fileA, False)
    dcb = get_video_info(fileB, False)
    # print(dca)
    # print(dcb)
    # 视频信息
    # # 音频比特率相差在10以内，判断为相同
    # tolerate = 10
    # key = 'a_bit_rate'
    # stra = dca[key].lower().replace('k','')
    # strb = dcb[key].lower().replace('k','')
    # a = math.ceil( float(stra) )
    # b = math.ceil( float(strb) )
    # c = a-b
    # if c>=0 and c<tolerate:
    #     isSame = True

    # ,'v_profile','v_profile_level'
    checks = ('v_codec', 'v_profile',
              'v_size', 'fps',
              'a_codec', 'a_profile', 'a_sample_rate', 'a_channels')
    count = 0
    for key in checks:
        if dca[key] == dcb[key]:
            count += 1

    if count < len(checks):
        return False
    else:
        return True


def check_bitrate(out_file):
    dc = get_video_info(out_file)
    return dc['v_bit_rate']


def str_to_millisecond(ss):
    """时间字符串转成毫秒值
    00:00:43.89 ==> 43089
    """
    ss = str(ss)
    dot_ms = ''
    if ss.count('.'):
        a = ss.split('.')
        ss = a[0]
        dot_ms = int(a[1])
        dot_ms = min(dot_ms, 999)

    a = ss.split(':')
    h = int(a[0])
    m = int(a[1])
    m = min(m, 59)
    s = int(a[2])
    s = min(s, 59)

    ms = (h * 60 * 60 + m * 60 + s) * 1000
    if dot_ms:
        ms = ms + dot_ms
    return ms


def millisecond_to_str(millisecond=1000):
    """毫秒值 转成 时间字符串
    43089 ==> 00:00:43.89
    """
    ms = millisecond % 1000
    ms = str(ms % 1000).zfill(3)

    import math
    s = math.floor(millisecond / 1000)
    h = math.floor(s / (60 * 60))
    m = math.floor(s / 60)
    h = str(h).zfill(2)
    m = str(m % 60).zfill(2)
    s = str(s % 60).zfill(2)

    if ms == '00':
        f = '{0}:{1}:{2}'.format(h, m, s)
    else:
        f = '{0}:{1}:{2}.{3}'.format(h, m, s, ms)
    return f


def millisecond_to_stand(millisecond=1000):
    """毫秒值 转成 时间字符串
    43089 ==> 00:00:43
    """
    s = millisecond_to_str(millisecond)
    s = s.split('.')[0]
    return s


def create_obj():
    return FF()


if __name__ == "__main__":
    # ___ffmpeg = os.path.expanduser('~/mytool/tool/ffmpeg')
    # # icloud = '~/Library/Mobile Documents/com~apple~CloudDocs/'
    # # icloud = os.path.expanduser(icloud)

    # # 初始化 ffmpeg 并持有
    ffmpeg_path = init_ffmpeg()
    if utils.is_windows:
        url = 'P:\\Test\\pt.mp4'
    else:
        url = os.path.expanduser('/Projects/Test/pt.mp4')
    dc = get_video_info(url)
    print(dc)
