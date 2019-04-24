from django.urls import path, re_path
from . import views


app_name = 'veriftions'

urlpatterns = [
    path('image_codes/<uuid:image_code_id>/', views.ImageCode.as_view(), name='image_codes'),
    re_path('usernames/(?P<username>\w{5,20})/', views.ChickUsernameView.as_view(), name='chick_username')
]