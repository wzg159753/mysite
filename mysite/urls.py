"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static # 自定义静态文件路径
from django.conf import settings

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('news1.urls')),
    path('', include('course.urls')),
    path('', include('doc.urls')),
    path('users/', include('users.urls')),
    path('', include('veriftions.urls')),
    path('admin/', include('admin.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# 固定写法 因为media是自定义的所以在前端找不到当前路径，配置了后就会找到