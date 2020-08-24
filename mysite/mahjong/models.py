from django.db import models
from django.utils import timezone

# Create your models here.

# ユーザ情報
class UserInfo(models.Model):
    user_id = models.CharField(max_length=4)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    eng_last_name = models.CharField(null=True, max_length=100)
    eng_first_name = models.CharField(null=True, max_length=100)
    score_sum = models.DecimalField(max_digits=6,decimal_places=1,default=0.0)
    
    def __str__(self):
        return self.user_id + ' ： ' + self.last_name + ' ' + self.first_name

# 半荘合計。基本hanso_id 1：user_id 4
class HansoSum(models.Model):
    hanso_id = models.IntegerField()
    user_id = models.ForeignKey(UserInfo, db_column='user_id', on_delete=models.DO_NOTHING)
    rank = models.CharField(max_length=1)
    score = models.IntegerField(default=0)
    score_result = models.DecimalField(max_digits=6,decimal_places=1,default=0.0)
    insert_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        userId = self.user_id.user_id
        user = UserInfo.objects.select_related().get(user_id=userId)
        return str(self.hanso_id) + '：' + user.last_name + ' ' + user.first_name

    class Meta:
        constraints = [
            # user_idをuniqueとする
            models.UniqueConstraint(fields=['hanso_id', 'user_id'], name='unique_booking')
        ]


