import sys
import datetime

from operator import itemgetter
from operator import attrgetter
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db.models import Max
from django.db.models import Count
from django.utils import timezone
from django.views import generic
from decimal import Decimal
from django.db.models import Q
from django.utils.timezone import localtime

from ..models import UserInfo, HansoSum, GameUser, GameResult, IsUpdateMng

class Query:
    "UserInfoをUserId指定で取得"
    def getUserInfo(userId):
        return UserInfo.objects.all().filter(user_id=userId)

    "UserIndoをスコアの降順で取得"
    def getUserInfoOrderByScoreDesc():
        return UserInfo.objects.select_related().all().order_by('-score_sum')

    "HansoSumを全件取得"
    def getHansoSum():
        return HansoSum.objects.all()

    "GameResultをUserId指定で取得"
    def getGameResult(userId):
        return GameResult.objects.all().filter(user_id=userId)
