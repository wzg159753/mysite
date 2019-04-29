import re

from django import forms
from django_redis import get_redis_connection

from utils.res_code import Code, error_map
from veriftions import constants
from .models import Users


class RegisterForm(forms.Form):
    """
    用户注册form
    """
    username = forms.CharField(label='用户名', max_length=20, min_length=5, error_messages={"min_length": "用户名长度要大于5", "max_length": "用户名长度要小于20",
                                               "required": "用户名不能为空"})

    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"}
                               )
    password_repeat = forms.CharField(label='确认密码', max_length=20, min_length=6,
                                      error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                                      "required": "密码不能为空"}
                                      )
    mobile = forms.CharField(label='手机号', max_length=11, min_length=11,
                             error_messages={"min_length": "手机号长度有误", "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})

    sms_code = forms.CharField(label='短信验证码', max_length=constants.SMS_CODE_NUMS, min_length=constants.SMS_CODE_NUMS,
                               error_messages={"min_length": "短信验证码长度有误", "max_length": "短信验证码长度有误",
                                               "required": "短信验证码不能为空"})

    def clean_mobile(self):
        """
        单个验证
        :return:
        """
        mobile = self.cleaned_data.get('mobile')
        # 验证手机号码格式
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            raise forms.ValidationError('手机号码格式错误')

        # 验证手机号是否已注册
        if Users.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError('手机号码已存在')

        return mobile

    def clean(self):
        # 继续使用父类方法
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')
        sms_code = cleaned_data.get('sms_code')
        mobile = cleaned_data.get('mobile')

        # 对两次输入的密码一致性校验
        if password != password_repeat:
            raise forms.ValidationError('两次输入密码不一致')

        # 对短信验证码正确性校验
        # 拼接出短信验证码的key
        sms_key = f'sms_{mobile}'
        # 连接redis数据库
        con = get_redis_connection(alias='verify_codes')
        # 取出对应key的values（短息验证码）
        sms_code_text = con.get(sms_key)

        # 如果没有值返回异常 如果输入的验证码和数据库中的不同返回异常
        if (not sms_code_text) or (sms_code != sms_code_text.decode('utf8')):
            raise forms.ValidationError('短信验证码错误')

