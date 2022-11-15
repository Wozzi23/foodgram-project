# from django.test import TestCase, Client
# from django.db import IntegrityError
# from django.test import TestCase
# from rest_framework.authtoken.models import Token
# from rest_framework.test import APIClient
#
# from users.models import User
#
# test_user = {
#     'username': 'test_user',
#     'email': 'test@test.ru',
#     'first_name': 'morgan',
#     'last_name': 'freeman',
# }
#
# test_user_admin = {
#     'username': 'test_user_admin',
#     'email': 'test_admin@test.ru',
#     'first_name': 'ilon',
#     'last_name': 'musk',
#     'permissions': 'admin'
# }
#
#
# class UserModelTest(TestCase):
#     """Базовый класс для проверки модели User"""
#
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.user = User.objects.create(
#             username=test_user['username'],
#             email=test_user['email'],
#             first_name=test_user['first_name'],
#             last_name=test_user['last_name'],
#         )
#
#         cls.user_admin = User.objects.create(
#             username=test_user_admin['username'],
#             email=test_user_admin['email'],
#             first_name=test_user_admin['first_name'],
#             last_name=test_user_admin['last_name'],
#             permissions=test_user_admin['permissions']
#         )
#
#     def test_user_create_form(self):
#         """Тест формы создания пользователя"""
#         user = self.user
#         self.assertEqual(user.username, test_user['username'])
#
#     def test_user_permissions_form(self):
#         """Тест доступа пользователя по умолчанию"""
#         user = self.user
#         self.assertEqual(user.permissions, 'user')
#
#     def test_user_permissions_admin_form(self):
#         """Тест создания пользователя с ролью администратора"""
#         user = self.user_admin
#         self.assertEqual(user.permissions, 'admin')
#
#     def test_user_unique_form(self):
#         """Тест создания пользователя с неуникальными username и email"""
#         with self.assertRaises(IntegrityError):
#             User.objects.create(
#                 username=test_user['username'],
#                 email=test_user['email'],
#             )
#
#     def test_verbose_name(self):
#         """verbose_name в полях совпадает с ожидаемым."""
#         user = self.user
#         field_verbose = {
#             'username': 'Логин',
#             'email': 'Адрес электронной почты',
#             'first_name': 'Имя',
#             'last_name': 'Фамилия',
#             'permissions': 'Роль',
#
#         }
#         for field, expected_value in field_verbose.items():
#             with self.subTest(field=field):
#                 self.assertEqual(
#                     user._meta.get_field(field).verbose_name, expected_value)
#
#
# class UserURLTests(UserModelTest):
#     def setUp(self):
#         self.client = APIClient()
#         self.token = Token.objects.create(user=self.user)
#
#     def test_api_url_user(self):
#         """Проверка доступности адреса /api/users/
#         неавторизованному пользователю
#         """
#         response = self.client.get('/api/users/')
#         self.assertEqual(response.status_code, 200)
#
#     def test_api_url_no_user(self):
#         """Проверка не доступности адреса /api/users/1/
#         не авторизованному пользователю"""
#         response = self.client.get('/api/users/1/')
#         self.assertEqual(response.status_code, 401)
#
#     def test_url_exists_at_desired(self):
#         """Проверка доступности адреса /api/users/1/
#         авторизованному пользователю"""
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
#         response = self.client.get('/api/users/1/')
#         self.assertEqual(response.status_code, 200)
#
#     def test_url_me(self):
#         """Проверка доступности адреса /api/users/me/
#         авторизованному пользователю с данными корректного пользователя"""
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
#         response = self.client.get('/api/users/me/')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['username'], self.user.username)
#
#     def test_url_me_no_auth(self):
#         """Проверка не доступности адреса /api/users/me/
#         не авторизованному пользователю"""
#         response = self.client.get('/api/users/me/')
#         self.assertEqual(response.status_code, 401)
