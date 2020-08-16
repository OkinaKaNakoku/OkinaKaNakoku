from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import UserInfo, HansoSum

class IndexScore(generic.ListView):
    template_name = 'mahjong/score.html'

    def get_queryset(self):
        user = UserInfo.objects.select_related().all()
        return user