import json

from django.shortcuts import render
from django.views import View

from utils.json_func import to_json_data
from utils.res_code import Code, error_map

# Create your views here.

def user_login(request):
    """
    用户登录
    :param request:
    :return:
    """
    return render(request, 'users/login.html')

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
            return to_json_data(error=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        