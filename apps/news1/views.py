import json
import logging

from django.views import View
from django.http import Http404
from django.shortcuts import render
from haystack.views import SearchView as _SearchView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from mysite import settings
from . import models
from . import contants
from .models import HotNews
from utils.json_func import to_json_data
from utils.res_code import Code, error_map
# Create your views here.

logger = logging.getLogger('django')


class IndexView(View):
    """
    新闻首页面视图
    """

    def get(self, request):
        # 查询标签信息，渲染到前端
        tags = models.Tag.objects.only('name', 'id').filter(is_delete=False)
        # 获取热门新闻的数据，渲染到前端，一个queryset，在前端遍历渲染
        hot_news = models.HotNews.objects.select_related('news').only('news__title', 'news__image_url', 'news_id').filter(is_delete=False).order_by('priority', '-news__clicks')[0:contants.SHOW_HOTNEWS_COUNT]
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
    轮播图视图,不需要额外参数,与js交互,返回json数据给ajax
    /news/banners/
    """
    def get(self, request):
        # 查轮播图表，关联新闻表，取出新闻的id和title，注意轮播图有几条
        # 并且用优先级进行排序，取出前六条
        banner_list = models.Banner.objects.select_related('news').only('image_url', 'news_id', 'news__title').filter(is_delete=False).order_by('priority')[0:contants.SHOW_BANNER_COUNT]

        # 序列化数据
        news_info_list = []
        for new in banner_list:
            news_info_list.append({
                "image_url": new.image_url,
                "news_id": new.news.id,
                "news_title": new.news.title
            })

        # 将构造好的数据发送给ajax
        data = {
            'banners': news_info_list
        }

        return to_json_data(data=data)


class NewsDetailView(View):
    """
    新闻详情视图，需要接收一个参数，新闻的唯一id
    /news/<int:news_id>/
    """
    def get(self, request, news_id):
        """
        用唯一id获取详情
        :param request:
        :param news_id:
        :return:
        """
        # 查询News新闻表，关联author和tag，因为需要这两个表中的字段
        # 注意查出来的是queryset用first()取出对象
        detail = models.News.objects.select_related('author', 'tag').only('title', 'content', 'update_time', 'author__username', 'tag__name').filter(id=news_id, is_delete=False).first()
        # 如果查到就返回
        if detail:
            # 查询出queryset对象集合
            comments = models.Comments.objects.select_related('author', 'parent').only('author__username', 'parent__author__username', 'update_time', 'content', 'parent__content', 'parent__update_time').filter(is_delete=False, news_id=news_id)
            comment_info_list = []
            # 对queryset遍历
            for comm in comments:
                # 取出每一个对象，调用模型中的返回字段函数，序列化一个列表传给前端。（一种方法）
                comment_info_list.append(comm.to_comment_dict())
            return render(request, 'news/news_detail.html', locals())
        # 查不到就抛出404
        else:
            raise Http404('新闻找不到了')


class NewsCommentView(View):
    """
    新闻评论视图
    /news/<int:news_id>/comments/
    """
    # 需要验证新闻存不存在，评论是否为空，是否有父评论，
    def post(self, request, news_id):

        # 验证用户是否登录
        if not request.user.is_authenticated:
            return to_json_data(errno=Code.SESSIONERR, errmsg=error_map[Code.SESSIONERR])

        # 验证当前新闻存不存在
        if not models.News.objects.only('id').filter(is_delete=False, id=news_id).exists():
            return to_json_data(errno=Code.NODATA, errmsg='新闻不存在')

        # 拿到ajax发送来的json格式数据 是一个二进制数据bytes
        json_data = request.body
        # 如果没有就返回错误
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json格式数据转化为字典
        dict_data = json.loads(json_data.decode('utf8'))

        # 拿到评论内容
        content = dict_data.get('content')
        if not content:
            return to_json_data(errno=Code.NODATA, errmsg='内容不能为空')

        # 拿到父评论  可以没有
        parent_id = dict_data.get('parent_id')
        # 捕捉异常 如果不是字符型数字，则强转会出错
        try:
            if parent_id:
                parent_id = int(parent_id)
                # 查看有没有这条父评论
                # 查询评论，条件是news_id是当前新闻，父评论id等于当前评论id
                if not models.Comments.objects.only('id').filter(is_delete=False, news_id=news_id, id=parent_id).exists():
                    return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        except Exception as e:
            logger.error(f'转义错误{e}')
            return to_json_data(errno=Code.PARAMERR, errmsg="未知异常")

        # 实例化一条空数据，赋值填充
        comment = models.Comments()
        comment.news_id = news_id
        comment.content = content
        comment.author = request.user
        comment.parent_id = parent_id if parent_id else None
        comment.save()
        # 保存成功后发送给前端，因为要渲染到前端，调用Comments类的自定义方法，获取数据
        return to_json_data(data=comment.to_comment_dict())


class NewsSearchView(_SearchView):
    """
    文章搜索视图
    /news/search/
    """
    template = 'news/search.html'
    
    def create_response(self):
        """
        重写SearchView的create_response方法，如果没传参 就用自己写的逻辑
        如果传参了 就用create_response的逻辑
        :return: 
        """
        # 获取前端传来的查询内容
        kw = self.request.GET.get('q')
        if not kw:
            show_all = True
            # 如果没有就返回热门新闻
            hot_news = HotNews.objects.select_related('news').only('news__title', 'news__image_url', 'news__content',  'news__digest', 'news__author').filter(is_delete=False).order_by('priority', '-news__clicks')
            # 对查询到的queryset进行分页
            pagate = Paginator(hot_news, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
            try:
                # 获取当前页  如果没传参就返回第一页
                pg = self.request.GET.get('page', 1)
                # 一定要异常捕获一下 因为有可能传来的不是数字str
                page = pagate.page(int(pg))
            except PageNotAnInteger:
                # 如果不是字符型数字
                # 就返回第一页
                page = pagate.page(1)
            except EmptyPage:
                # 如果超出索引  就返回最后一页
                page = pagate.page(pagate.num_pages)
            return render(self.request, self.template, locals())
        
        else:
            show_all = False
            # 如果有参数  就复用
            qs = super(NewsSearchView, self).create_response()
            return qs
