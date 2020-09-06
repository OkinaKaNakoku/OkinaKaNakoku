from django.contrib import admin

from .models import UserInfo
from .models import HansoSum
from .models import GameUser
from .models import GameResult
from .models import IsUpdateMng

class HansoSumInline(admin.TabularInline):
    model = HansoSum

class UserInfoAdmin(admin.ModelAdmin):
    fieldsets = [
        ('USER_ID',  {'fields':['user_id']}),
        ('LAST_NAME',     {'fields':['last_name']}),
        ('FIRST_NAME',    {'fields':['first_name']}),
        ('SCORE_SUM', {'fields':['score_sum']}),
        ('ENG_LAST_NAME', {'fields':['eng_last_name']}),
        ('ENG_FIRST_NAME', {'fields':['eng_first_name']}),
    ]
    ordering = ('user_id',)
    list_display = ('user_id', 'last_name', 'first_name', 'score_sum')

class HansoSumAdmin(admin.ModelAdmin):
    fieldsets = [
        ('HANSO_ID', {'fields':['hanso_id']}),
        ('USER_ID',  {'fields':['user_id']}),
        ('RANK',     {'fields':['rank']}),
        ('SCORE',    {'fields':['score']}),
        ('SCORE_RESULT', {'fields':['score_result']}),
        ('INSERT_DATE', {'fields':['insert_date']}),
    ]
    ordering = ('-hanso_id', 'rank')
    list_display = ('hanso_id', 'user_id', 'rank', 'score', 'score_result')

class GameResultAdmin(admin.ModelAdmin):
    fieldsets = [
        ('HANSO_ID', {'fields':['hanso_id']}),
        ('GAME_SEQ',     {'fields':['game_seq']}),
        ('USER_ID',  {'fields':['user_id']}),
        ('RESULT_DIV',    {'fields':['result_div']}),
        ('INSERT_DATE',    {'fields':['insert_date']})
    ]
    ordering = ('-hanso_id', 'game_seq', 'user_id')
    list_display = ('hanso_id', 'game_seq', 'user_id', 'result_div')

# Register your models here.
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(HansoSum, HansoSumAdmin)
admin.site.register(GameUser);
admin.site.register(GameResult, GameResultAdmin)
admin.site.register(IsUpdateMng)