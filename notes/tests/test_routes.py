from http import HTTPStatus

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
        test_cases = [
            (
                self.list_url,
                'Список заметок должен перенаправлять на логин'
            ),
            (
                self.success_url,
                'Страница успеха должна перенаправлять на логин'
            ),
            (
                self.add_url,
                'Добавление заметки должно перенаправлять на логин'
            ),
            (
                self.detail_url,
                'Просмотр заметки должен перенаправлять на логин'
            ),
            (
                self.edit_url,
                'Редактирование должно перенаправлять на логин'
            ),
            (
                self.delete_url,
                'Удаление должно перенаправлять на логин'
            ),
        ]
        for url, msg in test_cases:
            with self.subTest(url=url, msg=msg):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    redirect_url,
                    msg_prefix=f'{msg}. Ожидалось'
                    f'перенаправление на: {redirect_url}'
                )

    def test_pages_availability_for_all_users(self):
        """Проверяет доступность страниц для разных типов пользователей."""
        test_cases = [
            (
                self.home_url,
                self.client,
                HTTPStatus.OK,
                'Главная страница - аноним'
            ),
            (
                self.login_url,
                self.client,
                HTTPStatus.OK,
                'Страница входа - аноним'
            ),
            (
                self.logout_url,
                self.client,
                HTTPStatus.OK,
                'Страница выхода - аноним'
            ),
            (
                self.signup,
                self.client,
                HTTPStatus.OK,
                'Регистрация - аноним'
            ),
            (
                self.list_url,
                self.author_client,
                HTTPStatus.OK,
                'Список заметок - автор'
            ),
            (
                self.add_url,
                self.author_client,
                HTTPStatus.OK,
                'Добавление заметки - автор'
            ),
            (
                self.success_url,
                self.author_client,
                HTTPStatus.OK,
                'Успешное добавление - автор'
            ),
            (
                self.list_url,
                self.admin_client,
                HTTPStatus.OK,
                'Список заметок - админ'
            ),
            (
                self.detail_url,
                self.author_client,
                HTTPStatus.OK,
                'Просмотр заметки - автор'
            ),
            (
                self.edit_url,
                self.author_client,
                HTTPStatus.OK,
                'Редактирование - автор'
            ),
            (
                self.delete_url,
                self.author_client,
                HTTPStatus.OK,
                'Удаление - автор'
            ),
            (
                self.detail_url,
                self.not_author_client,
                HTTPStatus.NOT_FOUND,
                'Просмотр - не-автор'
            ),
            (
                self.edit_url,
                self.not_author_client,
                HTTPStatus.NOT_FOUND,
                'Редактирование - не-автор'
            ),
            (
                self.delete_url,
                self.not_author_client,
                HTTPStatus.NOT_FOUND,
                'Удаление - не-автор'
            ),
        ]

        for url, user_client, expected_status, test_name in test_cases:
            with self.subTest(test_name):
                response = user_client.get(url)
                self.assertEqual(
                    response.status_code,
                    expected_status,
                )
