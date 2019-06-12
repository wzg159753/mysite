import json
import logging

from django.shortcuts import render
from django.views import View
from django.db.models import Count

from news1 import models
# Create your views here.
from utils.json_func import to_json_data
from utils.res_code import Code, error_map
from . import contants

logger = logging.getLogger('django')


class IndexView(View):
    """
    /admin/
    后台主页
    """
    def get(self, request):
        return render(request, 'admin/index/index.html')


class TagManageView(View):
    """
    文章分类展示，添加文章标签
    /admin/tags/
    # 展示所有未删除的文章标签
    """
    def get(self, request):
        # 查询Tag与news关联，用聚合分组查出tag标签里面的文章数量，对数量进行排序
        tags = models.Tag.objects.select_related('news').values('id', 'name').filter(is_delete=False).annotate(nums=Count('news__tag_id')).order_by('-nums', 'update_time')
        return render(request, 'admin/news/tags_manage.html', locals())

    def post(self, request):
        """
        # 获取需要ajax传来的数据
        # 拿到用户输入的文章标签名
        # 查看标签名是否为空
        # 用orm的创建查询方法
        # 如果创建成功，就返回序列化的数据tag_dict给ajax
        :param request:
        :return:
        """
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        name = dict_data.get('name')
        if name:
            name = name.strip()
            # 如果已存在则返回实例和False， 创建成功返回实例和True
            tag, tag_boolen = models.Tag.objects.get_or_create(name=name)
            if tag_boolen:
                tag_dict = {
                    'id': tag.id,
                    'name': tag.name
                }
                return to_json_data(errmsg='标签添加成功', data=tag_dict)
            else:
                return to_json_data(errno=Code.DATAEXIST, errmsg='标签已存在')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='标签不能为空')


class TagEditView(View):
    """
    标签编辑，删除
    /admin/tags/tag_id/
    # 都需要tag_id，就写到一个类里面
    """
    def delete(self, request, tag_id):
        """
        删除标签
        # 查要删除的字段存不存在
        # 如果存在就将is_delete设置为True，逻辑删除，保存
        # 保存的时候只需要保存is_delete和修改时间就可以了
        :param request:
        :param tag_id:
        :return:
        """
        # 先查出这个字段，如果有这个字段才能删除
        tag = models.Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            tag.is_delete = True
            tag.save(update_fields=['is_delete', 'update_time'])
            return to_json_data(errmsg='标签删除成功!')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要删除的标签不存在")

    def put(self, request, tag_id):
        """
        修改标签
        # 从ajax获取用户输入的数据
        # 拿到用户输入的标签名
        # 将输入的标签名两边的空格去掉
        # 判断数据库中有没有这条标签，如果没有就保存，返回ajax
        :param request:
        :param tag_id:
        :return:
        """
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        # 拿到js传来的修改内容
        tag_name = dict_data.get('name', None)
        # 拿到对应id的标签
        tag = models.Tag.objects.only('name').filter(id=tag_id).first()
        if tag:
            # 有可能内容有空格，去处空格
            tag_name = tag_name.strip()
            # 判断两次名字是否一致，如果一致就未修改
            if tag.name == tag_name:
                return to_json_data(errno=Code.PARAMERR, errmsg='标签未修改')
            # 判断修改的内容是否在数据库已经存在
            if not models.Tag.objects.only('id').filter(name=tag_name).exists():
                tag.name = tag_name
                tag.save(update_fields=['name', 'update_time'])
                return to_json_data(errmsg='标签修改成功')
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg='标签重复')

        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='标签不存在')


class HotNewsManageView(View):
    """
    热门新闻
    /hotnews/
    """
    def get(self, request):
        """
        显示前三条的热门新闻
        :param request:
        :return:
        """
        # 需要显示news的title，news标签的name，优先级  select_related('news__tag'),关联news表并且关联tag表
        hot_news = models.HotNews.objects.select_related('news').only('news__title', 'news_id', 'news__tag__name', 'priority').filter(is_delete=False).order_by('priority', '-update_time')[:contants.SHOW_HOTNEWS_COUNT]
        return render(request, 'admin/news/news_hot.html', locals())


