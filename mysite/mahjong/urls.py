from django.urls import path

from . import views

app_name = 'mahjong'
urlpatterns = [
    path('', views.showRanking, name='showRanking'), # pythonanywhereでのホスト用
    path('showRanking', views.showRanking, name='showRanking'),
    path('showScoreUpdate', views.showScoreUpdate, name='showScoreUpdate'),
    path('settingUser', views.settingUser, name='settingUser'),
    path('updateScore', views.updateScore, name='updateScore'),
    path('updateGame', views.updateGame, name='updateGame'),
    path('scoreTable', views.scoreTable, name='scoreTable'),
    path('showDetail/<str:userId>/', views.showDetail, name='showDetail'),
    path('changeYear', views.changeYear, name='changeYear'),
    path('showYakuman', views.showYakuman, name='showYakuman')
]
