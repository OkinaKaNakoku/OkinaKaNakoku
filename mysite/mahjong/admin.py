from django.contrib import admin

from .models import UserInfo
from .models import HansoSum
from .models import GameUser
from .models import GameResult
from .models import IsUpdateMng
from .models import UserMst

class HansoSumInline(admin.TabularInline):
    model = HansoSum

class UserInfoAdmin(admin.ModelAdmin):
    fieldsets = [
        ('YEAR',  {'fields':['year']}),
        ('USER_ID',  {'fields':['user_id']}),
        ('SCORE_SUM', {'fields':['score_sum']})
    ]
    ordering = ('-year', 'user_id',)
    list_display = ('year', 'user_id', 'score_sum')

class HansoSumAdmin(admin.ModelAdmin):
    fieldsets = [
        ('YEAR',  {'fields':['year']}),
        ('HANSO_ID', {'fields':['hanso_id']}),
        ('USER_ID',  {'fields':['user_id']}),
        ('RANK',     {'fields':['rank']}),
        ('SCORE',    {'fields':['score']}),
        ('SCORE_RESULT', {'fields':['score_result']}),
        ('INSERT_DATE', {'fields':['insert_date']}),
    ]
    ordering = ('-year', '-hanso_id', 'rank')
    list_display = ('year', 'hanso_id', 'user_id', 'rank', 'score', 'score_result')

class GameResultAdmin(admin.ModelAdmin):
    fieldsets = [
        ('YEAR',  {'fields':['year']}),
        ('HANSO_ID', {'fields':['hanso_id']}),
        ('GAME_SEQ',     {'fields':['game_seq']}),
        ('USER_ID',  {'fields':['user_id']}),
        ('RESULT_DIV',    {'fields':['result_div']}),
        ('INSERT_DATE',    {'fields':['insert_date']}),
    ]
    ordering = ('-year', '-hanso_id', '-game_seq', 'user_id')
    list_display = ('year', 'hanso_id', 'game_seq', 'user_id', 'result_div')

class UserMstAdmin(admin.ModelAdmin):
    fieldsets = [
        ('USER_ID',  {'fields':['user_id']}),
        ('LAST_NAME',     {'fields':['last_name']}),
        ('FIRST_NAME',    {'fields':['first_name']}),
        ('ENG_LAST_NAME', {'fields':['eng_last_name']}),
        ('ENG_FIRST_NAME', {'fields':['eng_first_name']}),
    ]
    ordering = ('user_id',)
    list_display = ('user_id', 'last_name', 'first_name')

# Register your models here.
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(HansoSum, HansoSumAdmin)
admin.site.register(UserMst, UserMstAdmin)
admin.site.register(GameUser);
admin.site.register(GameResult, GameResultAdmin)
admin.site.register(IsUpdateMng)
