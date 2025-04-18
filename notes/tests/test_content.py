from django.urls import reverse

from notes.tests.utils import TestParentCase
from notes.forms import NoteForm


class TestNotesListForDifferentUsers(TestParentCase):

    def test_note_visibility(self):
        """Тестируем видимость заметки для разных пользователей."""
        test_cases = [
            (
                self.author_client,
                True,
                'Автор должен видеть свою заметку'
            ),
            (
                self.not_author_client,
                False,
                'Не-автор не должен видеть чужую заметку'
            )
        ]

        for client, should_be_seen, msg in test_cases:
            with self.subTest(
                client=client,
                should_be_seen=should_be_seen
            ):
                response = client.get(self.list_url)
                object_list = response.context['object_list']
                if should_be_seen:
                    self.assertIn(self.note, object_list, msg)
                else:
                    self.assertNotIn(self.note, object_list, msg)

    def test_pages_contain_form(self):
        """
        Проверяем наличие формы на страницах создания и
        редактирования заметки.
        """
        test_cases = (
            (
                'notes:add',
                None,
                'Проверьте наличие формы на странице создания заметки'
            ),
            (
                'notes:edit',
                (self.note.slug,),
                'Проверьте наличие формы на странице редактирования заметки'
            )
        )
        for name, args, msg in test_cases:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context, msg)
                self.assertIsInstance(response.context['form'], NoteForm, msg)
