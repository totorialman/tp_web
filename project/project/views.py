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
@login_required
def toggle_vote(request, model_type, model_id):
    """
    Универсальная функция для лайков/дизлайков вопросов и ответов.
    model_type: 'question' или 'answer' (тип модели).
    model_id: id вопроса или ответа.
    """
    is_upvote = request.GET.get('is_upvote') == 'true'  # Получаем, лайк ли это или дизлайк
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
    """
    Функция для установки правильного ответа для вопроса.
    Доступно только автору вопроса.
    """
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
    # Проверка, если запрос POST
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Аутентификация пользователя
            user = form.get_user()
            auth_login(request, user)
            # Редирект на главную страницу или на страницу, указанную в параметре continue
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
            # Проверка на существование пользователя с таким email
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
                return redirect('signup')
            
            # Проверка на существование пользователя с таким логином
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, "A user with this username already exists.")
                return redirect('signup')
            
            user = form.save()  # Сохранение пользователя
            auth_login(request, user)  # Логиним пользователя
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

# Выход
@login_required
def logout_view(request):
    next_url = request.GET.get('next', '/')
    auth_logout(request)
    return redirect(next_url)

# Редактирование профиля
@login_required
def edit_profile(request):
    # Получаем профиль пользователя (создаем его, если его нет)
    profile = Profile.objects.filter(user=request.user).first()
    if not profile:
        profile = Profile.objects.create(user=request.user)

    if request.method == "POST":
        # Обновление электронной почты и биографии
        user_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid():
            # Обновление почты, если она была изменена
            new_email = request.POST.get('email')
            if new_email != request.user.email:
                request.user.email = new_email
                request.user.save()

            user_form.save()  # Сохранить изменения в профиле
            return redirect('edit_profile')  # Перенаправляем на страницу редактирования после сохранения

    else:
        user_form = ProfileEditForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': user_form, 'profile': profile, 'user': request.user})

def get_popular_tags_and_best_users():
    popular_tags = cache.get('popular_tags')
    best_users = cache.get('best_users')

    if not popular_tags or not best_users:
        popular_tags = Tag.objects.annotate(question_count=Count('questions')).order_by('-question_count')[:10]
        best_users = User.objects.annotate(question_count=Count('questions')).order_by('-question_count')[:5]

        cache.set('popular_tags', popular_tags, timeout=3000)
        cache.set('best_users', best_users, timeout=3000)

    return popular_tags, best_users


@login_required
def question_detail(request, question_id):
    question = get_object_or_404(Question.objects.annotate(num_answers=Count('answers')), id=question_id)
    answers = Answer.objects.filter(question=question)

    # Получаем первый профиль автора вопроса
    profile = Profile.objects.filter(user=question.author).first()  # Получаем первый профиль автора

    popular_tags, best_users = get_popular_tags_and_best_users()

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user  # Присваиваем автору текущего пользователя
            answer.question = question  # Привязываем ответ к текущему вопросу
            answer.save()
            return redirect(request.path)  # Перенаправляем на страницу вопроса с привязкой к добавленному ответу

    else:
        form = AnswerForm()

    context = {
        'question': question,
        'answers': answers,
        'form': form,
        'popular_tags': popular_tags,
        'best_users': best_users,
        'profile': profile,  # Передаем профиль в контекст
    }

    return render(request, 'question.html', context)


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

@login_required
def new_ask(request):
    # Получаем популярные теги и пользователей
    popular_tags, best_users = get_popular_tags_and_best_users()

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        
        if form.is_valid():
            # Создаем новый вопрос, но не сохраняем его сразу
            question = form.save(commit=False)
            question.author = request.user  # Присваиваем автору текущего пользователя
            question.save()  # Сохраняем вопрос

            # Добавляем теги для вопроса
            tags = form.cleaned_data['tags']
            for tag_name in tags.split(','):
                tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                question.tags.add(tag)

            # Редиректим на страницу созданного вопроса
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
