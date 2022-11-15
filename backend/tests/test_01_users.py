import pytest
from django.contrib.auth import get_user_model


class Test01UserAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_users_not_authenticated(self, client):
        response = client.get('/api/users/')
        assert response.status_code != 404, (
            'Страница `/api/users/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/v1/users/` без токена авторизации возвращается статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_users_username_not_authenticated(self, client, user):
        response = client.get(f'/api/users/{user.id}/')
        assert response.status_code != 404, (
            f'Страница `/api/users/{user.id}/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 401, (
            'Проверьте, что при GET запросе `/api/users/{id}/` без токена авторизации возвращается статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_users_me_not_authenticated(self, client):
        response = client.get('/api/users/me/')
        assert response.status_code != 404, (
            'Страница `/api/users/me/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 401, (
            'Проверьте, что при GET запросе `/api/users/me/` без токена авторизации возвращается статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_users_get_user(self, client, user):
        request_type = 'GET'
        response = client.get('/api/users/')
        assert response.status_code != 404, (
            'Страница `/api/users/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/users/` с токеном авторизации возвращается статус 200'
        )
        pagination_data = ['count', 'next', 'previous', 'results']
        data = response.json()
        for field in pagination_data:
            assert (field in data
                    and isinstance(data['results'], list)), (
                f'Проверьте, что при {request_type} запросе /api/users/ без параметров '
                f'в ответе есть паджинация'
            )
        assert (
                len(data['results']) == 1
                and data['results'][0].get('username') == user.username
                and data['results'][0].get('email') == user.email
        ), (
            'Проверьте, что при GET запросе `/api/users/` возвращаете данные с пагинацией. '
            'Значение параметра `results` не правильное'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_users_post(self, user_client, user, client):
        empty_data = {}
        response = client.post('/api/users/', data=empty_data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе `/api/users/` с пустыми данными возвращаетe 400'
        )
        no_email_data = {
            'username': 'TestUser_noemail',
            'password': '123456789',
        }
        response = client.post('/api/users/', data=no_email_data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе `/api/users/` без email, возвращаетe статус 400'
        )
        valid_email = 'valid_email@yamdb.fake'
        no_username_data = {
            'email': valid_email,
            'password': '123456789',
        }
        response = client.post('/api/users/', data=no_username_data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе `/api/users/` без username, возвращаетe статус 400'
        )
        duplicate_email = {
            'username': 'TestUser_duplicate',
            'email': user.email
        }
        response = client.post('/api/users/', data=duplicate_email)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе `/api/users/` с уже существующим email, возвращаете статус 400. '
            '`Email` должен быть уникальный у каждого прользователя'
        )
        response_json = response.json()
        empty_fields = 'email'
        assert (empty_fields in response_json.keys()
                and response_json[empty_fields][0] == 'Пользователя с таким Адрес электронной почты уже существует.'), (
            'Проверьте, что при POST запросе `/api/users/` с уже существующим email, возвращаете статус 400. '
            'Пользователь с таким Адрес электронной почты уже существует.'
        )
        duplicate_username = {
            'username': user.username,
            'email': valid_email
        }
        response = client.post('/api/users/', data=duplicate_username)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе `/api/users/` с уже существующим username, возвращаете статус 400. '
            'Пользователя с таким Логин уже существует.'
        )
        response_json = response.json()
        empty_fields = 'username'
        assert (empty_fields in response_json.keys()
                and response_json[empty_fields][0] == 'Пользователя с таким Логин уже существует.'), (
            'Проверьте, что при POST запросе `/api/users/` с уже существующим username, возвращаете статус 400. '
            'Пользователь с таким Логин уже существует.'
        )
        valid_data = {
            'username': 'TestUser_2',
            'email': 'testuser2@yamdb.fake',
            'password': '1597q1dfffhj',
            'first_name': 'Role',
            'last_name': 'Vigi'
        }
        response = client.post('/api/users/', data=valid_data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе `/api/users/` с правильными данными возвращает 201.'
        )
        User = get_user_model()
        new_user = User.objects.get(username=valid_data['username'])
        assert new_user.permissions == 'user', (
            'Проверьте, что при POST запросе `/api/users/`, при создании пользователя, '
            'по умолчанию выдается роль user.'
        )
        response_data = response.json()
        assert response_data.get('first_name') == valid_data['first_name'], (
            'Проверьте, что при POST запросе `/api/users/` с правильными данными возвращаете `first_name`.'
        )
        assert response_data.get('last_name') == valid_data['last_name'], (
            'Проверьте, что при POST запросе `/api/users/` с правильными данными возвращаете `last_name`.'
        )
        assert response_data.get('username') == valid_data['username'], (
            'Проверьте, что при POST запросе `/api/users/` с правильными данными возвращаете `username`.'
        )
        assert response_data.get('email') == valid_data['email'], (
            'Проверьте, что при POST запросе `/api/users/` с правильными данными возвращаете `email`.'
        )
        users = User.objects.all()
        assert get_user_model().objects.count() == users.count(), (
            'Проверьте, что при POST запросе `/api/users/` вы создаёте пользователей.'
        )
        response = client.get('/api/users/')
        data = response.json()
        assert len(data['results']) == users.count(), (
            'Проверьте, что при GET запросе `/api/users/` возвращаете данные с пагинацией. '
            'Значение параметра `results` не правильное'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_users_method_not_allowed(self, user_client):
        response = user_client.delete('/api/users/')
        assert response.status_code == 405, (
            'Проверьте, что при DELETE запросе `/api/users/` возвращаете статус 405'
        )
        response = user_client.put('/api/users/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/users/` возвращаете статус 405'
        )
        response = user_client.patch('/api/users/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/users/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_users_me(self, user_client, client, user):
        response = client.get('/api/users/me/')
        assert response.status_code != 404, (
            'Страница `/api/v1/users/me/` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 401
        assert response.status_code == code, (
            'Проверьте, что при GET запросе `/api/v1/users/me/`'
            f' без токена возвращается статус {code}'
        )
        response = user_client.get('/api/users/me/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/v1/users/me/`'
            f' авторизованного пользователя возвращается статус {code}'
        )
        response_data = response.json()
        assert response_data.get('username') == user.username, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` возвращаете `username`.'
        )
        assert response_data.get('email') == user.email, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` возвращаете `email`.'
        )
        assert response_data.get('id') == user.id, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` возвращаете `id`.'
        )
        assert response_data.get('first_name') == user.first_name, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` возвращаете `first_name`.'
        )
        assert response_data.get('last_name') == user.first_name, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` возвращаете `last_name`.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_users_me_method_not_allowed(self, user_client):
        response = user_client.delete('/api/users/me/')
        assert response.status_code == 405, (
            'Проверьте, что при DELETE запросе `/api/v1/users/me/` возвращаете статус 405'
        )
        response = user_client.put('/api/users/me/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/v1/users/me/` возвращаете статус 405'
        )
        response = user_client.patch('/api/users/me/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/v1/users/me/` возвращаете статус 405'
        )
        response = user_client.post('/api/users/me/')
        assert response.status_code == 405, (
            'Проверьте, что при POST запросе `/api/v1/users/me/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_09_users_id_get(self, user_client, admin_client, user):
        response = admin_client.get(f'/api/users/{user.id}/')
        assert response.status_code != 404, (
            'Страница `/api/v1/users/{id}/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/v1/users/{id}/` '
            'с токеном авторизации другого пользователя возвращается статус 200'
        )
        response_data_user = response.json()
        assert response_data_user.get('username') == user.username, (
            'Проверьте, что при GET запросе `/api/v1/users/{id}/` возвращаете `username`.'
        )
        assert response_data_user.get('email') == user.email, (
            'Проверьте, что при GET запросе `/api/v1/users/{id}/` возвращаете `email`.'
        )
        assert response_data_user.get('id') == user.id, (
            'Проверьте, что при GET запросе `/api/v1/users/{id}/` возвращаете `id`.'
        )
        assert response_data_user.get('first_name') == user.first_name, (
            'Проверьте, что при GET запросе `/api/v1/users/{id}/` возвращаете `first_name`.'
        )
        assert response_data_user.get('last_name') == user.first_name, (
            'Проверьте, что при GET запросе `/api/v1/users/{id}/` возвращаете `last_name`.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_10_users_id_method_not_allowed(self, user_client, user):
        response = user_client.delete(f'/api/users/{user.id}/')
        assert response.status_code == 405, (
            'Проверьте, что при DELETE запросе `/api/v1/users/{id}/` возвращаете статус 405'
        )
        response = user_client.put('/api/users/me/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/v1/users/{id}/` возвращаете статус 405'
        )
        response = user_client.patch('/api/users/me/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/v1/users/{id}/` возвращаете статус 405'
        )
        response = user_client.post('/api/users/me/')
        assert response.status_code == 405, (
            'Проверьте, что при POST запросе `/api/v1/users/{id}/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_11_verbose_name(self, user):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verbose = {
            'username': 'Логин',
            'email': 'Адрес электронной почты',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'permissions': 'Роль',

        }
        for field, expected_value in field_verbose.items():
            assert expected_value in user._meta.get_field(field).verbose_name, (
                'Проверьте, что verbose_name в модели совпадает с ожидаемым'
            )


