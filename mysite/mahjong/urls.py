from django.urls import path

from . import views

app_name = 'mahjong'
urlpatterns = [
    path('', views.showRanking, name='showRanking'),
    path('showRanking', views.showRanking, name='showRanking'),
    path('showScoreUpdate', views.showScoreUpdate, name='showScoreUpdate'),
    path('settingUser', views.settingUser, name='settingUser'),
    path('updateScore', views.updateScore, name='updateScore'),
    path('updateGame', views.updateGame, name='updateGame'),
    path('scoreTable', views.scoreTable, name='scoreTable'),
    #path('<int:question_id>/vote/', views.vote, name='vote'),

]