from django.urls import path

from . import views


app_name = 'doc'

urlpatterns = [
    path('', views.doc_index, name='download')
]