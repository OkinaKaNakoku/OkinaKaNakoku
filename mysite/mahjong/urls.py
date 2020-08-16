from django.urls import path

from . import views

app_name = 'mahjong'
urlpatterns = [
    path('', views.IndexScore.as_view(), name='score'),
    #path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    #path('<int:pk>/results/', views.resultsview.as_view(), name='results'),
    #path('<int:question_id>/vote/', views.vote, name='vote'),
]