from django.urls import include,path
from .views import  *

urlpatterns = [
    path("doFeedBack",doFeedBack,name="doFeedBack"),

]