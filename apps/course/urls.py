from django.urls import path

from . import views

app_name = 'course'

urlpatterns = [
    path('course/', views.course_index, name='course_index')
]