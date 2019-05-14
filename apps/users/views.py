import json

from django.views import View
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout

from utils.json_func import to_json_data
from utils.res_code import Code, error_map
from .forms import RegisterForm, LoginForm
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from .models import Users

# Create your views here.

class LoginView(View):
    """
    用户登录
    /users/login/
    """
    # @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf-8'))
        # 将request传递给form表单
        forms = LoginForm(data=dict_data, request=request)
        # form验证的时候已经用login（）方法登录了
        if forms.is_valid():
            return to_json_data(errmsg='登陆成功')
        else:
            err_msg_list = []
            for item in forms.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class LogoutView(View):
    """
    退出逻辑
    /users/logout/
    """
    def get(self, request):
        logout(request)
        return redirect(reverse('user:login'))


class RegisterView(View):
    """
    用户注册逻辑
    /reg/
    """

    def get(self, request):
        """
        用户注册
        :param request:
        :return:
        """
        return render(request, 'users/register.html')

    def post(self, request):
        """
        接收参数
        内置form校验
        存储
        返回
        :return:
        """
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        forms = RegisterForm(data=dict_data)
        if forms.is_valid():
            username = forms.cleaned_data.get('username')
            password = forms.cleaned_data.get('password')
            mobile = forms.cleaned_data.get('mobile')
            user = Users.objects.create_user(username=username, password=password, mobile=mobile)
            login(request, user)
            return to_json_data(errmsg='注册成功')

        else:
            error_msg = []
            for item in forms.errors.get_json_data().values():
                error_msg.append(item[0].get('message'))
            error_msg_str = '/'.join(error_msg)
            return to_json_data(errno=Code.PARAMERR, errmsg=error_msg_str)

