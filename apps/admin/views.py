import json
import logging
from datetime import datetime
from collections import OrderedDict

import qiniu
from django.views import View
from django.db.models import Count
from django.shortcuts import render
from django.utils.http import urlencode
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator, EmptyPage

from . import forms
from . import contants
from news1 import models
from doc.models import Doc
from mysite import settings
from utils.secrets import qiniu_secret
from utils.json_func import to_json_data
from utils.res_code import Code, error_map
from utils.fastdfs.fast import FDFS_Client
from utils.paginator_script import get_paginator_data
from course.models import Course, Teacher, CourseCategory


logger = logging.getLogger('django')


class IndexView(View):
    """
    /admin/
    后台主页
    """
    def get(self, request):
        return render(request, 'admin/index/index.html')


# 标签管理，添加，删除，修改
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


# 热门新闻管理，添加，删除，修改
class HotNewsManageView(View):
    """
    热门新闻
    /admin/hotnews/
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
    /admin/hotnews/<int:hotnews_id>/
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


# 新闻管理
class NewsManageView(View):
    """
    文章管理页
    /admin/
    title author_username tag_name update_time id
    """
    def get(self, request):
        # 先查出所有newses，供后面查询使用
        newses = models.News.objects.select_related('tag', 'author').only('id', 'title', 'author__username',
                                                                          'tag__name', 'update_time').filter(
            is_delete=False)
        # 查出所有tag，需要展示到前端，让客户选择查询
        tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)

        fmt = '%Y/%m/%d'
        try:
            # 对时间字符串进行处理，转化为日期格式
            start_time = request.GET.get('start_time', '')
            start_time = datetime.strptime(start_time, fmt) if start_time else ''
            end_time = request.GET.get('end_time', '')
            end_time = datetime.strptime(end_time, fmt) if end_time else ''
        except Exception as e:
            logger.info("用户输入的时间有误：\n{}".format(e))
            start_time = end_time = ''

        # 如果有开始时间 没有结束时间
        if start_time and (not end_time):
            # 就返回大于开始时间的所有
            newses = newses.filter(update_time__gte=start_time)
        if end_time and (not start_time):
            newses = newses.filter(update_time__lte=end_time)
        if start_time and end_time:
            newses = newses.filter(update_time__range=(start_time, end_time))

        # 对作者进行忽略大小写的模糊查询
        author_username = request.GET.get('author_name', '')
        if author_username:
            newses = newses.filter(author__username__icontains=author_username)

        # 对文章标题进行模糊查询
        title = request.GET.get('title', '')
        if title:
            newses = newses.filter(title__icontains=title)

        # 对标签进行查询
        try:
            # int型 如果没传 就等于0
            tag_id = int(request.GET.get('tag_id', 0))
        except Exception as e:
            logger.info("标签错误：\n{}".format(e))
            # 如果出错 也等于0
            tag_id = 0
        if tag_id:
            newses = newses.filter(tag_id=tag_id)

        # 生成分页对象
        paginator = Paginator(newses, contants.PER_PAGE_NEWS_COUNT)

        # 获取当前页号，int一下，捕捉一下
        try:
            pg = int(request.GET.get('page', 1))
        except Exception as e:
            logger.info("当前页数错误：\n{}".format(e))
            pg = 1
        # 获取当前页数据
        try:
            news_list = paginator.page(pg)
        except EmptyPage:
            logging.info("用户访问的页数大于总页数。")
            news_list = paginator.page(paginator.num_pages)

        # 获取分页后的数据,手写分页
        paginator_data = get_paginator_data(paginator, news_list)

        # 将时间日期格式转为str格式
        # 一定要判断存不存在，如果不判断，会报错
        start_time = start_time.strftime(fmt) if start_time else ''
        end_time = end_time.strftime(fmt) if end_time else ''

        # 构造参数
        context = {
            'news_info': news_list,
            'tags': tags,
            'start_time': start_time,
            "end_time": end_time,
            "title": title,
            "author_name": author_username,
            "tag_id": tag_id,
            # 点击下一页数据时，自动带上之前的搜索条件
            "other_param": urlencode({
                "start_time": start_time,
                "end_time": end_time,
                "title": title,
                "author_name": author_username,
                "tag_id": tag_id,
            })
        }
        # 将分页里的参数更新到参数中
        context.update(paginator_data)
        return render(request, 'admin/news/news_manage.html', context=context)


# 文章上传，编辑，删除
class NewsEditView(View):
    """
    新闻编辑，删除
    /admin/news/<int:new_id>/
    """
    def get(self, request, new_id):
        """
        返回新闻修改页面
        :param request:
        :param new_id:
        :return:
        """

        news = models.News.objects.only('id', 'title').filter(is_delete=False, id=new_id)
        # 拿到文章，展示数据
        if news:
            # 返回tags，用于选择
            tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)
            context = {
                'news': news.first(),
                'tags': tags
            }
            return render(request, 'admin/news/news_pub.html', context=context)

        else:
            return Http404

    def put(self, request, new_id):
        """
        修改新闻
        :param request:
        :param new_id:
        :return:
        """
        news = models.News.objects.only('id').filter(is_delete=False, id=new_id).first()
        if not news:
            return to_json_data(errno=Code.PARAMERR, errmsg='文章不存在')

        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.NewsPubForm(data=dict_data)
        if form.is_valid():
            news.title = form.cleaned_data.get('title')
            news.digest = form.cleaned_data.get('digest')
            news.content = form.cleaned_data.get('content')
            news.image_url = form.cleaned_data.get('image_url')
            news.tag = form.cleaned_data.get('tag')
            news.save()
            return to_json_data(errmsg='文章更新成功')

        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

    def delete(self, request, new_id):
        """
        删除新闻
        :param request:
        :param new_id:
        :return:
        """
        news = models.News.objects.only('id').filter(is_delete=False, id=new_id).first()
        if news:
            news.is_delete = True
            news.save(update_fields=['is_delete', 'update_time'])
            return to_json_data(errmsg='文章删除成功')
        else:
            return to_json_data(errmsg='文章删除失败')


class NewsPubView(View):
    """
    文章添加和文章修改差不多，所以写成一个页面
    /admin/news/pub/
    """
    def get(self, request):
        # 渲染文章添加页面，将文章可选的tag返回渲染
        tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)
        return render(request, 'admin/news/news_pub.html', locals())

    def post(self, request):
        """
        文章上传功能
        :param request:
        :return:
        """
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 2.将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.NewsPubForm(data=dict_data)
        # 验证文章字段  django内置form认证
        if form.is_valid():
            news_instance = form.save(commit=False)
            news_instance.author_id = request.user.id
            news_instance.save()
            return to_json_data()

        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 图片上传到fdfs
class NewsUploadImageView(View):
    """
    ajax发送post
    /admin/news/images/
    """
    def post(self, request):
        # 获取上传的image图片对象
        # 是通过ajax发送来的，获取方式相同
        image = request.FILES.get('image_file', None)
        # 如果没传就返回错误
        if not image:
            logger.info('从前端获取图片失败')
            return to_json_data(errno=Code.NODATA, errmsg='从前端获取图片失败')

        # 如果image对象的属性不在这些当中，就返回不能上传非图片文件
        if image.content_type not in ('image/jpg', 'image/png', 'image/gif', 'image/jpeg'):
            return to_json_data(errno=Code.DATAERR, errmsg='不能上传非图片文件')

        try:
            # 获取后缀，供上传到fastdfs使用
            ext = image.name.split('.')[-1]
        except Exception as e:
            # 如果没有后缀，默认为jpg
            logger.info('图片拓展名异常：{}'.format(e))
            ext = 'jpg'

        # 用FDFS_Client对象，从utils中定义好的，调用上传二进制数据的上传方式，加上后缀，上传到fastdfs
        try:
            ret = FDFS_Client.upload_by_buffer(image.read(), file_ext_name=ext)

        except Exception as e:
            logger.error('图片上传出现异常：{}'.format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg='图片上传异常')

        else:
            # 判断上传完成返回的数据中的状态码登不等于成功，注意successed后面有个.
            if ret.get('Status') != 'Upload successed.':
                logger.info('图片上传到FastDFS服务器失败')
                return to_json_data(Code.UNKOWNERR, errmsg='图片上传到服务器失败')
            else:
                # 如果上传成功，获取图片相对路径
                image_rel_url = ret.get('Remote file_id')
                # 拼接成绝对路径，返回给前端
                image_url = settings.FASTDFS_SERVER_DOMAIN + image_rel_url
                return to_json_data(data={'image_url': image_url}, errmsg='图片上传成功')


# 获取七牛云token
class UploadToken(View):
    """
    /admin/token/
    获取七牛云token
    """

    def get(self, request):
        access_key = qiniu_secret.QI_NIU_ACCESS_KEY
        secret_key = qiniu_secret.QI_NIU_SECRET_KEY
        bucket_name = qiniu_secret.QI_NIU_BUCKET_NAME
        # 构建鉴权对象
        q = qiniu.Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)

        return JsonResponse({"uptoken": token})


class MarkDownUploadImage(View):
    """
    富文本编辑器图片上传
    /admin/markdown/images/
    """
    def post(self, request):
        image_file = request.FILES.get('editormd-image-file')
        if not image_file:
            logger.info('从前端获取图片失败')
            return JsonResponse({'success': 0, 'message': '从前端获取图片失败'})

        if image_file.content_type not in ('image/jpeg', 'image/png', 'image/gif'):
            return JsonResponse({'success': 0, 'message': '不能上传非图片文件'})

        try:
            image_ext_name = image_file.name.split('.')[-1]
        except Exception as e:
            logger.info('图片拓展名异常：{}'.format(e))
            image_ext_name = 'jpg'

        try:
            upload_res = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
        except Exception as e:
            logger.error('图片上传出现异常：{}'.format(e))
            return JsonResponse({'success': 0, 'message': '图片上传异常'})
        else:
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('图片上传到FastDFS服务器失败')
                return JsonResponse({'success': 0, 'message': '图片上传到服务器失败'})
            else:
                image_name = upload_res.get('Remote file_id')
                image_url = settings.FASTDFS_SERVER_DOMAIN + image_name
                return JsonResponse({'success': 1, 'message': '图片上传成功', 'url': image_url})


# 录播图管理，删除，修改，添加
class BannerManageView(View):
    """
    /admin/banners/
    """
    def get(self, request):
        """
        轮播图管理，展示
        :param request:
        :return:
        """
        # 拿到排序的优先级dict
        priority_dict = OrderedDict(models.Banner.PRI_CHOICES)
        # 拿到对应的轮播图
        banners = models.Banner.objects.only('image_url', 'priority').filter(is_delete=False)
        return render(request, 'admin/news/news_banner.html', locals())


class BannerEditView(View):
    """
    /admin/banners/<banner_id>/
    轮播图删除，编辑
    """
    def delete(self, request, banner_id):
        """
        删除
        :param request:
        :param banner_id:
        :return:
        """
        banner = models.Banner.objects.only('id').filter(id=banner_id, is_delete=False).first()
        if banner:
            banner.is_delete = True
            banner.save(update_fields=['is_delete', 'update_time'])
            return to_json_data(errmsg='轮播图删除成功')
        else:
            return to_json_data('轮播图不存在')

    def put(self, request, banner_id):
        """
        编辑
        :param request:
        :param banner_id:
        :return:
        """
        banner = models.Banner.objects.only('id').filter(id=banner_id, is_delete=False).first()
        if not banner:
            return to_json_data(errno=Code.DATAEXIST, errmsg=error_map[Code.DATAEXIST])

        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 2.将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in models.Banner.PRI_CHOICES]
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='轮播图优先级设置错误')
        except Exception as e:
            logger.info('轮播图优先级异常\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图优先级设置错误')

        image_url = dict_data.get('image_url')
        if not image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg='图片为空')
        if banner.image_url == priority and banner.image_url == image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图优先级未更改')

        banner.image_url = image_url
        banner.priority = priority
        banner.save(update_fields=['image_url', 'priority', 'update_time'])
        return to_json_data(errmsg='更新成功')


class BannerAddView(View):
    """
    /admin/banners/add/
    """
    def get(self, request):
        """
        展示轮播图添加
        :param request:
        :return:
        """
        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')).filter(is_delete=False).order_by('-num_news', 'update_time')
        priority_dict = OrderedDict(models.Banner.PRI_CHOICES)

        return render(request, 'admin/news/news_banner_add.html', locals())

    def post(self, request):
        """
        添加轮播图
        :param request:
        :return:
        """
        json_data = request.body
        if not json_data:
            return to_json_data()
        dict_data = json.loads(json_data.decode('utf-8'))

        try:
            news_id = int(dict_data.get('news_id'))
            if not models.News.objects.only('id').filter(id=news_id).exists():
                to_json_data(errno=Code.PARAMERR, errmsg='文章不存在')

        except Exception as e:
            logger.info('前端传过来的文章id参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in models.Banner.PRI_CHOICES]
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='轮播图的优先级设置错误')

        except Exception as e:
            logger.info('轮播图优先级异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图的优先级设置错误')

        image_url = dict_data.get('image_url')
        if not image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图url为空')

        banner, is_created = models.Banner.objects.get_or_create(news_id=news_id)
        if is_created:
            banner.image_url = image_url
            banner.priority = priority
            banner.save(update_fields=['priority', 'image_url', 'update_time'])
            return to_json_data(errmsg="轮播图创建成功")
        else:
            return to_json_data(errno=Code.DATAEXIST, errmsg='数据已存在')


# 文档管理，删除，修改，添加
class DocsManageView(View):

    def get(self, request):
        docs = Doc.objects.only('id', 'title', 'create_time').filter(is_delete=False)
        return render(request, 'admin/doc/docs_manage.html', locals())


class DocsEditView(View):

    def get(self, request, doc_id):
        doc = Doc.objects.only('id').filter(id=doc_id).first()
        if doc:
            return render(request, 'admin/doc/docs_pub.html', locals())
        else:
            raise Http404('需要更新得文档不存在')

    def delete(self, request, doc_id):
        doc = Doc.objects.only('id').filter(id=doc_id).first()
        if doc:
            doc.is_delete = True
            doc.save(update_fields=['is_delete'])
            return to_json_data(errmsg='文档删除成功')
        else:
            to_json_data(errno=Code.PARAMERR, errmsg='需要删除的文档不存在')

    def put(self, request, doc_id):
        doc = Doc.objects.only('id').filter(is_delete=False, id=doc_id).first()
        if not doc:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的文档不存在')

        json_dict = request.body
        if not json_dict:
            return to_json_data()
        dict_date = json.loads(json_dict.decode('utf-8'))

        form = forms.DocsPubForm(data=dict_date)
        if form.is_valid():
            doc.title = form.cleaned_data.get('title')
            doc.desc = form.cleaned_data.get('desc')
            doc.file_url = form.cleaned_data.get('file_url')
            doc.image_url = form.cleaned_data.get('image_url')
            doc.save()
            return to_json_data(errmsg='文档更新成功')

        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class DocsPubView(View):
    """
    文档上传
    /admin/docs/pub/
    """
    def get(self, request):
        return render(request, 'admin/doc/docs_pub.html')

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        # django内置表单验证
        form = forms.DocsPubForm(data=dict_data)
        if form.is_valid():
            # 未存储到数据库 先提交成一个对象
            docs_instance = form.save(commit=False)
            # 给数据对象的author字段赋值
            docs_instance.author_id = request.user.id
            # 保存
            docs_instance.save()
            return to_json_data(errmsg='文档创建成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class DocsUploadFile(View):
    """
    文档上传到fdfs
    /admin/docs/files/
    """

    def post(self, request):
        text_file = request.FILES.get('text_file')
        if not text_file:
            logger.info('从前端获取文件失败')
            return to_json_data(errno=Code.NODATA, errmsg='从前端获取文件失败')

        if text_file.content_type not in ('application/octet-stream', 'application/pdf',
                                          'application/zip', 'text/plain', 'application/x-rar'):
            return to_json_data(errno=Code.DATAERR, errmsg='不能上传非文本文件')

        try:
            text_ext_name = text_file.name.split('.')[-1]
        except Exception as e:
            logger.info('文件拓展名异常：{}'.format(e))
            text_ext_name = 'pdf'

        try:
            upload_res = FDFS_Client.upload_by_buffer(text_file.read(), file_ext_name=text_ext_name)
        except Exception as e:
            logger.error('文件上传出现异常：{}'.format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg='文件上传异常')
        else:
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('文件上传到FastDFS服务器失败')
                return to_json_data(Code.UNKOWNERR, errmsg='文件上传到服务器失败')
            else:
                text_name = upload_res.get('Remote file_id')
                text_url = settings.FASTDFS_SERVER_DOMAIN + text_name
                return to_json_data(data={'text_file': text_url}, errmsg='文件上传成功')


# 课程管理，删除，修改，添加
class CourseManageView(View):
    """
    课程管理
    /admin/courses/
    """
    def get(self, request):
        courses = Course.objects.select_related('category', 'teacher').only('id', 'category__name', 'teacher__name').filter(is_delete=False)
        return render(request, 'admin/course/courses_manage.html', locals())


class CourseEditView(View):
    """
    课程编辑，删除
    """
    def get(self, request, course_id):
        """
        展示修改和添加
        :param request:
        :param course_id:
        :return:
        """
        course = Course.objects.only('id').filter(is_delete=False, id=course_id).first()
        if course:
            categories = CourseCategory.objects.only('id', 'name').filter(is_delete=False)
            teachers = Teacher.objects.only('id', 'name').filter(is_delete=False)
            return render(request, 'admin/course/course_pub.html', locals())
        else:
            return Http404('课程不存在')

    def delete(self, request, course_id):
        """
        删除
        :param request:
        :param course_id:
        :return:
        """
        course = Course.objects.only('id').filter(is_delete=False, id=course_id).first()
        if course:
            course.is_delete = True
            course.save(update_fields=['is_delete', 'update_time'])
            return to_json_data(errmsg='课程删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='更新的课程不存在')

    def put(self, request, course_id):
        """
        更新
        :param request:
        :param course_id:
        :return:
        """
        # 判断有没有这个课程
        course = Course.objects.only('id').filter(is_delete=False, id=course_id).first()
        if not course:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的课程不存在')

        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_date = json.loads(json_data.decode('utf-8'))

        # 内置表单认证
        form = forms.CoursesPubForm(data=dict_date)
        if form.is_valid():
            # 取出认证完成的数据{'cover_url': xxxxx, 'image_url': xxxxx}
            # 设置类属性的方式  将遍历出来的 key和value设置到course中
            for attr, value in form.cleaned_data.items():
                setattr(course, attr, value)
            # 保存
            course.save()
            return to_json_data(errmsg='课程更新成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class CoursePubView(View):
    """
    课程发布
    /admin/courses/pub/
    """
    def get(self, request):
        """
        展示发布页
        :param request:
        :return:
        """
        teachers = Teacher.objects.only('id', 'name').filter(is_delete=False)
        categories = CourseCategory.objects.only('id', 'name').filter(is_delete=False)
        return render(request, 'admin/course/course_pub.html', locals())

    def post(self, request):
        """
        课程发布
        :param request:
        :return:
        """
        json_data = request.body
        if not json_data:
            return to_json_data()
        dict_data = json.loads(json_data.decode('utf-8'))

        form = forms.CoursesPubForm(data=dict_data)
        if form.is_valid():
            course_instance = form.save(commit=False)
            course_instance.save()
            return to_json_data(errmsg='课程发布成功')

        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)