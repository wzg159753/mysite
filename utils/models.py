from django.db import models


class ModelBase(models.Model):
    """
    模型基类 用于存放共有字段
    """
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    is_delete = models.BooleanField(verbose_name='软删除', default=False)

    class Meta:
        # 自定义抽象类，数据迁移时忽略此类
        abstract = True