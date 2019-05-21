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

def getOrder(request):#获得某个订单的具体信息
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

def sendOrder(request):
    if request.method=='POST':
        openid = request.session.get("openid")
        cur_user = get_object_or_404(openid=openid)
        value = request.POST.get("value","")
        hidden_info = request.POST.get("hidden_info","")
        orderid = request.POST.get('orderid',"")
        expireTime = request.POST.get("expireTime","")
        money = request.POST.get('money',"")
        pos = request.POST.get("pos","")
        kuaidi = request.POST.get("kuaidi","")
        received_pos = request.POST.get('received_pos',"")
        try:
            value = int(value)
            expireTime = int(expireTime)
            money = float(expireTime)
        except ValueError as e:
            print(e)
            return JsonResponse({"msg":"字段有错误"},status=404)

        if not cur_user or not hidden_info or not orderid or not (expireTime in [x[0] for x in order.expireTime_choices]) or not money or not pos or not kuaidi or not received_pos or not (value in [x[0] for x in order.value_choices]):
            return JsonResponse({"msg":"字段不全"},status=404)
        else:
            if cur_user.sended_order_count<=0:
                return JsonResponse({"msg":"你已有10个订单，到达额度"},status=404)
            cur_user.sended_order_count -= 1
            cur_user.save()
            newOrder = order()
            newOrder.order_owner = cur_user
            newOrder.hidden_info = hidden_info
            newOrder.expireTime = expireTime
            newOrder.value = value
            newOrder.money = money
            newOrder.pos = pos
            newOrder.kuaidi = kuaidi
            newOrder.recieved_pos = received_pos
            newOrder.save()
            return JsonResponse({"msg":"创建订单成功"})
    else:
        return JsonResponse({"msg":"请使用post"},status=406)#not acceptable

def receiveOrder(request):
    #需要登录
    """
    :param request:
    :param orderid:
    :return:
    """
    openid = request.session.get("openid")
    orderid = request.GET.get("orderid")
    cur_user = get_object_or_404(user,openid=openid)
    cur_order = get_object_or_404(order,orderid=orderid)
    if not cur_user.phone:
        return JsonResponse({"msg":"请绑定手机号"})
    elif cur_user.received_order_count<=0:
        return JsonResponse({"msg":"你已有10个订单"})
    elif cur_user.status == user.banned:
        return JsonResponse({"msg":"被禁止用户"})
    elif not cur_user.studentId or not cur_user.stuIdPwd:
        return JsonResponse({"msg":"未绑定学号"})
    else:
        cur_order.free_lancer = cur_user
        cur_order.save()
        cur_user.received_order_count -= 1
        return JsonResponse({"msg":"领取订单成功"})

