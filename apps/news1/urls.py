from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('news/', views.NewsListView.as_view(), name='news'),
    path('news/banners/', views.NewsBannerView.as_view(), name='banner_news'),
    path('news/<int:news_id>/', views.NewsDetailView.as_view(), name='detail_news'),
    path('news/<int:news_id>/comments/', views.NewsCommentView.as_view(), name='comment_news'),
    path('search/', views.NewsSearchView(), name='search')
]