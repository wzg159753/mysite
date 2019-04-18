from django.shortcuts import render

# Create your views here.

def index(request):
    """
    首页面逻辑
    :param request:
    :return:
    """
    return render(request, 'news/index.html')

def search(request):
    """
    搜索页
    :param request:
    :return:
    """
    return render(request, 'news/search.html')