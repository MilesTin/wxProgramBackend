from django.db import models
from account.models import *
# Create your models here.

class feedback(models.Model):
    text = models.TextField(null=True,blank=True,default="")
    owner = models.ForeignKey(user,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
