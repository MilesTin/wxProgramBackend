from django.shortcuts import render
from account.models import *
from order.models import *
from .models import *
from django.shortcuts import redirect,get_object_or_404
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from order.models import *
from order.views import calRate
from django.core.exceptions import ObjectDoesNotExist

class serializeType(DjangoJSONEncoder):
    def default(self, o, Type=type(None),*fields):
        ret_value = {}
        if type(o)==Type and o:
            for key in fields:
                value = getattr(o, key)
                if isinstance(value, str):
                    ret_value[key] = value
                elif type(value) == type(None):
                    ret_value[key] = ''
                elif type(value) == int:
                    ret_value[key] = value
                elif type(value)==bool:
                    ret_value[key] = value
                else:
                    serializeValue = super().default(value)
                    ret_value[key] = serializeValue
            return str(ret_value)

        elif type(o) == str:
            return o
        elif type(o) == None:
            return ''
        return super().default(o)

serializer = serializeType()

@csrf_exempt
def toComment(request):
    #method post
    openid = request.session.get("openid","")

    cur_user = get_object_or_404(user,openid=openid)
    if request.method=='POST':
        orderid = request.POST.get("orderid","")
        cur_order = get_object_or_404(order,orderid=orderid)
        if cur_order.order_status != order.completed:
            return JsonResponse({"msg":"订单未完成不能评价"},status=404)
        star = request.POST.get("star","")
        try:
            star = int(star)
        except ValueError:
            return JsonResponse({"msg":"star字段有问题"},status=404)
        text = request.POST.get("text","")

        if cur_order.order_owner == cur_user:
            try:
                if cur_order.comment.owner_commented:
                    return JsonResponse({"msg":"你已评价"},status=404)
                else:
                    commentObj = cur_order.comment
                    commentObj.owner_star = star
                    commentObj.owner_text = text
                    commentObj.owner_commented = True
                    commentObj.save()
                    calRate(cur_order.free_lancer)  # 计算小哥评分
                    return JsonResponse({"msg": "评价成功"})
            except ObjectDoesNotExist as e:
                print(e)
                commentObj = comment()

                commentObj.owner_text = text
                commentObj.owner_star = star
                commentObj.owner_commented = True
                commentObj.order = cur_order
                commentObj.save()
                calRate(cur_order.free_lancer)#计算小哥评分

                return JsonResponse({"msg":"评价成功"})
        elif cur_order.free_lancer == cur_user:
            try:
                if cur_order.comment.lancer_commented:
                    return JsonResponse({"msg": "你已评价"}, status=404)
                else:
                    commentObj = cur_order.comment
                    commentObj.lancer_star = star
                    commentObj.lancer_text = text
                    commentObj.lancer_commented = True
                    commentObj.save()
                    calRate(cur_order.order_owner)  # 计算主人评分
                    return JsonResponse({"msg": "评价成功"})
            except ObjectDoesNotExist as e:
                print(e)
                commentObj = comment()
                commentObj.lancer_text = text
                commentObj.lancer_star = star
                commentObj.lancer_commented = True
                commentObj.order = cur_order
                commentObj.save()
                calRate(cur_order.order_owner)  # 计算主人评分
                return JsonResponse({"msg": "评价成功"})
    else:
        return JsonResponse({"msg":"请使用POST"},status=404)


def get_comment(request):
    orderid = request.GET.get("orderid")
    cur_order = get_object_or_404(order,orderid=orderid)

    if cur_order.order_status != cur_order.completed:
        return JsonResponse({"msg":"订单未完成"})
    else:
        commentObj = cur_order.comment
        return JsonResponse({"orderid":orderid,"comment":serializer.default(commentObj,type(comment()),*["owner_star","lancer_star","owner_text","lancer_text","owner_commented","lancer_commented"])})


