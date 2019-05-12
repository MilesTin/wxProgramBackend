from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.shortcuts import get_object_or_404,redirect
import urllib.request
from django.conf import settings
import json
import requests
from PIL import Image
import os
from .models import *
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError



class sculogin(object):
    url = "http://zhjw.scu.edu.cn/j_spring_security_check"
    img_url = "http://zhjw.scu.edu.cn/img/captcha.jpg"
    is_updated = False

    #验证码地址
    #ip + 'static/' + 'account/img/login.jpg'



    def getCapatcha(self):
        """
        :return 图片的url:
        """
        self.session = requests.Session()
        print(sculogin.url)
        ir = self.session.get(sculogin.img_url)
        if ir.status_code == 200:
            open('static/account/img/login.jpg', 'wb').write(ir.content)
        #test
        # img = Image.open("static/account/img/login.jpg")
        # img.show()


    def login(self,username,password,captcha:str)->bool:
        """
        :param captcha:
        :param username:
        :param password:
        :return bool:
        """
        data = {
            'j_username':username,
            'j_password':password,
            'j_captcha':captcha,
        }
        res = self.session.post(sculogin.url,data=data)

        if (res.status_code==200):
            return True

        return False
scuLoginer = sculogin()

def login(request):
    wx_name = request.GET.get("wx_name")
    appid = request.GET.get("appid","")
    secret = request.GET.get("secret","")
    code = request.GET.get("code","")
    errmsg = ""
    if not appid:
        errmsg+= "appid不能为空"
    elif not secret:
        errmsg+="秘钥secret不能为空"
    elif not code:
        errmsg+="登录code为空"

    if errmsg:
        return JsonResponse({"errmsg":errmsg},status=404)

    #发送请求获得openid session_key unionid errcode errmsg

    tencent_url = "https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code".format(appid,secret,code)


    headers = {'content-type':'application/json'}

    R = urllib.request.Request(url=tencent_url,headers=headers)#接口成功只返回openid session_key

    response = urllib.request.urlopen(R).read()

    response_json = json.loads(response)
    openid=response_json.get("openid")
    session_key = response_json.get("session_key")

    errmsg = response_json.get("errmsg","")
    errcode = response_json.get("errcode")

    if not errcode:
        request.session['openid'] = openid
        try:
            cur_user = user.objects.get(openid=openid)
        except:
            #创建user
            newUser = user()
            newUser.openid = openid
            newUser.wx_name = wx_name
            newUser.save()


        request.session['session_key'] = session_key
        request.session['is_login'] = True
        request.session.set_expiry(100000000)
        return JsonResponse({"msg":"You are logged in"})
    else:#errcode由微信api决定(auth code2session), https://developers.weixin.qq.com/miniprogram/dev/api-backend/auth.code2Session.html
        return JsonResponse({"errmsg": errmsg,"errcode":errcode}, status=404)


def logout(request):
    if request.session.exists('openid'):
        del request.session['openid']
    if request.session.exists('session_key'):
        del request.session['session_key']
    return JsonResponse({"msg":"You are logged out"})


def verifStuId(request):
    stuId = request.GET.get("stuId","")
    passwd = request.GET.get("passwd")
    captcha = request.GET.get("captcha")
    openid = request.session.get("openid","")
    cur_user = get_object_or_404(user,openid=openid)

    if not sculogin.is_updated:
        return JsonResponse({"msg":"验证码未更新"},status=404,)

    result = scuLoginer.login(username=stuId,password=passwd,captcha=captcha)
    if result:
        #保存学号和密码
        cur_user.studentId = stuId
        cur_user.stuIdPwd = passwd
        cur_user.save()
        return JsonResponse({"msg":"绑定成功"})

    else:
        return JsonResponse({"msg":"绑定失败"},status=404)


def getCaptcha(request):
    scuLoginer.getCapatcha()
    sculogin.is_updated = True
    return JsonResponse({"msg":"获取验证码成功"})

def verifPhone(request):
    openid = request.session.get("openid","")
    cur_user = get_object_or_404(user,openid=openid)
    phone = request.GET.get("phone")
    #调用短信接口

    try:
        sms_appid = settings.sms_appid
        sms_appkey = settings.sms_appkey
    except NotImplementedError as e:
        raise NotImplementedError("sms_appid 或 sms_appkey 未设置")

    ssender = SmsSingleSender(sms_appid,sms_appkey)
    # try:
    #     result = ssender.send_with_param(86, phone_numbers[0],
    #                                      template_id, params, sign=sms_sign, extend="",
    #                                      ext="")  # 签名参数未提供或者为空时，会使用默认签名发送短信
    # except HTTPError as e:
    #     print(e)
    # except Exception as e:
    #     print(e)

    #user手机号存储
    return JsonResponse({"msg":""})
#test函数
if __name__=="__main__":
    scuL = sculogin()
    print(scuL.is_updated)
    scuL.getCapatcha()
    captcha = input("验证码:")
    print(scuL.login("2017141461248","014170",captcha))