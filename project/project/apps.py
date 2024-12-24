from django.apps import AppConfig


class ProjectConfig(AppConfig):  # Назовите класс по имени вашего проекта/приложения
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project'  # Укажите имя вашей директории с кодом

    def ready(self):
        import project.signals  # Подключите ваши сигналы
