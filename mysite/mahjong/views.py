import sys
from mahjong.dto import indexScoreDto
from mahjong.dto import showScoreUpdateDto
from mahjong.dto import updateScoreDAO

from operator import itemgetter
from operator import attrgetter
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db.models import Max
from django.utils import timezone
from django.views import generic
from decimal import Decimal
from django.db.models import Q

from .models import UserInfo, HansoSum, GameUser, GameResult, IsUpdateMng

# 定数
USER_UNREG = 'userUnreg'
USER_DUP = 'userDup'
和了 = '1'
放銃 = '2'


# スコア表示
class IndexScore(generic.ListView):
    template_name = 'mahjong/score.html'
    context_object_name = 'users'

    def get_queryset(self, **kwargs):
        # ■UserInfoをスコアの降順で取得
        users_obj = UserInfo.objects.select_related().all().order_by('-score_sum')
        
        usersRes = []
        scoreList = []  # 同率で使う
        cnt = 0        # 同率で使う
        isFirst = True # 同率で使う
        rank = 1
        if users_obj is None:
            return usersRes

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
            if not scoreList[cnt] == user.score_sum:
                isDoritsu = False
            cnt = cnt + 1
            if not isDoritsu:
                rank = len(scoreList) + 1
            scoreList.append(user.score_sum)
            usersRes.append(indexScoreDto.UserScore(user, rank, topDiff))

        return usersRes

# スコア更新表示
def showScoreUpdate(request):
    # ■UserInfoをuser_idの昇順で取得
    settingUsers = getShowScoreUpdateDto()
    # ■GameUserを全取得
    user1 = None
    user2 = None
    user3 = None
    user4 = None
    gameUserQuery = GameUser.objects.select_related().all()
    if gameUserQuery.first() is not None:
        # context別だからそれぞれで取る
        user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
        user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
        user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
        user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
    return render(request, 'mahjong/show-score-update.html',
                 {'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4,
                  'settingUsers':settingUsers})

