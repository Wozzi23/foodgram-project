import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


class Test00UserRegistration:
    url_user = '/api/users/'
    url_user_set_password = '/api/users/set_password/'
    url_user_login = '/api/auth/token/login/'
    url_user_logout = '/api/auth/token/logout/'

    @pytest.mark.django_db(transaction=True)
    def test_00_nodata_user_registration(self, client):
        request_type = 'POST'
        response = client.post(self.url_user)
        assert response.status_code != 404, (
            f'Страница `{self.url_user}` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_user}` без параметров '
            f'не создается пользователь и возвращается статус {code}'
        )
        response_json = response.json()
        empty_fields = ['email', 'username', 'first_name', 'last_name', 'password']
        for field in empty_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверьте, что при {request_type} запросе `{self.url_user}` без параметров '
                f'в ответе есть сообщение о том, какие поля заполенены неправильно'
            )

    @pytest.mark.django_db(transaction=True)
    def test_00_invalid_data_user_registration(self, client):
        invalid_email = 'invalid_email'
        invalid_username = 'invalid_username@apifood.fake'

        invalid_data = {
            'email': invalid_email,
            'username': invalid_username
        }
        request_type = 'POST'
        response = client.post(self.url_user, data=invalid_data)
        response_json = response.json()
        invalid_fields = ['email']
        for field in invalid_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверьте, что при {request_type} запросе `{self.url_user}` с невалидными параметрами, '
                f'в ответе есть сообщение о том, какие поля заполенены неправильно'
            )

    @pytest.mark.django_db(transaction=True)
    def test_00_data_user_set_password(self, user_client, user):
        new_password = '987654321'
        current_password = '123456789'
        data = {
            'new_password': new_password,
            'current_password': current_password
        }
        request_type = 'POST'
        response = user_client.post(self.url_user_set_password, data=data)
        assert response.status_code != 404, (
            f'Страница `{self.url_user_set_password}` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_user_set_password}` с невалидными параметрами, '
            f'в ответе есть сообщение о том, что пароль не прошел валидацию'
        )

    @pytest.mark.django_db(transaction=True)
    def test_00_nodata_user_login(self, client):
        request_type = 'POST'
        response = client.post(self.url_user_login)
        assert response.status_code != 404, (
            f'Страница `{self.url_user_login}` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_user_login}` без параметров '
            f'не выдается токен и возвращается статус {code}'
        )
        response_json = response.json()
        empty_fields = ['non_field_errors']
        for field in empty_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверьте, что при {request_type} запросе `{self.url_user_login}` без параметров '
                f'в ответе есть сообщение о невозможности войти с предоставленными учетными данными.'
            )

    @pytest.mark.django_db(transaction=True)
    def test_00_incorrect_data_user_login(self, client, user):
        correct_email = user.email
        incorrect_password = 'Qry4rtyja'
        incorrect_data = {
            'email': correct_email,
            'password': incorrect_password
        }
        request_type = 'POST'
        response = client.post(self.url_user, data=incorrect_data)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_user_login}` некорректными данными '
            f'не выдается токен и возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_00_data_user_logout(self, user_client):
        request_type = 'POST'
        response = user_client.post(self.url_user_logout)
        assert response.status_code != 404, (
            f'Страница `{self.url_user_login}` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 204
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_user_logout}`'
            f'возвращается статус {code}'
        )
