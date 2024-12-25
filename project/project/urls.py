from django.contrib import admin
from django.urls import path
from . import views
from .views import toggle_vote
from django.conf import settings
from django.conf.urls.static import static
from .views import search_questions


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
    path('search/', views.search_questions, name='search_questions'),
    path('top-likes/', views.top_liked_questions, name='top-liked-questions'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)