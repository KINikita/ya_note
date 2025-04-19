from http import HTTPStatus

from pytils.translit import slugify


from notes.forms import WARNING
from notes.models import Note
from notes.tests.utils import TestParentCase


class TestNoteLogic(TestParentCase):

    def test_user_can_create_note(self):
        self.delete_notes
        initial_count = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        initial_count = Note.objects.count()
        url = self.add_url
        response = self.client.post(url, data=self.form_data)

        login_url = self.login_url
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_not_unique_slug(self):
        initial_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, data=self.form_data)

        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), initial_count)

    def test_empty_slug(self):
        self.delete_notes
        form_data = self.form_data.copy()
        form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=form_data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 2)

        new_note = Note.objects.last()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        self.delete_notes
        response = self.author_client.post(self.edit_url, self.form_data)

        self.assertRedirects(response, self.success_url)
        updated_note = Note.objects.last()

        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, self.author)

    def test_other_user_cant_edit_note(self):
        self.delete_notes
        response = self.not_author_client.post(self.edit_url, self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.last()
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.author, note_from_db.author)

    def test_author_can_delete_note(self):
        initial_count = Note.objects.count()
        response = self.author_client.post(self.delete_url)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_other_user_cant_delete_note(self):
        initial_count = Note.objects.count()
        response = self.not_author_client.post(self.delete_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
