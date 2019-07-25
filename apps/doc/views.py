import json
import math

import os
import logging
from lxml import etree

import requests
from datetime import datetime
from django.shortcuts import render
from django.http import FileResponse, Http404, HttpResponse
from django.utils.encoding import escape_uri_path
from django.views import View


from . import models
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
            _, ext = root.split('.')
            # 拼接成路由url
            dir_path = 'http://192.168.35.133:9000' + doc_url
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


class SpiderDownloadView(View):
    """
    天眼查爬虫
    """
    def get(self, request):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'Cookie': 'ssuid=8382144908; TYCID=74ec6020a2d611e98c68bf4e5261bedb; undefined=74ec6020a2d611e98c68bf4e5261bedb; _ga=GA1.2.1702490168.1562737758; RTYCID=d53d7889ecea46899d6ca5a58cfedfa4; CT_TYCID=bcc24dbd9f2c4bc5a827f83fa25ed13f; aliyungf_tc=AQAAALDv+xbHLAEAniP/kLHfRMu1MBm/; bannerFlag=undefined; csrfToken=qOoWhuFMSPTOR4w5PsQKaKO3; Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1562737758,1563343625,1563935551,1564071780; _gid=GA1.2.2009323628.1564071781; _gat_gtag_UA_123487620_1=1; tyc-user-info=%257B%2522claimEditPoint%2522%253A%25220%2522%252C%2522myAnswerCount%2522%253A%25220%2522%252C%2522myQuestionCount%2522%253A%25220%2522%252C%2522signUp%2522%253A%25220%2522%252C%2522explainPoint%2522%253A%25220%2522%252C%2522privateMessagePointWeb%2522%253A%25220%2522%252C%2522nickname%2522%253A%2522%25E5%2585%258B%25E9%2587%258C%25E6%2596%25AF%25E8%2592%2582%25E5%25A8%259C%25C2%25B7%25E8%2589%25BE%25E4%25BC%25AF%25E7%259B%2596%25E7%2589%25B9%2522%252C%2522integrity%2522%253A%25220%2525%2522%252C%2522privateMessagePoint%2522%253A%25220%2522%252C%2522state%2522%253A%25220%2522%252C%2522announcementPoint%2522%253A%25220%2522%252C%2522isClaim%2522%253A%25220%2522%252C%2522vipManager%2522%253A%25220%2522%252C%2522discussCommendCount%2522%253A%25221%2522%252C%2522monitorUnreadCount%2522%253A%252210%2522%252C%2522onum%2522%253A%25220%2522%252C%2522claimPoint%2522%253A%25220%2522%252C%2522token%2522%253A%2522eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzg1MzI3NTA5MCIsImlhdCI6MTU2NDA3MTc5NSwiZXhwIjoxNTk1NjA3Nzk1fQ.zG46NSQkyEntf3La92iRPA7p6GlwRi6SVuJiaQOE03qzq3ofBb5u8AmoR2099-_C2ACM1uHAa5mLFtQWxzFcxQ%2522%252C%2522pleaseAnswerCount%2522%253A%25220%2522%252C%2522redPoint%2522%253A%25220%2522%252C%2522bizCardUnread%2522%253A%25220%2522%252C%2522vnum%2522%253A%25220%2522%252C%2522mobile%2522%253A%252213853275090%2522%257D; auth_token=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzg1MzI3NTA5MCIsImlhdCI6MTU2NDA3MTc5NSwiZXhwIjoxNTk1NjA3Nzk1fQ.zG46NSQkyEntf3La92iRPA7p6GlwRi6SVuJiaQOE03qzq3ofBb5u8AmoR2099-_C2ACM1uHAa5mLFtQWxzFcxQ; Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=1564071809'
        }
        resp = requests.get('https://www.tianyancha.com/company/14270846', headers=headers)
        html = etree.HTML(resp.text)
        pages = html.xpath(
            '//div[@id="_container_judicialSale"]/div[@class="company_pager pagination-warp"]/ul/@page-total')
        if pages:
            result = {}
            pns = math.ceil(int(pages[0]) / 30)
            lis = []
            for pn in range(1, pns + 1):
                params = {
                    'ps': '30',
                    'pn': str(pn),
                    'id': '14270846',
                    '_': str(int(datetime.now().timestamp() * 1000))
                }
                resp = requests.get('https://www.tianyancha.com/pagination/judicialSale.xhtml', headers=headers,
                                    params=params)
                if resp.status_code == 200:
                    code = etree.HTML(resp.text)
                    trs = code.xpath('//table/tbody/tr')
                    # print(tbody)
                    for tr in trs:
                        lis.append({
                            'num': tr.xpath('./td[1]/text()')[0],
                            'time': tr.xpath('./td[2]/text()')[0],
                            'info': tr.xpath('./td[3]/text()')[0],
                            'biaodi': '-'.join(tr.xpath('./td[4]//text()')),
                            'fayuan': tr.xpath('./td[5]/text()')[0]
                        })
                    # print(tbody)

                else:
                    return HttpResponse('验证码<br>')
            result['result'] = lis
            return HttpResponse(json.dumps(result))
        else:

            return HttpResponse('验证码')
