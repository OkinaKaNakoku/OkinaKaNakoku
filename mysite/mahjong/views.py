import sys
import datetime
from mahjong.dto import showScoreUpdateDto
from .dto.changeYear import *
from mahjong.dto import updateScoreDAO
from .dto.showDetail import *
from .dto.lineBot import lineBotDto
from mahjong.command import *
from mahjong.command import lineBotCommand
from .const import const
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
import json
from django.http.response import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import urllib.parse
from django.shortcuts import redirect

from .models import UserInfo, HansoSum, GameUser, GameResult, IsUpdateMng, UserMst, GameStatus, DoLogin

# 定数
USER_UNREG = 'userUnreg'
USER_DUP = 'userDup'
和了 = '1'
放銃 = '2'

# ランキング
def showRanking(request):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    command = showRankingCommand.ShowRankingCommand()
    showRankingInfo = command.getShowRankingInfo(request)
    response = render(request, 'mahjong/score.html',
        {'users':showRankingInfo.users, 'usersHanso':showRankingInfo.usersHanso, 'usersHora':showRankingInfo.usersHora,
         'userHoju':showRankingInfo.userHoju})
    # cookieに保存されていない場合はシステム日付の年をデフォルトで設定
    cookie = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
    # ここのifホンマに謎。NoneなのにTrueにならない
    if cookie is None or len(cookie) == 0:
        cookie = datetime.datetime.now()
        response.set_cookie(const.Const.Cookie.SELECT_YEAR, str(cookie.year))
    return response

# スコア更新表示
def showScoreUpdate(request):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    # ■UserInfoをuser_idの昇順で取得
    settingUsers = getShowScoreUpdateDto()
    # ■GameUserを全取得
    user1 = None
    user2 = None
    user3 = None
    user4 = None
    gameUserQuery = GameUser.objects.select_related().all().order_by('seq')
    gameStatusQuery = GameStatus.objects.select_related().all()[0] # 戦闘固定。1件しかない
    gameUserScoreSortedQuery = sorted(gameUserQuery, key=attrgetter('score'), reverse=True)

    # rankとUserIdで紐付け
    rankDic = {}
    for gameUser in gameUserQuery:
        rank = 1
        for gameUserScoreSorted in gameUserScoreSortedQuery:
            if  gameUser.user_id == gameUserScoreSorted.user_id:
                rankDic[gameUser.user_id] = rank
                break
            rank = rank + 1

    if 4 <= len(gameUserQuery):
        # context別だからそれぞれで取る
        user1 = showScoreUpdateDto.ShowScoreUpdateLabel(gameUserQuery[0], rankDic[gameUserQuery[0].user_id], gameStatusQuery.kyoku == 1)
        user2 = showScoreUpdateDto.ShowScoreUpdateLabel(gameUserQuery[1], rankDic[gameUserQuery[1].user_id], gameStatusQuery.kyoku == 2)
        user3 = showScoreUpdateDto.ShowScoreUpdateLabel(gameUserQuery[2], rankDic[gameUserQuery[2].user_id], gameStatusQuery.kyoku == 3)
        user4 = showScoreUpdateDto.ShowScoreUpdateLabel(gameUserQuery[3], rankDic[gameUserQuery[3].user_id], gameStatusQuery.kyoku == 4)
    gameStatus = showScoreUpdateDto.GameStatus(gameStatusQuery)
    response = render(request, 'mahjong/show-score-update.html',
    {'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4,
    'settingUsers':settingUsers, 'gameStatus':gameStatus, 'isReload':0})

    # cookieに保存されていない場合はシステム日付の年をデフォルトで設定
    cookie = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
    # ここのifホンマに謎。NoneなのにTrueにならない
    if cookie is None or len(cookie) == 0:
         cookie = datetime.datetime.now()
         response.set_cookie(const.Const.Cookie.SELECT_YEAR, str(cookie.year))
    return response

