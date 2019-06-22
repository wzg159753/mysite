import re

from django import forms
from django.db.models import Q
from django.contrib.auth import login
from django_redis import get_redis_connection

from .models import Users
from veriftions import constants
from users import constants as const
from utils.res_code import Code, error_map


class RegisterForm(forms.Form):
    """
    用户注册form
    字段要和前端html中的name属性一致
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

    def clean_username(self):
        """
        验证用户名是否注册
        :return:
        """
        username = self.cleaned_data.get('username')
        if Users.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已经存在')

        return username

    def clean_mobile(self):
        """
        单个验证手机号
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
        # 用户输入的短信验证码
        sms_code = cleaned_data.get('sms_code')
        # 用户输入的手机号
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
        
        
class LoginForm(forms.Form):
    """
    登录表单验证
    """
    # 因为可以传用户名和手机号进行登录，所以不需要设置其他属性
    user_account = forms.CharField()
    password = forms.CharField(label='密码', max_length=20, min_length=6, required=True, error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20","required": "密码不能为空"})
    # 是否记住登录
    remember_me = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        # 注意这里一定要pop取值，自己测试用get会报错
        self.request = kwargs.pop('request', None) # 获取view中实例化传来的request
        super(LoginForm, self).__init__(*args, **kwargs) # 复用父类方法

    def clean_user_account(self):
        # 获取用户名或手机号
        user_account = self.cleaned_data.get('user_account')
        if not user_account:
            raise forms.ValidationError('用户名为空!')
        # 如果不是手机号 并且用户名小于5或大于20
        if not re.match(r"^1[3-9]\d{9}$", user_account) and ((len(user_account) < 5) or (len(user_account) > 20)):
            raise forms.ValidationError('用户名或手机号格式错误')

        return user_account
        
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        user_account = cleaned_data.get('user_account', None)
        password = cleaned_data.get('password')
        remember_me = cleaned_data.get('remember_me')

        # models的Q方法是进行or（或）查询，
        user_query = Users.objects.filter(Q(username=user_account) | Q(mobile=user_account))
        # 如果存在这个queryset（对象集合）
        if user_query:
            # 取集合中的对象
            user = user_query.first()
            # 用form的内置方法判断密码是否一致
            if user.check_password(password):
                # 判断是否点击前端 记住我
                if remember_me:
                    # 如果有点击，则设置 session过期时间为五天
                    self.request.session.set_expiry(const.USER_SESSION_EXPIRES)
                else:
                    # 如果没点击则设置过期时间为关闭浏览器
                    self.request.session.set_expiry(0)

                # 登录 django内置登录 自动设置一条session 为user
                login(self.request, user)
            else:
                raise forms.ValidationError('密码错误')

        else:
            raise forms.ValidationError('用户名不存在')

