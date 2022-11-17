import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class Test01RecipesAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_verbose_name(self, recipe):
        field_verbose = {
            'author': 'Автор',
            'name': 'Название рецепта',
            'text': 'Описание рецепта',
            'cooking_time': 'Время приготовления (в минутах)',
            'image': 'Ссылка на картинку на сайте',
            'tags': 'Тег',
            'pub_date': 'Дата публикации',
            'ingredients': 'Ингридиента в рецепте'

        }
        for field, expected_value in field_verbose.items():
            assert expected_value in recipe._meta.get_field(field).verbose_name, (
                'Проверьте, что verbose_name в модели совпадает с ожидаемым'
            )

    @pytest.mark.django_db(transaction=True)
    def test_02_unique_name_author(self, recipe, user):
        from recipes.models import Recipes
        with pytest.raises(IntegrityError):
            Recipes.objects.create(
                author=user,
                name='Test recipe',
                cooking_time=2
            ), (
                'Проверьте, что невозможно повторно добавить рецепт'
                'с существующей связкой название рецепта - автор'
            )

    @pytest.mark.django_db(transaction=True)
    def test_03_no_unique_author(self, recipe, user_test):
        from recipes.models import Recipes
        new_recipe = Recipes.objects.create(
            author=user_test,
            name='Test recipe',
            cooking_time=2
        )
        assert new_recipe.author == user_test, (
            'Проверьте, что возможно добавить рецепт'
            'с существующим названием от другого автора'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_no_unique_ingredients_in_recipe(self, recipe, ingredients):
        from recipes.models import IngredientInRecipe
        with pytest.raises(IntegrityError):
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredients,
                amount=6
            ), (
                'Проверьте, что невозможно повторно добавить тот же ингридиент'
                'в рецепт'
            )

    @pytest.mark.django_db(transaction=True)
    def test_05_get_recipes(self, client, recipe, user):
        request_type = 'GET'
        response = client.get('/api/recipes/')
        assert response.status_code != 404, (
            'Страница `/api/tags/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/recipes/` '
            'от неавторизованного пользователя возвращается статус 200'
        )
        pagination_data = ['count', 'next', 'previous', 'results']
        data = response.json()
        for field in pagination_data:
            assert (field in data
                    and isinstance(data['results'], list)), (
                f'Проверьте, что при {request_type} запросе /api/recipes/ без параметров '
                f'в ответе есть паджинация'
            )
        author = data['results'][0].get('author')
        ingredient = data['results'][0].get('ingredients')
        ingredient_one = ingredient[0]
        tag = data['results'][0].get('tags')
        tag_one = tag[0]
        User = get_user_model()
        author_model = User.objects.get(id=author['id'])
        from recipes.models import IngredientInRecipe, Tags
        ingredient_model = IngredientInRecipe.objects.get(ingredient=ingredient_one['id'], recipe=recipe.id)
        tag_model = Tags.objects.get(id=tag_one['id'])
        assert (
                len(data['results']) == 1
                and data['results'][0].get('name') == recipe.name
                and data['results'][0].get('text') == recipe.text
                and data['results'][0].get('cooking_time') == recipe.cooking_time
                and author_model == user
                and ingredient_model.amount == ingredient_one['amount']
                and ingredient_model.ingredient.id == ingredient_one['id']
                and ingredient_model.ingredient.name == ingredient_one['name']
                and ingredient_model.ingredient.measurement_unit == ingredient_one['measurement_unit']
                and tag_model.id == tag_one['id']
                and tag_model.name == tag_one['name']
                and tag_model.slug == tag_one['slug']
                and tag_model.color == tag_one['color']
        ), (
            'Проверьте, что при GET запросе `/api/recipes/` возвращаете данные с пагинацией. '
            'Значение параметра `results` не правильное'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_get_recipes_id(self, client, recipe, user):
        response = client.get(f'/api/recipes/{recipe.id}/')
        assert response.status_code != 404, (
            'Страница `/api/tags/{id}/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` '
            'от неавторизованного пользователя возвращается статус 200'
        )
        data = response.json()

        author = data.get('author')
        ingredient = data.get('ingredients')
        ingredient_one = ingredient[0]
        tag = data.get('tags')
        tag_one = tag[0]
        User = get_user_model()
        author_model = User.objects.get(id=author['id'])
        from recipes.models import IngredientInRecipe, Tags
        ingredient_model = IngredientInRecipe.objects.get(ingredient=ingredient_one['id'], recipe=recipe.id)
        tag_model = Tags.objects.get(id=tag_one['id'])
        assert (
                data.get('name') == recipe.name
                and data.get('text') == recipe.text
                and data.get('cooking_time') == recipe.cooking_time
                and author_model == user
                and ingredient_model.amount == ingredient_one['amount']
                and ingredient_model.ingredient.id == ingredient_one['id']
                and ingredient_model.ingredient.name == ingredient_one['name']
                and ingredient_model.ingredient.measurement_unit == ingredient_one['measurement_unit']
                and tag_model.id == tag_one['id']
                and tag_model.name == tag_one['name']
                and tag_model.slug == tag_one['slug']
                and tag_model.color == tag_one['color']
        ), (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете корректные данные. '
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_recipes_method_not_allowed(self, user_client):
        response = user_client.delete('/api/recipes/')
        assert response.status_code == 405, (
            'Проверьте, что при DELETE запросе `/api/recipes/` возвращаете статус 405'
        )
        response = user_client.put('/api/recipes/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/recipes/` возвращаете статус 405'
        )
        response = user_client.patch('/api/recipes/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/recipes/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_recipes_id_method_not_allowed(self, user_client, recipe):
        response = user_client.put(f'/api/recipes/{recipe.id}/')
        assert response.status_code == 405, (
            'Проверьте, что при PUT запросе `/api/recipes/{id}/` возвращаете статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_09_recipes_post(self, user_client, tags, ingredients, mock_media):
        data = {}
        response = user_client.post('/api/recipes/', data=data, format='json')
        assert response.status_code == 400, (
            'Проверьте что при POST запросе `/api/recipes/`'
            ' с незаполненными данными возвращается статус 400')
        data = response.json()
        assert (
                data.get('tags') == ['Обязательное поле.']
                and data.get('ingredients') == ['Обязательное поле.']
                and data.get('name') == ['Обязательное поле.']
                and data.get('image') == ['Ни одного файла не было отправлено.']
                and data.get('text') == ['Обязательное поле.']
                and data.get('cooking_time') == ['Обязательное поле.']
        ), (
            'Проверьте, что при POST запросе `/api/recipes/` '
            'в ответе есть укзаание полей обязательных для заполнения '
        )
        data = {
            'name': 'Test recipe',
            'text': 'Test Text',
            'cooking_time': 11,
            'tags': [22],
            'ingredients': [
                {
                    'id': 22,
                    'amount': 10
                }
            ]
            ,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1'
                     '/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg== '
        }
        response = user_client.post('/api/recipes/', data=data, format='json')
        assert response.status_code == 400, (
            'Проверьте что при POST запросе `/api/recipes/`'
            ' с ингридиентами и тегами отсутствующими в базе возвращается статус 400')
        data = response.json()
        assert (
                data.get('tags')[0]['id'] == ['Тега нет в базе']
                and data.get('ingredients')[0]['id'] == ['Ингридиента нет в базе']
        ), (
            'Проверьте что при POST запросе `/api/recipes/`'
            ' с ингридиентами и тегами отсутствующими в базе в ответе есть соотвествующие сообщения')

        data = {
            'name': 'Test recipe',
            'text': 'Test Text',
            'cooking_time': 11,
            'tags': [tags.id],
            'ingredients': [
                {
                    'id': ingredients.id,
                    'amount': 10
                }
            ]
            ,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1'
                     '/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg== '
        }
        response = user_client.post('/api/recipes/', data=data, format='json')
        assert response.status_code == 201, (
            'Проверьте что при POST запросе `/api/recipes/`'
            ' с валидными данными возвращается статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_10_recipes_post_uniq(self, user_client, recipe, tags, ingredients):
        data = {
            'name': recipe.name,
            'text': 'Test Text',
            'cooking_time': 11,
            'tags': [tags.id],
            'ingredients': [
                {
                    'id': ingredients.id,
                    'amount': 10
                }
            ]
            ,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1'
                     '/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg== '
        }
        response = user_client.post('/api/recipes/', data=data, format='json')
        assert response.status_code == 400, (
            'Проверьте что при POST запросе `/api/recipes/`'
            ' существующей связкой author, name возвращается статус 400'
        )
        data = response.json()
        assert data.get('name') == ['Вы уже создали такой рецепт'], (
            'Проверьте что при POST запросе `/api/recipes/`'
            ' с существующей связкой author,name возвращается сообщение о том что такой рецепт существует'
        )

    @pytest.mark.django_db(transaction=True)
    def test_11_recipes_patch(self, user_client, admin_client, tags, ingredients, recipe):
        response = admin_client.patch(f'/api/recipes/{recipe.id}/')
        assert response.status_code == 403, (
            'Проверьте что при POST запросе `/api/recipes/{id}/`'
            'от пользователя не являщегося автором возвращается статус 403'
        )
        data = {
            'name': 'New name',
            'text': 'New text',
            'cooking_time': 11,
            'tags': [tags.id],
            'ingredients': [
                {
                    'id': ingredients.id,
                    'amount': 10
                }
            ]
            ,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1'
                     '/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg== '
        }
        response = user_client.patch(f'/api/recipes/{recipe.id}/', data=data, format='json')
        assert response.status_code == 200, (
            'Проверьте что при PATCH запросе `/api/recipes/{id}/`'
            'от пользователя являщегося автором возвращается статус 200'
        )
        response_json = response.json()
        assert (
                response_json.get('name') == data['name']
                and response_json.get('text') == data['text']
                and response_json.get('cooking_time') == data['cooking_time']
        ), (
            'Проверьте что при PATCH запросе `/api/recipes/{id}/`'
            'возвращаются обновленные данные'
        )
        from recipes.models import Recipes
        recipe_new = Recipes.objects.get(id=recipe.id)
        assert (
            recipe_new.name == data['name']
            and recipe_new.text == data['text']
            and recipe_new.cooking_time == data['cooking_time']
        ), (
            'Проверьте что при PATCH запросе `/api/recipes/{id}/`'
            'в модели происходит обновление данных'
        )

    @pytest.mark.django_db(transaction=True)
    def test_12_recipes_delete(self, user_client, admin_client, recipe):
        request_type = 'DELETE'
        response = admin_client.delete(f'/api/recipes/{recipe.id}/')
        assert response.status_code == 403, (
            'Проверьте, что при DELETE запросе `/api/recipes/{id}` '
            'от пользователя не являющегося автором возвращается статус 403'
        )
        response = user_client.delete(f'/api/recipes/{recipe.id}/')
        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе `/api/recipes/{id}` '
            'от пользователя являющегося автором возвращается статус 204'
        )
        response = user_client.get(f'/api/recipes/{recipe.id}/')
        assert response.status_code == 404, (
            'Проверьте, после DELETE запроса `/api/recipes/{id}` '
            'от пользователя являющегося автором, при запросе обьекта'
            'возвращается статус 404'
        )




