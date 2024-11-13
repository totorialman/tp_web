# Домашнее задание 3

## Проектирование модели данных

Целью домашнего задания является проектирование модели базы данных, наполнение ее тестовыми данными и и отображение этих данных на сайте. Таким образом будет создана read-only версия сайта.

### 3. Наполнение данными
Требования к объему данных:
- Пользователи > 10 000.
- Вопросы > 100 000.
- Ответы > 1 000 000.
- Тэги > 10 000.
- Оценки пользователей > 2 000 000.

**Внимание!** Management command должна быть вида: 
```Bash
python manage.py fill_db [ratio]
```
Где num_users — коэффициент заполнения сущностей. Соответственно, после применения команды в базу должно быть добавлено:
 - пользователей — равное ratio;
 - вопросов — ratio * 10;
 - ответы — ratio * 100;
 - тэгов - ratio;
 - оценок пользователей - ratio * 200;

### 6. Баллы

#### Максимальные баллы за ДЗ - 16 баллов

Проектирование модели - 5:
```python
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
# Create your models here.
class Tag(models.Model):
    name = models.CharField(verbose_name="Название", max_length=100)
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name

class Question(models.Model):
    title = models.TextField("Заголовок")
    description = models.TextField("Содержание")
    profile = models.ForeignKey(Profile, verbose_name="Профиль", on_delete=models.CASCADE, related_name='questions')
    created_date = models.DateField("Дата создания", auto_now=False, auto_now_add=True)
    rating = models.IntegerField("Рейтинг")
    tags = models.ManyToManyField(Tag, verbose_name="Теги")
    objects = QuestionManager()
    
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.title[:30] + '...'

class Answer(models.Model):
    question = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE, related_name='answers')
    description = models.TextField("Ответ")
    profile = models.ForeignKey(Profile, verbose_name="Автор", on_delete=models.CASCADE)
    created_date = models.DateField("Дата создания", auto_now=False, auto_now_add=True)
    correct = models.BooleanField("Правильный ответ")
    rating = models.IntegerField("Рейтинг")
    objects = AnswerManager()

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return self.description[:30] + '...'
```
- [X] правильные адекватные типы данных и внешние ключи - 1;
- [X] своя модель пользователя - 1;
```python
class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads')
    rating = models.IntegerField()
    
    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.username
```
- [X] таблицы тегов, лайков - 1;
```python
class QuestionLike(models.Model):
    STATUS_CHOICES = (
        (1, "Нравится"),
        (-1, "Не нравится")
    )
    status = models.IntegerField("Статус", choices=STATUS_CHOICES)
    question = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, verbose_name="Профиль", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Оценка вопроса"
        verbose_name_plural = "Оценки вопросов"

    def __str__(self):
        return self.question.title


class AnswerLike(models.Model):
    STATUS_CHOICES = (
        (1, "Нравится"),
        (-1, "Не нравится")
    )
    status = models.IntegerField("Статус", choices=STATUS_CHOICES)
    answer = models.ForeignKey(Answer, verbose_name="Ответ", on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, verbose_name="Профиль", on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Оценка ответа"
        verbose_name_plural = "Оценки ответов"

    def __str__(self):
        return self.answer.title[:30] + '...'
```
- [X] query-set'ы для типовых выборок: новые вопросы, популярные, по тегу - 2.
```python
class QuestionManager(models.Manager):
    def new_questions(self):
        """Выбрать все вопросы и количество ответов к ним."""
        return self.annotate(answer_count=Count('answers')).order_by('-id')

    def hot_questions(self):
        """Выбрать популярные вопросы, отсортированные по рейтингу, и количество ответов к ним."""
        return self.annotate(answer_count=Count('answers')).order_by('-rating')

    def tag_questions(self, tag_name):
        """Выбрать вопросы с указанным тегом и количество ответов к ним."""
        return self.filter(tags__name=tag_name).annotate(answer_count=Count('answers')).order_by('-id')

class AnswerManager(models.Manager):
    def question_answers(self, id):
        return self.filter(question__id=id).order_by('id')
```
Наполнение базы тестовыми данными - 3:

- [X] скрипт для наполнения данными - 1;
  
  [Файл](./ask_larin/ask/management/commands/filldb.py)
- [X] использование django management commands - 1;
- [X] соблюдение требований по объему данных - 1.

Отображение списка вопросов - 3:

```python
def questions_catalog(request):
    question = Question.objects.new_questions()
    page = paginate(question, request)
    return render(request, 'index.html', {
        'data': page["page"].object_list,
        'page': page,
        'login': True
    })

def hot_questions_catalog(request):
    question = Question.objects.hot_questions()
    page = paginate(question, request)
    return render(request, 'index.html', {
        'data': page["page"].object_list,
        'page': page,
        'hot': True,
    })

def tag(request, tag):
    question = Question.objects.tag_questions(tag)
    page = paginate(question, request)
    return render(request, 'index.html', {
        'data': page["page"].object_list,
        'page': page
    })

def question(request, id):
    answers = Answer.objects.question_answers(id)
    question = Question.objects.get(id=id)
    return render(request, 'question.html', {
        'title': question.title,
        'question': question,
        'answers': answers
    })
```

- [X] список новых вопросов - 1;
  
  ![Общий вид новых вопросов](./img/lab3_1.png)

- [X] список популярных - 1;
  
  ![Общий вид популярных вопросов](./img/lab3_2.png)

- [X] список вопросов по тегу - 1
  
  ![Общий вид вопросов по тегу](./img/lab3_3.png)

Отображение страницы вопроса - 3:

- [X] общее - 3.
  
  ![Общий вид страницы ответов](./img/lab3_4.png)

Использование СУДБ - 2:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ask_larin', # Имя вашей БД. Если вы создали черезе psql или IDE свою базу и хотите использовать его - пропишите его имя здесь
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': 5432, # Стандартный порт PostgreSQL
    }
}
```

- [X] MySQL или PostgreSQL - 2.
