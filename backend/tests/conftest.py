import tempfile

import pytest


@pytest.fixture()
def mock_media(settings):
    with tempfile.TemporaryDirectory() as temp_directory:
        settings.MEDIA_ROOT = temp_directory
        yield temp_directory


@pytest.fixture
def user_superuser(django_user_model):
    return django_user_model.objects.create_superuser(
        username='TestSuperuser',
        email='testsuperuser@yamdb.fake',
        password='1234567',
        permissions='user',
    )


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username='TestAdmin',
        email='testadmin@yamdb.fake',
        password='1234567',
        permissions='admin',
    )


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser',
        email='testuser@yamdb.fake',
        password='123456789',
        permissions='user',
    )


@pytest.fixture
def user_test(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser2',
        email='testuser2@yamdb.fake',
        password='123456789',
        permissions='user',
    )


@pytest.fixture
def token_user_superuser(user_superuser):
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=user_superuser)
    return {
        'access': str(token),
    }


@pytest.fixture
def user_superuser_client(token_user_superuser):
    from rest_framework.test import APIClient
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_user_superuser["access"]}')
    return client


@pytest.fixture
def token_admin(admin):
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=admin)
    return {
        'access': str(token),
    }


@pytest.fixture
def admin_client(token_admin):
    from rest_framework.test import APIClient
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_admin["access"]}')
    return client


@pytest.fixture
def token_user(user):
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=user)
    return {
        'access': str(token),
    }


@pytest.fixture
def user_client(token_user):
    from rest_framework.test import APIClient
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_user["access"]}')
    return client


@pytest.fixture
def ingredients():
    from recipes.models import Ingredients
    ingredients = Ingredients.objects.create(
        name='Test_Ingredients',
        measurement_unit='liter'
    )
    return ingredients


@pytest.fixture
def search_ingredients():
    from recipes.models import Ingredients
    search_ingredients = Ingredients.objects.create(
        name='Search_Ingred',
        measurement_unit='кг'
    )
    return search_ingredients


@pytest.fixture
def tags():
    from recipes.models import Tags
    tag = Tags.objects.create(
        name='Test_tag',
        color='#6AFF9B',
        slug='Test_slug'
    )
    return tag


@pytest.fixture
def recipe(ingredients, user, tags, mock_media):
    from recipes.models import Recipes
    create_recipe = Recipes.objects.create(
        author=user,
        name='Test recipe',
        text='Test Text',
        cooking_time=2,
        image='http://foodgram.example.org/media/recipes/images/image.jpeg'
    )
    create_recipe.tags.add(tags)
    create_recipe.ingredients.add(ingredients, through_defaults={'amount': 3})
    return create_recipe


@pytest.fixture
def ingredients_in_recipe(ingredients, recipe):
    from recipes.models import IngredientInRecipe
    create_ingredients_in_recipe = IngredientInRecipe.objects.create(
        recipe=recipe,
        ingredient=ingredients,
        amount=3
    )
    return create_ingredients_in_recipe


@pytest.fixture
def favorite_recipe(user, recipe):
    from recipes.models import FavoriteRecipes
    create_favorite_recipe = FavoriteRecipes.objects.create(
        recipe=recipe,
        user=user,
    )
    return create_favorite_recipe


@pytest.fixture
def subscriptions(user, admin):
    from users.models import Subscriptions
    create_subscriptions = Subscriptions.objects.create(
        author=admin,
        user=user,
    )
    return create_subscriptions


@pytest.fixture
def shopping_cart(user, recipe):
    from recipes.models import ShoppingCart
    create_shopping_cart = ShoppingCart.objects.create(
        recipe=recipe,
        user=user,
    )
    return create_shopping_cart
