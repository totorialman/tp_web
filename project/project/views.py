from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count
from django.core.cache import cache
from .models import Question, Answer, Tag, User, Profile, QuestionLike, AnswerLike
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileEditForm, QuestionForm, AnswerForm, CustomUserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.postgres.search import SearchQuery,SearchVector
from .models import Question
from django.db.models import Q

from django.shortcuts import render
from django.db.models import Q
from .models import Question

def search_questions(request):
    query = request.GET.get('q', '')  
    questions = Question.objects.none()  
    popular_tags, best_users = get_popular_tags_and_best_users()
    if query:
        questions = Question.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    
    return render(request, 'questions.html', {'questions': questions, 'query': query,'popular_tags': popular_tags,
        'best_users': best_users,})

def paginate_objects(request, object_list, per_page=10):
    paginator = Paginator(object_list, per_page)
    page_number = request.GET.get('page', 1)

    try:
        objects = paginator.page(page_number)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    return objects, paginator

@login_required
def toggle_vote(request, model_type, model_id):
    is_upvote = request.GET.get('is_upvote') == 'true'  
    user = request.user

    if model_type == 'question':
        model = get_object_or_404(Question, id=model_id)
        vote = QuestionLike.objects.filter(user=user, question=model).first()

        if vote:
            if (is_upvote and vote.value == 1) or (not is_upvote and vote.value == -1):
                # Снять лайк/дизлайк
                model.vote_count -= vote.value
                vote.value = 0
                vote.save()
                model.save()
                return JsonResponse({'vote_count': model.vote_count})
            else:
                # Обновить оценку
                model.vote_count -= vote.value
                vote.value = 1 if is_upvote else -1
                vote.save()
                model.vote_count += vote.value
                model.save()
                return JsonResponse({'vote_count': model.vote_count})
        else:
            # Создать новую оценку
            value = 1 if is_upvote else -1
            QuestionLike.objects.create(user=user, question=model, value=value)
            model.vote_count += value
            model.save()
            return JsonResponse({'vote_count': model.vote_count})

    elif model_type == 'answer':
        model = get_object_or_404(Answer, id=model_id)
        vote = AnswerLike.objects.filter(user=user, answer=model).first()

        if vote:
            if (is_upvote and vote.value == 1) or (not is_upvote and vote.value == -1):
                # Снять лайк/дизлайк
                model.vote_count -= vote.value
                vote.value = 0
                vote.save()
                model.save()
                return JsonResponse({'vote_count': model.vote_count})
            else:
                model.vote_count -= vote.value
                vote.value = 1 if is_upvote else -1
                vote.save()
                model.vote_count += vote.value
                model.save()
                return JsonResponse({'vote_count': model.vote_count})
        else:
            value = 1 if is_upvote else -1
            AnswerLike.objects.create(user=user, answer=model, value=value)
            model.vote_count += value
            model.save()
            return JsonResponse({'vote_count': model.vote_count})

    else:
        return JsonResponse({'error': 'Invalid model type'}, status=400)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Question, Answer

@login_required
def set_correct_answer(request, question_id, answer_id):

    question = get_object_or_404(Question, id=question_id)
    if question.author != request.user:
        return JsonResponse({'error': 'Only the question author can set the correct answer'}, status=403)

    answer = get_object_or_404(Answer, id=answer_id, question=question)

    # Устанавливаем этот ответ как правильный
    answer.is_correct = not answer.is_correct
    answer.save()

    # Убираем правильный ответ с остальных ответов
    if answer.is_correct:
        question.answers.exclude(id=answer_id).update(is_correct=False)

    return JsonResponse({'is_correct': answer.is_correct, 'answer_id': answer.id})
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.GET.get('continue', '/')
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})
from django.contrib import messages

# Регистрация
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
                return redirect('signup')
            
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, "A user with this username already exists.")
                return redirect('signup')
            
            user = form.save()  
            auth_login(request, user)  
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def logout_view(request):
    next_url = request.GET.get('next', '/')
    auth_logout(request)
    return redirect(next_url)

@login_required
def edit_profile(request):
    profile = Profile.objects.filter(user=request.user).first()
    if not profile:
        profile = Profile.objects.create(user=request.user)

    if request.method == "POST":
        user_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid():
            new_email = request.POST.get('email')
            if new_email != request.user.email:
                request.user.email = new_email
                request.user.save()

            user_form.save()  
            return redirect('edit_profile')  

    else:
        user_form = ProfileEditForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': user_form, 'profile': profile, 'user': request.user})

from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

from itertools import chain

def get_popular_tags_and_best_users():
    now = timezone.now()
    
    three_months_ago = now - timedelta(days=90)  
    one_week_ago = now - timedelta(weeks=1)      

    popular_tags = cache.get('popular_tags')

    if not popular_tags:
        popular_tags = (
            Tag.objects
            .filter(questions__created_at__gte=three_months_ago)  
            .annotate(question_count=Count('questions'))
            .order_by('-question_count')[:10]  
        )
        cache.set('popular_tags', popular_tags, timeout=3000)

    best_users = cache.get('best_users')

    if not best_users:
        best_users_questions = (
            User.objects
            .filter(questions__created_at__gte=one_week_ago)  
            .annotate(question_count=Count('questions'))
            .order_by('-question_count')[:5]  
        )

        best_users_answers = (
            User.objects
            .filter(answers__created_at__gte=one_week_ago)  
            .annotate(answer_count=Count('answers'))
            .order_by('-answer_count')[:5]  
        )

        best_users = list(chain(best_users_questions, best_users_answers))
        best_users = list({user.id: user for user in best_users}.values())[:10]

        cache.set('best_users', best_users, timeout=3000)

    return popular_tags, best_users



@login_required
def question_detail(request, question_id):
    question = get_object_or_404(Question.objects.annotate(num_answers=Count('answers')), id=question_id)
    answers = Answer.objects.filter(question=question).order_by('-id')  

    paginator = Paginator(answers, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    profile = Profile.objects.filter(user=question.author).first()

    popular_tags, best_users = get_popular_tags_and_best_users()

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question
            answer.save()
            return redirect(request.path)

    else:
        form = AnswerForm()

    context = {
        'question': question,
        'answers': page_obj,  
        'form': form,
        'popular_tags': popular_tags,
        'best_users': best_users,
        'profile': profile,
        'paginator': paginator,  
    }

    return render(request, 'question.html', context)


def question_list_view(request):
    questions = Question.objects.annotate(num_answers=Count('answers')).order_by('-id')
    paginator = Paginator(questions, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    popular_tags, best_users = get_popular_tags_and_best_users()

    context = {
        'questions': page_obj,
        'popular_tags': popular_tags,
        'best_users': best_users,
        'paginator': paginator,
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

@login_required
def new_ask(request):
    popular_tags, best_users = get_popular_tags_and_best_users()

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user  
            question.save()  

            tags = form.cleaned_data['tags']
            for tag_name in tags.split(','):
                tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                question.tags.add(tag)
            return redirect('question_detail', question_id=question.id)

    else:
        form = QuestionForm()

    context = {
        'form': form,
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
