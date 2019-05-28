from haystack import indexes
# from haystack import site

from .models import News


class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    """
    News索引数据模型类
    """
    # 这句话的意思是 document是否使用文件，use_template是否使用模板
    text = indexes.CharField(document=True, use_template=True)

    # 下面的意思是，方便操作，也可以不写，如果不写，要使用news实例的id为news.object.id
    # 如果写了 要使用就是 news.id
    id = indexes.IntegerField(model_attr='id')
    title = indexes.CharField(model_attr='title')
    digest = indexes.CharField(model_attr='digest')
    content = indexes.CharField(model_attr='content')
    image_url = indexes.CharField(model_attr='image_url')

    # comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类
        """
        return News

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集
        """
        # 就是返回那几类标签的所有数据
        # return self.get_model().objects.filter(is_delete=False, tag_id=1)
        return self.get_model().objects.filter(is_delete=False, tag_id__in=[1, 2, 3, 4, 5, 6])
