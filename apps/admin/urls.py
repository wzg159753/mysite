from django.urls import path
from . import views


app_name = 'admin'

urlpatterns = [
    # 后台admin首页面
    path('', views.IndexView.as_view(), name='index'),

    # 文章标签
    path('tags/', views.TagManageView.as_view(), name='tags'),
    path('tags/<int:tag_id>/', views.TagEditView.as_view(), name='tag_edit'),

    # 热门新闻
    path('hotnews/', views.HotNewsManageView.as_view(), name='hotnews'),
    path('hotnews/<int:hotnews_id>/', views.HotNewsEditView.as_view(), name='hotnews_edit'),
    path('hotnews/add/', views.HotNewsAddView.as_view(), name='hotnews_add'),
    path('tags/<int:tag_id>/news/', views.NewsByTagIdView.as_view(), name='news_by_tagid'),

    # 文章管理
    path('news/', views.NewsManageView.as_view(), name='news_manage'),

    # 文章添加
    path('news/pub/', views.NewsPubView.as_view(), name='news_pub'),
    path('news/images/', views.NewsUploadImageView.as_view(), name='upload_image'),

    # 获取七牛云token
    path('token/'),

    # 富文本编辑器图片上传
    path('markdown/images', views.MarkDownUploadImage.as_view(), name='markdown_image_upload')

]