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
    path('news/<int:new_id>/', views.NewsEditView.as_view(), name='news_edit'),
    path('news/pub/', views.NewsPubView.as_view(), name='news_pub'),
    path('news/images/', views.NewsUploadImageView.as_view(), name='upload_image'),

    # 获取七牛云token
    path('token/', views.UploadToken.as_view(), name='upload_token'),

    # 富文本编辑器图片上传
    path('markdown/images', views.MarkDownUploadImage.as_view(), name='markdown_image_upload'),

    # 轮播图 管理 删除 修改 添加
    path('banners/', views.BannerManageView.as_view(), name='banners_manage'),
    path('banners/<int:banner_id>/', views.BannerEditView.as_view(), name='banners_edit'),
    path('banners/add/', views.BannerAddView.as_view(), name='banners_add'),

    # 文档管理 删除 修改 添加
    path('docs/', views.DocsManageView.as_view(), name='docs_manage'),
    path('docs/<int:doc_id>/', views.DocsEditView.as_view(), name='docs_edit'),
    path('docs/pub/', views.DocsPubView.as_view(), name='docs_pub'),
    path('docs/files/', views.DocsUploadFile.as_view(), name='upload_text'),

    # 在线课堂管理，删除 修改 添加
    path('courses/', views.CourseManageView.as_view(), name='courses_manage'),
    path('courses/<int:course_id>/', views.CourseEditView.as_view(), name='courses_edit'),
    path('courses/pub/', views.CoursePubView.as_view(), name='courses_pub'),

    # 组管理，删除，添加, 编辑
    path('groups/', views.GroupManageView.as_view(), name='groups_manage'),
    path('groups/<int:group_id>/', views.GroupEditView.as_view(), name='groups_edit'),

]