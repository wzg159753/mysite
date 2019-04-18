from django.shortcuts import render

# Create your views here.

def doc_index(request):
    """
    下载页
    :param request:
    :return:
    """
    return render(request, 'doc/docDownload.html')