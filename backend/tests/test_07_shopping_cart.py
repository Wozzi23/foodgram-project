import pytest
from django.db import IntegrityError


class Test01ShoppingCartAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_verbose_name(self, shopping_cart):
        field_verbose = {
            'user': 'Позователь',
            'recipe': 'Рецепт'
        }
        for field, expected_value in field_verbose.items():
            assert expected_value in shopping_cart._meta.get_field(field).verbose_name, (
                'Проверьте, что verbose_name в модели совпадает с ожидаемым'
            )

    @pytest.mark.django_db(transaction=True)
    def test_02_unique_shopping_cart(self, shopping_cart, user):
        from recipes.models import ShoppingCart
        with pytest.raises(IntegrityError):
            ShoppingCart.objects.create(
                user=user,
                recipe=shopping_cart.recipe,
            ), (
                'Проверьте, что невозможно повторно добавить в список покупок рецепт'
                'с таким же user'
            )

    @pytest.mark.django_db(transaction=True)
    def test_03_shopping_cart_method_not_allowed(self, admin_client, recipe):
        response = admin_client.get(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert response.status_code == 405, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/shopping_cart/` возвращаете статус 405'
        )
        response = admin_client.patch(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/recipes/{id}/shopping_cart/` возвращаете статус 405'
        )
        response = admin_client.put(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/recipes/{id}/shopping_cart/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_shopping_cart_404(self, admin_client, shopping_cart):
        response = admin_client.post(f'/api/recipes/{666}/shopping_cart/')
        assert response.status_code == 404, (
            'Проверьте что при попытке добавить в список покупок несуществующий рецепт'
            'возвращаете статус 404'
        )
        response = admin_client.delete(f'/api/recipes/{666}/shopping_cart/')
        assert response.status_code == 404, (
            'Проверьте что при попытке удалить из списока покупок несуществующий рецепт'
            'возвращаете статус 404'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_shopping_cart_not_auth(self, client, shopping_cart):
        response = client.post(f'/api/recipes/{shopping_cart.recipe_id}/shopping_cart/')
        assert response.status_code == 401, (
            'Проверьте что при попытке добавить в список покупок неавторизованному пользователю'
            'возвращаете статус 401'
        )
        response = client.delete(f'/api/recipes/{shopping_cart.recipe_id}/shopping_cart/')
        assert response.status_code == 401, (
            'Проверьте что при попытке удалить из списока покупок неавторизованному пользователю'
            'возвращаете статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_shopping_cart_post(self, admin_client, shopping_cart):
        response = admin_client.post(f'/api/recipes/{shopping_cart.recipe_id}/shopping_cart/')
        assert response.status_code == 201, (
            'Проверьте что при попытке добавить в список покупок авторизованному пользователю'
            'возвращаете статус 201'
        )
        data = response.json()
        assert (
                data.get('id') == shopping_cart.recipe.id
                and data.get('name') == shopping_cart.recipe.name
                and data.get('cooking_time') == shopping_cart.recipe.cooking_time
                and data['image'].split('/')[-1] == 'image.jpeg'
        ), (
            'Проверьте что при успешной попытке добавить в список покупок авторизованному пользователю'
            'возвращается ответ с корректным рецептом'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_shopping_cart_post_no_uniq(self, user_client, shopping_cart):
        response = user_client.post(f'/api/recipes/{shopping_cart.recipe_id}/shopping_cart/')
        assert response.status_code == 400, (
            'Проверьте что при попытке добавить в список покупок рецепт который уже добавлен'
            'возвращаете статус 400'
        )
        data = response.json()
        assert data.get('errors') == "Рецепт уже добален", (
            'Проверьте что при попытке подписаться на рецепт который уже добавлен'
            'возвращаете ответ в описанием ошибки'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_shopping_cart_delete(self, user_client, shopping_cart, admin_client):
        response = user_client.delete(f'/api/recipes/{shopping_cart.recipe_id}/shopping_cart/')
        assert response.status_code == 204, (
            'Проверьте что при попытке удалить рецепт из списка покупок авторизованному пользователю'
            'возвращаете статус 204'
        )
        response = admin_client.delete(f'/api/recipes/{shopping_cart.recipe_id}/shopping_cart/')
        assert response.status_code == 400, (
            'Проверьте что при попытке удалить рецепт из списка покупок авторизованному пользователю'
            'возвращаете статус 400'
        )
        data = response.json()
        assert data.get('errors') == "Рецепт не был добален", (
            'Проверьте что при попытке удалить рецепт из списка покупок если он не был добавлен'
            'авторизованному пользователю возвращаете ответ в описанием ошибки'
        )

    @pytest.mark.django_db(transaction=True)
    def test_09_is_in_shopping_cart_in_recipe_no_auth(self, client, recipe):
        response = client.get(f'/api/recipes/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/recipes/` '
            'от неавторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        assert data['results'][0].get('is_in_shopping_cart') is False, (
            'Проверьте, что при GET запросе `/api/recipes/` в выдаче'
            'присутствует параметр is_in_shopping_cart и по умолчанию для неавторизованного'
            'пользователя парамет False. '
        )
        response = client.get(f'/api/recipes/{recipe.id}/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` '
            'от неавторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        assert data.get('is_in_shopping_cart') is False, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` в выдаче'
            'присутствует параметр is_favorited и по умолчанию для неавторизованного'
            'пользователя парамет False. '
        )
        response = client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert response.status_code == 401, (
            'Проверьте, что при POST запросе `/api/recipes/{id}/` '
            'от неавторизованного пользователя возвращается статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_10_is_favorite_in_recipe_auth(self, user_client, recipe):
        response = user_client.get(f'/api/recipes/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/recipes/` '
            'от авторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        assert data['results'][0].get('is_in_shopping_cart') is False, (
            'Проверьте, что при GET запросе `/api/recipes/` в выдаче'
            'присутствует параметр is_in_shopping_cart и по умолчанию для неавторизованного'
            'пользователя парамет False. '
        )
        response = user_client.get(f'/api/recipes/{recipe.id}/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` '
            'от авторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        assert data.get('is_favorited') is False, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` в выдаче'
            'присутствует параметр is_in_shopping_cart и по умолчанию для авторизованного'
            'пользователя парамет False. '
        )
        response = user_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе `/api/recipes/{id}/favorite/` '
            'от авторизованного пользователя возвращается статус 201'
        )
        response = user_client.get(f'/api/recipes/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/recipes/` '
            'от авторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        assert data['results'][0].get('is_in_shopping_cart') is True, (
            'Проверьте, что при GET запросе `/api/recipes/` в выдаче'
            'после добавления рецепта в список покупок изменяется статус'
            'на True'
        )