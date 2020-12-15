import sys
import datetime
from mahjong.dto import indexScoreDto
from mahjong.dto import showScoreUpdateDto
from mahjong.dto import updateScoreDAO
from mahjong.dto import hansoCntRankDto
from mahjong.dto import horaPercentageRankDto
from ..dto.showDetail import *
from ..const import const
from mahjong.command import showDetailCommand
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

class ShowDetailCommand:
    def __init__(self, userId):
        self.userId = userId

    "個人詳細を取得"
    def getShowDetailInfo(cmd):
        userId = cmd.userId
        q = query.Query
        # UserInfo取得
        userInfoQuerys = q.getUserInfoOrderByScoreDesc()

        # 総合順位の確定。対象のuserIdのクエリ取得
        rank = 0
        userInfo = None
        for userInfoQuery in userInfoQuerys:
            rank += 1
            if userId == userInfoQuery.user_id:
                userInfo = userInfoQuery
                break

        # 半荘回数の取得
        # 参加日数も取得するため、全取得
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
            name = userInfo.last_name + ' ' + userInfo.first_name
            score = userInfo.score_sum
            hansoCnt = len(userHansoScores)
            recordDto = userRecordDto.UserRecordDto(name, rank, score, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            detailResDto = showDetailResDto.ShowDetailResDto(rankDto, recordDto)
            return detailResDto

        # 対局数・和了放銃数、率
        gameResultQuerys = q.getGameResult(userId)
        gameCnt = len(gameResultQuerys)
        horaCnt = 0
        hojuCnt = 0
        for gameResultQuery in gameResultQuerys:
            if (const.Const.GameConst.和了 == gameResultQuery.result_div):
                horaCnt += 1
            elif (const.Const.GameConst.放銃 == gameResultQuery.result_div):
                hojuCnt += 1
        horaPercentage = format(horaCnt / gameCnt * 100, '.2f') # 小数点以下2桁まで
        hojuPercentage = format(hojuCnt / gameCnt * 100, '.2f')

        #参加日数
        dayCnt = 1
        print(userHansoSums)
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
        rankFirstPercentage = format(rankFirstCnt / hansoCnt * 100, '.2f')
        ranksecondPercentage = format(rankSecondCnt / hansoCnt * 100, '.2f')
        rankThirdPercentage = format(rankThirdCnt / hansoCnt * 100, '.2f')
        rankFourthPercentage = format(rankFourthCnt / hansoCnt * 100, '.2f')
        tobiPercentage = format(tobiCnt / hansoCnt * 100, '.2f')
        # Response作成
        # pythonなんで適当な箇所で改行できないのか
        rankDto = userGetRankDto.UserGetRankDto(rankFirstCnt, rankFirstPercentage, rankSecondCnt, ranksecondPercentage, rankThirdCnt, rankThirdPercentage, rankFourthCnt, rankFourthPercentage, tobiCnt, tobiPercentage)
        name = userInfo.last_name + ' ' + userInfo.first_name
        score = userInfo.score_sum
        maxScore = max(userHansoScores)
        minScore = min(userHansoScores)
        recordDto = userRecordDto.UserRecordDto(name, rank, score, hansoCnt, maxScore, minScore, gameCnt, horaCnt, horaPercentage, hojuCnt, hojuPercentage, dayCnt)
        detailResDto = showDetailResDto.ShowDetailResDto(rankDto, recordDto)
        return detailResDto
