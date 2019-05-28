from django.db import models



class user(models.Model):
    banned = 0
    normal = 1


    openid = models.CharField(verbose_name="微信openid",max_length=30,unique=True,primary_key=True)
    wx_name = models.CharField(verbose_name="微信名",max_length=256,null=True,blank=True,)
    phone = models.CharField(verbose_name="手机号",max_length=11,null=True,blank=True)#手机号为11位
    studentId = models.CharField(verbose_name="学号",max_length=13,unique=True,null=True,blank=True)#学号为13为
    stuIdPwd = models.CharField(verbose_name="学号密码",max_length=30,null=True,blank=True)
    address = models.CharField(verbose_name="学生地址",max_length=50,null=True,blank=True)#这是学生的地址，跟收货地址不一样，由爬虫得到


    #接的订单
    #发的订单
    rate = models.FloatField(verbose_name="评分",default=5.0)#信用评分
    receiveAddress = models.CharField(verbose_name="收货地址",max_length=50,null=True,blank=True)

    received_order_count = models.IntegerField(verbose_name="收单数剩余",default=10)
    sended_order_count = models.IntegerField("发单数剩余",default=10)

    status_choices = (
        (banned,"banned"),
        (normal,"normal"),
    )
    status = models.IntegerField(verbose_name="状态",choices=status_choices,default=normal)
    head_img = models.CharField(verbose_name="头像图片url",max_length=2000,default="/static/account/img/default.jpg")
    created_date = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)
    def __str__(self):
        if self.wx_name:
            return self.wx_name
        else:
            return self.openid

    class Meta:
        verbose_name = "账户"
        verbose_name_plural = "账户"


