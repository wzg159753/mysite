import json
from django.shortcuts import render
from django.views import View
from django.db.models import Count

from news1 import models
# Create your views here.
from utils.json_func import to_json_data
from utils.res_code import Code, error_map



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

