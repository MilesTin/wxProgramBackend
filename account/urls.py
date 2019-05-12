from django.urls import include, path
from .views import *

urlpatterns = [
    path("login/", login, name="account"),
    path("logout/", logout, name="logout"),
    path("getCaptcha",getCaptcha,name="getCaptch"),#获得验证码
    path("verifStuId",verifStuId,name="verifStuId"),#绑定学号,学号验证

]