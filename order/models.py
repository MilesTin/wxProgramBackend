from django.db import models
from account.models import user
# Create your models here.


class order(models.Model):
    value_low = 0
    value_middle = 1
    value_high = 2

    value_choices = (
        (value_low,"low value"),
        (value_middle,"normal value"),
        (value_high,"high value"),
    )

    onehour = 1
    sixhour = 6
    oneday = 24
    twoday = 48
    threeday = 72

    expireTime_choices = (
        (onehour,"one hour"),
        (sixhour,"six hour"),
        (oneday,"one day"),
        (twoday,"two day"),
        (threeday,"three day")
    )

    weijiedan = 0#未接单
    completed = 1#已完成
    owner_canceled = 2
    lancer_canceled = 3
    jiedan = 4#已接单

    order_status_choices = (
        (weijiedan,"no free lancer"),
        (completed,"completed"),
        (owner_canceled,"owner canceled"),
        (lancer_canceled,"lancer canceled"),
        (jiedan, "has a lancer"),
    )
    orderid = models.CharField(max_length=30,unique=True,primary_key=True)
    value = models.IntegerField("价值",choices=value_choices)
    createTime = models.DateTimeField(auto_now_add=True)
    expireTime = models.IntegerField("过期时长",choices=expireTime_choices)#hour

    order_owner = models.ForeignKey(user,verbose_name="订单主人",null=True,blank=True,on_delete=models.SET_NULL,related_name="owner_orders")
    #接订单的人
    free_lancer = models.ForeignKey(user,verbose_name="小哥",null=True,blank=True,on_delete=models.SET_NULL,related_name="lancer_orders")
    #酬劳
    money = models.FloatField(default=0,verbose_name="酬劳")
    #地点
    pos = models.CharField(verbose_name="地点",max_length=256)

    kuaidi = models.CharField(verbose_name="快递商",max_length=256)

    recieved_pos = models.CharField(verbose_name="收货地址",max_length=256)

    order_status = models.IntegerField(verbose_name="订单状态",choices=order_status_choices)

    #hidden infor
    phone_number = models.CharField(verbose_name="电话号码",max_length=11)
    #取件码
    code = models.CharField(verbose_name="取件码",max_length=64)
    #收货人姓名
    owner_name = models.CharField(verbose_name="主人名",max_length=256)