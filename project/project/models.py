from django.db import models
from django.contrib.auth.models import User

# Модель для профиля пользователя
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)


# Модель для тегов
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)


class QuestionManager(models.Manager):
    def best(self):
        return self.filter(vote_count__gt=10).order_by('-vote_count')  

    def new(self):
        return self.order_by('-created_at')  
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import SearchVectorField
# Модель для вопросов
class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='questions')
    vote_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)

    objects = QuestionManager()
    search_index = SearchVectorField(null=True)

    def save(self, *args, **kwargs):
        self.search_index = SearchVector('title', 'content')
        super().save(*args, **kwargs)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vote_count = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)

# Модель для лайков вопросов
class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    value = models.IntegerField(default=0)  # +1 для лайков, -1 для дизлайков

    class Meta:
        unique_together = ('user', 'question')  

class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)
    value = models.IntegerField(default=0)  # +1 для лайков, -1 для дизлайков

    class Meta:
        unique_together = ('user', 'answer')