# スコア登録
def updateScore(request):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    if isUpdatePossible() == False: # 更新不可
        # レンダリング
        gameUserQuery = GameUser.objects.select_related().all()
        user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
        user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
        user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
        user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
        users_obj = UserInfo.objects.select_related().all().order_by('user_id')
        settingUsers = []
        for user in users_obj:
            settingUsers.append(showScoreUpdateDto.ShowScoreUpdate(user))
        # return render(request, 'mahjong/show-score-update.html', {
        # 'settingUsers': settingUsers,
        # 'error_message': "更新不可です。更新管理をUPDATEしてください",
        # 'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4})
        return redirect('/mahjong/showScoreUpdate?messageDiv=3')

    # ■form取得。多分もっといい方法ある
    noUser = 'default'
    userIds = []
    userScores = []
    userIds.append(request.POST['user1'])
    userScores.append(request.POST['score1'])
    userIds.append(request.POST['user2'])
    userScores.append(request.POST['score2'])
    userIds.append(request.POST['user3'])
    userScores.append(request.POST['score3'])
    userIds.append(request.POST['user4'])
    userScores.append(request.POST['score4'])

    # ■スコアのバリデーションチェック
    for userScore in userScores:
        if userScore == '': # スコア未登録
            # レンダリング
            gameUserQuery = GameUser.objects.select_related().all()
            user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
            user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
            user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
            user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
            users_obj = UserMst.objects.select_related().all().order_by('user_id')
            usersRes = []
            for user in users_obj:
                usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
            # return render(request, 'mahjong/show-score-update.html', {
            # 'users': usersRes,
            # 'error_message': "スコアを全て登録してください",
            # 'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4})
            return redirect('/mahjong/showScoreUpdate?messageDiv=6')

    year = str(datetime.datetime.now().year)
    # ■userとscoreの紐付け
    cnt = 0
    insertDaos = []
    for index, userId in enumerate(userIds):
        for index, mappingScore in enumerate(userScores):
            if cnt == index:
                cnt = cnt + 1
                insertDaos.append(updateScoreDAO.UpdateScoreDAO(userId, mappingScore))
                break

    # ■順位ソート
    rankSortDaos = sorted(insertDaos, key=attrgetter('score'), reverse=True)

    # ■半荘IDのMAXを取得。連番で登録するため、+1
    hanso_obj = HansoSum.objects.all().aggregate(Max('hanso_id'))
    # 初回のみ取得できないのでロジックとして入れるが実質デッドコード
    maxHansoId = 0
    if hanso_obj.get('hanso_id__max') is None:
        maxHansoId = 1
    else:
        maxHansoId = hanso_obj.get('hanso_id__max') + 1

    lineBotMsgs = []

    # ■HansoSum to Insert
    # ■UserInfo to Update
    hansoIdParam = maxHansoId
    rankParam = 1
    for dao in rankSortDaos:
        # TODO 同率順位などのレアケースは見ない。javaなら書いてやるよ
        # 計算処理
        userIdParam = dao.userId
        scoreParam = dao.score
        userObj = UserMst.objects.all().filter(user_id=userIdParam)

        # ウマ・オカ計算
        if rankParam == 1:
            scoreResultParam = int(scoreParam) + 20000 + 30000
        elif rankParam == 2:
            scoreResultParam = int(scoreParam) + 10000
        elif rankParam == 3:
            scoreResultParam = int(scoreParam) - 10000
        elif rankParam == 4:
            scoreResultParam = int(scoreParam) - 30000
        scoreResultParam = scoreResultParam / 1000
        scoreResultParam = scoreResultParam - 30

        # botメッセージ
        lineMsg = lineBotDto.LineBotMsg(userObj.first().last_name, scoreParam, scoreResultParam)
        lineBotMsgs.append(lineMsg)

        HansoSum(year=year
                ,hanso_id=hansoIdParam
                , user_id=userObj.first()
                , rank=rankParam
                , score=scoreParam
                , score_result=scoreResultParam).save()
        dao = UserInfo.objects.filter(user_id=userIdParam, year=year).first()
        # 初回登録は対象の年で登録後、再取得
        # 全員登録がないはずなので、全登録
        if dao == None:
            userMstQuery = UserMst.objects.all()
            for userMst in userMstQuery:
                UserInfo(year=year, user_id=userMst, score_sum=0.0).save()
            dao = UserInfo.objects.filter(user_id=userIdParam, year=year).first()
        dao.score_sum += Decimal(str(scoreResultParam))
        dao.save()
        rankParam = rankParam + 1

    # botメッセージ作成
    rank = 1
    lineMsg = "【 -対局が終了しました- 】\r\n"
    for msg in lineBotMsgs:
        lineMsg = lineMsg + str(rank) + "位 | " + str(msg.name) + " ["
        if 0 < msg.scoreResult:
            lineMsg = lineMsg + "+"
        lineMsg = lineMsg + str(int(msg.scoreResult)) + "]\r\n"
        rank += 1
    lineBotCommand.LineBotCommand.pushMessage(lineMsg)

    # エラーメッセージを返して、レンダリングするが、正常終了のはず
    gameStatusQuery = GameStatus.objects.select_related().all()[0] # 戦闘固定。1件しかない
    gameUserQuery = GameUser.objects.select_related().all()
    user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
    user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
    user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
    user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
    users_obj = UserMst.objects.select_related().all().order_by('user_id')
    usersRes = []
    for user in users_obj:
        usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
    gameStatus = showScoreUpdateDto.GameStatus(gameStatusQuery)
    # return render(request, 'mahjong/show-score-update.html', {
    # 'settingUsers': usersRes,
    # 'error_message': "スコア登録が完了しました",
    # 'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4, 'gameStatus':gameStatus})
    return redirect('/mahjong/showScoreUpdate?messageDiv=2')

# 点数表表示
def scoreTable(request):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    response = render(request, 'mahjong/score-table.html')
    # cookieに保存されていない場合はシステム日付の年をデフォルトで設定
    cookie = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
    # ここのifホンマに謎。NoneなのにTrueにならない
    if cookie is None or len(cookie) == 0:
         cookie = datetime.datetime.now()
         response.set_cookie(const.Const.Cookie.SELECT_YEAR, str(cookie.year))
    return response

