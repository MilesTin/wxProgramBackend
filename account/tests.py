from django.test import TestCase
from .views import *
from .models import *
from order.models import *
# Create your tests here.

orderObj = order.objects.all()[0]
class test_serialize(TestCase):

    def test_order_user_serialize(self):
        print(orderObj)
        orderFields = ["orderid", "value", "createTime", "expireTime", "order_owner", "free_lancer", "money", "pos",
                       "kuaidi", "recieved_pos", "hidden_info"]
        userFields = ["openid", "wx_name", "phone", "studentId"]
        value = order_user_Serializer(orderObj,orderFields,userFields)
        print(value)