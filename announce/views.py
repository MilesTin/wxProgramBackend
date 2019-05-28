from django.shortcuts import render
from django.http import JsonResponse
from .models import *
# Create your views here.


def announce(request):
    count = request.GET.get("count",1)
    try:
        count = int(count)
    except ValueError:
        count = 1

    announcements = announcement.objects.values("content", "createdTime")[:count]
    results = sorted(announcements,key=lambda announceObj:announceObj['createdTime'],reverse=True)

    return JsonResponse(results,safe=False)


