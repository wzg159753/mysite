from django.urls import path

from . import views


app_name = 'user'
urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('reg/', views.RegisterView.as_view(), name='register')
]