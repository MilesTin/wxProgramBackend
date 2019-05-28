from django.db import models
from order.models import order
# Create your models here.

class comment(models.Model):
    owner_star = models.IntegerField(verbose_name="主人评分",null=True,blank=True,default=5)
    owner_text = models.TextField("主人评价内容",null=True,blank=True,default="")
    order = models.OneToOneField(verbose_name="订单",to=order,on_delete=models.CASCADE,null=True,blank=True,default=None)
    lancer_star = models.IntegerField(verbose_name="小哥评分",null=True, blank=True, default=5)
    lancer_text = models.TextField(verbose_name="小哥评价内容",null=True, blank=True, default="")
    owner_commented = models.BooleanField(verbose_name="主人是否评价",default=False)
    lancer_commented = models.BooleanField(verbose_name="小哥是否评价",default=False)

    class Meta:
        verbose_name = "评价"
        verbose_name_plural = "评价s"
