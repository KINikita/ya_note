from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestParentCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.admin = User.objects.create_user(username='admin')

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.admin_client = Client()
        cls.admin_client.force_login(cls.admin)

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )

        cls.list_url = reverse('notes:list')

    @classmethod
    def tearDownClass(cls):
        """Вызывается один раз после запуска всех тестов класса."""
        Note.objects.all().delete()
        User.objects.all().delete()
        super().tearDownClass() if hasattr(super(), 'tearDownClass') else None
        print('>> tearDownClass')
