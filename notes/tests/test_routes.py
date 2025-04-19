from http import HTTPStatus

from django.test import Client

from notes.tests.utils import TestParentCase


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
        url_names = (
            self.add_url,
            self.edit_url,
            self.delete_url,
            self.detail_url,
            self.list_url,
            self.success_url,
            self.success_url,
        )
        for url in url_names:
            redirect_url = f'{self.login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)

    def test_pages_availability_for_all_users(self):
        """Проверяет доступность страниц для разных типов пользователей."""
        test_cases = [
            # Анонимные пользователи
            (self.home_url, None, HTTPStatus.OK, "Главная страница - аноним"),
            (self.login_url, None, HTTPStatus.OK, "Страница входа - аноним"),
            (self.logout_url, None, HTTPStatus.OK, "Страница выхода - аноним"),
            (self.signup, None, HTTPStatus.OK, "Регистрация - аноним"),

            # Авторизованные пользователи (общие страницы)
            (
                self.list_url,
                self.author,
                HTTPStatus.OK,
                "Список заметок - автор"
            ),
            (
                self.add_url,
                self.author,
                HTTPStatus.OK,
                "Добавление заметки - автор"
            ),
            (
                self.success_url,
                self.author,
                HTTPStatus.OK,
                "Успешное добавление - автор"
            ),
            (
                self.list_url,
                self.admin,
                HTTPStatus.OK,
                "Список заметок - админ"
            ),
            (
                self.detail_url,
                self.author,
                HTTPStatus.OK,
                "Просмотр заметки - автор"
            ),
            (
                self.edit_url,
                self.author,
                HTTPStatus.OK,
                "Редактирование - автор"
            ),
            (
                self.delete_url,
                self.author,
                HTTPStatus.OK,
                "Удаление - автор"
            ),
            (
                self.detail_url,
                self.not_author,
                HTTPStatus.NOT_FOUND,
                "Просмотр - не-автор"
            ),
            (
                self.edit_url,
                self.not_author,
                HTTPStatus.NOT_FOUND,
                "Редактирование - не-автор"
            ),
            (
                self.delete_url,
                self.not_author,
                HTTPStatus.NOT_FOUND,
                "Удаление - не-автор"
            ),
        ]

        for url, user, expected_status, test_name in test_cases:
            with self.subTest(test_name):
                client = Client()
                if user is not None:
                    client.force_login(user)
                response = client.get(url)
                self.assertEqual(
                    response.status_code,
                    expected_status,
                    f"Ошибка в тесте '{test_name}'\n"
                    f"URL: {url}\n"
                    f"Пользователь: {user.username if user else 'аноним'}\n"
                    f"Ожидался статус: {expected_status}\n"
                    f"Получен статус: {response.status_code}"
                )
