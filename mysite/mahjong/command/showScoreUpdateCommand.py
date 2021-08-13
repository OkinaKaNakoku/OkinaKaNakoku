import sys
import datetime
from ..dto.showRanking import *
from ..const import const
from mahjong.query import query

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

def getTsumoScore(score):
    koTsumoScoreDic = {}
    koTsumoScoreDic[1300] = {'ko':400, 'oya':700}
    koTsumoScoreDic[2600] = {'ko':700, 'oya':1300}
    koTsumoScoreDic[5200] = {'ko':1300, 'oya':2600}
    koTsumoScoreDic[1000] = {'ko':300, 'oya':500}
    koTsumoScoreDic[2000] = {'ko':500, 'oya':1000}
    koTsumoScoreDic[3900] = {'ko':1000, 'oya':2000}
    koTsumoScoreDic[7700] = {'ko':2000, 'oya':3900}
    koTsumoScoreDic[1600] = {'ko':400, 'oya':800}
    koTsumoScoreDic[3200] = {'ko':800, 'oya':1600}
    koTsumoScoreDic[6400] = {'ko':1600, 'oya':3200}
    koTsumoScoreDic[2300] = {'ko':600, 'oya':1200}
    koTsumoScoreDic[4500] = {'ko':1200, 'oya':2600}
    koTsumoScoreDic[2900] = {'ko':800, 'oya':1500}
    koTsumoScoreDic[5800] = {'ko':1500, 'oya':2900}
    koTsumoScoreDic[3600] = {'ko':900, 'oya':1800}
    koTsumoScoreDic[7100] = {'ko':1800, 'oya':3600}
    koTsumoScoreDic[8000] = {'ko':2000, 'oya':4000}
    koTsumoScoreDic[12000] = {'ko':3000, 'oya':6000}
    koTsumoScoreDic[18000] = {'ko':4000, 'oya':8000}
    koTsumoScoreDic[24000] = {'ko':6000, 'oya':12000}
    koTsumoScoreDic[32000] = {'ko':8000, 'oya':16000}
    oyaTsumoScoreDic = {}
    oyaTsumoScoreDic[2000] = 700
    oyaTsumoScoreDic[3900] = 1300
    oyaTsumoScoreDic[7700] = 2600
    oyaTsumoScoreDic[4800] = 1600
    oyaTsumoScoreDic[9600] = 3200
    oyaTsumoScoreDic[1500] = 500
    oyaTsumoScoreDic[2900] = 1000
    oyaTsumoScoreDic[5800] = 2000
    oyaTsumoScoreDic[11600] = 3900
    oyaTsumoScoreDic[2400] = 800
    oyaTsumoScoreDic[3400] = 1200
    oyaTsumoScoreDic[6800] = 2300
    oyaTsumoScoreDic[4400] = 1500
    oyaTsumoScoreDic[8700] = 2900
    oyaTsumoScoreDic[5300] = 1800
    oyaTsumoScoreDic[10600] = 3600
    oyaTsumoScoreDic[12000] = 4000
    oyaTsumoScoreDic[18000] = 6000
    oyaTsumoScoreDic[24000] = 8000
    oyaTsumoScoreDic[36000] = 12000
    oyaTsumoScoreDic[48000] = 16000
    obj = {'ko':koTsumoScoreDic.get(score), 'oya':oyaTsumoScoreDic.get(score)}
    return obj
