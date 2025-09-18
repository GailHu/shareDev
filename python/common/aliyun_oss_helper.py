# -*- coding: utf-8 -*-

import oss2
from PIL import Image


# 阿里云操作oss
def resize_image(image_path, new_width, new_height):
    with Image.open(image_path) as img:
        img.thumbnail((new_width, new_height))
        width, height = img.size
    return width, height


class OssHelper:
    def __init__(self, access_key_id, access_key_secret,
                 endpoint, bucket_name):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        # 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        # yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
        # 填写Bucket名称。
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)

    # 填写目录名称，目录需以正斜线结尾。
    def mkdir(self, dir_name: str):
        self.bucket.put_object(dir_name, '')

    # 上传文件
    def upload_file(self, oss_key, file):
        self.bucket.put_object(oss_key, file)
        return f"https://{self.bucket_name}.{self.endpoint}/{oss_key}"

    # 上传文件
    def upload(self, oss_key, file_path):
        with open(file_path, 'rb') as f:
            self.upload_file(oss_key, f)
            return f"https://{self.bucket_name}.{self.endpoint}/{oss_key}"

    def upload_image(self, oss_key, image_path, is_avif=True):
        url = self.upload(oss_key, image_path)
        new_short_side = 256
        width, height = resize_image(image_path, new_short_side, new_short_side)
        if is_avif:
            return f"{url}?x-oss-process=image%2Fresize%2Cl_{width}%2Ch_{height}%2Fformat%2Cavif"
        return url

    # 判断文件或目录是否存在
    def object_exists(self, object_name):
        return self.bucket.object_exists(object_name)

    # ---------------以下是扩展方法---------------------
    # 创建绘图目录
    def mkdir_draw(self, dir_name: str):
        self.bucket.put_object(f'applesay_sd/{dir_name}/', '')
