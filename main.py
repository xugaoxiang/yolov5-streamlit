from io import StringIO
import streamlit as st
import time
from detect import detect
import os
import sys
import argparse
from PIL import Image
import PIL


def _all_subdirs_of(b='.'):
    '''
        Returns all sub-directories in a specific Path
    '''
    result = []
    for d in os.listdir(b):
        bd = os.path.join(b, d)
        if os.path.isdir(bd):
            result.append(bd)
    return result


def _get_latest_folder():
    '''
        Returns the latest folder in a runs\detect
    '''
    return max(_all_subdirs_of(os.path.join('runs', 'detect')), key=os.path.getmtime)


def _save_uploadedfile(uploadedfile):
    '''
        Saves uploaded videos to disk.
    '''
    with open(os.path.join("data", "videos", uploadedfile.name), "wb") as f:
        f.write(uploadedfile.getbuffer())


def _format_func(option):
    '''
        Format function for select Key/Value implementation.
    '''
    return SOURCES[option]


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str,
                        default='weights/yolov5s.pt', help='model.pt path(s)')
    # file/folder, 0 for webcam
    parser.add_argument('--source', type=str,
                        default='data/images', help='source')
    parser.add_argument('--img-size', type=int, default=640,
                        help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float,
                        default=0.25, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float,
                        default=0.45, help='IOU threshold for NMS')
    parser.add_argument('--device', default='',
                        help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true',
                        help='display results')
    parser.add_argument('--save-txt', action='store_true',
                        help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true',
                        help='save confidences in --save-txt labels')
    parser.add_argument('--nosave', action='store_true',
                        help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int,
                        help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true',
                        help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true',
                        help='augmented inference')
    parser.add_argument('--update', action='store_true',
                        help='update all models')
    parser.add_argument('--project', default='runs/detect',
                        help='save results to project/name')
    parser.add_argument('--name', default='exp',
                        help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true',
                        help='existing project/name ok, do not increment')
    opt = parser.parse_args()
    print(opt)

    SOURCES = {0: "图片检测", 1: "视频检测"}

    inferenceSource = str(st.sidebar.selectbox(
        '选择输入', options=list(SOURCES.keys()), format_func=_format_func))

    if inferenceSource == '0':
        uploaded_file = st.sidebar.file_uploader(
            "上传图片", type=['png', 'jpeg', 'jpg'])
        if uploaded_file is not None:
            is_valid = True
            with st.spinner(text='资源加载中...'):
                st.sidebar.image(uploaded_file)
                picture = Image.open(uploaded_file)
                picture = picture.save(f'data/images/{uploaded_file.name}')
                opt.source = f'data/images/{uploaded_file.name}'
        else:
            is_valid = False
    else:
        uploaded_file = st.sidebar.file_uploader("上传视频", type=['mp4'])
        if uploaded_file is not None:
            is_valid = True
            with st.spinner(text='资源加载中...'):
                st.sidebar.video(uploaded_file)
                _save_uploadedfile(uploaded_file)
                opt.source = f'data/videos/{uploaded_file.name}'
        else:
            is_valid = False

    st.title('YOLOv5 Streamlit App')

    inferenceButton = st.empty()

    if is_valid:
        if inferenceButton.button('开始检测'):
            detect(opt)

            if inferenceSource != '0':
                st.warning(
                    'Video playback not available on deployed version due to licensing restrictions. ')
                with st.spinner(text='Preparing Video'):
                    for vid in os.listdir(_get_latest_folder()):
                        st.video(f'{_get_latest_folder()}/{vid}')
                    st.balloons()
            else:
                with st.spinner(text='Preparing Images'):
                    for img in os.listdir(_get_latest_folder()):
                        st.image(f'{_get_latest_folder()}/{img}')
                    st.balloons()
