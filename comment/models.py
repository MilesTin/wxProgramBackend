from django.db import models
from order.models import order
# Create your models here.

class comment(models.Model):
    owner_star = models.IntegerField(null=True,blank=True,default=5)
    owner_text = models.TextField(null=True,blank=True,default="")
    order = models.OneToOneField(to=order,on_delete=models.CASCADE,null=True,blank=True,default=None)
    lancer_star = models.IntegerField(null=True, blank=True, default=5)
    lancer_text = models.TextField(null=True, blank=True, default="")
    owner_commented = models.BooleanField(default=False)
    lancer_commented = models.BooleanField(default=False)