# 対局登録
def updateGame(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    settingUsers = getShowScoreUpdateDto()
    gameStatusQuery = GameStatus.objects.select_related().all()[0] # 戦闘固定。1件しかない
    gameStatus = showScoreUpdateDto.GameStatus(gameStatusQuery)
    if isUpdatePossible() == False:
        # レンダリング
        gameUserQuery = GameUser.objects.select_related().all()
        user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
        user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
        user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
        user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
        users_obj = UserMst.objects.select_related().all().order_by('user_id')
        settingUsers = []
        for user in users_obj:
            settingUsers.append(showScoreUpdateDto.ShowScoreUpdate(user))
        # return render(request, 'mahjong/show-score-update.html', {
        # 'settingUsers': settingUsers,
        # 'error_message': "更新不可です。更新管理をUPDATEしてください",
        # 'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4, 'gameStatus':gameStatus})
        return redirect('/mahjong/showScoreUpdate?messageDiv=3')

    # バリデーションチェック
    validResult = []
    if request.POST.get('gameResult1') == 和了:
        validResult.append(request.POST['gameResult1'])
    if request.POST.get('gameResult2') == 和了:
        validResult.append(request.POST['gameResult2'])
    if request.POST.get('gameResult3') == 和了:
        validResult.append(request.POST['gameResult3'])
    if request.POST.get('gameResult4') == 和了:
        validResult.append(request.POST['gameResult4'])
    if 1 < len(validResult):
        # 和了者が複数
        gameUserQuery = GameUser.objects.select_related().all()
        user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
        user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
        user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
        user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
        users_obj = UserMst.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
        # return render(request, 'mahjong/show-score-update.html', {
        # 'settingUsers': usersRes,
        # 'error_message': "和了者は複数登録できません",
        # 'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4,
        # 'settingUsers':settingUsers, 'gameStatus':gameStatus})
        return redirect('/mahjong/showScoreUpdate?messageDiv=7')

    validResult = []
    if request.POST.get('gameResult1') == 放銃:
        validResult.append(request.POST['gameResult1'])
    if request.POST.get('gameResult2') == 放銃:
        validResult.append(request.POST['gameResult2'])
    if request.POST.get('gameResult3') == 放銃:
        validResult.append(request.POST['gameResult3'])
    if request.POST.get('gameResult4') == 放銃:
        validResult.append(request.POST['gameResult4'])
    if 1 < len(validResult):
        # 放銃者が複数
        gameUserQuery = GameUser.objects.select_related().all()
        user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
        user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
        user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
        user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
        users_obj = UserMst.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
        return render(request, 'mahjong/show-score-update.html', {
        'settingUsers': usersRes,
        'error_message': "放銃者は複数登録できません",
        'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4, 'gameStatus':gameStatus})

    year = str(datetime.datetime.now().year)
    # ■form取得
    scoreValue = int(request.POST.get('score'))

    gameStatusQuery = GameStatus.objects.select_related().all()[0] # 戦闘固定。1件しかない
    # 供託計算
    kyotakuCnt = gameStatusQuery.kyotaku
    huroResults = []
    huroResults.append(request.POST['huroResult1'])
    huroResults.append(request.POST['huroResult2'])
    huroResults.append(request.POST['huroResult3'])
    huroResults.append(request.POST['huroResult4'])
    addKyotaku = 0
    for huroResult in huroResults:
        if str(const.Const.HuroConst.供託) == huroResult:
            kyotakuCnt = kyotakuCnt + 1
            addKyotaku = addKyotaku + 1
    kyotakuScore = kyotakuCnt * 1000
    # 本場計算
    honbaScore = gameStatusQuery.honba * 300

    horaScore = scoreValue + kyotakuScore + honbaScore
    hojuScore = scoreValue + honbaScore

    #　和了者・放銃者・親の確定
    gameResults = []
    gameResults.append(request.POST['gameResult1'])
    gameResults.append(request.POST['gameResult2'])
    gameResults.append(request.POST['gameResult3'])
    gameResults.append(request.POST['gameResult4'])
    cnt = 0
    horaUserId = None
    hojuUserId = None
    oyaUserId = None
    for gameResult in gameResults:
        cnt = cnt + 1
        if str(const.Const.GameConst.和了) == gameResult:
            horaUserId = request.POST['user' + str(cnt)]
        elif str(const.Const.GameConst.放銃) == gameResult:
            hojuUserId = request.POST['user' + str(cnt)]

    # 何局目かで親を確定
    oyaUserId = request.POST['user' + str(gameStatusQuery.kyoku)]
    # ツモ時の点数を取得
    # 親のツモロン、子のツモロンそれぞれ取得
    tsumoScoreDic = {}
    tsumoScoreDic = showScoreUpdateCommand.getTsumoScore(scoreValue)
    isTsumo = False
    isOyaTsumo = False
    if hojuUserId is None and horaUserId is not None:
        isTsumo = True
        if horaUserId == oyaUserId:
            isOyaTsumo = True

    # 聴牌人数確定
    tenpais = []
    tenpais.append(request.POST['tenpaiResult1'])
    tenpais.append(request.POST['tenpaiResult2'])
    tenpais.append(request.POST['tenpaiResult3'])
    tenpais.append(request.POST['tenpaiResult4'])
    notenCnt = 0
    bappu = 0
    tenpairyo = 0
    wk = 0
    for tenpai in tenpais:
        wk = wk + 1
        if tenpai != "1":
            if request.POST['huroResult' + str(wk)] != str(const.Const.HuroConst.供託):
                notenCnt = notenCnt + 1
    if notenCnt != 0 and notenCnt != 4:
        bappu = 3000 / notenCnt
        tenpairyo = 3000 / (4-notenCnt)

    userId = request.POST.get('user1')
    gameResult = request.POST.get('gameResult1')
    huroResult = request.POST.get('huroResult1')
    tenpaiResult = request.POST.get('tenpaiResult1')
    # ■userInfo取得
    conditionUserId = Q(user_id = userId)
    userQuery = UserMst.objects.all().filter(conditionUserId)
    # 登録されている半荘IDのmaxを取得。初回のみ取得できないので実質デッドコード
    maxHansoId = 1
    maxHansoIdQuery = HansoSum.objects.all().aggregate(Max('hanso_id'))
    if maxHansoIdQuery.get('hanso_id__max') is not None:
        maxHansoId = int(maxHansoIdQuery.get('hanso_id__max')) + 1
    # 登録されている対局seqのmaxを取得
    maxGameSeq = 1
    conditionHansoId = Q(hanso_id=maxHansoId)
    maxGameSeqQuery = GameResult.objects.all().filter(conditionHansoId).aggregate(Max('game_seq'))
    if maxGameSeqQuery.get('game_seq__max') is not None:
        maxGameSeq = int(maxGameSeqQuery.get('game_seq__max')) + 1
    userOpeDic = {}
    userOpeDic[userId] = {'userId':userId, 'gameResult':gameResult, 'huroResult':huroResult, 'tenpaiResult':tenpaiResult}

    # 点数パターン網羅
    score = 0
    if isTsumo == True and gameResult == str(const.Const.GameConst.和了):
        if userOpeDic[userQuery[0].user_id].get('huroResult') == str(const.Const.HuroConst.供託):
            kyotakuScore = kyotakuScore - 1000
        if oyaUserId == userQuery[0].user_id:
            score = tsumoScoreDic.get('oya') * 3
            score = score + gameStatusQuery.honba * 300
            score = score + kyotakuScore
        else:
            score = tsumoScoreDic.get('ko').get('oya')
            score = score + tsumoScoreDic.get('ko').get('ko') * 2
            score = score + gameStatusQuery.honba * 300
            score = score + kyotakuScore
    elif isTsumo == True:
        if oyaUserId == userQuery[0].user_id:
            score = score - tsumoScoreDic.get('ko').get('oya')
            score = score - gameStatusQuery.honba * 100
        else:
            if isOyaTsumo == True:
                score = score - tsumoScoreDic.get('oya')
                score = score - gameStatusQuery.honba * 100
            else:
                score = score - tsumoScoreDic.get('ko').get('ko')
                score = score - gameStatusQuery.honba * 100
    elif gameResult == str(const.Const.GameConst.和了):
        if userOpeDic[userQuery[0].user_id].get('huroResult') == str(const.Const.HuroConst.供託):
            score = score - 1000
        score = score + horaScore
    elif gameResult == str(const.Const.GameConst.放銃):
        score = score - hojuScore
    elif (horaUserId is None and userOpeDic[userQuery[0].user_id].get('tenpaiResult') == "1") or (horaUserId is None and userOpeDic[userQuery[0].user_id].get('huroResult') == const.Const.HuroConst.供託):
        score = score + tenpairyo
    elif horaUserId is None and userOpeDic[userQuery[0].user_id].get('tenpaiResult') == "0":
        score = score - bappu
    else:
        score = 0
    GameResult(year=year, hanso_id=maxHansoId, user_id=userQuery[0], game_seq=maxGameSeq, result_div=gameResult, huro_div=huroResult, score=score).save()

    userId = request.POST['user2']
    gameResult = request.POST['gameResult2']
    huroResult = request.POST['huroResult2']
    tenpaiResult = request.POST['tenpaiResult2']
    # ■userInfo取得
    conditionUserId = Q(user_id = userId)
    userQuery = UserMst.objects.all().filter(conditionUserId)

    userOpeDic[userId] = {'userId':userId, 'gameResult':gameResult, 'huroResult':huroResult, 'tenpaiResult':tenpaiResult}
    # 点数パターン網羅
    score = 0
    if isTsumo == True and gameResult == str(const.Const.GameConst.和了):
        if userOpeDic[userQuery[0].user_id].get('huroResult') == str(const.Const.HuroConst.供託):
            kyotakuScore = kyotakuScore - 1000
        if oyaUserId == userQuery[0].user_id:
            score = tsumoScoreDic.get('oya') * 3
            score = score + gameStatusQuery.honba * 300
            score = score + kyotakuScore
        else:
            score = tsumoScoreDic.get('ko').get('oya')
            score = score + tsumoScoreDic.get('ko').get('ko') * 2
            score = score + gameStatusQuery.honba * 300
            score = score + kyotakuScore
    elif isTsumo == True:
        if oyaUserId == userQuery[0].user_id:
            score = score - tsumoScoreDic.get('ko').get('oya')
            score = score - gameStatusQuery.honba * 100
        else:
            if isOyaTsumo == True:
                score = score - tsumoScoreDic.get('oya')
                score = score - gameStatusQuery.honba * 100
            else:
                score = score - tsumoScoreDic.get('ko').get('ko')
                score = score - gameStatusQuery.honba * 100
    elif gameResult == str(const.Const.GameConst.和了):
        if userOpeDic[userQuery[0].user_id].get('huroResult') == str(const.Const.HuroConst.供託):
            score = score - 1000
        score = score + horaScore
    elif gameResult == str(const.Const.GameConst.放銃):
        score = score - hojuScore
    elif (horaUserId is None and userOpeDic[userQuery[0].user_id].get('tenpaiResult') == "1") or (horaUserId is None and userOpeDic[userQuery[0].user_id].get('huroResult') == const.Const.HuroConst.供託):
        score = score + tenpairyo
    elif horaUserId is None and userOpeDic[userQuery[0].user_id].get('tenpaiResult') == "0":
        score = score - bappu
    else:
        score = 0
    GameResult(year=year, hanso_id=maxHansoId, user_id=userQuery[0], game_seq=maxGameSeq, result_div=gameResult, huro_div=huroResult, score=score).save()

    userId = request.POST['user3']
    gameResult = request.POST['gameResult3']
    huroResult = request.POST['huroResult3']
    tenpaiResult = request.POST['tenpaiResult3']
    # ■userInfo取得
    conditionUserId = Q(user_id = userId)
    userQuery = UserMst.objects.all().filter(conditionUserId)

    userOpeDic[userId] = {'userId':userId, 'gameResult':gameResult, 'huroResult':huroResult, 'tenpaiResult':tenpaiResult}
    # 点数パターン網羅
    score = 0
    if isTsumo == True and gameResult == str(const.Const.GameConst.和了):
        if userOpeDic[userQuery[0].user_id].get('huroResult') == str(const.Const.HuroConst.供託):
            kyotakuScore = kyotakuScore - 1000
        if oyaUserId == userQuery[0].user_id:
            score = tsumoScoreDic.get('oya') * 3
            score = score + gameStatusQuery.honba * 300
            score = score + kyotakuScore
        else:
            score = tsumoScoreDic.get('ko').get('oya')
            score = score + tsumoScoreDic.get('ko').get('ko') * 2
            score = score + gameStatusQuery.honba * 300
            score = score + kyotakuScore
    elif isTsumo == True:
        if oyaUserId == userQuery[0].user_id:
            score = score - tsumoScoreDic.get('ko').get('oya')
            score = score - gameStatusQuery.honba * 100
        else:
            if isOyaTsumo == True:
                score = score - tsumoScoreDic.get('oya')
                score = score - gameStatusQuery.honba * 100
            else:
                score = score - tsumoScoreDic.get('ko').get('ko')
                score = score - gameStatusQuery.honba * 100
    elif gameResult == str(const.Const.GameConst.和了):
        if userOpeDic[userQuery[0].user_id].get('huroResult') == str(const.Const.HuroConst.供託):
            score = score - 1000
        score = score + horaScore
    elif gameResult == str(const.Const.GameConst.放銃):
        score = score - hojuScore
    elif horaUserId is None and userOpeDic[userQuery[0].user_id].get('tenpaiResult') == "1" or (horaUserId is None and userOpeDic[userQuery[0].user_id].get('huroResult') == const.Const.HuroConst.供託):
        score = score + tenpairyo
    elif horaUserId is None and userOpeDic[userQuery[0].user_id].get('tenpaiResult') == "0":
        score = score - bappu
    else:
        score = 0
    GameResult(year=year, hanso_id=maxHansoId, user_id=userQuery[0], game_seq=maxGameSeq, result_div=gameResult, huro_div=huroResult, score=score).save()

    userId = request.POST['user4']
    gameResult = request.POST['gameResult4']
    huroResult = request.POST['huroResult4']
    tenpaiResult = request.POST['tenpaiResult4']
    # ■userInfo取得
    conditionUserId = Q(user_id = userId)
    userQuery = UserMst.objects.all().filter(conditionUserId)

    userOpeDic[userId] = {'userId':userId, 'gameResult':gameResult, 'huroResult':huroResult, 'tenpaiResult':tenpaiResult}
    # 点数パターン網羅
    score = 0
    if isTsumo == True and gameResult == str(const.Const.GameConst.和了):
        if userOpeDic[userQuery[0].user_id].get('huroResult') == str(const.Const.HuroConst.供託):
            kyotakuScore = kyotakuScore - 1000
        if oyaUserId == userQuery[0].user_id:
            score = tsumoScoreDic.get('oya') * 3
            score = score + gameStatusQuery.honba * 300
            score = score + kyotakuScore
        else:
            score = tsumoScoreDic.get('ko').get('oya')
            score = score + tsumoScoreDic.get('ko').get('ko') * 2
            score = score + gameStatusQuery.honba * 300
            score = score + kyotakuScore
    elif isTsumo == True:
        if oyaUserId == userQuery[0].user_id:
            score = score - tsumoScoreDic.get('ko').get('oya')
            score = score - gameStatusQuery.honba * 100
        else:
            if isOyaTsumo == True:
                score = score - tsumoScoreDic.get('oya')
                score = score - gameStatusQuery.honba * 100
            else:
                score = score - tsumoScoreDic.get('ko').get('ko')
                score = score - gameStatusQuery.honba * 100
    elif gameResult == str(const.Const.GameConst.和了):
        if userOpeDic[userQuery[0].user_id].get('huroResult') == str(const.Const.HuroConst.供託):
            score = score - 1000
        score = score + horaScore
    elif gameResult == str(const.Const.GameConst.放銃):
        score = score - hojuScore
    elif horaUserId is None and userOpeDic[userQuery[0].user_id].get('tenpaiResult') == "1" or (horaUserId is None and userOpeDic[userQuery[0].user_id].get('huroResult') == const.Const.HuroConst.供託):
        score = score + tenpairyo
    elif horaUserId is None and userOpeDic[userQuery[0].user_id].get('tenpaiResult') == "0":
        score = score - bappu
    else:
        score = 0
    GameResult(year=year, hanso_id=maxHansoId, user_id=userQuery[0], game_seq=maxGameSeq, result_div=gameResult, huro_div=huroResult, score=score).save()

    ########## 対局状況管理 ##########
    gameUserQuery = GameUser.objects.select_related().all().order_by('seq')
    gameStatusQuery = GameStatus.objects.select_related().all()[0] # 戦闘固定。1件しかない
    gameUserScoreSortedQuery = sorted(gameUserQuery, key=attrgetter('score'), reverse=True)

    # 次の局に進むかどうか
    isNextGame = False
    isHonbaAddRyukyoku = request.POST['checkRyukyoku']
    # 和了者なし、和了者が親ではない場合は次局へ
    # ただし、積み棒なしの場合は（親聴牌や九種九牌など）は積み棒のみ加算させるため次局へは進まない
    if horaUserId is None or horaUserId != oyaUserId or userOpeDic[oyaUserId].get('tenpaiResult') != "1":
        if isHonbaAddRyukyoku == "0":
            isNextGame = True

    # 各プレイヤーの点数の更新
    userIds = userOpeDic.keys()
    for userId in userIds:
        userOpe = userOpeDic[userId]
        score = 0
        gameResultQery = GameResult.objects.select_related().all().filter(year=year, hanso_id=maxHansoId, user_id=userOpe.get('userId'), game_seq=maxGameSeq).first()
        score = gameResultQery.score
        if userOpe.get('gameResult') != str(const.Const.GameConst.和了) and userOpe.get('huroResult') == str(const.Const.HuroConst.供託):
            score = score - 1000
        user = GameUser.objects.filter(user_id=userId).first()
        user.score += score
        user.save()

    ba = gameStatusQuery.ba
    kyoku = gameStatusQuery.kyoku
    kyotaku = gameStatusQuery.kyotaku
    honba = gameStatusQuery.honba

    # 次局に進む条件網羅
    isNext = False
    if horaUserId is not None and oyaUserId != horaUserId: # 親以外の和了
        isNext = True
    if (horaUserId is None and userOpeDic[oyaUserId].get('tenpaiResult') != "1"): # 親がノーテン
        if horaUserId is None and userOpeDic[oyaUserId].get('huroResult') != str(const.Const.HuroConst.供託):
            if isHonbaAddRyukyoku == "0":
                isNext = True

    # 供託網羅
    if horaUserId is None:
        kyotaku = kyotaku + addKyotaku
    else:
        kyotaku = 0
    # 本場網羅
    isAddHonba = False
    if horaUserId == oyaUserId:
        isAddHonba = True
    if horaUserId is None:
        if userOpeDic[oyaUserId].get('tenpaiResult') == "1" or userOpeDic[oyaUserId].get('tenpaiResult') == "0":
            isAddHonba = True
    if isHonbaAddRyukyoku == "1":
        isAddHonba = True

    if isNext == True:
        if ba == "東" and kyoku == 4:
            ba = "南"
            kyoku = 1
        elif ba == "南" and kyoku == 4:
            ba = "南" # 終了時はそのままキープする
            kyoku = 4
        else:
            kyoku = kyoku + 1
    if isAddHonba == True:
        honba = honba + 1
    else:
        honba = 0

    GameStatus.objects.all().delete()
    GameStatus(ba=ba, kyoku=kyoku, honba=honba, kyotaku=kyotaku).save()
    gameStatusQuery = GameStatus.objects.select_related().all()[0] # 戦闘固定。1件しかない

    # rankとUserIdで紐付け
    rankDic = {}
    for gameUser in gameUserQuery:
        rank = 1
        for gameUserScoreSorted in gameUserScoreSortedQuery:
            if  gameUser.user_id == gameUserScoreSorted.user_id:
                rankDic[gameUser.user_id] = rank
                break
            rank = rank + 1

    if 4 <= len(gameUserQuery):
        # context別だからそれぞれで取る
        user1 = showScoreUpdateDto.ShowScoreUpdateLabel(gameUserQuery[0], rankDic[gameUserQuery[0].user_id], gameStatusQuery.kyoku == 1)
        user2 = showScoreUpdateDto.ShowScoreUpdateLabel(gameUserQuery[1], rankDic[gameUserQuery[1].user_id], gameStatusQuery.kyoku == 2)
        user3 = showScoreUpdateDto.ShowScoreUpdateLabel(gameUserQuery[2], rankDic[gameUserQuery[2].user_id], gameStatusQuery.kyoku == 3)
        user4 = showScoreUpdateDto.ShowScoreUpdateLabel(gameUserQuery[3], rankDic[gameUserQuery[3].user_id], gameStatusQuery.kyoku == 4)
    settingUsers = getShowScoreUpdateDto()
    gameStatus = showScoreUpdateDto.GameStatus(gameStatusQuery)
    # return render(request, 'mahjong/show-score-update.html',
    #              {'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4,
    #               'settingUsers':settingUsers, 'gameStatus':gameStatus, 'isReload':1,
    #               'error_message': "対局登録が完了しました"})
    return redirect('/mahjong/showScoreUpdate?messageDiv=1')

# 対局設定
def settingUser(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    # バリデーションチェック
    check = userValidation(request)
    if check == USER_UNREG:
        # レンダリング
        users_obj = UserMst.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
        # return render(request, 'mahjong/show-score-update.html', {
        # 'settingUsers': usersRes,
        # 'error_message': "プレイヤーを4人登録してください"})
        return redirect('/mahjong/showScoreUpdate?messageDiv=4')
    if check == USER_DUP:
        # レンダリング
        users_obj = UserMst.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
        # return render(request, 'mahjong/show-score-update.html', {
        # 'settingUsers': usersRes,
        # 'error_message': "プレイヤーが重複しています"})
        return redirect('/mahjong/showScoreUpdate?messageDiv=5')

    # GameUserをdelete-insert。同期遷移しても保持させる
    GameUser.objects.all().delete()
    GameStatus.objects.all().delete()
    GameStatus(ba="東", kyoku=1, honba=0, kyotaku=0).save()
    gameStatusQuery = GameStatus.objects.select_related().all()[0] # 戦闘固定。1件しかない

    # ■form取得。たぶんもっといい方法ある
    userId = request.POST['user1']
    user1 = getSettingUser(userId, 1)
    userId = request.POST['user2']
    user2 = getSettingUser(userId, 2)
    userId = request.POST['user3']
    user3 = getSettingUser(userId, 3)
    userId = request.POST['user4']
    user4 = getSettingUser(userId, 4)
    settingUsers = getShowScoreUpdateDto()
    gameStatus = showScoreUpdateDto.GameStatus(gameStatusQuery)
    return render(request, 'mahjong/show-score-update.html',
                 {'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4,
                  'settingUsers':settingUsers,'gameStatus':gameStatus })

# fromでそれぞれで取得するため、別出
def getSettingUser(userId, seq):
    conditionUserId = Q(user_id = userId)
    userQuery = UserMst.objects.all().filter(conditionUserId)
    user = None
    if (seq == 1):
        isOya = True
    else:
        isOya = False

    for user in userQuery:
        # GameUserについでに登録する
        GameUser(seq = seq, user_id = user.user_id, last_name = user.last_name, first_name = user.first_name, score=25000).save()
        user = query.Query.getGameUserWhereUserId(userId)
        # 初回登録なので固定
        user = (showScoreUpdateDto.ShowScoreUpdateLabel(user[0], seq, isOya))
    return user

def getShowScoreUpdateDto():
    # ■UserInfoをuser_idの昇順で取得
    users_obj = UserMst.objects.select_related().all().order_by('user_id')
    usersRes = []
    for user in users_obj:
        # 使わないので0固定
        usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
    return usersRes

def userValidation(request):
    # ■form取得。多分もっといい方法ある
    noUser = 'default'
    userIds = []
    userScores = []
    userIds.append(request.POST['user1'])
    userIds.append(request.POST['user2'])
    userIds.append(request.POST['user3'])
    userIds.append(request.POST['user4'])

    # ■IDのバリデーションチェック：ユーザ未選択
    for userId in userIds:
        if userId == noUser:
            return USER_UNREG

    # ■IDのバリデーションチェック：重複
    cnt = -1
    for userId in userIds:
        cnt = cnt + 1 # 仕方なし
        for index, chkUserId in enumerate(userIds):
            if cnt == index: # 自身は重複として見ない
                continue
            if userId == chkUserId:
                return USER_DUP

# 更新管理チェック
def isUpdatePossible():
    isUpdatePossibleQuery = IsUpdateMng.objects.all().filter(is_update='1')
    if isUpdatePossibleQuery.first() is None:
        return False
    return True

# 個人詳細表示
def showDetail(request, userId):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    command = showDetailCommand.ShowDetailCommand(userId)
    showDetailInfo = command.getShowDetailInfo(request)

    # 表示する年を確定させる
    # cookieに保存されていない場合はシステム日付の年をデフォルトにする
    selectYear = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
    # ここのifホンマに謎。NoneなのにTrueにならない
    if selectYear is None:
        selectYear = datetime.datetime.now()
        selectYear = str(selectYear.year)

    users = UserInfo.objects.values()
    userMstQuery = UserMst.objects.values()
    if const.Const.ScreenConst.ALL_YEAR != selectYear:
        hansos = HansoSum.objects.values().filter(year=selectYear)
        results = GameResult.objects.values().filter(year=selectYear)
    else:
        hansos = HansoSum.objects.values()
        results = GameResult.objects.values()

    userMstDictionary = {}
    for userMst in userMstQuery:
        userMstDictionary[userMst.get('user_id')] = userMst

    resultDictionary = {}
    for result in results:
        resultList = []
        if result.get('hanso_id') in resultDictionary:
            resultList[len(resultList):len(resultList)] = resultDictionary[result.get('hanso_id')]
        resultList.append(result)
        resultDictionary[result.get('hanso_id')] = resultList

    # 対象のユーザの半荘IDのみ取得
    hansoIdList = []
    for hanso in hansos:
        if hanso.get('user_id_id') == userId:
            hansoIdList.append(hanso)
    # 半荘データなしは以降処理なし
    if len(hansoIdList) == 0:
         response = render(request, 'mahjong/show-detail.html', {'details':None, 'info':showDetailInfo})
         # cookieに保存されていない場合はシステム日付の年をデフォルトで設定
         cookie = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
         # ここのifホンマに謎。NoneなのにTrueにならない
         if cookie is None or len(cookie) == 0:
              cookie = datetime.datetime.now()
              response.set_cookie(const.Const.Cookie.SELECT_YEAR, str(cookie.year))
         return response

    # 同半荘IDの情報取得
    scoreDetails = []
    for hansoId in hansoIdList:
        for hanso in hansos:
            if hansoId.get('hanso_id') == hanso.get('hanso_id'):
                scoreDetails.append(hanso)

    # 先頭だけ普通に日付いれる
    dateWk = localtime(scoreDetails[0].get('insert_date'))
    dateWk = str(dateWk.year) + '/' + str(dateWk.month) + '/' + str(dateWk.day)
    hansoIdWk = scoreDetails[0].get('hanso_id')

    detailUsers = []
    detailBattles = []
    details = []
    battleNo = 0
    isFirst = True
    for scoreDetail in scoreDetails:
        date = localtime(scoreDetail.get('insert_date'))
        date = str(date.year) + '/' + str(date.month) + '/' + str(date.day)
        user = getUser(users, scoreDetail.get('user_id_id'))

        # 半荘毎の和了率・放銃率
        # データ取得ミスの関係で取得できない場合あり。0固定
        hansoResultList = resultDictionary.get(scoreDetail.get('hanso_id'))
        horaCnt = 0
        hojuCnt = 0
        totalCnt = 0
        if hansoResultList is not None:
            for hansoResult in hansoResultList:
                if hansoResult.get('user_id_id') == scoreDetail.get('user_id_id'):
                    totalCnt = totalCnt + 1
                    if hansoResult.get('result_div') == int(const.Const.GameConst.和了):
                        horaCnt = horaCnt + 1
                    elif hansoResult.get('result_div') == int(const.Const.GameConst.放銃):
                        hojuCnt = hojuCnt + 1

        isMine = 1 if user.get('user_id_id') == userId else 0

        # 同じ半荘ID
        if hansoIdWk == scoreDetail.get('hanso_id'):
            totalCntWk = totalCnt
            hansoIdWk = scoreDetail.get('hanso_id')
            detailUsers.append(showDetailUserListDto.ShowDetailUserListDto(user.get('user_id_id')
                                                                            , userMstDictionary[user.get('user_id_id')].get('last_name')
                                                                            , userMstDictionary[user.get('user_id_id')].get('first_name')
                                                                            , scoreDetail.get('rank')
                                                                            , scoreDetail.get('score')
                                                                            , horaCnt
                                                                            , format(horaCnt / totalCnt, '.1f') if totalCnt != 0 else 0
                                                                            , hojuCnt
                                                                            , format(hojuCnt / totalCnt, '.1f') if totalCnt != 0 else 0
                                                                            , scoreDetail.get('score_result')
                                                                            , isMine))
            continue
        else:
            hansoIdWk = scoreDetail.get('hanso_id')
            battleNo = battleNo + 1
            showDetailBattleDto = showDetailBattleListDto.ShowDetailBattleListDto(battleNo, detailUsers, totalCntWk)
            detailBattles.append(showDetailBattleDto)
            detailUsers = []
            detailUsers.append(showDetailUserListDto.ShowDetailUserListDto(user.get('user_id_id')
                                                                            , userMstDictionary[user.get('user_id_id')].get('last_name')
                                                                            , userMstDictionary[user.get('user_id_id')].get('first_name')
                                                                            , scoreDetail.get('rank')
                                                                            , scoreDetail.get('score')
                                                                            , horaCnt
                                                                            , format(horaCnt / totalCnt, '.1f') if totalCnt != 0 else 0
                                                                            , hojuCnt
                                                                            , format(hojuCnt / totalCnt, '.1f') if totalCnt != 0 else 0
                                                                            , scoreDetail.get('score_result')
                                                                            , isMine))
        # 同じ日付内
        if dateWk == date:
            dateWk = date
            continue
        else:
            battleNo = 0
            dayScore = 0
            for battle in detailBattles:
                for us in battle.detailUsers:
                    if userId == us.userId:
                        dayScore = dayScore + us.scoreResult
            showDetail = showDetailDto.ShowDetailDto(dateWk, dayScore, detailBattles)
            details.append(showDetail)
            detailBattles = []
            detailUsers = []
            detailUsers.append(showDetailUserListDto.ShowDetailUserListDto(user.get('user_id_id')
                                                                            , userMstDictionary[user.get('user_id_id')].get('last_name')
                                                                            , userMstDictionary[user.get('user_id_id')].get('first_name')
                                                                            , scoreDetail.get('rank')
                                                                            , scoreDetail.get('score')
                                                                            , horaCnt
                                                                            , format(horaCnt / totalCnt, '.1f') if totalCnt != 0 else 0
                                                                            , hojuCnt
                                                                            , format(hojuCnt / totalCnt, '.1f') if totalCnt != 0 else 0
                                                                            , scoreDetail.get('score_result')
                                                                            , isMine))
            dateWk = date

    battleNo = battleNo + 1
    showDetailBattleDto = showDetailBattleListDto.ShowDetailBattleListDto(battleNo, detailUsers, totalCnt)
    detailBattles.append(showDetailBattleDto)
    dayScore = 0
    for battle in detailBattles:
        for user in battle.detailUsers:
            if userId == user.userId:
                dayScore = dayScore + user.scoreResult
    showDetail = showDetailDto.ShowDetailDto(dateWk, dayScore, detailBattles)
    details.append(showDetail)
    response = render(request, 'mahjong/show-detail.html', {'details':details, 'info':showDetailInfo})

    # cookieに保存されていない場合はシステム日付の年をデフォルトで設定
    cookie = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
    # ここのifホンマに謎。NoneなのにTrueにならない
    if cookie is None or len(cookie) == 0:
         cookie = datetime.datetime.now()
         response.set_cookie(const.Const.Cookie.SELECT_YEAR, str(cookie.year))
    return response

# 年変更
def changeYear(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    # 登録済みの年の取得
    yearQuery = UserInfo.objects.all().values('year').annotate().order_by('-year')
    years = []
    for year in yearQuery:
        if str(year.get('year')) not in years:
            years.append(str(year.get('year')))
            continue
    # いつが選択済みなのかを決める
    selectYear = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
    yearsInfo = []
    for year in years:
        isSelected = False
        if selectYear == year:
            isSelected = True
        yearsInfo.append(yearInfoDto.YearInfoDto(year, isSelected))

    isAllYear = False
    if const.Const.ScreenConst.ALL_YEAR == selectYear:
        isAllYear = True
    yearsInfo = changeYearDto.ChangeYearDto(yearsInfo, isAllYear)
    return render(request, 'mahjong/change-year.html', {'yearsInfo':yearsInfo})

def getUser(users, userId):
    for user in users:
        if user.get('user_id_id') == userId:
            return user

# 役満一覧
def showYakuman(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    # 登録済みの年の取得
    yearQuery = UserInfo.objects.all().values('year').annotate().order_by('-year')
    years = []
    for year in yearQuery:
        if str(year.get('year')) not in years:
            years.append(str(year.get('year')))
            continue
    # いつが選択済みなのかを決める
    selectYear = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
    yearsInfo = []
    for year in years:
        isSelected = False
        if selectYear == year:
            isSelected = True
        yearsInfo.append(yearInfoDto.YearInfoDto(year, isSelected))

    isAllYear = False
    if const.Const.ScreenConst.ALL_YEAR == selectYear:
        isAllYear = True
    yearsInfo = changeYearDto.ChangeYearDto(yearsInfo, isAllYear)
    return render(request, 'mahjong/show-yakuman.html', {'yearsInfo':yearsInfo})

def getGraph(request, userId):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response

    # 表示する年を確定させる
    # cookieに保存されていない場合はシステム日付の年をデフォルトにする
    selectYear = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
    # ここのifホンマに謎。NoneなのにTrueにならない
    if selectYear is None:
        selectYear = datetime.datetime.now()
        selectYear = str(selectYear.year)

    if const.Const.ScreenConst.ALL_YEAR != selectYear:
        hansos = HansoSum.objects.values().filter(year=selectYear, user_id=userId)
    else:
        hansos = HansoSum.objects.values().filter(user_id=userId)
    cnt = 1
    list = []
    scoreWk = 0
    for hanso in hansos:
        scoreWk = scoreWk + hanso.get('score_result')
        obj = {"year":cnt, "value":scoreWk}
        list.append(obj)
        cnt = cnt + 1
    dict = {"data":list}
    return JsonResponse(dict)

# スコア更新の点数状況を取得、反映させる
def getReView(request):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    gameUsers = GameUser.objects.values()
    list = []
    for gameUser in gameUsers:
        userId = gameUser.get('user_id')
        score = gameUser.get('score')
        obj = {"userId":userId, "score":score}
        list.append(obj)

    gameStatuses = GameStatus.objects.values()
    gameStatus = gameStatuses[0]
    dict = {"users":list, "ba":gameStatus.get('ba'), "kyoku":gameStatus.get('kyoku'), "honba":gameStatus.get('honba'), "kyotaku":gameStatus.get('kyotaku')}
    return JsonResponse(dict)

# スコア修正
def fixScore(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    ba = request.POST['ba']
    kyoku = request.POST['kyoku']
    if type(kyoku) is str and 1 < len(kyoku):
        kyoku = kyoku[2]
        kyoku.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
    kyotaku = request.POST['kyotaku']
    honba = request.POST['tsumibo']

    #delete - insert
    GameStatus.objects.all().delete()
    GameStatus(ba=ba, kyoku=kyoku, honba=honba, kyotaku=kyotaku).save()
    gameStatusQuery = GameStatus.objects.select_related().all()[0] # 戦闘固定。1件しかない

    # ■form取得。たぶんもっといい方法ある
    userId1 = request.POST['user1']
    score1 = request.POST['score1']
    userId2 = request.POST['user2']
    score2 = request.POST['score2']
    userId3 = request.POST['user3']
    score3 = request.POST['score3']
    userId4 = request.POST['user4']
    score4 = request.POST['score4']
    # 更新。最高に頭悪い。俺しか見ないからいい
    user = GameUser.objects.filter(user_id=userId1).first()
    user.score = score1
    user.save()
    user = GameUser.objects.filter(user_id=userId2).first()
    user.score = score2
    user.save()
    user = GameUser.objects.filter(user_id=userId3).first()
    user.score = score3
    user.save()
    user = GameUser.objects.filter(user_id=userId4).first()
    user.score = score4
    user.save()

    return redirect('/mahjong/showScoreUpdate?messageDiv=7')

def manage(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    return render(request, 'mahjong/manage.html')
def manageDBUpdate(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    return render(request, 'mahjong/manageDBUpdate.html')
def manageDB(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    return render(request, 'mahjong/manageDB.html')
def manageGit(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    return render(request, 'mahjong/manageGit.html')
def managePythonAnywhere(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    return render(request, 'mahjong/managePythonAnywhere.html')
def manageYakuman(request, **kwargs):
    if isOkinaMem(request) == False:
        response = redirect('/login')
        return response
    return render(request, 'mahjong/manageYakuman.html')
def login(request, **kwargs):
    if isOkinaMem(request):
        command = showRankingCommand.ShowRankingCommand()
        showRankingInfo = command.getShowRankingInfo(request)
        response = render(request, 'mahjong/score.html',
            {'users':showRankingInfo.users, 'usersHanso':showRankingInfo.usersHanso, 'usersHora':showRankingInfo.usersHora,
             'userHoju':showRankingInfo.userHoju})
        response.set_cookie(const.Const.Cookie.IS_OKINA_MEM, 'success')
        # cookieに保存されていない場合はシステム日付の年をデフォルトで設定
        cookie = request.COOKIES.get(const.Const.Cookie.SELECT_YEAR)
        # ここのifホンマに謎。NoneなのにTrueにならない
        if cookie is None or len(cookie) == 0:
            cookie = datetime.datetime.now()
            response.set_cookie(const.Const.Cookie.SELECT_YEAR, str(cookie.year))
        return response
    else:
        return render(request, 'mahjong/login.html')

def doLogin(request, **kwargs):
    loginId = request.POST['loginIdvalue']
    password = request.POST['passwordvalue']
    # 1件しかない
    doLoginQuery = DoLogin.objects.values()[0]
    if loginId == doLoginQuery.get('loginid') and password == doLoginQuery.get('password'):
        max_age = 60 * 60 * 24 * 365
        response = redirect('/showRanking')
        response.set_cookie(const.Const.Cookie.IS_OKINA_MEM, 'success', max_age = max_age)
        return response
    else:
        response = render(request, 'mahjong/login.html', {'message':'ログインID、またはパスワードが異なります'})
    return response

def isOkinaMem(request):
    return request.COOKIES.get(const.Const.Cookie.IS_OKINA_MEM) == 'success'

def test(request, **kwargs):
    lineBotCommand.LineBotCommand.pushTest("Hi, OkinaKaNakoku")
    return render(request, 'mahjong/test.html')
