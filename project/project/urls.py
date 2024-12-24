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
from .views import toggle_vote
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('ask/', views.new_ask, name='new_ask'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('questions/', views.question_list_view, name='questions'),
    path('tags/<str:tag_name>/', views.tag_detail, name='tag_detail'),
    path('', views.question_list_view, name='home'),
    path('settings/', views.edit_profile, name='edit_profile'),
    path('toggle-vote/<str:model_type>/<int:model_id>/', toggle_vote, name='toggle_vote'),
    path('set-correct-answer/<int:question_id>/<int:answer_id>/', views.set_correct_answer, name='set_correct_answer'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)