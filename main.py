# Ref: https://wiki.archlinux.org/title/FFmpeg#VA-API
# command = "ffmpeg -i input.mp4 -vaapi_device /dev/dri/renderD128 -codec:v hevc_vaapi " \
#           "-filter:v \"subtitles=subtitle.srt,format=nv12|vaapi,hwupload\" output.mp4"
import os.path
import sys
import json


def load_tasks():
    with open('tasks.json', encoding='UTF-8') as f:
        tasks = json.loads(f.read())
    return tasks


def generate(task):
    _input = os.path.realpath(task['input'])
    _output_format = task['output-format'] if 'output-format' in task else 'mp4'
    _subtitle = os.path.realpath(task['subtitle'])
    _vcodec = task['vcodec'] if 'vcodec' in task else 'h264'
    _vfilter = task['vfilter'] if 'vfilter' in task else None
    _acodec = task['acodec'] if 'acodec' in task else 'copy'

    # Fix a bug on Windows, Ref: https://www.bilibili.com/read/cv11490614/
    if sys.platform.startswith('win'):
        replacements = {  # Ordered
            '\\': '\\\\',
            ':': '\\:'
        }
        for old, new in replacements.items():
            _subtitle = _subtitle.replace(old, new)

    ipt = "-i \"{}\"".format(_input)
    vc = "-codec:v {}".format(_vcodec)
    ac = "-codec:a {}".format(_acodec)
    opt = "\"{}.{}\"".format(os.path.splitext(os.path.split(_input)[1])[0], _output_format)

    vaapi_device = ''
    if _vcodec.find('vaapi') != -1:
        vaapi_device = '-vaapi_device /dev/dri/renderD128'

    sub_type = os.path.splitext(_subtitle)[1][1:]
    if _vfilter is not None:
        if sub_type == 'srt':
            vf = "-filter:v \"subtitles=\'{}\',{}\"".format(_subtitle, _vfilter)
        elif sub_type == 'ass':
            vf = "-filter:v \"ass=\'{}\',{}\"".format(_subtitle, _vfilter)
    else:
        if sub_type == 'srt':
            vf = "-filter:v \"subtitles=\'{}\'\"".format(_subtitle)
        elif sub_type == 'ass':
            vf = "-filter:v \"ass=\'{}\'\"".format(_subtitle)

    if vaapi_device == '':
        command = "ffmpeg {} {} {} {} {}".format(ipt, vc, ac, vf, opt)
    else:
        command = "ffmpeg {} {} {} {} {} {}".format(ipt, vaapi_device, vc, ac, vf, opt)
    return command


def main():
    tasks = load_tasks()['tasks']
    for task in tasks:
        print(generate(task))


if __name__ == '__main__':
    main()
