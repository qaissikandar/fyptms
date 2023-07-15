from django.contrib import admin



from django.urls import path
from dev import views
urlpatterns = [
    path('',views.index),
    path('login/', views.login),
    path('callback/', views.callback),
    path('dashboard/', views.dashboard),
    path('following/', views.follow),
    path('followers/', views.followers),
    path('search_users/<search_query>', views.search_users),
    path('follow_user/', views.follow_user),
    path('unfollow_user/', views.unfollow_user),
    path('nonfollowers/', views.nonfollowers),
    path('analysis/',views.analysis),
    path('sentiments/',views.sentiments, name= "sentiments"),
    path('blocked_user/',views.blockeduser ),
    path('tweet/',views.tweet, name="tweet"),
    path("suggest/",views.suggest, name = 'suggest'),
    path('suggest/', views.suggest, name='suggest')

]
