# -*- coding: utf-8 -*-

import base64
import uuid

import requests
from PIL import Image
from log_util import *
import os

image_temp_dir = "./temp/image"


# 转换图片为png
def convert_to_png(input_image_path, output_image_path, delete_temp_file=False):
    image = Image.open(input_image_path)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    image.save(output_image_path, 'PNG')
    if delete_temp_file:
        # 删除input_path
        os.remove(input_image_path)


# 判断指定目录下的图片是否存在，如果存在返回True，否则返回false
def image_exist(image_path):
    if os.path.exists(image_path):
        return True
    return False


# 根据url将图片读取为image对象
def read_image_for_url(image_url, image_dir=image_temp_dir, delete_temp_file=False):
    filename = get_image_path(image_url, image_dir)
    # 如果本地文件存在
    if os.path.exists(filename):
        info(f'[{filename}]本地文件存在，直接读取本地文件。')
        img_obj = Image.open(filename)
    else:
        # 否则需要下载
        download_image_for_url(image_url, filename)
        img_obj = Image.open(filename)
    if delete_temp_file:
        info(f'删除临时文件{filename}')
        os.remove(filename)
    return img_obj


# 根据url下载图片到指定目录
def get_image_path(image_url, image_dir=image_temp_dir):
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    url_name = os.path.basename(image_url)
    temp_path = os.path.join(image_dir, url_name)
    return temp_path


from urllib.parse import unquote, urlsplit


def extract_image_filename_from_url(url):
    """
    从图片URL中提取文件名及后缀。

    :param url: 图片的URL地址
    :return: 文件名包括后缀
    """
    # 使用urlsplit解析URL，然后用path属性获取路径部分
    path = urlsplit(url).path

    # 使用unquote解码路径中的百分号编码字符（如空格被编码为%20）
    decoded_path = unquote(path)

    # 分割路径得到文件名部分，[-1]表示取最后一部分，即文件名及后缀
    filename_with_extension = decoded_path.split('/')[-1]

    return filename_with_extension


def download_image_url(image_url, dirct_path):
    file_name = extract_image_filename_from_url(image_url)
    file_path = f"{dirct_path}/{str(uuid.uuid4())}/{file_name}"
    return download_image_for_url(image_url, file_path)


# 下载图片url到指定目录，默认connect_timeout连接超时时间为30秒，read_timeout响应超时时间为3分钟，3分钟未下载完毕，抛异常，结束程序
def download_image_for_url(image_url, file_path, connect_timeout=30, read_timeout=180):
    try:
        info(f'开始下载[{image_url}]图片数据到[{file_path}]目录...')
        # 获取目录路径
        directory = os.path.dirname(file_path)
        # 判断目录是否存在，如果不存在则创建
        if not os.path.exists(directory):
            os.makedirs(directory)
            debug(f"The directory '{directory}' has been created.")
        else:
            debug(f"The directory '{directory}' already exists.")
        image_data = requests.get(image_url, timeout=(connect_timeout, read_timeout)).content
        with open(file_path, 'wb') as f:  # 将下载的文件保存到本地目录
            f.write(image_data)
        info(f'[{file_path}]下载成功！')
        return True
    except Exception as e:
        # 处理响应超时异常
        error(f'异常！！！[{image_url}]图片下载失败，临时文件已清理，异常信息：{e}')
        # 删除临时文件
        os.remove(file_path)
        # 抛出一个异常
        err_message = f'[{image_url}]图片文件下载异常，请查看日志！'
        raise Exception(err_message)


# 此方法用于读取url，转成base64编码
def read_image_base64_for_url(image_url, image_dir=image_temp_dir, delete_temp_file=False):
    filename = get_image_path(image_url, image_dir)
    # 如果本地文件存在
    if os.path.exists(filename):
        info(f'[{filename}]本地文件存在，直接读取本地文件。')
    else:
        # 否则需要下载
        download_image_for_url(image_url, filename)
    # 将图像数据转换为 base64 字符串
    with open(filename, 'rb') as f:
        image_data = f.read()
    base64_string = base64.b64encode(image_data).decode('utf-8')
    if delete_temp_file:
        info(f'删除临时文件{filename}')
        os.remove(filename)
    return base64_string


if __name__ == '__main__':
    # convert_to_png用法示例
    # input_path = 'C:/Users/Ray/Pictures/Saved Pictures/01.jpg'
    # output_path = 'C:/Users/Ray/Pictures/Saved Pictures/02.png'
    # convert_to_png(input_path, output_path)
    # info('ok')

    # image_exist
    # info(image_exist("C:/Users/Ray/Pictures/Camera Roll/221.png"))

    # img = read_image_for_url("https://nlp-eb.cdn.bcebos.com/logo/icon-robin.png")
    # img = read_image_for_url("https://nlp-eb.cdn.bcebos.com/logo/icon-robin123.png")
    # info(img.size)
    print(download_image_url("https://applesay-meye.oss-cn-shanghai.aliyuncs.com/meye/051e8611c38dc05f7e1985c0b2ba35e6ac95a656a19cc1f6d77e92be6b7e7762.jpg", "d:/temp"))

    # base64_str = read_image_base64_for_url("https://nlp-eb.cdn.bcebos.com/logo/icon-robin.png")
    # info(base64_str)

