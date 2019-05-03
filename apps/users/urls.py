from django.urls import path

from . import views


app_name = 'user'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'), # 登录路由
    path('register/', views.RegisterView.as_view(), name='register'), # 注册路由
    path('logout/', views.LogoutView.as_view(), name='logout')
]