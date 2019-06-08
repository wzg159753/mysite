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
    文章分类展示
    /admin/tags/
    """
    def get(self, request):
        # 查询Tag与news关联，用聚合分组查出tag标签里面的文章数量，对数量进行排序
        tags = models.Tag.objects.select_related('news').values('id', 'name').annotate(nums=Count('news')).order_by('-nums', 'update_time')
        return render(request, 'admin/news/tags_manage.html', locals())


class TagEditView(View):
    """
    标签编辑，删除
    /admin/tags/tag_id/
    """
    def delete(self, request, tag_id):
        """
        删除标签
        :param request:
        :param tag_id:
        :return:
        """
        # 先查出这个字段，如果有这个字段才能删除
        tag = models.Tag.objects.only('id').filter(id=tag_id, is_delete=False).first()
        if tag:
            tag.is_delete = True
            # 数据库保存优化操作，默认save是将每个字段不管改没改，都保存一遍，
            # update_fields是将列表中的字段保存
            tag.save(update_fields=['is_delete'])
            # 局部刷新，用ajax，返回json数据
            return to_json_data(errmsg='标签删除成功')

        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='标签不存在')

    def put(self, request, tag_id):
        """
        修改标签
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
                tag.save(update_fields=['name'])
                return to_json_data(errmsg='标签修改成功')
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg='标签重复')

        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='标签不存在')

