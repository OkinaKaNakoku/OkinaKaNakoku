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

class ShowRankingCommand:
    # def __init__(self):

    #ランキングを取得
    def getShowRankingInfo(self, request):
        # 表示する年を確定させる
        # cookieに保存されていない場合はシステム日付の年をデフォルトにする
        selectYear = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
        # ここのifホンマに謎。NoneなのにTrueにならない
        if selectYear is None or len(selectYear) == 0:
            selectYear = datetime.datetime.now()
            selectYear = str(selectYear.year)

        q = query.Query

        # UserMstの取得
        userMstQuery = q. getUserMst()
        users_obj = []
        userInfoDictionary = {}
        # 年単位は対象の年のみで取得する
        # 年跨ぐ際にデータがない場合を考慮。insertしてから取得し直す
        if const.Const.ScreenConst.ALL_YEAR != selectYear:
            users_obj = q.getUserInfoWhereYearOrderByScoreDesc(selectYear)
            if len(users_obj) == 0:
                year = str(datetime.datetime.now().year)
                for userMst in userMstQuery:
                    UserInfo(year=year, user_id=userMst, score_sum=0.0).save()
                users_obj = q.getUserInfoWhereYearOrderByScoreDesc(selectYear)
        else:
            # 通算は全件取得
            # スコアをまとめてから管理
            users_obj = q.getUserInfo()
            for user in users_obj:
                if user.user_id.user_id in userInfoDictionary:
                    userInfoDictionary[user.user_id.user_id].score_sum += user.score_sum
                else:
                    userInfoDictionary[user.user_id.user_id] = user
            users_obj = userInfoDictionary.values()

        usersResScore = []
        scoreList = []  # 同率で使う
        cnt = 0        # 同率で使う
        isFirst = True # 同率で使う
        rank = 1
        topScore = 0.0
        # スコアの降順でソート
        users_obj = sorted(users_obj, key=attrgetter('score_sum'), reverse=True)
        # トップ差で使用するため降順で先頭だけ取得
        topScore = users_obj[0].score_sum

        for user in users_obj:
            topDiff = '-' + str(topScore - user.score_sum)
            tgtUser = None
            for userMst in userMstQuery:
                if user.user_id.user_id == userMst.user_id:
                    tgtUser = userMst
            if isFirst: # 先頭は同率の考慮なし。ロジック効率より可読性を優先
                isFirst = False
                scoreList.append(user.score_sum)
                usersResScore.append(indexScoreDto.UserScore(tgtUser, rank, topDiff, user))
                continue

            """ 同率を見る
            同率ならrankをupしない。次のrankはscoreListの要素+1とする"""
            isDoritsu = True
            if not scoreList[cnt] == user.score_sum:
                isDoritsu = False
            cnt = cnt + 1
            if not isDoritsu:
                rank = len(scoreList) + 1
            scoreList.append(user.score_sum)

            usersResScore.append(indexScoreDto.UserScore(tgtUser, rank, topDiff, user))

        # ■■■半荘回数ランキング■■■■■■■■■■■■■■■■■■
        # 半荘回数のレコード数の降順
        users_obj = UserInfo.objects.select_related().all().order_by('user_id')
        # 年単位は対象の年のみで取得する
        if const.Const.ScreenConst.ALL_YEAR != selectYear:
            hansoSumCnt = len(HansoSum.objects.values('hanso_id').filter(year=selectYear).annotate(Count=Count('hanso_id')))
            hansoSumQueryUserCnt = HansoSum.objects.values('user_id').filter(year=selectYear).annotate(count=Count('user_id')).order_by('-count')
        else:
            # 通算は全件取得
            hansoSumCnt = len(HansoSum.objects.values('hanso_id').annotate(Count=Count('hanso_id')))
            hansoSumQueryUserCnt = HansoSum.objects.values('user_id').annotate(count=Count('user_id')).order_by('-count')

        # ランキング紐付け。一旦ランクは固定で入れる
        usersHansoCnt = []
        for user in userMstQuery:
            registed = False
            for userCnt in hansoSumQueryUserCnt:
                if user.user_id == userCnt.get('user_id'):
                    registed = True
                    userSum = userCnt.get('count')
                    percentage = format(userSum / hansoSumCnt * 100, '.2f') # 小数点以下2桁まで
                    usersHansoCnt.append(hansoCntRankDto.HansoCntRank(user, userSum, percentage, 1))
                    break
            if not registed: # 半荘回数0がいるので分ける
                usersHansoCnt.append(hansoCntRankDto.HansoCntRank(user, 0, float(0.0), 1))
        # 並び替え
        usersHansoCnt = sorted(usersHansoCnt, key=attrgetter('hansoSum'), reverse=True)
        hansoSumList = []  # 同率で使う
        cnt = 0        # 同率で使う
        isFirst = True # 同率で使う
        rank = 1
        usersResHansoCnt = []
        for user in usersHansoCnt:
            if isFirst: # 先頭は同率の考慮なし。ロジック効率より可読性を優先
                isFirst = False
                hansoSumList.append(user.hansoSum)
                user.rank = rank
                usersResHansoCnt.append(user)
                continue

            """ 同率を見る
            同率ならrankをupしない。次のrankはscoreListの要素+1とする"""
            isDoritsu = True
            if not hansoSumList[cnt] == user.hansoSum:
                isDoritsu = False
            cnt = cnt + 1
            if not isDoritsu:
                rank = len(hansoSumList) + 1
            hansoSumList.append(user.hansoSum)
            user.rank = rank
            usersResHansoCnt.append(user)

        # ■■■和了率・放銃率ランキング■■■■■■■■■■■■■■■■■■■■■
        # GAME_RESULT取得
        gameResult = []
        # 年単位は対象の年のみで取得する
        if const.Const.ScreenConst.ALL_YEAR != selectYear:
            gameResult = GameResult.objects.select_related().all().filter(year=selectYear).order_by('user_id')
        else:
            # 通算は全件取得
            gameResult = GameResult.objects.select_related().all().order_by('user_id')

        # 和了率・放銃率計算
        # ユーザの和了数をユーザの全局数で割る
        # ランキング紐付け。一旦ランクは固定で入れる（後で並び替え時に入れる）
        horaPercentageRankList =[]
        hojuPercentageRankList =[]
        for user in userMstQuery:
            userList = []
            userHoraList = []
            userHojuList = []
            for userGameResult in gameResult:
                if user.user_id == userGameResult.user_id.user_id:
                    userList.append(userGameResult)
                    if (userGameResult.result_div == int(const.Const.GameConst.和了)):
                        userHoraList.append(userGameResult)
                    elif (userGameResult.result_div == int(const.Const.GameConst.放銃)):
                        userHojuList.append(userGameResult)
            if (len(userList) != 0 ): # 対局ありのみ計算（0割考慮）
                horaCnt = len(userHoraList)
                hojuCnt = len(userHojuList)
                cnt = len(userList)
                percentage = format(horaCnt / cnt * 100, '.2f') # 小数点以下2桁まで
                percentageHoju = format(hojuCnt / cnt * 100, '.2f') # 小数点以下2桁まで
                horaPercentageRankList.append(horaPercentageRankDto.HoraPercentageRankDto(user, cnt, horaCnt, float(percentage), 1))
                hojuPercentageRankList.append(horaPercentageRankDto.HoraPercentageRankDto(user, cnt, hojuCnt, float(percentageHoju), 1))
            else:
                horaPercentageRankList.append(horaPercentageRankDto.HoraPercentageRankDto(user, 0, 0,  float(0.0), 1))
                hojuPercentageRankList.append(horaPercentageRankDto.HoraPercentageRankDto(user, 0, 0,  float(0.0), 1))
        # 和了率・並び替え
        horaPercentageRankList = sorted(horaPercentageRankList, key=attrgetter('percentage'), reverse=True)
        percentageList = []  # 同率で使う
        cnt = 0        # 同率で使う
        isFirst = True # 同率で使う
        rank = 1
        usersResHoraPercentage = []
        for user in horaPercentageRankList:
            if isFirst: # 先頭は同率の考慮なし。ロジック効率より可読性を優先
                isFirst = False
                percentageList.append(user.percentage)
                user.rank = rank
                usersResHoraPercentage.append(user)
                continue

            """ 同率を見る
            同率ならrankをupしない。次のrankはscoreListの要素+1とする"""
            isDoritsu = True
            if not percentageList[cnt] == user.percentage:
                isDoritsu = False
            cnt = cnt + 1
            if not isDoritsu:
                rank = len(percentageList) + 1
            percentageList.append(user.percentage)
            user.rank = rank
            usersResHoraPercentage.append(user)

        # 放銃率・並び替え
        hojuPercentageRankList = sorted(hojuPercentageRankList, key=attrgetter('percentage'), reverse=False)
        percentageList = []  # 同率で使う
        cnt = 0        # 同率で使う
        isFirst = True # 同率で使う
        rank = 1
        usersResHojuPercentage = []
        for user in hojuPercentageRankList:
            if isFirst: # 先頭は同率の考慮なし。ロジック効率より可読性を優先
                isFirst = False
                percentageList.append(user.percentage)
                user.rank = rank
                usersResHojuPercentage.append(user)
                continue

            """ 同率を見る
            同率ならrankをupしない。次のrankはscoreListの要素+1とする"""
            isDoritsu = True
            if not percentageList[cnt] == user.percentage:
                isDoritsu = False
            cnt = cnt + 1
            if not isDoritsu:
                rank = len(percentageList) + 1
            percentageList.append(user.percentage)
            user.rank = rank
            usersResHojuPercentage.append(user)
        showRankingRes = showRankingDto.ShowRankingDto(usersResScore, usersResHansoCnt, usersResHoraPercentage, usersResHojuPercentage)
        return showRankingRes
