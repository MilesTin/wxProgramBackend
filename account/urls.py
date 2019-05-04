from django.urls import include, path
from .views import *

urlpatterns = [
    path("login/", login, name="account"),
    path("logout/", logout, name="logout"),
    path("login2/",login2,name="login2"),
    path("index/",index,name="index")
]