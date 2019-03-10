from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('figure', views.figure, name='figure'),
    path('figures', views.figures, name='figures'),
    path('tweet', views.tweet, name='tweet'),
    path('tweets', views.tweets, name='tweets'),
    path('about', views.about, name='about')
]