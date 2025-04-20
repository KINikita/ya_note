from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestParentCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='password'
        )
        cls.not_author = User.objects.create_user(
            username='not_author',
            password='password'
        )
        cls.admin = User.objects.create_user(
            username='admin',
            password='password',
            is_staff=True
        )

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
        cls.home_url = reverse('notes:home')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.list_url = reverse('notes:list')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup = reverse('users:signup')

    @classmethod
    def tearDownClass(cls):
        """Вызывается один раз после запуска всех тестов класса."""
        Note.objects.all().delete()
        User.objects.all().delete()
        super().tearDownClass() if hasattr(super(), 'tearDownClass') else None
        print('>> tearDownClass')
