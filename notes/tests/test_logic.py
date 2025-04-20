from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.utils import TestParentCase


class TestNoteLogic(TestParentCase):

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        initial_count = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        initial_count = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_not_unique_slug(self):
        initial_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))

    def test_empty_slug(self):
        Note.objects.all().delete()
        form_data = self.form_data.copy()
        form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=form_data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)

        new_note = Note.objects.get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, self.form_data)

        self.assertRedirects(response, self.success_url)
        updated_note = Note.objects.get(id=self.note.id)

        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_other_user_cant_edit_note(self):
        response = self.not_author_client.post(self.edit_url, self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        same_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, same_note.title)
        self.assertEqual(self.note.text, same_note.text)
        self.assertEqual(self.note.slug, same_note.slug)
        self.assertEqual(self.author, same_note.author)

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