# スコア更新
def updateScore(request):
    if isUpdatePossible() == False: # 更新不可
        # レンダリング
        gameUserQuery = GameUser.objects.select_related().all()
        user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
        user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
        user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
        user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
        users_obj = UserInfo.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
        return render(request, 'mahjong/show-score-update.html', {
        'users': usersRes,
        'error_message': "更新不可です。更新管理をUPDATEしてください",
        'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4})


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
            users_obj = UserInfo.objects.select_related().all().order_by('user_id')
            usersRes = []
            for user in users_obj:
                usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
            return render(request, 'mahjong/show-score-update.html', {
            'users': usersRes,
            'error_message': "スコアを全て登録してください",
            'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4})
    
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

    # ■HansoSum to Insert
    # ■UserInfo to Update
    hansoIdParam = maxHansoId
    rankParam = 1
    for dao in rankSortDaos:
        # ★★TODO 同率順位などのレアケースは見ない。javaなら書いてやるよ
        # 計算処理
        userIdParam = dao.userId
        scoreParam = dao.score
        userObj = UserInfo.objects.all().filter(user_id=userIdParam)

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
        HansoSum(hanso_id=hansoIdParam
                , user_id=userObj.first()
                , rank=rankParam
                , score=scoreParam
                , score_result=scoreResultParam).save()
        dao = UserInfo.objects.filter(user_id=userIdParam).first()
        dao.score_sum += Decimal(str(scoreResultParam))
        dao.save()
        rankParam = rankParam + 1

    # エラーメッセージを返して、レンダリングするが、正常終了のはず
    gameUserQuery = GameUser.objects.select_related().all()
    user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
    user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
    user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
    user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
    users_obj = UserInfo.objects.select_related().all().order_by('user_id')
    usersRes = []
    for user in users_obj:
        usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
    return render(request, 'mahjong/show-score-update.html', {
    'settingUsers': usersRes,
    'error_message': "スコア登録が完了しました",
    'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4})

# 点数表表示
def scoreTable(request):
    return render(request, 'mahjong/score-table.html')

# 対局登録
def updateGame(request, **kwargs):
    if isUpdatePossible() == False:
        # レンダリング
        gameUserQuery = GameUser.objects.select_related().all()
        user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
        user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
        user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
        user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
        users_obj = UserInfo.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
        return render(request, 'mahjong/show-score-update.html', {
        'users': usersRes,
        'error_message': "更新不可です。更新管理をUPDATEしてください",
        'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4})

    # バリデーションチェック
    validResult = []
    if request.POST['gameResult1'] == 和了:
        validResult.append(request.POST['gameResult1'])
    if request.POST['gameResult2'] == 和了:
        validResult.append(request.POST['gameResult2'])
    if request.POST['gameResult3'] == 和了:
        validResult.append(request.POST['gameResult3'])
    if request.POST['gameResult4'] == 和了:
        validResult.append(request.POST['gameResult4'])
    if 1 < len(validResult):
        # 和了者が複数
        gameUserQuery = GameUser.objects.select_related().all()
        user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
        user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
        user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
        user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
        users_obj = UserInfo.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
        return render(request, 'mahjong/show-score-update.html', {
        'settingUsers': usersRes,
        'error_message': "和了者は複数登録できません",
        'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4})

    validResult = []
    if request.POST['gameResult1'] == 放銃:
        validResult.append(request.POST['gameResult1'])
    if request.POST['gameResult2'] == 放銃:
        validResult.append(request.POST['gameResult2'])
    if request.POST['gameResult3'] == 放銃:
        validResult.append(request.POST['gameResult3'])
    if request.POST['gameResult4'] == 放銃:
        validResult.append(request.POST['gameResult4'])
    if 1 < len(validResult):
        # 和了者が複数
        gameUserQuery = GameUser.objects.select_related().all()
        user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
        user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
        user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
        user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
        users_obj = UserInfo.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
        return render(request, 'mahjong/show-score-update.html', {
        'settingUsers': usersRes,
        'error_message': "放銃者は複数登録できません",
        'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4})

    # ■form取得
    userId = request.POST['user1']
    gameResult = request.POST['gameResult1']
    
    # ■userInfo取得
    conditionUserId = Q(user_id = userId)
    userQuery = UserInfo.objects.all().filter(conditionUserId)
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
    GameResult(hanso_id=maxHansoId, user_id=userQuery[0], game_seq=maxGameSeq, result_div=gameResult).save()

    userId = request.POST['user2']
    gameResult = request.POST['gameResult2']
    # ■userInfo取得
    conditionUserId = Q(user_id = userId)
    userQuery = UserInfo.objects.all().filter(conditionUserId)
    GameResult(hanso_id=maxHansoId, user_id=userQuery[0], game_seq=maxGameSeq, result_div=gameResult).save()

    userId = request.POST['user3']
    gameResult = request.POST['gameResult3']
    # ■userInfo取得
    conditionUserId = Q(user_id = userId)
    userQuery = UserInfo.objects.all().filter(conditionUserId)
    GameResult(hanso_id=maxHansoId, user_id=userQuery[0], game_seq=maxGameSeq, result_div=gameResult).save()
    
    userId = request.POST['user4']
    gameResult = request.POST['gameResult4']
    # ■userInfo取得
    conditionUserId = Q(user_id = userId)
    userQuery = UserInfo.objects.all().filter(conditionUserId)
    GameResult(hanso_id=maxHansoId, user_id=userQuery[0], game_seq=maxGameSeq, result_div=gameResult).save()


    # ■レンダリング用オブジェクト取得。TODO そのうち共通化
    gameUserQuery = GameUser.objects.select_related().all()
    user1 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[0])
    user2 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[1])
    user3 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[2])
    user4 = showScoreUpdateDto.ShowScoreUpdate(gameUserQuery[3])
    settingUsers = getShowScoreUpdateDto()
    return render(request, 'mahjong/show-score-update.html',
                 {'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4,
                  'settingUsers':settingUsers,
                  'error_message': "対局登録が完了しました"})

# プレイヤー設定
def settingUser(request, **kwargs):
    # バリデーションチェック
    check = userValidation(request)
    if check == USER_UNREG:
        # レンダリング
        users_obj = UserInfo.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
        return render(request, 'mahjong/show-score-update.html', {
        'settingUsers': usersRes,
        'error_message': "プレイヤーを4人登録してください"})
    if check == USER_DUP:
        # レンダリング
        users_obj = UserInfo.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
        return render(request, 'mahjong/show-score-update.html', {
        'settingUsers': usersRes,
        'error_message': "プレイヤーが重複しています"})
    
    # GameUserをdelete-insert。同期遷移しても保持させる
    GameUser.objects.all().delete()
    # ■form取得。たぶんもっといい方法ある
    userId = request.POST['user1']
    user1 = getSettingUser(userId)
    userId = request.POST['user2']
    user2 = getSettingUser(userId)
    userId = request.POST['user3']
    user3 = getSettingUser(userId)
    userId = request.POST['user4']
    user4 = getSettingUser(userId)
    settingUsers = getShowScoreUpdateDto()
    return render(request, 'mahjong/show-score-update.html',
                 {'user1':user1, 'user2':user2, 'user3':user3, 'user4':user4,
                  'settingUsers':settingUsers})

# fromでそれぞれで取得するため、別出
def getSettingUser(userId):
    conditionUserId = Q(user_id = userId)
    userQuery = UserInfo.objects.all().filter(conditionUserId)
    user = None
    for user in userQuery:
        # GameUserについでに登録する
        GameUser(user_id = user.user_id, last_name = user.last_name, first_name = user.first_name).save()
        user = (showScoreUpdateDto.ShowScoreUpdate(user))
    return user

def getShowScoreUpdateDto():
    # ■UserInfoをuser_idの昇順で取得
    users_obj = UserInfo.objects.select_related().all().order_by('user_id')
    usersRes = []
    for user in users_obj:
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

