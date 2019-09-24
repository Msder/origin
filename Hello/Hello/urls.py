"""BiShe URL Configuration

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
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', views.main),
    url(r'login/', views.login),
    url(r'register/', views.register),
    url(r'^pc-geetest/register', views.get_geetest),
    #checkUser用来注册时实时判断用户名是否已经存在
    url(r'checkUser/', views.checkUser),
    #logout用来登出
    url(r'logout/', views.logout),
    #loginData传输登录数据
    url(r'loginData/', views.loginData),
    #listUser列出所有用户来修改他们的权限
    url(r'listUser/', views.listUser),
    url(r'personalCenter/', views.personalCenter),
    url(r'uploadRegisterData/', views.uploadRegisterData),
    #修改权限
    url(r'changeThePower/', views.changeThePower),
    url(r'setQuestion/', views.setQuestion),
    #uploadQuestions用来显示提交数据页面
    url(r'uploadQuestion/', views.uploadQuestion),
    #uploadSingle用来上传单选
    url(r'uploadSingle/', views.uploadSingle),
    url(r'uploadMultiple/', views.uploadMultiple),
    url(r'uploadJundge/', views.uploadJudge),
    url(r'editInfo/', views.editInfo),
    url(r'uploadInfo/', views.uploadInfo),
    path(r'infoPage/<int:id>/', views.infoPage),
    url(r'testPage/', views.testPage),

    path(r'changePage/<int:page>/', views.changePage),

    #这是为了上传题目种类以组成试卷的url
    url(r'uploadPageSetting/', views.uploadPageSetting),

    url(r'choosePage/', views.choosePage),

    #这是申请测试的
    path(r'needTest/<int:id>/', views.needTest),

    #这是上传试卷答案的
    url(r'uploadAnswer/', views.uploadAnswer),
]
