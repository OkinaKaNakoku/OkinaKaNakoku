from django.db import models
from django.utils import timezone

# Create your models here.

## ユーザマスタ
class UserMst(models.Model):
    user_id = models.CharField(primary_key=True, max_length=4)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    eng_last_name = models.CharField(null=True, max_length=100)
    eng_first_name = models.CharField(null=True, max_length=100)

    def __str__(self):
        #return str(self.user_id + ' ： ' + self.last_name + ' ' + self.first_name)
        return str(self.user_id) + ' ： ' + str(self.last_name) + ' ' + str(self.first_name)

## ユーザ情報
class UserInfo(models.Model):
    year = models.IntegerField(null=False, default=2020)
    user_id = models.ForeignKey(UserMst, db_column='user_id', on_delete=models.DO_NOTHING, null=True)
    score_sum = models.DecimalField(max_digits=6,decimal_places=1,default=0.0)

    def __str__(self):
        return str(self.user_id)

# 半荘合計。基本hanso_id 1：user_id 4
class HansoSum(models.Model):
    year = models.IntegerField(null=False, default=2020)
    hanso_id = models.IntegerField()
    user_id = models.ForeignKey(UserMst, db_column='user_id', on_delete=models.DO_NOTHING)
    rank = models.CharField(max_length=1)
    score = models.IntegerField(default=0)
    score_result = models.DecimalField(max_digits=6,decimal_places=1,default=0.0)
    insert_date = models.DateTimeField(default=timezone.now)
    update_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        userId = self.user_id.user_id
        user = UserMst.objects.select_related().get(user_id=userId)
        return str(self.hanso_id) + '：' + user.last_name + ' ' + user.first_name

    class Meta:
        constraints = [
            # user_idをuniqueとする
            models.UniqueConstraint(fields=['hanso_id', 'user_id'], name='unique_hanso')
        ]

# 対局結果
class GameResult(models.Model):
    year = models.IntegerField(null=False, default=2020)
    hanso_id = models.IntegerField()
    user_id = models.ForeignKey(UserMst, db_column='user_id', on_delete=models.DO_NOTHING, default=0000)
    game_seq = models.IntegerField()
    '''結果区分｜「0：なし」・「1：和了」・「2：放銃」'''
    result_div = models.IntegerField(default=0)
    '''副露区分｜「0：なし」・「1：副露」・「2：供託」・「9：計算対象外」'''
    huro_div = models.IntegerField(null=False, default=9)
    '''その局でやりとりした点数。出上がりのみ（ツモによる若干の点差は考慮しない）。供託や本場はあり'''
    score = models.IntegerField(default=0)
    insert_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        userId = self.user_id.user_id
        user = UserMst.objects.select_related().get(user_id=userId)
        return str(self.hanso_id) + '-' + str(self.game_seq) + ':' + user.last_name + ' ' + user.first_name

    class Meta:
        constraints = [
            # user_idをuniqueとする
            models.UniqueConstraint(fields=['hanso_id', 'user_id', 'game_seq'], name='unique_game')
        ]

# 対局中のユーザ。tempの役割。点数早見表と同期遷移するし非同期むつかしい…
# 実質tempTableだし外部keyは設けない。登録のたびにdelete-insert
class GameUser(models.Model):
    seq = models.IntegerField(default=0)
    user_id = models.CharField(max_length=4)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    score = models.IntegerField(default=25000)
    # score = models.IntegerField(default=0)

    def __str__(self):
        return self.user_id + ' ： ' + self.last_name + ' ' + self.first_name

# 対局状況
# 本場とか供託とかの管理
class GameStatus(models.Model):
    ba = models.CharField(max_length=1)
    kyoku = models.IntegerField()
    honba = models.IntegerField()
    kyotaku = models.IntegerField()
    #
    # def __str__(self):
    #     return self.user_id + ' ： ' + self.last_name + ' ' + self.first_name

class DoLogin(models.Model):
    loginid = models.CharField(max_length=16)
    password = models.CharField(max_length=16)

# 更新管理
class IsUpdateMng(models.Model):
    is_update = models.CharField( max_length=1)
    insert_date = models.DateTimeField(default=timezone.now)
    year = models.IntegerField(default=2020)
    def __str__(self):
        if self.is_update == '1':
            return '更新可'
        else:
            return '更新不可'
