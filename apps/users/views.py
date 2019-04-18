from django.shortcuts import render

# Create your views here.

def user_login(request):
    """
    用户登录
    :param request:
    :return:
    """
    return render(request, 'users/login.html')

def user_register(request):
    """
    用户注册
    :param request:
    :return:
    """
    return render(request, 'users/register.html')