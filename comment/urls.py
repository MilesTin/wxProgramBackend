from django.urls import path,include
from .views import *


urlpatterns = [
    path("toComment",toComment,name="toComment"),
    path("getComment",get_comment,name="getComment"),
]