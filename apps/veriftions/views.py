import json
import random
import string
import logging

from django.views import View
from django.shortcuts import render
from utils.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse, JsonResponse

from . import constants
from users import models
from .forms import SmsCodeForm
from utils.yuntongxun import sms
from utils.json_func import to_json_data
from utils.res_code import Code, error_map
# Create your views here.

# 生成日志器
logger = logging.getLogger('django')

class CheckUsernameView(View):
    """
    # 验证用户名是否存在
    /usernames/(?P<username>\w{5,20})/
    # 前端发送ajax请求，携带username参数，后台判断数据库中username存不存在
    """
    def get(self, request, username):
        # 统计一下数据库中用户名个数验证是否唯一
        count = models.Users.objects.filter(username=username).count()
        data = {
            'count': count,
            'username': username
        }
        return to_json_data(data=data)


class CheckMobileView(View):
    """
    验证手机号
    /mobiles/(?P<mobile>1[3-9]\d{9})/
    # 前端发送ajax请求，携带手机号参数，后台判断数据库中mobile存不存在
    """
    def get(self, request, mobile):
        # 统计mobile个数验证唯一
        count = models.Users.objects.filter(mobile=mobile).count()
        data = {
            'count': count,
            'mobile': mobile
        }
        return to_json_data(data=data)


class ImageCode(View):
    """
    返回图片验证码  图片src=“/image_codes/<uuid:image_code_id>/” 可以访问到后台
    自动发送请求，访问后台，获取图片
    /image_codes/<uuid:image_code_id>/
    # 前端发送ajax请求，携带uuid唯一值（js中生成uuid）,后台调用生成验证码方法，生成验证码和图片
    # 连接redis，生成一个唯一key，将验证码文本当做value存到redis
    # 返回图片二进制，指定类型，展示到前端的图片验证码中
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


class SmsCodeView(View):
    """
    验证发送短信验证码
    /sms_codes/
    # 前端ajax传来数据，是json格式，转化为dict，用form内置表单验证，如果验证成功，自己生成六位数验证码
    # 将验证码生成一个key，验证码当做value存放到redis中，生成一个验证码状态标记
    # 连接redis，初始化管道pipeline，作用可以保存多个
    # 保存验证码（验证码过期时间为五分钟）和状态标签（状态标签过期时间为60s）
    # 然后就可以发送短息（这里成本原因，如果保存成功就代表验证成功，return成功）
    """
    def post(self, request):
        """
        接收ajax发送的请求
        :param request:
        :return:
        """
        # 拿到ajax发送来的json格式数据 是一个二进制数据bytes
        json_data = request.body
        # 如果没有就返回错误
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json格式数据转化为字典
        dict_data = json.loads(json_data.decode('utf8'))
        # 填充form 用于验证
        forms = SmsCodeForm(data=dict_data)
        if forms.is_valid():
            mobile = forms.cleaned_data.get('mobile', '')
            # 创建短信验证码内容
            # 生成六位数短信验证码 string.digits() 生成字符型数字列表  random.choice 随机选择
            sms_text = ''.join([random.choice(string.digits) for _ in range(constants.SMS_CODE_NUMS)])
            logger.info(sms_text)

            # 将短信信息保存到redis数据库
            # 生成短信验证码的key
            sms_key = f'sms_{mobile}'
            # 生成短信状态的key 创建一个在60s以内是否有发送短信记录的标记
            sms_flag_key = f'sms_flag_{mobile}'
            # 连接redis
            con = get_redis_connection(alias='verify_codes')
            # 初始化管道，可以保存多个键值对
            pi = con.pipeline()

            # 有时候会保存失败 使用管道pipeline有时会发生异常
            try:
                # 储存key的时候可以encode().binascii.b2a_hex() 隐藏原始key
                # 保存短信验证码和状态
                pi.setex(sms_flag_key, constants.SEND_SMS_CODE_INTERVAL, 1)
                pi.setex(sms_key, constants.SMS_CODE_REDIS_EXPIRES, sms_text)
                # 执行保存命令
                pi.execute()

                # 保存成功默认发送成功 费用问题
                logger.info(f"短信验证码：{sms_text}")
                return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")

            except Exception as e:
                logger.debug(f'redis_保存文件失败_{e}')
                return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])


            # 发送短信验证码
            # try:
            #     result = sms.ccp.send_template_sms(mobile, [sms_text, constants.SMS_CODE_REDIS_EXPIRES], constants.SMS_CODE_TEMP_ID)
            #     logger.info(f'发送成功_{mobile}')
            # except Exception as e:
            #     logger.error(f'发送验证码错误_error_msg_{e}')
            #     return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
            # else:
            #     if result == 0:
            #         logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_text))
            #         return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
            #     else:
            #         logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
            #         return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])

        else:
            error_msg = []
            for item in forms.errors.get_json_data().values():
                error_msg.append(item[0].get('message'))
            error_msg_str = '/'.join(error_msg)
            return to_json_data(errno=Code.PARAMERR, errmsg=error_msg_str)



