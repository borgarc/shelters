import os
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands import createsuperuser
from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_signs_in_with_lowercased_email(self):
        user = User.objects.create_user(
            email='Alice@Example.COM', password='s3cret-pass'
        )

        self.assertEqual(user.email, 'alice@example.com')
        self.assertEqual(user.get_username(), 'alice@example.com')
        self.assertTrue(user.check_password('s3cret-pass'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(hasattr(user, 'username'))

    def test_create_superuser_sets_staff_and_superuser_flags(self):
        user = User.objects.create_superuser(
            email='admin@example.com', password='s3cret-pass'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_email_is_unique_regardless_of_case(self):
        User.objects.create_user(email='alice@example.com', password='s3cret-pass')

        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='ALICE@example.com', password='other-pass')

    def test_plain_save_lowercases_email(self):
        user = User(email='Bob@Example.COM')
        user.save()

        user.refresh_from_db()
        self.assertEqual(user.email, 'bob@example.com')

    def test_database_rejects_email_differing_only_in_case(self):
        User.objects.create_user(email='bob@example.com', password='s3cret-pass')

        with self.assertRaises(IntegrityError):
            User.objects.bulk_create([User(email='BOB@example.com')])


class CreateSuperuserCommandTests(TestCase):
    def test_creates_superuser_from_email_without_username(self):
        with mock.patch.dict(os.environ, {'DJANGO_SUPERUSER_PASSWORD': 's3cret-pass'}):
            call_command(
                'createsuperuser',
                '--noinput',
                '--email=Admin@Example.com',
                stdout=StringIO(),
            )

        user = User.objects.get()
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('s3cret-pass'))

    def test_interactive_prompt_asks_for_email_not_username(self):
        prompts = []

        def fake_input(prompt):
            prompts.append(prompt)
            return 'admin@example.com'

        tty = mock.Mock(isatty=lambda: True)
        with (
            mock.patch('builtins.input', fake_input),
            mock.patch.object(
                createsuperuser.getpass, 'getpass', return_value='s3cret-pass'
            ),
        ):
            call_command(
                'createsuperuser', interactive=True, stdin=tty, stdout=StringIO()
            )

        self.assertEqual(len(prompts), 1)
        self.assertIn('Email address', prompts[0])
        self.assertNotIn('Username', prompts[0])
        self.assertTrue(User.objects.get(email='admin@example.com').is_superuser)


class AdminSignInTests(TestCase):
    def setUp(self):
        User.objects.create_superuser(email='admin@example.com', password='s3cret-pass')

    def sign_in(self, email, password='s3cret-pass'):
        return self.client.post(
            reverse('admin:login'),
            {'username': email, 'password': password, 'next': reverse('admin:index')},
        )

    def test_login_form_asks_for_email(self):
        response = self.client.get(reverse('admin:login'))

        self.assertContains(response, 'Email address')

    def test_superuser_signs_in_with_email_and_password(self):
        response = self.sign_in('admin@example.com')

        self.assertRedirects(response, reverse('admin:index'))

    def test_sign_in_ignores_email_case(self):
        response = self.sign_in('Admin@Example.COM')

        self.assertRedirects(response, reverse('admin:index'))

    def test_wrong_password_is_rejected(self):
        response = self.sign_in('admin@example.com', password='wrong-pass')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)


class UserAdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@example.com', password='s3cret-pass'
        )
        self.client.force_login(self.admin)

    def test_changelist_lists_users_by_email(self):
        response = self.client.get(reverse('admin:users_user_changelist'))

        self.assertContains(response, 'admin@example.com')

    def test_change_page_renders(self):
        response = self.client.get(
            reverse('admin:users_user_change', args=[self.admin.pk])
        )

        self.assertContains(response, 'admin@example.com')
        self.assertNotContains(response, 'name="username"')

    def test_add_user_with_email_and_password(self):
        response = self.client.post(
            reverse('admin:users_user_add'),
            {
                'email': 'Carol@Example.com',
                'usable_password': 'true',
                'password1': 'a-long-s3cret-pass',
                'password2': 'a-long-s3cret-pass',
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='carol@example.com')
        self.assertTrue(user.check_password('a-long-s3cret-pass'))

    def test_add_user_rejects_email_differing_only_in_case(self):
        response = self.client.post(
            reverse('admin:users_user_add'),
            {
                'email': 'ADMIN@example.com',
                'usable_password': 'true',
                'password1': 'a-long-s3cret-pass',
                'password2': 'a-long-s3cret-pass',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
