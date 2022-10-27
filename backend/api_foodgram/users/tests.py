from django.db import IntegrityError
from django.test import TestCase

from users.models import User

test_user = {
    'username': 'test_user',
    'email': 'test@test.ru',
    'first_name': 'morgan',
    'last_name': 'freeman',
}

test_user_admin = {
    'username': 'test_user_admin',
    'email': 'test_admin@test.ru',
    'first_name': 'ilon',
    'last_name': 'musk',
    'user_permissions': 'admin'
}


class UserModelTest(TestCase):
    """Базовый класс для проверки модели User"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=test_user['username'],
            email=test_user['email'],
            first_name=test_user['first_name'],
            last_name=test_user['last_name'],
        )

        cls.user_admin = User.objects.create(
            username=test_user_admin['username'],
            email=test_user_admin['email'],
            first_name=test_user_admin['first_name'],
            last_name=test_user_admin['last_name'],
            user_permissions=test_user_admin['user_permissions']
        )

    def test_user_create_form(self):
        """Тест формы создания пользователя"""
        user = self.user
        self.assertEqual(user.username, test_user['username'])

    def test_user_permissions_form(self):
        """Тест доступа пользователя по умолчанию"""
        user = self.user
        self.assertEqual(user.user_permissions, 'user')

    def test_user_permissions_admin_form(self):
        """Тест создания пользователя с ролью администратора"""
        user = self.user_admin
        self.assertEqual(user.user_permissions, 'admin')

    def test_user_unique_form(self):
        """Тест создания пользователя с неуникальными username и email"""
        with self.assertRaises(IntegrityError):
            User.objects.create(
                username=test_user['username'],
                email=test_user['email'],
            )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        user = self.user
        field_verbose = {
            'username': 'Уникальный юзернейм',
            'email': 'Адрес электронной почты',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'user_permissions': 'Роль',

        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    user._meta.get_field(field).verbose_name, expected_value)