class HotNewsEditView(View):
    """
    热门文章修改删除
    /hotnews/<int:hotnews_id>/
    """
    def delete(self, request, hotnews_id):
        """
        删除热门新闻
        :param request:
        :return:
        """
        # 先查出这条新闻有没有
        hotnews = models.HotNews.objects.only('id').filter(id=hotnews_id).first()
        if hotnews:
            # 逻辑删除
            hotnews.is_delete = True
            # 只保存修改的字段
            hotnews.save(update_fields=['is_delete', 'update_time'])
            return to_json_data(errmsg='热门文章删除成功!')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要删除的热门文章不存在!')

    def put(self, request, hotnews_id):
        """
        修改热门新闻
        :param request:
        :param hotnews_id:
        :return:
        """
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        try:
            # 获取传来的参数，并且转为int，可能出错 try一下，因为传来的可能不是字符型数字
            priority = int(dict_data.get('priority'))
            # 生成优先级列表 就是里面有哪些优先级
            priority_list = [num for num, _ in models.HotNews.PRI_CHOICES]
            # 判断修改的优先级是不是列表中的优先级
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='热门文章优先级设置错误')
        except Exception as e:
            logger.info('热门文章优先级异常:\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='热门文章优先级设置错误')

        # 查看这条热门新闻存不存在
        hotnews = models.HotNews.objects.only('id').filter(id=hotnews_id).first()
        if not hotnews:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要更新的热门文章不存在')
        # 判断输入的优先级和这条新闻的优先级是否一样，如果一样则代表没修改
        if hotnews.priority == priority:
            return to_json_data(errno=Code.PARAMERR, errmsg='热门文章的优先级未改变')

        # 如果上面验证没问题 就重新赋值，保存
        hotnews.priority = priority
        hotnews.save(update_fields=['priority', 'update_time'])
        return to_json_data(errmsg='热门文章修改成功')


class HotNewsAddView(View):
    """
    添加热门新闻
    /admin/hotnews/add/
    """
    def get(self, request):
        # 查出所有tags标签和每个标签下的新闻数量，聚合分组
        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')).filter(is_delete=False).order_by('-num_news', 'update_time')
        # 将HotNews中的优先级别拿到 转成dict，供前端展示选择
        priority_dict = dict(models.HotNews.PRI_CHOICES)
        return render(request, 'admin/news/news_hot_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        # 判断文章存不存在，以及int转的时候异常捕捉
        try:
            news_id = int(dict_data.get('news_id', None))
            # 如果没有这条新闻，return错误
            if not models.News.objects.only('id').filter(is_delete=False, id=news_id).exists():
                return to_json_data(errno=Code.PARAMERR, errmsg='文章不存在')
        except Exception as e:
            logger.info('热门文章:\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        # 判断优先级
        try:
            # 转int，可能会报错，try
            priority = int(dict_data.get('priority', None))
            # 拿到优先级列表
            priority_nums = [num for num, _ in models.HotNews.PRI_CHOICES]
            # 判断用户输入的优先级在不在列表中
            if priority not in priority_nums:
                return to_json_data(errno=Code.PARAMERR, errmsg='热门文章的优先级设置错误')
        except Exception as e:
            logger.info('热门文章优先级异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='热门文章的优先级设置错误')

        # 有则查无责增方法，如果查出来，is_created就是False， 如果创建，则为True（hotnews是查出来或创建的实例）
        hotnews, is_created = models.HotNews.objects.get_or_create(news_id=news_id)
        # 如果创建成功
        if is_created:
            # 就改优先级
            hotnews.priority = priority
            hotnews.save(update_fields=['priority', 'update_time'])
            return to_json_data(errmsg="热门文章创建成功")
        else:
            # 否则就是已存在
            return to_json_data(errmsg='热门新闻已存在')


class NewsByTagIdView(View):
    """
    返回所有对应tag_id的新闻
    /admin/tags/<int:tag_id>/news/
    """
    def get(self, request, tag_id):
        newses = models.News.objects.values('id', 'title').filter(is_delete=False, tag_id=tag_id)
        news_list = [i for i in newses]
        data = {
            'news': news_list
        }
        return to_json_data(data=data)








