from django.core.management.base import BaseCommand
from ...models import User, Question, Answer, Tag, QuestionLike, AnswerLike, Profile
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Заполняет базу данных фейковыми данными для тестирования'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Количество пользователей, вопросов и ответов для генерации')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        fake = Faker()

        # Генерация пользователей
        users = []
        avatar_path = 'avatars/default_avatar.jpg'

        for i in range(ratio):
            username = f"{fake.user_name()}_{i}"
            email = fake.email()
            users.append(User(username=username, email=email, password='password'))

        User.objects.bulk_create(users)

        # Генерация профилей для пользователей
        profiles = []
        for user in users:
            profiles.append(Profile(user=user, avatar=avatar_path, bio=fake.text()))

        Profile.objects.bulk_create(profiles)

        # Генерация тегов с уникальными именами
        tags = []
        for i in range(ratio):
            tag_name = f"tag_{i}"  
            tags.append(Tag(name=tag_name))

        Tag.objects.bulk_create(tags)

        # Генерация вопросов
        questions = []
        for _ in range(ratio * 10):
            question = Question(
                title=fake.sentence(),
                content=fake.text(),
                author=random.choice(users),
                vote_count=random.randint(0, 100),
                answer_count=0
            )
            questions.append(question)

        Question.objects.bulk_create(questions)
        
        # Генерация тегов для вопросов
        tags = Tag.objects.all()
        for question in questions:
            question.tags.add(*random.sample(list(tags), 3))

        # Генерация ответов для случайных вопросов
        answers = []
        for _ in range(ratio * 100):
            question = random.choice(questions)
            answer = Answer(
            question=question,
            author=random.choice(users),
            content=fake.text(),
            vote_count=random.randint(0, 20)
            )
            answers.append(answer)
        batch_size = 5000
        for i in range(0, len(answers), batch_size):
            Answer.objects.bulk_create(answers[i:i + batch_size])

        # Случайное распределение лайков для вопросов
        question_likes = []
        for _ in range(ratio * 100):  
            question_likes.append(QuestionLike(
                user=random.choice(users),
                question=random.choice(questions)
            ))

        QuestionLike.objects.bulk_create(question_likes)

        # Случайное распределение лайков для ответов
        answer_likes = []
        for _ in range(ratio * 100):  
            answer_likes.append(AnswerLike(
                user=random.choice(users),
                answer=random.choice(answers)
            ))

        AnswerLike.objects.bulk_create(answer_likes)

        self.stdout.write(self.style.SUCCESS(f'Заполнено {ratio} пользователей, {ratio * 10} вопросов и {ratio * 50} ответов'))
