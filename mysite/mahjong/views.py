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

from .models import UserInfo, HansoSum

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
        print(users_obj)
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
class ShowScoreUpdate(generic.ListView):
    template_name = 'mahjong/show-score-update.html'
    context_object_name = 'users'

    def get_queryset(self):
        # ■UserInfoをuser_idの昇順で取得
        users_obj = UserInfo.objects.select_related().all().order_by('user_id')
        usersRes = []
        for user in users_obj:
            usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))

        return usersRes

# スコア更新
def updateScore(request):
    # f■orm取得
    noUser = 'default'
    userIds = []
    userScores = []
    userIds.append(request.POST['user1'])
    userIds.append(request.POST['user2'])
    userIds.append(request.POST['user3'])
    userIds.append(request.POST['user4'])
    userScores.append(request.POST['score1'])
    userScores.append(request.POST['score2'])
    userScores.append(request.POST['score3'])
    userScores.append(request.POST['score4'])

    # ■IDのバリデーションチェック：ユーザ未選択
    for userId in userIds:
        if userId == noUser:
            # レンダリング
            users_obj = UserInfo.objects.select_related().all().order_by('user_id')
            usersRes = []
            for user in users_obj:
                usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
            return render(request, 'mahjong/show-score-update.html', {
            'users': usersRes,
            'error_message': "プレイヤーを4人登録してください"})

    # ■IDのバリデーションチェック：重複
    cnt = -1
    for userId in userIds:
        cnt = cnt + 1 # 仕方なし
        for index, chkUserId in enumerate(userIds):
            if cnt == index: # 自身は重複として見ない
                continue
            if userId == chkUserId:
                # レンダリング
                users_obj = UserInfo.objects.select_related().all().order_by('user_id')
                usersRes = []
                for user in users_obj:
                    usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
                return render(request, 'mahjong/show-score-update.html', {
                'users': usersRes,
                'error_message': "プレイヤーが重複しています"})
    
    # ■スコアのバリデーションチェック
    for userScore in userScores:
        if userScore == '': # スコア未登録
            # レンダリング
            users_obj = UserInfo.objects.select_related().all().order_by('user_id')
            usersRes = []
            for user in users_obj:
                usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
            return render(request, 'mahjong/show-score-update.html', {
            'users': usersRes,
            'error_message': "スコアを全て登録してください"})
    
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
    for rank in rankSortDaos:
        print(rank.userId)
        print(rank.score)

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
        print(userObj)

        # ウマ・オカ計算 ★★TODO 関数化
        if rankParam == 1:
            scoreResultParam = int(scoreParam) + 20000 + 10000
            scoreResultParam = scoreResultParam / 1000
            scoreResultParam = scoreResultParam - 30
            HansoSum(hanso_id=hansoIdParam
                   , user_id=userObj.first()
                   , rank=rankParam
                   , score=scoreParam
                   , score_result=scoreResultParam).save()
            dao = UserInfo.objects.filter(user_id=userIdParam).first()
            dao.score_sum += scoreResultParam
            dao.save()
            
        elif rankParam == 2:
            scoreResultParam = int(scoreParam) + 5000
            scoreResultParam = scoreResultParam / 1000
            scoreResultParam = scoreResultParam - 30
            HansoSum(hanso_id=hansoIdParam
                   , user_id=userObj.first()
                   , rank=rankParam
                   , score=scoreParam
                   , score_result=scoreResultParam).save()
            dao = UserInfo.objects.filter(user_id=userIdParam).first()
            dao.score_sum += scoreResultParam
            dao.save()
        elif rankParam == 3:
            scoreResultParam = int(scoreParam) - 5000
            scoreResultParam = scoreResultParam / 1000
            scoreResultParam = scoreResultParam - 30
            HansoSum(hanso_id=hansoIdParam
                   , user_id=userObj.first()
                   , rank=rankParam
                   , score=scoreParam
                   , score_result=scoreResultParam).save()
            dao = UserInfo.objects.filter(user_id=userIdParam).first()
            dao.score_sum += scoreResultParam
            dao.save()
        elif rankParam == 4:
            scoreResultParam = int(scoreParam) - 10000
            scoreResultParam = scoreResultParam / 1000
            scoreResultParam = scoreResultParam - 30
            HansoSum(hanso_id=hansoIdParam
                   , user_id=userObj.first()
                   , rank=rankParam
                   , score=scoreParam
                   , score_result=scoreResultParam).save()
            dao = UserInfo.objects.filter(user_id=userIdParam).first()
            dao.score_sum += scoreResultParam
            dao.save()
        rankParam = rankParam + 1






    # エラーメッセージを返して、レンダリングするが、正常終了のはず
                # レンダリング
    users_obj = UserInfo.objects.select_related().all().order_by('user_id')
    usersRes = []
    for user in users_obj:
        usersRes.append(showScoreUpdateDto.ShowScoreUpdate(user))
    return render(request, 'mahjong/show-score-update.html', {
    'users': usersRes,
    'error_message': "登録が完了しました"})

# user重複チェック
def user_duplicate(user):
    return len(user) != len(setattr(user))