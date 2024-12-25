# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import Question

@receiver(post_save, sender=Question)
def update_search_index(sender, instance, created, **kwargs):
    # Проверим, был ли объект обновлен или только что создан
    if not created:  # Только обновляем если объект уже существует
        if instance.search_index is None:
            instance.search_index = SearchVector('title', 'content')
            instance.save(update_fields=['search_index'])