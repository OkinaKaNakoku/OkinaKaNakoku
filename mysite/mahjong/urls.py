from django.urls import path

from . import views

app_name = 'mahjong'
urlpatterns = [
    path('', views.showRanking, name='showRanking'), # pythonanywhereでのホスト用
    path('', views.login, name='login'), # pythonanywhereでのホスト用
    path('showRanking', views.showRanking, name='showRanking'),
    path('showScoreUpdate', views.showScoreUpdate, name='showScoreUpdate'),
    path('settingUser', views.settingUser, name='settingUser'),
    path('updateScore', views.updateScore, name='updateScore'),
    path('updateGame', views.updateGame, name='updateGame'),
    path('scoreTable', views.scoreTable, name='scoreTable'),
    path('showDetail/<str:userId>/', views.showDetail, name='showDetail'),
    path('changeYear', views.changeYear, name='changeYear'),
    path('showYakuman', views.showYakuman, name='showYakuman'),
    path('test', views.test, name='test'),
    path('getGraph/<str:userId>', views.getGraph, name='getGraph'),
    path('getReView', views.getReView, name='getReView'),
    path('fixScore', views.fixScore, name='fixScore'),
    path('login', views.login, name='login'),
    path('doLogin', views.doLogin, name='doLogin'),
    path('manage', views.manage, name='manage'),
    path('manageDB', views.manageDB, name='manageDB'),
    path('manageDBUpdate', views.manageDBUpdate, name='manageDBUpdate'),
    path('manageGit', views.manageGit, name='manageGit'),
    path('managePythonAnywhere', views.managePythonAnywhere, name='managePythonAnywhere'),
    path('manageYakuman', views.manageYakuman, name='manageYakuman'),
]
