import pytest



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
