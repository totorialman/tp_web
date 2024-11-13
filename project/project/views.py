from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count
from django.core.cache import cache
from .models import Question, Answer, Tag, User

def get_popular_tags_and_best_users():
    popular_tags = cache.get('popular_tags')
    best_users = cache.get('best_users')

    if not popular_tags or not best_users:
        popular_tags = Tag.objects.annotate(question_count=Count('questions')).order_by('-question_count')[:10]
        best_users = User.objects.annotate(question_count=Count('questions')).order_by('-question_count')[:5]

        cache.set('popular_tags', popular_tags, timeout=300)
        cache.set('best_users', best_users, timeout=300)

    return popular_tags, best_users

def question_detail(request, question_id):
    question = get_object_or_404(Question.objects.annotate(num_answers=Count('answers')), id=question_id)
    answers = Answer.objects.filter(question=question)

    popular_tags, best_users = get_popular_tags_and_best_users()

    return render(request, 'question.html', {
        'question': question,
        'answers': answers,
        'popular_tags': popular_tags,
        'best_users': best_users,
    })

def question_list_view(request):
    questions = Question.objects.annotate(num_answers=Count('answers')).order_by('-id')
    paginator = Paginator(questions, 20)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    popular_tags, best_users = get_popular_tags_and_best_users()

    context = {
        'questions': page_obj,
        'popular_tags': popular_tags,
        'best_users': best_users,
    }
    
    return render(request, 'questions.html', context)

def top_liked_questions(request):
    top_questions = Question.objects.annotate(num_answers=Count('answers')).order_by('-vote_count')[:5]
    paginator = Paginator(top_questions, 20)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    popular_tags, best_users = get_popular_tags_and_best_users()

    context = {
        'questions': page_obj,
        'popular_tags': popular_tags,
        'best_users': best_users,
    }
    
    return render(request, 'questions.html', context)

def base(request):
    popular_tags, best_users = get_popular_tags_and_best_users()

    context = {
        'popular_tags': popular_tags,
        'best_users': best_users,
    }

    return render(request, 'base.html', context)

def new_ask(request):
    popular_tags, best_users = get_popular_tags_and_best_users()
    context = {
        'popular_tags': popular_tags,
        'best_users': best_users,
    }
    return render(request, 'ask.html', context)

def singup(request):
    popular_tags, best_users = get_popular_tags_and_best_users()
    context = {
        'popular_tags': popular_tags,
        'best_users': best_users,
    }
    return render(request, 'singup.html', context)

def login(request):
    popular_tags, best_users = get_popular_tags_and_best_users()
    context = {
        'popular_tags': popular_tags,
        'best_users': best_users,
    }
    return render(request, 'login.html', context)

def setting(request):
    popular_tags, best_users = get_popular_tags_and_best_users()
    context = {
        'popular_tags': popular_tags,
        'best_users': best_users,
    }
    return render(request, 'setting.html', context)

def tag_detail(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.filter(tags=tag).order_by('-created_at')

    paginator = Paginator(questions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    popular_tags, best_users = get_popular_tags_and_best_users()

    context = {
        'tag': tag,
        'questions': page_obj,
        'popular_tags': popular_tags,
        'best_users': best_users,
    }

    return render(request, 'tag.html', context)
