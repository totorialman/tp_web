"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.question_list_view, name='question-list'),
    path('top-likes/', views.top_liked_questions, name='top-liked-questions'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('tag/<str:tag_name>/', views.tag_detail, name='tag_detail'),
    path('new-ask/', views.new_ask, name='new_ask'),
    path('login/', views.login, name='login'),
    path('singup/', views.singup, name='singup'),
    path('setting/', views.setting, name='setting'),
    path('base/', views.base, name='base'),

]