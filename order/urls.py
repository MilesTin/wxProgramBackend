from django.urls import include,path
from .views import *

urlpatterns = [
    path("search/",search,name="search"),#GET 包含orderby,search
    path("getOrder/",getOrder,name="getOrder"),
    path("sendOrder/",sendOrder,name="sendOrder"),
    path("receiveOrder/",receiveOrder,name="receiveOrder"),
    path("cancelOrder/",cancelOrder,name="cancelOrder"),
    path("orderComplete",orderComplete,name="orderComplete"),
]