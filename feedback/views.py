from django.shortcuts import render
from django.shortcuts import render,get_object_or_404
from account.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *

# Create your views here.

@csrf_exempt
def doFeedBack(request):
    #需要登录 post
    openid = request.session.get("openid","")
    cur_user = get_object_or_404(user,openid=openid)
    print(cur_user)
    text = request.POST.get("text","")
    if len(text) < 10:
        return JsonResponse({"msg":"反馈太短"},status=404)
    else:
        feedBackObj = feedback()
        feedback.owner = cur_user
        feedback.text = text
        feedback.save()
        return JsonResponse({"msg":"反馈成功，我们会尽快处理"})

