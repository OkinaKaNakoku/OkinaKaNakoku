from django.urls import path

from . import views

app_name = 'mahjong'
urlpatterns = [
    path('', views.IndexScore.as_view(), name='showScore'),
    path('showScore', views.IndexScore.as_view(), name='showScore'),
    path('showScoreUpdate', views.showScoreUpdate, name='showScoreUpdate'),
    path('settingUser', views.settingUser, name='settingUser'),
    path('updateScore', views.updateScore, name='updateScore'),
    path('updateGame', views.updateGame, name='updateGame'),
    path('scoreTable', views.scoreTable, name='scoreTable'),
    #path('<int:question_id>/vote/', views.vote, name='vote'),

]