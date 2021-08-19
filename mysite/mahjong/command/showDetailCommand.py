import sys
import datetime
from ..dto.showDetail import *
from ..const import const
from mahjong.command import showDetailCommand
from mahjong.query import query

import math
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

class ShowDetailCommand:
    def __init__(self, userId):
        self.userId = userId

    "個人詳細を取得"
    def getShowDetailInfo(cmd, request):
        # 表示する年を確定させる
        # cookieに保存されていない場合はシステム日付の年をデフォルトにする
        selectYear = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
        # ここのifホンマに謎。NoneなのにTrueにならない
        if selectYear is None:
            selectYear = datetime.datetime.now()
            selectYear = str(selectYear.year)

        userId = cmd.userId
        q = query.Query
        userMstQuery = q.getUserMst()

        # UserInfo取得
        # 年単位は対象の年のみで取得する
        # 年跨ぐ際にデータがない場合を考慮。insertしてから取得し直す
        users_obj = []
        userInfoDictionary = {}
        if const.Const.ScreenConst.ALL_YEAR != selectYear:
            userInfoQuerys = q.getUserInfoWhereYearOrderByScoreDesc(selectYear)
            if len(userInfoQuerys) == 0:
                year = str(datetime.datetime.now().year)
                for userMst in userMstQuery:
                    UserInfo(year=year, user_id=userMst, score_sum=0.0).save()
                users_obj = q.getUserInfoWhereYearOrderByScoreDesc(selectYear)
        else:
            # 通算は全件取得
            # スコアをまとめてから管理
            userInfoQuerys = q.getUserInfo()
            for user in userInfoQuerys:
                if user.user_id.user_id in userInfoDictionary:
                    userInfoDictionary[user.user_id.user_id].score_sum += user.score_sum
                else:
                    userInfoDictionary[user.user_id.user_id] = user
            userInfoQuerys = userInfoDictionary.values()
            # スコアの降順でソート
            userInfoQuerys = sorted(userInfoQuerys, key=attrgetter('score_sum'), reverse=True)

        # 総合順位の確定。対象のuserIdのクエリ取得
        rank = 0
        userInfo = None
        for userInfoQuery in userInfoQuerys:
            rank += 1
            if userId == userInfoQuery.user_id.user_id:
                userInfo = userInfoQuery
                break
        userMst = q.getUserMstFilterUserId(userId)

        # 半荘回数の取得
        # 参加日数も取得するため、全取得
        if const.Const.ScreenConst.ALL_YEAR != selectYear:
            hansoSumQuerys = q.getHansoSumWhereYearOrderByYearDescHansoIdDesc(selectYear)
        else:
            hansoSumQuerys = q.getHansoSum()

        # 半荘回数・参加日数
        userHansoSums = []
        # 最高スコア・最低スコア
        # レスポンスよりも可読性を重視
        userHansoScores = []
        for hansoSumQuery in hansoSumQuerys:
            if (userId == hansoSumQuery.user_id.user_id):
                userHansoSums.append(hansoSumQuery)
                userHansoScores.append(hansoSumQuery.score)

        if (0 == len(userHansoSums)):
            # 半荘回数0は固定で返す
            # 最高に頭悪い。他にいい方法あるはず
            rankDto = userGetRankDto.UserGetRankDto(0, 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0, 0.0)
            name = userMst.last_name + ' ' + userMst.first_name
            score = userInfo.score_sum
            hansoCnt = len(userHansoScores)
            recordDto = userRecordDto.UserRecordDto(userId, name, rank, score, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            detailResDto = showDetailResDto.ShowDetailResDto(rankDto, recordDto)
            return detailResDto

        # 対局数・和了放銃数、率
        if const.Const.ScreenConst.ALL_YEAR != selectYear:
            gameResultQuerys = q.getGameResultWhereUserIdAndYear(userId, selectYear)
        else:
            gameResultQuerys = q.getGameResultWhereUserId(userId)
        gameCnt = len(gameResultQuerys)
        horaCnt = 0
        hojuCnt = 0
        horaScore = 0
        horaScoreCnt = 0
        hojuScore = 0
        hojuScoreCnt = 0
        for gameResultQuery in gameResultQuerys:
            if int(const.Const.GameConst.和了) == gameResultQuery.result_div:
                horaCnt += 1
                if gameResultQuery.score != 0:
                    horaScore = horaScore + gameResultQuery.score
                    horaScoreCnt = horaScoreCnt + 1
            elif int(const.Const.GameConst.放銃) == gameResultQuery.result_div:
                hojuCnt += 1
                if gameResultQuery.score != 0:
                    hojuScore = hojuScore + gameResultQuery.score
                    hojuScoreCnt = hojuScoreCnt + 1
        horaPercentage = format(horaCnt / gameCnt, '.3f') # 小数点以下2桁まで
        hojuPercentage = format(hojuCnt / gameCnt, '.3f')
        if horaScore != 0:
            horaScore = "{:,}".format(math.floor(horaScore / horaScoreCnt))
        if hojuScore != 0:
            hojuScore = "{:,}".format(math.floor(hojuScore / hojuScoreCnt))

        #参加日数
        dayCnt = 1
        dayWk = localtime(userHansoSums[0].insert_date)
        dayWk = str(dayWk.year) + '/' + str(dayWk.month) + '/' + str(dayWk.day)
        for userHansoSum in userHansoSums:
            day = localtime(userHansoSum.insert_date)
            day = str(day.year) + '/' + str(day.month) + '/' + str(day.day)
            if (day != dayWk):
                dayCnt += 1
                dayWk = day

        # 獲得順位数
        rankFirstCnt = 0
        rankSecondCnt = 0
        rankThirdCnt = 0
        rankFourthCnt = 0
        tobiCnt = 0
        for userHansoSum in userHansoSums:
            rankResult = userHansoSum.rank
            if (rankResult == '1'):
                rankFirstCnt += 1
            if (rankResult == '2'):
                rankSecondCnt += 1
            if (rankResult == '3'):
                rankThirdCnt += 1
            if (rankResult == '4'):
                rankFourthCnt += 1
            if (userHansoSum.score < 0):
                tobiCnt += 1
        hansoCnt = len(userHansoSums)
        rankFirstPercentage = format(rankFirstCnt / hansoCnt, '.2f')
        ranksecondPercentage = format(rankSecondCnt / hansoCnt, '.2f')
        rankThirdPercentage = format(rankThirdCnt / hansoCnt, '.2f')
        rankFourthPercentage = format(rankFourthCnt / hansoCnt, '.2f')
        tobiPercentage = format(tobiCnt / hansoCnt, '.2f')
        # 順位率
        perRank = 1 * rankFirstCnt
        perRank = perRank + 2 * rankSecondCnt
        perRank = perRank + 3 * rankThirdCnt
        perRank = perRank + 4 * rankFourthCnt
        perRank = format(perRank / hansoCnt, '.2f')

        # Response作成
        # pythonなんで適当な箇所で改行できないのか
        rankDto = userGetRankDto.UserGetRankDto(rankFirstCnt, rankFirstPercentage, rankSecondCnt, ranksecondPercentage, rankThirdCnt, rankThirdPercentage, rankFourthCnt, rankFourthPercentage, tobiCnt, tobiPercentage)
        name = userMst.last_name + ' ' + userMst.first_name
        engName = userMst.eng_last_name.upper() + ' ' + userMst.eng_first_name.upper()
        score = userInfo.score_sum
        maxScore = max(userHansoScores)
        minScore = min(userHansoScores)
        recordDto = userRecordDto.UserRecordDto(userId, name, engName, rank, score, perRank, hansoCnt, maxScore, minScore, gameCnt, horaCnt, horaPercentage, hojuCnt, hojuPercentage, horaScore, hojuScore, dayCnt)
        detailResDto = showDetailResDto.ShowDetailResDto(rankDto, recordDto)
        return detailResDto
