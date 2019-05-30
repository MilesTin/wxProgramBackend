from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.core.exceptions import *
from django.shortcuts import get_object_or_404
from django.core.serializers import serialize
from account.views import serializeUser
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from comment.models import *
# Create your views here.

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

    results = order.objects.filter(order_status=order.incompleted,free_lancer=None).values(*["orderid","createTime","money","pos","received_pos","kuaidi","expireDateTime",])

    results = [_ for _ in results if search in _['pos'] or search in _["received_pos"] or search in _["kuaidi"] ]

    orderByTime = request.GET.get("orderByTime",'')
    orderByPrice = request.GET.get("orderByPrice",'')

    if orderByTime:
        results.sort(key = lambda x: x['createTime'],reverse=True)
    if orderByTime=="-1":#时间最长的订单
        results.reverse()
    print(orderByTime)
    print(orderByPrice)
    if orderByPrice:
        results.sort(key=lambda x:x['money'],reverse=True)

    if orderByPrice=="-1":#价钱最小的订单
        results.reverse()

    if page<1:
        page = 1
    results = results[10*page-10:10*page]
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

@csrf_exempt
def sendOrder(request):
    if request.method=='POST':
        openid = request.session.get("openid")
        print("openid",openid)
        cur_user = get_object_or_404(user,openid=openid)
        value = request.POST.get("value",1)
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
            print("value:",value)
            print("expireTime",expireTime)
            return JsonResponse({"msg":"字段有错误"},status=404)
        try:
            cur_order = order.objects.get(orderid=orderid)
            return JsonResponse({"msg":"订单id重复"},status=404)
        except:
            pass
        if not cur_user or not hidden_info or not orderid or not expireTime or not money or not pos or not kuaidi or not received_pos or not (value in [x[0] for x in order.value_choices]):
            return JsonResponse({"msg":"字段不全"},status=404)
        else:
            if cur_user.sended_order_count<=0:
                return JsonResponse({"msg":"你已有10个订单，到达额度"},status=404)

            cur_user.sended_order_count -= 1

            newOrder = order()
            print(orderid,order.incompleted,cur_user,hidden_info,timezone.now()+timedelta(hours=expireTime),value,money,pos,kuaidi,received_pos)
            newOrder.orderid = orderid
            newOrder.order_status = order.incompleted
            newOrder.order_owner = cur_user
            newOrder.hidden_info = hidden_info
            newOrder.expireDateTime = timezone.now() + timedelta(hours=expireTime)
            newOrder.value = value
            newOrder.money = money
            newOrder.pos = pos
            newOrder.kuaidi = kuaidi
            newOrder.recieved_pos = received_pos
            newOrder.save()
            cur_user.save()
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
    # if not cur_user.phone:
    #     return JsonResponse({"msg":"请绑定手机号"},status=404)
    if cur_user.received_order_count<=0:
        return JsonResponse({"msg":"你已有10个订单"},status=404)
    elif cur_user.status == user.banned:
        return JsonResponse({"msg":"被禁止用户"},status=404)
    elif not cur_user.studentId or not cur_user.stuIdPwd:
        return JsonResponse({"msg":"未绑定学号"},status=404)
    elif cur_order.free_lancer:
        return JsonResponse({"msg":"该订单已经有人领单"},status=404)
    else:
        cur_order.free_lancer = cur_user
        cur_user.received_order_count -= 1
        cur_order.save()
        return JsonResponse({"msg":"领取订单成功"})

def cancelOrder(request):
    openid = request.session.get("openid","")
    orderid = request.GET.get("orderid","")
    cur_user = get_object_or_404(user,openid=openid)
    cur_order = get_object_or_404(order,orderid=orderid)
    if cur_order.order_owner==cur_user:
        if cur_order.order_status==order.canceled:
            return JsonResponse({"msg":"订单早已取消"},status=404)
        elif cur_order.order_status!=order.incompleted:
            return JsonResponse({"msg":"订单已完成或过期不能取消"},status=404)
        cur_order.order_status = order.canceled
        cur_user.sended_order_count += 1
        lancer_user = cur_order.free_lancer
        lancer_user.received_order_count += 1
        lancer_user.save()
        cur_user.save()
        cur_order.save()
        return JsonResponse({"msg":"取消成功请重新发起订单"})
    if cur_order.free_lancer==cur_user:
        return JsonResponse({"msg":"请联系订单主人协商后由主人取消"},status=404)

    return JsonResponse({"msg":"你无权取消"},status=404)


def calRate(cur_user:user):
    owner_orders = order.objects.filter(order_owner=cur_user)
    lancer_orders = order.objects.filter(free_lancer=cur_user)
    orders_count = len(owner_orders) + len(lancer_orders)

    rateSum = 0
    count = 0
    for orderObj in owner_orders:
        try:
            commentObj = comment.objects.get(order=orderObj)
            if commentObj.lancer_commented:
                rateSum += commentObj.lancer_star
                count += 1
        except ObjectDoesNotExist:
            continue
    for orderObj in lancer_orders:
        try:
            commentObj = comment.objects.get(order=orderObj)
            if commentObj.owner_commented:
                rateSum += commentObj.owner_star
                count += 1
        except ObjectDoesNotExist:
            continue
    try:
        rate = rateSum/count
    except ZeroDivisionError:
        rate = 5.0
    cur_user.rate = rate
    cur_user.save()
    return rate
def orderComplete(request):
    openid = request.session.get("openid","")
    orderid = request.GET.get("orderid","")
    cur_user = get_object_or_404(user, openid=openid)
    cur_order = get_object_or_404(order, orderid=orderid)
    if cur_order.order_owner==cur_user:
        if cur_order.order_status==order.completed:
            return JsonResponse({"msg":"订单早已完成"},status=404)
        elif cur_order.order_status!=order.incompleted:
            return JsonResponse({"msg":"订单已取消或过期不能完成"},status=404)
        cur_order.order_status = order.completed
        cur_order.save()
        cur_user.sended_order_count+=1
        lancer_user = cur_order.free_lancer
        lancer_user.received_order_count += 1

        cur_user.save()
        lancer_user.save()
        return JsonResponse({"msg":"完成订单确认成功"})
    if cur_order.free_lancer==cur_user:
        return JsonResponse({"msg":"请联系订单主人后由主人确认"},status=404)

    return JsonResponse({"msg":"你无权确认完成订单"},status=404)