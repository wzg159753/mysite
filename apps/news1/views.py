import logging

from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage

from utils.json_func import to_json_data
from . import models
from . import contants
# Create your views here.

logger = logging.getLogger('django')


class IndexView(View):
    """
    新闻首页面视图
    """

    def get(self, request):
        tags = models.Tag.objects.only('name', 'id').filter(is_delete=False)
        # context = {
        #     'tags': tags
        # }
        # locals()方法是python内置方法，将所有作用域内的属性传递到对应地方
        return render(request, 'news/index.html', locals())


class NewsListView(View):
    """
    返回数据列表 前端ajax请求
    """
    def get(self, request):
        # 1、获取参数
        # 2、校验参数
        # 一起用try都干了
        # 用异常捕获的方法获取参数
        try:
            # 获取的参数是str型的，用int转换类型，如果没有值则默认为0
            tag_id = int(request.GET.get('tag_id', 0))
        except Exception as e:
            # 如果传入是字母或其他 也默认为0
            logger.error(f'接收tag_id错误：{e}')
            tag_id = 0

        try:
            # page和tag_id一样
            page = int(request.GET.get('page', 1))
        except Exception as e:
            # 如果tag_id不存在 则默认为1
            logger.error(f'接收的页码page出错:{e}')
            page = 1

        # 3、从数据库拿数据
        # 字段 title, digest, image_url, update_time, id
        # 外键字段 tag__name, author__username # 有关联的字段才能取，用 表名小写__字段名
        news_queryset = models.News.objects.select_related('tag', 'author').only('title', 'digest', 'image_url', 'update_time', 'tag__name', 'author__username')
        news = news_queryset.filter(tag_id=tag_id, is_delete=False) or news_queryset.filter(is_delete=False)
        # 4、分页
        paginate = Paginator(news, contants.PER_PAGE_NEWS_NUM)
        try:
            new_info = paginate.page(page)
        except EmptyPage as e:
            logger.error(f'页码超出索引:{e}')
            new_info = paginate.page(paginate.num_pages)

        # 5、序列化要返回数据
        news_info_list = []
        for new in new_info:
            news_info_list.append({
                'id': new.id,
                'title': new.title,
                'digest': new.digest,
                'image_url': new.image_url,
                'update_time': new.update_time,
                'tag_name': new.tag.name,
                'author_username': new.author.username
            })
        data = {
            'total_pages': paginate.num_pages,
            'news': news_info_list
        }

        return to_json_data(data=data)



