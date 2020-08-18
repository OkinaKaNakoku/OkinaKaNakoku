import sys
sys.path.append('mahjong/dto')
import indexScoreDto

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import UserInfo, HansoSum

class IndexScore(generic.ListView):
    template_name = 'mahjong/score.html'
    context_object_name = 'users'

    def get_queryset(self, **kwargs):
        # UserInfoをスコアの降順で取得
        users_obj = UserInfo.objects.select_related().all().order_by('-score_sum')
        
        usersRes = []
        scoreList = []  # 同率で使う
        cnt = 0        # 同率で使う
        isFirst = True # 同率で使う
        rank = 1
        topScore = users_obj.first().score_sum # トップ差で使う

        for user in users_obj:
            topDiff = '-' + str(topScore - user.score_sum)
            if isFirst: # 先頭は同率の考慮なし。ロジック効率より可読性を優先
                isFirst = False
                scoreList.append(user.score_sum)
                usersRes.append(indexScoreDto.UserScore(user, rank, topDiff))
                continue

            """ 同率を見る
            同率ならrankをupしない。次のrankはscoreListの要素+1とする"""
            isDoritsu = True
            
            print(str(scoreList[cnt]) + '-' + str(user.score_sum))
            if not scoreList[cnt] == user.score_sum:
                isDoritsu = False
            cnt = cnt + 1
            if not isDoritsu:
                rank = len(scoreList) + 1
            scoreList.append(user.score_sum)
            usersRes.append(indexScoreDto.UserScore(user, rank, topDiff))

        return usersRes