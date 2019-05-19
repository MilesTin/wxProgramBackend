from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.core.exceptions import *
from django.shortcuts import get_object_or_404
# Create your views here.

def search(request):
    #不验证是否登录
    #search也不一定需要 搜索的关键字可以是快递商种类，地址
    search = request.GET.get("search","")

    results = order.objects.filter(order_status=order.incompleted).values(*["orderid","value","createTime","expireTime","order_owner","free_lancer","money","pos","kuaidi","recieved_pos"])
    results = [_ for _ in results if search in _.pos or search in _.recieved_pos or search in _.kuaidi]

    orderByTime = request.GET.get("orderbytime",'')
    orderByPrice = request.GET.get("orderbyprice",'')

    if orderByTime:
        results.sort(key = lambda x: x.createTime)
    if orderByTime=="-1":#时间最长的订单
        results.reverse()

    if orderByPrice:
        results.sort(key=lambda x:x.money)

    if orderByPrice=="-1":#价钱最小的订单
        results.reverse()

    return JsonResponse({'results':results},safe=False)

def getOrder(request):
    #还有一种是已经登录，并且是自己的订单
    openid = request.session.get("openid","")
    user_exists = True
    try:
        cur_user = user.objects.get(openid=openid)
    except user.DoesNotExist as e:
        user_exists = False

    orderid = request.GET.get("orderid")
    if not orderid:
        return JsonResponse({"msg":"orderid字段不存在"},status=404)

    ret_order = ""
    try:
        ret_order = order.objects.get(orderid=orderid)
    except order.DoesNotExist:
        ret_order = ""

    if not ret_order:
        return JsonResponse({"msg":"orderid"+orderid+"用户不存在"})
    ret_values = ["orderid", "value", "createTime", "expireTime", "order_owner", "free_lancer", "money", "pos",
                  "kuaidi", "recieved_pos","order_status"]
    if user_exists and (ret_order.free_lancer == cur_user or ret_order.order_owner==cur_user):
        ret_values.append("hidden_info")

    ret_values = {}
    for key in ret_values:
        ret_values[key] = ret_order[key]

    return JsonResponse({"order":ret_values},safe=False)

def newOrder(request):
    if request.method=='POST':
        openid = request.session.get("openid")
        cur_user = get_object_or_404(openid=openid)

    else:
        return JsonResponse({"msg":"请使用post"},status=406)#not acceptable
