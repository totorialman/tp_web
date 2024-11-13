Домашнее задание 2
====

Обработка HTTP запросов
----
Целью домашнего задания является:

- создание основных view сайта (отображающих “рыбу”);
- настройка маршрутизации URL;
- использование шаблонизатора для генерации HTML;
- постраничное отображение (пагинация).


Баллы
---

**Максимальные баллы за ДЗ - 14 баллов**

Создать views и шаблоны для основных страниц - 6
---
[Файл views](../../views.py)

- [X] Главная - 1;
  
  [Список вопросов](../../templates/questions.html)


  [Карточка вопросов](../../templates/question.html)
  [Базовый файл](../../templates/base.html)
  
- [X] Страница вопроса (список ответов) - 1;

- [X] Страница добавления вопроса - 1;

  [Добавление вопроса](../../templates/ask.html)


- [X] Форма регистрации - 1;

  [Регистрация](../../templates/singup.html)

  
- [X] Форма входа - 1;
  
  [Вход](../../templates/login.html)

  
- [X] форма редактирования профиля - 1.
  
  [Настройки](../../templates/setting.html)



Создать urls.py для всех страниц - 4:
---

- [X] Собственно urls.py - 2;
  
``` python
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
```
- [X] Именованные маршруты (во всех шаблонах) - 2.
  
  sidebar.html
  ``` html
    <div class="mb-4">
    <h5>Popular Tags</h5>
    <p class="custom-links">
        {% for tag in popular_tags %}
            <a href="{% url 'tag_detail' tag.name %}" class="badge bg-secondary">{{ tag.name }}</a> 
        {% endfor %}
    </p>
    </div>
  ```

  catalog_card.html
  ```html
    <div class="card-body">
      <h5 class="card-title"><a href={%url 'question' data.question.id%}>{{data.question.title}}</a></h5>
      <p class="card-text">{{data.question.text}}</p>
    </div>
    <div class="card-footer">
       <div class="row">
          <div class="col-md-3">
             <a href={% url 'question' data.question.id %} class="btn btn-outline-primary">
               Ответов <span class="badge text-bg-primary">{{data.answers_amount}}</span>
             </a>
          </div>
          <div class="col-md-9">
             {% for tag in data.question.tags%}
             <span class="badge rounded-pill text-bg-primary"><a href={% url 'tag' tag %} class="tag">{{tag}}</a></span>
             {% endfor %}
          </div>
       </div>
    </div>
  ```


Постраничное отображение - 4:
---

- [X] функция пагинации - 1;
```python
def paginate(objects_list, request, per_page=10):
    p = Paginator(objects_list, 10)
    try:
        number = int(request.GET.get("page", 1))
        if number > p.num_pages + 1 or number < 1:
            raise Exception()
        current_page = p.get_page(number)
    except:
        number = 1
        current_page = p.get_page(number)
    result = {
            "has_previous": False,
            "has_next": False,
    }
    result["page"] = current_page
    result["current_page"] = current_page.number
    if current_page.has_previous() == True:
        result["has_previous"] = True
        result["previous_page"] = current_page.previous_page_number()
    if current_page.has_next() == True:
        result["has_next"] = True
        result["next_page"] = current_page.next_page_number()
    return result
```
- [X] шаблон для отрисовки пагинатора - 2;
  
  [Файл](./ask_larin/templates/paginator.html)

- [X] корректная обработка “неправильных” параметров - 1.
  
  ![Значение не число](./img/lab2_1.png)

  ![Значение < 0](./img/lab2_2.png)

