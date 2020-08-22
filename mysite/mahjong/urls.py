from django.urls import path

from . import views

app_name = 'mahjong'
urlpatterns = [
    path('', views.IndexScore.as_view(), name='showScore'),
    path('showScore', views.IndexScore.as_view(), name='showScore'),
    path('showScoreUpdate', views.ShowScoreUpdate.as_view(), name='showScoreUpdate'),
    path('updateScore', views.updateScore, name='updateScore'),
    #path('<int:question_id>/vote/', views.vote, name='vote'),
]