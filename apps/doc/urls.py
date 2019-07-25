from django.urls import path

from . import views


app_name = 'doc'

urlpatterns = [
    path('doc/', views.doc_index, name='download'),
    path('doc/<int:doc_id>/', views.DocDownload.as_view(), name='download_doc'),
    path('doc/spider/', views.SpiderDownloadView.as_view(), name='download_spider')
]