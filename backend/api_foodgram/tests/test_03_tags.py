import pytest
from django.db import IntegrityError


class Test01TagsAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_verbose_name(self, tags):
        field_verbose = {
            'name': 'Название тега',
            'color': 'Цвет в HEX',
            'slug': 'Уникальный слаг'
        }
        for field, expected_value in field_verbose.items():
            assert expected_value in tags._meta.get_field(field).verbose_name, (
                'Проверьте, что verbose_name в модели совпадает с ожидаемым'
            )

    @pytest.mark.django_db(transaction=True)
    def test_02_unique_tags(self, tags):
        from recipes.models import Tags
        with pytest.raises(IntegrityError):
            Tags.objects.create(
                name='Test',
                color='#E26C2D',
                slug=tags.slug
            ), (
                'Проверьте, что невозможно добавить тег с существующим slug'
            )

    @pytest.mark.django_db(transaction=True)
    def test_03_get_tags(self, client, tags):
        response = client.get('/api/tags/')
        assert response.status_code != 404, (
            'Страница `/api/tags/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/tags/` '
            'от неавторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        assert (
                len(data) == 1
                and data[0].get('id') == tags.id
                and data[0].get('name') == tags.name
                and data[0].get('color') == tags.color
                and data[0].get('slug') == tags.slug
        ), (
            'Проверьте, что при GET запросе `/api/tags/` структура соответствует ожидаемой. '
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_tags_method_not_allowed(self, client):
        response = client.delete('/api/tags/')
        assert response.status_code == 405, (
            'Проверьте, что при DELETE запросе `/api/tags/` возвращаете статус 405'
        )
        response = client.put('/api/tags/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/tags/` возвращаете статус 405'
        )
        response = client.patch('/api/tags/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/tags/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_get_tags_id(self, client, tags):
        response = client.get(f'/api/tags/{tags.id}/')
        assert response.status_code != 404, (
            'Страница `/api/tags/{id}/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/tags/{id}/` '
            'от неавторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        assert (
                data.get('id') == tags.id
                and data.get('name') == tags.name
                and data.get('color') == tags.color
                and data.get('slug') == tags.slug
        ), (
            'Проверьте, что при GET запросе `/api/tags/{id}/` структура соответствует ожидаемой. '
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_tags_id_method_not_allowed(self, client, tags):
        response = client.delete(f'/api/tags/{tags.id}/')
        assert response.status_code == 405, (
            'Проверьте, что при DELETE запросе `/api/tags/{id}/` возвращаете статус 405'
        )
        response = client.put(f'/api/tags/{tags.id}/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/tags/{id}/` возвращаете статус 405'
        )
        response = client.patch(f'/api/tags/{tags.id}/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/tags/{id}/` возвращаете статус 405'
        )
