import os
import logging

import requests
from django.shortcuts import render
from django.http import FileResponse, Http404
from django.utils.encoding import escape_uri_path
from django.views import View

from . import models
from mysite.settings import SITE_DOMAIN_PORT
# Create your views here.

logger = logging.getLogger('django')

def doc_index(request):
    """
    下载页
    :param request:
    :return:
    """
    # 查询被下载的书籍 展示
    docs = models.Doc.objects.only('title', 'file_url', 'desc', 'image_url').filter(is_delete=False)
    return render(request, 'doc/docDownload.html', locals())


class DocDownload(View):
    """
    文件下载模块
    /doc/doc_id/
    # 获取书籍的id，用于找到哪本书
    # 如果书存在，获取书的url路径
    # 将书名和后缀取出，用os方法
    # 用split方法将后缀和书名分割，供下载使用
    # 书的url地址拼接成绝对url路径
    # 用requests方法请求书的url，下载二进制文件
    # 使用django内置返回文件的FileResponse，返回二进制文件，stream在下载大文件时优化（try捕捉一下异常，可能会下载失败）
    # 判断如果没有后缀，抛出异常， 有后缀就转化为小写
    # 判断是什么后缀，就把COntent-type设置成什么后缀
    # 用django内置方法，将书名中的不规范字符转化为规范
    # 拼接Content-Disposition属性，然后返回FileResponse
    """
    def get(self, request, doc_id):
        # 查出要下载的是哪一本书
        doc = models.Doc.objects.only('file_url').filter(is_delete=False, id=doc_id).first()
        if doc:
            # 书的url地址
            doc_url = doc.file_url
            # split方法将地址分割成xxxx.pdf
            _, root = os.path.split(doc_url)
            # 用split将书分割成书名和后缀，供后面使用
            # (xxx, pdf)
            _, ext = root.split('.')
            # 拼接成路由url
            dir_path = SITE_DOMAIN_PORT + doc_url
            try:
                # 有可能下载失败，需要try
                # stream 在下载大文件时候速度快
                # 请求这个url，就会下载
                res = FileResponse(requests.get(dir_path, stream=True))


            except Exception as e:
                logger.info("获取文档内容出现异常：\n{}".format(e))
                raise Http404("文档下载异常！")

            if not ext:
                raise Http404("文档url异常！")

            else:
                # 将后缀转化为小写
                ext = ext.lower()

            if ext == "pdf":
                res["Content-type"] = "application/pdf"
            elif ext == "zip":
                res["Content-type"] = "application/zip"
            elif ext == "doc":
                res["Content-type"] = "application/msword"
            elif ext == "xls":
                res["Content-type"] = "application/vnd.ms-excel"
            elif ext == "docx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext == "ppt":
                res["Content-type"] = "application/vnd.ms-powerpoint"
            elif ext == "pptx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            else:
                raise Http404("文档格式不正确！")

            # 将书名中的不规范字符转为其他格式
            doc_filename = escape_uri_path(root)
            # 将书名和编码给response设置
            res["Content-Disposition"] = f"attachment; filename*=UTF-8''{doc_filename}"
            return res

        else:
            raise Http404("文档不存在！")