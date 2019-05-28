from django.db import models
from account.models import *
# Create your models here.

class feedback(models.Model):
    text = models.TextField(verbose_name="反馈内容",null=True,blank=True,default="")
    owner = models.ForeignKey(user,verbose_name="反馈的用户",on_delete=models.CASCADE)
    time = models.DateTimeField("反馈时间",auto_now_add=True)

    class Meta:
        verbose_name_plural = "反馈s"
        verbose_name = "反馈"