import pytest
from django.db import IntegrityError


class Test01SubscribeUserAPI:
    @pytest.mark.django_db(transaction=True)
    def test_01_verbose_name(self, subscriptions):
        field_verbose = {
            'author': 'Автор рецептов',
            'user': 'Подписчик'
        }
        for field, expected_value in field_verbose.items():
            assert expected_value in subscriptions._meta.get_field(field).verbose_name, (
                'Проверьте, что verbose_name в модели совпадает с ожидаемым'
            )

    @pytest.mark.django_db(transaction=True)
    def test_02_unique_favorite_recipe(self, subscriptions, user):
        from users.models import Subscriptions
        with pytest.raises(IntegrityError):
            Subscriptions.objects.create(
                user=user,
                author=subscriptions.author,
            ), (
                'Проверьте, что попытке поавторно подписаться на того же автора'
                'с таким же user возникает ошибка'
            )

    @pytest.mark.django_db(transaction=True)
    def test_03_subscribe_to_yourself(self, user):
        from users.models import Subscriptions
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            Subscriptions.objects.create(
                user=user,
                author=user
            ), (
                'Проверьте что на уровне базы есть ограничение на '
                'запрет создания подписки на самого себя'
            )

    @pytest.mark.django_db(transaction=True)
    def test_04_subscriptions_method_not_allowed(self, admin_client, user):
        response = admin_client.post(f'/api/users/subscriptions/')
        assert response.status_code == 405, (
            'Проверьте, что при GET запросе `/api/users/subscriptions/` возвращаете статус 405'
        )
        response = admin_client.patch(f'/api/users/subscriptions/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/users/subscriptions/` возвращаете статус 405'
        )
        response = admin_client.put(f'/api/users/subscriptions/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/users/subscriptions/` возвращаете статус 405'
        )
        response = admin_client.delete(f'/api/users/subscriptions/')
        assert response.status_code == 405, (
            'Проверьте, что при DELETE запросе `/api/users/subscriptions/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_subscriptions_not_auth(self, client):
        response = client.get(f'/api/users/subscriptions/')
        assert response.status_code == 401, (
            'Проверьте что при попытке просмотреть подписки неавторизованному пользователю'
            'возвращаете статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_subscriptions_get(self, user_client, subscriptions, admin):
        request_type = 'GET'
        response = user_client.get(f'/api/users/subscriptions/')
        assert response.status_code == 200, (
            'Проверьте что при  попытке просмотреть подписки авторизованному пользователю'
            'возвращаете статус 200'
        )
        pagination_data = ['count', 'next', 'previous', 'results']
        data = response.json()
        for field in pagination_data:
            assert (field in data
                    and isinstance(data['results'], list)), (
                f'Проверьте, что при {request_type} запросе /api/users/subscriptions/'
                f'в ответе есть паджинация'
            )
        assert (
                len(data['results']) == 1
                and data['results'][0].get('username') == admin.username
                and data['results'][0].get('id') == admin.id
                and data['results'][0].get('email') == admin.email
                and data['results'][0].get('is_subscribed') is True
                and data['results'][0].get('recipes') == []
                and data['results'][0].get('recipes_count') == 0
        ), (
            f'Проверьте, что при {request_type} запросе /api/users/subscriptions/'
            f'поле results соответствует ожиданиям'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_subscribe_not_auth(self, subscriptions, client, user):
        response = client.post(f'/api/users/{user.id}/subscribe/')
        assert response.status_code == 401, (
            'Проверьте что при  попытке подписаться неавторизованному пользователю'
            'возвращаете статус 401'
        )
        response = client.delete(f'/api/users/{user.id}/subscribe/')
        assert response.status_code == 401, (
            'Проверьте что при  попытке отписаться неавторизованному пользователю'
            'возвращаете статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_subscribe_to_yourself(self, user_client, user):
        response = user_client.post(f'/api/users/{user.id}/subscribe/')
        assert response.status_code == 400, (
            'Проверьте что при попытке подписаться на самого себя'
            'возвращаете статус 400'
        )
        data = response.json()
        assert data.get('errors') == 'Нельзя подписаться на самого себя', (
            'Проверьте что при попытке подписаться на самого себя'
            'в ответе есть описание ошибки'
        )

    @pytest.mark.django_db(transaction=True)
    def test_09_subscribe_no_unique(self, subscriptions, user_client, admin):
        response = user_client.post(f'/api/users/{admin.id}/subscribe/')
        assert response.status_code == 400, (
            'Проверьте что при попытке повторно подписаться на автора'
            'возвращаете статус 400'
        )
        data = response.json()
        assert data.get('errors') == 'Вы уже подписаны на данного автора', (
            'Проверьте что при попытке повторно подписаться на автора'
            'в ответе есть описание ошибки'
        )

    @pytest.mark.django_db(transaction=True)
    def test_10_subscribe_post(self, user_client, admin):
        response = user_client.post(f'/api/users/{admin.id}/subscribe/')
        assert response.status_code == 201, (
            'Проверьте что при  попытке подписаться авторизованному пользователю'
            'возвращаете статус 201'
        )
        response = user_client.get(f'/api/users/subscriptions/')
        assert response.status_code == 200, (
            'Проверьте что при  попытке просмотреть подписки авторизованному пользователю'
            'возвращаете статус 200'
        )
        data = response.json()
        assert (
                data['results'][0].get('username') == admin.username
                and data['results'][0].get('is_subscribed') is True
        ), (
            f'Проверьте, что при  запросе GET /api/users/subscriptions/'
            f'появляется автор'
        )

    @pytest.mark.django_db(transaction=True)
    def test_10_subscribe_404(self, user_client, admin):
        response = user_client.post(f'/api/users/{666}/subscribe/')
        assert response.status_code == 404, (
            'Проверьте что при  попытке подписаться на несуществующего пользователя'
            'возвращаете статус 404'
        )
        response = user_client.delete(f'/api/users/{666}/subscribe/')
        assert response.status_code == 404, (
            'Проверьте что при  попытке отписаться на несуществующего пользователя'
            'возвращаете статус 404'
        )

    @pytest.mark.django_db(transaction=True)
    def test_10_subscribe_delete(self, user_client, subscriptions, admin):
        response = user_client.delete(f'/api/users/{admin.id}/subscribe/')
        assert response.status_code == 204, (
            'Проверьте что при попытке отписаться от автора успешный запрос'
            'возвращает статус 204'
        )

    def test_11_subscribe_delete_no(self, user_client, admin):
        response = user_client.delete(f'/api/users/{admin.id}/subscribe/')
        assert response.status_code == 400, (
            'Проверьте что при попытке отписаться от автора на которого'
            'не был подписан пользователь возвращает статус 400'
        )
        data = response.json()
        assert data.get('errors') == 'Вы не подписанны на этого автора', (
            'Проверьте что при попытке повторно подписаться на автора'
            'в ответе есть описание ошибки'
        )

