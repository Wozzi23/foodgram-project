import pytest
from django.db import IntegrityError


class Test01FavoriteRecipeAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_verbose_name(self, favorite_recipe):
        field_verbose = {
            'user': 'Позователь',
            'recipe': 'Рецепт'
        }
        for field, expected_value in field_verbose.items():
            assert expected_value in favorite_recipe._meta.get_field(field).verbose_name, (
                'Проверьте, что verbose_name в модели совпадает с ожидаемым'
            )

    @pytest.mark.django_db(transaction=True)
    def test_02_unique_favorite_recipe(self, favorite_recipe, user):
        from recipes.models import FavoriteRecipes
        with pytest.raises(IntegrityError):
            FavoriteRecipes.objects.create(
                user=user,
                recipe=favorite_recipe.recipe,
            ), (
                'Проверьте, что невозможно повторно добавить в избранное рецепт'
                'с таким же user'
            )

    @pytest.mark.django_db(transaction=True)
    def test_03_favorite_recipe_method_not_allowed(self, admin_client, recipe):
        response = admin_client.get(f'/api/recipes/{recipe.id}/favorite/')
        assert response.status_code == 405, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/favorite/` возвращаете статус 405'
        )
        response = admin_client.patch(f'/api/recipes/{recipe.id}/favorite/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/recipes/{id}/favorite/` возвращаете статус 405'
        )
        response = admin_client.put(f'/api/recipes/{recipe.id}/favorite/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/recipes/{id}/favorite/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_favorite_recipe_404(self, admin_client, favorite_recipe):
        response = admin_client.post(f'/api/recipes/{666}/favorite/')
        assert response.status_code == 404, (
            'Проверьте что при попытке подписаться на несуществующий рецепт'
            'возвращаете статус 404'
        )
        response = admin_client.delete(f'/api/recipes/{666}/favorite/')
        assert response.status_code == 404, (
            'Проверьте что при попытке отписаться от несуществующего рецепта'
            'возвращаете статус 404'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_favorite_recipe_not_auth(self, client, favorite_recipe):
        response = client.post(f'/api/recipes/{favorite_recipe.recipe_id}/favorite/')
        assert response.status_code == 401, (
            'Проверьте что при попытке подписаться неавторизованному пользователю'
            'возвращаете статус 401'
        )
        response = client.delete(f'/api/recipes/{favorite_recipe.recipe_id}/favorite/')
        assert response.status_code == 401, (
            'Проверьте что при попытке отписаться неавторизованному пользователю'
            'возвращаете статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_favorite_recipe_post(self, admin_client, favorite_recipe):
        response = admin_client.post(f'/api/recipes/{favorite_recipe.recipe_id}/favorite/')
        assert response.status_code == 201, (
            'Проверьте что при попытке подписаться авторизованному пользователю'
            'возвращаете статус 201'
        )
        data = response.json()
        assert (
                data.get('id') == favorite_recipe.recipe.id
                and data.get('name') == favorite_recipe.recipe.name
                and data.get('cooking_time') == favorite_recipe.recipe.cooking_time
                and data['image'].split('/')[-1] == 'image.jpeg'
        ), (
            'Проверьте что при успешной попытке подписаться авторизованному пользователю'
            'возвращается ответ с корректным рецептом'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_favorite_recipe_post_no_uniq(self, user_client, favorite_recipe):
        response = user_client.post(f'/api/recipes/{favorite_recipe.recipe_id}/favorite/')
        assert response.status_code == 400, (
            'Проверьте что при попытке подписаться на рецепт который уже добавлен'
            'возвращаете статус 400'
        )
        data = response.json()
        assert data.get('errors') == "Рецепт уже добален", (
            'Проверьте что при попытке подписаться на рецепт который уже добавлен'
            'возвращаете ответ в описанием ошибки'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_favorite_recipe_delete(self, user_client, favorite_recipe, admin_client):
        response = user_client.delete(f'/api/recipes/{favorite_recipe.recipe_id}/favorite/')
        assert response.status_code == 204, (
            'Проверьте что при попытке отписаться на добаленный рецепт авторизованному пользователю'
            'возвращаете статус 204'
        )
        response = admin_client.delete(f'/api/recipes/{favorite_recipe.recipe_id}/favorite/')
        assert response.status_code == 400, (
            'Проверьте что при попытке отписаться на не добаленный рецепт авторизованному пользователю'
            'возвращаете статус 400'
        )
        data = response.json()
        assert data.get('errors') == "Рецепт не был добален", (
            'Проверьте что при попытке отписаться на не добаленный рецепт'
            'авторизованному пользователю возвращаете ответ в описанием ошибки'
        )

    @pytest.mark.django_db(transaction=True)
    def test_09_is_favorite_in_recipe_no_auth(self, client, recipe):
        response = client.get(f'/api/recipes/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/recipes/` '
            'от неавторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        assert data['results'][0].get('is_favorited') is False, (
            'Проверьте, что при GET запросе `/api/recipes/` в выдаче'
            'присутствует параметр is_favorited и по умолчанию для неавторизованного'
            'пользователя парамет False. '
        )
        response = client.get(f'/api/recipes/{recipe.id}/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` '
            'от неавторизованного пользователя возвращается статус 200'
        )
        data = response.json()
        assert data.get('is_favorited') is False, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` в выдаче'
            'присутствует параметр is_favorited и по умолчанию для неавторизованного'
            'пользователя парамет False. '
        )
        response = client.post(f'/api/recipes/{recipe.id}/favorite/')
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
        assert data['results'][0].get('is_favorited') is False, (
            'Проверьте, что при GET запросе `/api/recipes/` в выдаче'
            'присутствует параметр is_favorited и по умолчанию для неавторизованного'
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
            'присутствует параметр is_favorited и по умолчанию для авторизованного'
            'пользователя парамет False. '
        )
        response = user_client.post(f'/api/recipes/{recipe.id}/favorite/')
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе `/api/recipes/{id}/favorite/` '
            'от авторизованного пользователя возвращается статус 200'
        )

