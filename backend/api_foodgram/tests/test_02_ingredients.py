import pytest
from django.db import IntegrityError


class Test01IngredientsAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_verbose_name(self, ingredients):
        field_verbose = {
            'name': 'Название ингридиента',
            'measurement_unit': 'Единица измерения',
        }
        for field, expected_value in field_verbose.items():
            assert expected_value in ingredients._meta.get_field(field).verbose_name, (
                'Проверьте, что verbose_name в модели совпадает с ожидаемым'
            )

    @pytest.mark.django_db(transaction=True)
    def test_02_unique_ingredients(self, ingredients):
        from recipes.models import Ingredients
        with pytest.raises(IntegrityError):
            Ingredients.objects.create(
                name=ingredients.name,
                measurement_unit=ingredients.measurement_unit
            ), (
                'Проверьте, что невозможно добавить существующий ингридиент'
            )

    @pytest.mark.django_db(transaction=True)
    def test_03_get_ingredients(self, client, ingredients):
        response = client.get('/api/ingredients/')
        assert response.status_code != 404, (
            'Страница `/api/ingredients/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/ingredients/` '
            'от неавторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        print(data)
        assert (
                len(data) == 1
                and data[0].get('id') == ingredients.id
                and data[0].get('name') == ingredients.name
                and data[0].get('measurement_unit') == ingredients.measurement_unit
        ), (
            'Проверьте, что при GET запросе `/api/ingredients/` структура соответствует ожидаемой. '
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_ingredients_method_not_allowed(self, client):
        response = client.delete('/api/ingredients/')
        assert response.status_code == 405, (
            'Проверьте, что при DELETE запросе `/api/ingredients/` возвращаете статус 405'
        )
        response = client.put('/api/ingredients/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/ingredients/` возвращаете статус 405'
        )
        response = client.patch('/api/ingredients/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/ingredients/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_get_ingredients_id(self, client, ingredients):
        response = client.get(f'/api/ingredients/{ingredients.id}/')
        assert response.status_code != 404, (
            'Страница `/api/ingredients/{id}/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/ingredients/{id}/` '
            'от неавторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        assert (
                data.get('id') == ingredients.id
                and data.get('name') == ingredients.name
                and data.get('measurement_unit') == ingredients.measurement_unit
        ), (
            'Проверьте, что при GET запросе `/api/ingredients/{id}/` структура соответствует ожидаемой. '
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_ingredients_id_method_not_allowed(self, client, ingredients):
        response = client.delete(f'/api/ingredients/{ingredients.id}/')
        assert response.status_code == 405, (
            'Проверьте, что при DELETE запросе `/api/ingredients/{id}/` возвращаете статус 405'
        )
        response = client.put(f'/api/ingredients/{ingredients.id}/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/ingredients/{id}/` возвращаете статус 405'
        )
        response = client.patch(f'/api/ingredients/{ingredients.id}/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/ingredients/{id}/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_search_ingredient(self, client, ingredients, search_ingredients):
        response = client.get(f'/api/ingredients/?name={search_ingredients.name}')
        data = response.json()
        assert (
                data[0].get('id') == search_ingredients.id
                and data[0].get('name') == search_ingredients.name
                and data[0].get('measurement_unit') == search_ingredients.measurement_unit
        ), (
            'Проверьте, что при GET запросе `/api/ingredients/?name=ingredients.name/` '
            'происходит поиск и данные фильтруются. '
        )
