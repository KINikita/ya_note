from notes.forms import NoteForm

from notes.tests.utils import TestParentCase


class TestNotesListForDifferentUsers(TestParentCase):

    def test_note_visibility(self):
        """Тестируем видимость заметки для разных пользователей."""
        test_cases = [
            (
                self.author_client,
                self.assertIn,
                'Автор должен видеть свою заметку'
            ),
            (
                self.not_author_client,
                self.assertNotIn,
                'Не-автор не должен видеть чужую заметку'
            )
        ]

        for client, assertion, msg in test_cases:
            with self.subTest(client=client, msg=msg):
                response = client.get(self.list_url)
                assertion(self.note, response.context['object_list'])

    def test_pages_contain_form(self):
        """
        Проверяем наличие формы на страницах создания и
        редактирования заметки.
        """
        test_cases = (
            (
                self.add_url,
                'Проверьте наличие формы на странице создания заметки'
            ),
            (
                self.edit_url,
                'Проверьте наличие формы на странице редактирования заметки'
            )
        )
        for url_name, msg in test_cases:
            with self.subTest(url_name=url_name):
                response = self.author_client.get(url_name)
                self.assertIn('form', response.context, msg)
                self.assertIsInstance(response.context['form'], NoteForm, msg)
