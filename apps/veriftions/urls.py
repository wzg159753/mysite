from django.urls import path, re_path
from . import views


app_name = 'veriftions'

urlpatterns = [
    path('image_codes/<uuid:image_code_id>/', views.ImageCode.as_view(), name='image_codes'), # 返回图片验证码
    re_path('usernames/(?P<username>\w{5,20})/', views.CheckUsernameView.as_view(), name='chick_username'), # 验证用户名是否存在
    re_path('mobiles/(?P<mobile>1[3-9]\d{9})', views.CheckMobileView.as_view(), name='mobile') # 验证手机号是否存在
]