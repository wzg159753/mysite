import logging
from datetime import datetime

from django.http import Http404
from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage

from . import models
from . import contants
from utils.json_func import to_json_data
# Create your views here.

logger = logging.getLogger('django')


class IndexView(View):
    """
    新闻首页面视图
    """

    def get(self, request):
        tags = models.Tag.objects.only('name', 'id').filter(is_delete=False)
        hot_news = models.HotNews.objects.select_related('news').only('news__title', 'news__image_url', 'news_id').filter(is_delete=False).order_by('priority', '-news__clicks')[0:3]
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
        # select_related优化方法 提前将模型字段关联
        news_queryset = models.News.objects.select_related('tag', 'author').only('title', 'digest', 'image_url', 'update_time', 'tag__name', 'author__username')
        news = news_queryset.filter(tag_id=tag_id, is_delete=False) or news_queryset.filter(is_delete=False)
        # 4、分页
        # 用django内置分页方法，第一个参数传对象集合，第二个参数传一页多少条数据
        paginate = Paginator(news, contants.PER_PAGE_NEWS_NUM)
        try:
            # 拿到paginate对象的对应页数的数据
            new_info = paginate.page(page)
        except EmptyPage as e:
            logger.error(f'页码超出索引:{e}')
            # 如果页码超出索引 就将最后一页赋值给他
            new_info = paginate.page(paginate.num_pages)

        # 5、序列化要返回数据
        news_info_list = []
        # 循环每一个对象
        for new in new_info:
            # 将每个对象的字段值构建成一个dict，将dict数据再添加到列表中生成列表字典数据，用于生成json数据
            news_info_list.append({
                'news_id': new.id,
                'title': new.title,
                'digest': new.digest,
                'image_url': new.image_url,
                'update_time': new.update_time.strftime('%Y年%m月%d日 %H时:%M分'),
                'tag_name': new.tag.name,
                'author_username': new.author.username
            })
        # 将列表数据和总页数构建成字典
        data = {
            'total_pages': paginate.num_pages,
            'news': news_info_list
        }

        # 将json数据返回给ajax
        return to_json_data(data=data)


class NewsBannerView(View):
    """
    轮播图视图

    """
    def get(self, request):
        banner_list = models.Banner.objects.select_related('news').only('image_url', 'news_id', 'news__title').filter(is_delete=False).order_by('priority')[0:contants.SHOW_BANNER_COUNT]

        news_info_list = []
        for new in banner_list:
            news_info_list.append({
                "image_url": new.image_url,
                "news_id": new.news.id,
                "news_title": new.news.title
            })

        data = {
            'banners': news_info_list
        }

        return to_json_data(data=data)


class NewsDetailView(View):
    """
    新闻详情视图
    /news/<int:news_id>/
    """
    def get(self, request, news_id):
        """
        用唯一id获取详情
        :param request:
        :param news_id:
        :return:
        """
        detail = models.News.objects.select_related('author', 'tag').only('title', 'content', 'update_time', 'author__username', 'tag__name').filter(id=news_id, is_delete=False).first()
        if detail:
            return render(request, 'news/news_detail.html', locals())
        else:
            raise Http404('新闻找不到了')
