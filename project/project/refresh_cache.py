from django.core.management.base import BaseCommand
from django.core.cache import cache
from models import Tag, User
from django.db.models import Count

class Command(BaseCommand):
    help = 'Обновляет кэш популярных тегов и лучших пользователей'

    def handle(self, *args, **kwargs):
        # Обновляем кэш популярных тегов
        popular_tags = Tag.objects.annotate(question_count=Count('questions')).order_by('-question_count')[:10]
        cache.set('popular_tags', popular_tags, timeout=3000)

        # Обновляем кэш лучших пользователей
        best_users = User.objects.annotate(question_count=Count('questions')).order_by('-question_count')[:10]
        cache.set('best_users', best_users, timeout=3000)

        self.stdout.write(self.style.SUCCESS('Кэш был успешно обновлен!'))
