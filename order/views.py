from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.core.exceptions import *
from django.shortcuts import get_object_or_404
from django.core.serializers import serialize
from account.views import serializeUser
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
# Create your views here.
"""
    bug:expireTime应改为datetime,新订单时创建
    
"""
userSerializer = serializeUser()

def orderStatusUpdate():
    for order_obj in order.objects.all():
        if order_obj.expireDateTime<timezone.now():
            order_obj.order_status = order.expired
            order_obj.save()

def search(request):
    #不验证是否登录
    #search也不一定需要 搜索的关键字可以是快递商种类，地址
    #每次返回10个订单
    orderStatusUpdate()#更新数据库状态
    search = request.GET.get("search","")
    page = request.GET.get("page","")
    try:
        page = int(page)
    except ValueError as e:
        print(e)
        return JsonResponse({"msg":"page字段有问题"},status=404)

    results = order.objects.filter(order_status=order.incompleted).values(*["orderid","createTime","money","pos","kuaidi","expireDateTime",])
    results = [_ for _ in results  if search in _.recieved_pos or search in _.kuaidi]

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
    results = results[10*page:10*(page+1)]
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
    ret_keys = ["orderid", "value", "createTime", "expireDateTime", "order_owner", "money", "pos",
                  "kuaidi","order_status",]
    if user_exists and (ret_order.free_lancer == cur_user or ret_order.order_owner==cur_user):
        ret_keys.append(["hidden_info","free_lancer","recieved_pos"])

    ret_values = {}

    fields = ("wx_name","openid","head_img")
    for key in ret_keys:
        value = getattr(ret_order,key)
        if type(value)==type(user()):
            serializedValue = userSerializer.default(value,*fields)
            # print("serializedValue:",serializedValue)
            ret_values[key] = serializedValue
        else:
            ret_values[key] = value
    print(ret_values)
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
            newOrder.order_status = order.incompleted
            newOrder.order_owner = cur_user
            newOrder.hidden_info = hidden_info
            newOrder.expireDateTime = datetime.today() + timedelta(hours=expireTime)
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
        return JsonResponse({"msg":"请绑定手机号"},status=404)
    elif cur_user.received_order_count<=0:
        return JsonResponse({"msg":"你已有10个订单"},status=404)
    elif cur_user.status == user.banned:
        return JsonResponse({"msg":"被禁止用户"},status=404)
    elif not cur_user.studentId or not cur_user.stuIdPwd:
        return JsonResponse({"msg":"未绑定学号"},status=404)
    else:
        cur_order.free_lancer = cur_user
        cur_order.save()
        cur_user.received_order_count -= 1
        return JsonResponse({"msg":"领取订单成功"})

def cancelOrder(request):
    openid = request.session.get("openid","")
    orderid = request.GET.get("orderid","")
    cur_user = get_object_or_404(user,openid=openid)
    cur_order = get_object_or_404(order,orderid=orderid)
    if cur_order.order_owner==cur_user:
        cur_order.order_status = order.canceled
        return JsonResponse({"msg":"取消成功"})
    if cur_order.free_lancer==cur_user:
        return JsonResponse({"msg":"请联系订单主人协商后由主人取消"},status=404)

    return JsonResponse({"msg":"你无权取消"},status=404)

def orderComplete(request):
    openid = request.GET.get("openid","")
    orderid = request.GET.get("orderid","")
    cur_user = get_object_or_404(user, openid=openid)
    cur_order = get_object_or_404(order, orderid=orderid)
    if cur_order.order_owner==cur_user:
        cur_order.order_status = order.completed
        return JsonResponse({"msg":"确认成功"})
    if cur_order.free_lancer==cur_user:
        return JsonResponse({"msg":"请联系订单主人后由主人确认"},status=404)

    return JsonResponse({"msg":"你无权确认完成订单"},status=404)
