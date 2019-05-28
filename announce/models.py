from django.db import models

# Create your models here.
class announcement(models.Model):
    content = models.CharField(verbose_name="内容", max_length=200)
    createdTime = models.DateTimeField(verbose_name="创建时间",auto_now=True)

    def __str__(self):
        return self.content[:10]

    class Meta:
        verbose_name = "公告"
        verbose_name_plural = "公告"



