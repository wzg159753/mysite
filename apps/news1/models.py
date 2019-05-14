from django.db import models

from utils.models import ModelBase
# Create your models here.


class Tag(ModelBase):
    """
    标签模型
    name: 标签名
    """
    name = models.CharField(max_length=64, verbose_name="标签名", help_text="标签名")

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_tag"  # 指明数据库表名
        verbose_name = "新闻标签"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.name


class News(ModelBase):
    """
    文章模型
    title: 文章标题
    digest: 文章摘要
    content: 文章内容
    clicks: 点击量
    image_url: 文章图片url路径
    tag: 外键关联的标签 foreginkey在多的那张表
    author: 外键关联的用户
    """
    title = models.CharField(max_length=150, verbose_name="标题", help_text="标题")
    digest = models.CharField(max_length=200, verbose_name="摘要", help_text="摘要")
    content = models.TextField(verbose_name="内容", help_text="内容")
    clicks = models.IntegerField(default=0, verbose_name="点击量", help_text="点击量")
    image_url = models.URLField(default="", verbose_name="图片url", help_text="图片url")
    tag = models.ForeignKey('Tag', on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey('users.Users', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_news"  # 指明数据库表名
        verbose_name = "新闻"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.title


class Comments(ModelBase):
    """
    评论模型
    content: 评论内容
    author: 谁评论的 外键关联Users表
    news: 哪个文章被评论 外键关联文章表
    """
    content = models.TextField(verbose_name="内容", help_text="内容")

    author = models.ForeignKey('users.Users', on_delete=models.SET_NULL, null=True)
    news = models.ForeignKey('News', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_comments"  # 指明数据库表名
        verbose_name = "评论"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return '<评论{}>'.format(self.id)


class HotNews(ModelBase):
    """
    热门文章表
    news: 一对一关联哪个文章
    priority: 优先级
    """
    PRI_CHOICES = [
        (1, '第一级'),
        (2, '第二级'),
        (3, '第三级')
    ]

    news = models.OneToOneField('News', on_delete=models.CASCADE)
    # 限制范围choices，中能从绑定的列表中选择
    priority = models.IntegerField(choices=PRI_CHOICES, verbose_name="优先级", help_text="优先级", default=3)

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_hotnews"  # 指明数据库表名
        verbose_name = "热门新闻"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return '<热门新闻{}>'.format(self.id)


class Banner(ModelBase):
    """
    轮播图模型
    image_url: 大图的url路径
    priority: 优先级
    news: 哪个文章， 一对一关联对应的文章
    """
    PRI_CHOICES = [
        (1, '第一级'),
        (2, '第二级'),
        (3, '第三级'),
        (4, '第四级'),
        (5, '第五级'),
        (6, '第六级')
    ]

    image_url = models.URLField(verbose_name="轮播图url", help_text="轮播图url")
    priority = models.IntegerField(choices=PRI_CHOICES, verbose_name="优先级", help_text="优先级", default=6)
    news = models.OneToOneField('News', on_delete=models.CASCADE)

    class Meta:
        ordering = ['priority', '-update_time', '-id']
        db_table = "tb_banner"  # 指明数据库表名
        verbose_name = "轮播图"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return '<轮播图{}>'.format(self.id)