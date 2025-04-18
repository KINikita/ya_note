from http import HTTPStatus

from notes.tests.utils import TestParentCase
from django.urls import reverse


class TestRoutes(TestParentCase):

    def test_redirect_anonymous_client_to_login(self):
        """
        Проверяет перенаправление на страницу 'users:login'
        анонимного пользователя со следующих страниц:
        - список заметок ('notes:list')
        - успешное добавление заметки ('notes:success')
        - добавление заметки ('notes:add')
        - отдельная заметка ('notes:detail')
        - редактирование заметки ('notes:edit')
        - удаление заметки ('notes:delete')
        Тест выполняет следующие проверки:
        1. Для каждой указанной страницы проверяется, что
        анонимный пользователь перенаправляется на
        страницу входа ('users:login').
        2. Проверяется, что в URL перенаправления корректно
        указан параметр 'next', содержащий исходный запрашиваемый URL.
        3. Для страниц, требующих slug заметки (edit, delete, detail),
        проверяется формирование корректного URL с переданным slug.
        4. Для страниц, не требующих slug (add, list, success), проверяется
        формирование корректного URL без дополнительных аргументов.
        """
        login_url = reverse('users:login')
        redirect_from_names = (
            ('notes:edit', self.note.slug),
            ('notes:delete', self.note.slug),
            ('notes:detail', self.note.slug),
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, slug in redirect_from_names:
            if slug:
                with self.subTest(name=name):
                    url = reverse(name, args=(slug,))
            else:
                with self.subTest(name=name):
                    url = reverse(name)
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)

    def test_pages_availability_for_all_users(self):
        """
        Проверяет доступность страниц для разных типов пользователей:
        - анонимных пользователей
        - авторизованных пользователей
        - администраторов

        Тестируемые страницы:
        - Главная страница ('notes:home')
        - Страница входа ('users:login')
        - Страница выхода ('users:logout')
        - Страница регистрации ('users:signup')
        - Список заметок ('notes:list')
        - Добавление заметки ('notes:add')
        - Успешное добавление заметки ('notes:success')
        - Конкретная заметка ('notes:detail')
        - Обновление заметки ('notes:edit')
        - Удаление заметки ('notes:delete')

        Ожидаемое поведение:
        Должны быть доступны для всех типов пользователей:
        - Главная страница ('notes:home')
        - Страница входа ('users:login')
        - Страница выхода ('users:logout')
        - Страница регистрации ('users:signup')
        Должны быть доступны только для аутентифицированных пользователей:
        - Список заметок ('notes:list')
        - Добавление заметки ('notes:add')
        - Успешное добавление заметки ('notes:success')
        Должны быть доступны только для авторов
        (для аутентифицированных пользователей вернется ошибка 404):
        - Конкретная заметка ('notes:detail')
        - Обновление заметки ('notes:edit')
        - Удаление заметки ('notes:delete')
        """
        test_cases = (
            (
                ('notes:home', 'users:login', 'users:logout', 'users:signup'),
                HTTPStatus.OK,
                False,
                (None, self.author, self.admin)
            ),
            (
                ('notes:list', 'notes:add', 'notes:success'),
                HTTPStatus.OK,
                False,
                (self.author, self.admin)
            ),
            (
                ('notes:detail', 'notes:edit', 'notes:delete'),
                HTTPStatus.OK,
                True,
                (self.author,)
            ),
            (
                ('notes:detail', 'notes:edit', 'notes:delete'),
                HTTPStatus.NOT_FOUND,
                True,
                (self.not_author,)
            )
        )

        for urls, expected_status, needs_slug, users in test_cases:
            for user in users:
                if user:
                    self.client.force_login(user)

                for url_name in urls:
                    with self.subTest(url=url_name, user=user):
                        if needs_slug:
                            url = reverse(url_name, args=(self.note.slug,))
                        else:
                            url = reverse(url_name)
                        response = self.client.get(url)
                        self.assertEqual(response.status_code, expected_status)
