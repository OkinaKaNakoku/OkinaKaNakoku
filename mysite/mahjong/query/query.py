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

from ..models import UserInfo, HansoSum, GameUser, GameResult, IsUpdateMng, UserMst

class Query:
    "UserMstを取得"
    def getUserMst():
        return UserMst.objects.all()

    "UserMstをUserId指定で取得"
    def getUserMstFilterUserId(userId):
        return UserMst.objects.all().filter(user_id=userId).first()

    "UserInfoを全件取得"
    def getUserInfo():
        return UserInfo.objects.all()

    "UserInfoをUserId指定で取得"
    def getUserInfoWhereUserId(userId):
        return UserInfo.objects.all().filter(user_id=userId)

    "UserInfoをスコアの降順で取得"
    def getUserInfoOrderByScoreDesc():
        return UserInfo.objects.select_related().all().order_by('-score_sum')

    "UserIndoを年指定・スコアの降順で取得"
    def getUserInfoWhereYearOrderByScoreDesc(year):
        return UserInfo.objects.select_related().all().filter(year=year).order_by('-score_sum')

    "HansoSumを全件取得"
    def getHansoSum():
        return HansoSum.objects.all()

    "HansoSumを年指定で取得"
    def getHansoSumWhereYearOrderByYearDescHansoIdDesc(year):
        return HansoSum.objects.all().filter(year=year).order_by('-year', '-hanso_id')

    "GameResultをUserId指定で取得"
    def getGameResultWhereUserId(userId):
        return GameResult.objects.all().filter(user_id=userId)

    def getGameResultWhereUserIdAndYear(userId, year):
        return GameResult.objects.all().filter(user_id=userId, year=year)
