import logging
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from utils.captcha.captcha import captcha
from django.views import View
from django_redis import get_redis_connection

from . import constants
from users import models
# Create your views here.

# 生成日志器
logger = logging.getLogger('django')

class ImageCode(View):
    """
    /image_codes/<uuid:image_code_id>/
    """
    def get(self, request, image_code_id):
        """

        :param request:
        :param image_code_id: 获取唯一值用作redis中的key 储存验证码
        :return:
        """
        # 用拆包的方式将验证码和验证图片拆分（‘SUMY’， b‘图片二进制数据’）
        text, image = captcha.generate_captcha()

        # 连接redis数据库， 指定settings中用哪个redis库
        con_redis = get_redis_connection(alias='verify_codes')
        # 生成唯一值img_key
        img_key = f'img_{image_code_id}'
        # 调用setex方法， 将key value存入redis， 第一个参数放key 第二个参数为过期时间
        # 第三个参数为value 过期时间这种常量的值一般找个单独文件存放
        con_redis.setex(img_key, constants.IMAGE_CODE_REDIS_EXPIRSE, text)
        # 打印日志到console
        logger.info(f'image_code: {text}')
        # 返回数据 如果是二进制数据就用content=b'' ， 指定类型为image， 这样浏览器才能准确解析
        return HttpResponse(content=image, content_type='image/jpg')


class ChickUsernameView(View):
    """
    usernames/(?P<username>\w{5,20})/
    """
    def get(self, request, username):
        count = models.Users.objects.filter(username=username).count()
        data = {
            'count': count,
            'username': username
        }
        return JsonResponse({'data': data})