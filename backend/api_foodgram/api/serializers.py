import base64

from api import paginations

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction

from recipes.models import IngredientInRecipe, Ingredients, Recipes, Tags

from rest_framework import serializers

from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
    """
    Класс сериализации модели User.

    ...

    Атрибуты
    --------
    is_subscribed: bool
        подписка на автора

    Методы
    ------
    get_is_subscribed(obj):
        Проверяет наличие связки пользователя сделавшего запрос
        и автора в модели Subscriptions

    to_representation(instance):
        Убирает из POST запроса на адрес /api/users/
        поле is_subscribed для соответсвия ответа техзаданию.

    create(validated_data):
        Создает обьект модели User из проверенных данных.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        read_only_fields = (
            'id',
            'is_subscribed'
        )
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_is_subscribed(self, obj) -> bool:
        """
        Проверяет наличие связки пользователя сделавшего запрос
        и автора в модели Subscriptions

        Параметры
        ---------
        obj: int
            id автора

        Возвращаемое значение
        ---------------------
        Bool
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return user.subscribe_user.filter(
                author=obj).exists()
        return False

    def to_representation(self, instance):
        """
        Убирает из POST запроса на адрес /api/users/
        поле is_subscribed для соответсвия ответа техзаданию.

        Параметры
        ---------
        instance: dict
            словарь ответов на запрос

        Возвращаемое значение
        ---------------------
        dict
        """
        res = super().to_representation(instance)
        if (self.context['request'].method == 'POST'
                and self.context['request'].path == '/api/users/'):
            res.pop('is_subscribed')
        return res

    def create(self, validated_data):
        """
        Создает обьект модели User из проверенных данных.

        Параметры
        ---------
        validated_data: dict
            Словарь значений для модели User

        Возвращаемое значение
        ---------------------
        Queryset[User]
        """
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class IngredientsSerializer(serializers.ModelSerializer):
    """
    Класс сериализации модели Ingredients.
    """

    class Meta:
        model = Ingredients
        read_only_fields = ('name', 'measurement_unit')
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeRepresentationSerializer(IngredientsSerializer):
    """
    Класс сериализации модели Ingredients.

    ...

    Методы
    ------
    to_representation(instance):
        Добавляет поле amount в конкретном рецепте.
    """

    def to_representation(self, instance):
        """
        Добавляет поле amount в конкретном рецепте.

        Параметры
        ---------
        instance: dict
            словарь значений из запроса

        Возвращаемое значение
        ---------------------
        dict
        """
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount
        }


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """
    Класс сериализации модели связующий модели между Recipes и Ingredients.
    Добавляет поле amount для рецепта.

    ...

    Атрибуты
    --------
    id: int
        номер ингридиента в базе
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        error_messages={'does_not_exist': 'Ингридиента нет в базе'})

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class TagsSerializer(serializers.ModelSerializer):
    """
    Класс сериализации модели Tags.

    ...

    Атрибуты
    --------
    id: int
        номер тега в базе

    Методы
    ------
    to_internal_value(data):
        Пересобирает ответ убирая вложенность значений.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        error_messages={'does_not_exist': 'Тега нет в базе'})

    class Meta:
        model = Tags
        read_only_fields = ('name', 'color', 'slug')
        fields = ('id', 'name', 'color', 'slug')

    def to_internal_value(self, data):
        """
        Пересобирает ответ убирая вложенность значений.

        Параметры
        ---------
        data: dict
            словарь значений из запроса

        Возвращаемое значение
        ---------------------
        dict
        """
        tag = {'id': data}
        return super().to_internal_value(tag)


class Base64ImageField(serializers.ImageField):
    """
    Сериализатор поля с картинкой [image]
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Класс сериализации модели Recipes. Иcпользуется для вложенных полей
    других сериализаторов.

    ...

    Атрибуты
    --------
    name: str
        название рецепта
    image: dict
        картинка зашифрованная в формат base64
    """
    name = serializers.CharField(
        min_length=2,
        max_length=200
    )
    image = Base64ImageField()

    class Meta:
        model = Recipes
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipesSerializer(RecipeMinifiedSerializer):
    """
    Класс сериализации модели Recipes. Наследуется от
    модели RecipeMinifiedSerializer и новыми полями расширяем
    модель.

    ...

    Атрибуты
    --------
    tags: list
        теги
    ingredients: list
        ингридиенты
    text: str
        описание рецепта
    is_favorited: bool
        нахождение в избранном у пользователя
    is_in_shopping_cart: bool
        нахождение в корзине у пользователя
    author: dict
        автор рецепта

    Методы
    ------
    to_representation(instance):
        Меняет сериализатор для выдачи. Добавляя расширенные данные
        по полю ingredients.
    __create_or_update_obj(recipe, tags, ingredients):
        Функция для корректного обновления или создания рецепта
    create(validated_data):
        Функция создания рецепта
    update(instance, validated_data):
        Функция обработки PATCH запроса
    validate(attrs):
        Валидация уникальности имени рецепта и автора
    validate_tags(attrs):
        Валидации поля tags
    validate_ingredients(attrs):
        Валидации поля ingredients
    get_is_favorited(obj):
        Функция обработки поля is_favorited на основе
        связи пользователя и рецепта через модель FavoriteRecipes.
    get_is_in_shopping_cart(obj):
        Функция обработки поля is_in_shopping_cart на основе
        связи пользователя и рецепта через модель ShoppingCart.
    """
    tags = TagsSerializer(many=True)
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        write_only=True
    )
    text = serializers.CharField(min_length=5)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = SignUpSerializer(read_only=True)

    class Meta:
        model = Recipes
        read_only_fields = (
            'id',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def to_representation(self, instance):
        """
        Меняет сериализатор для выдачи. добавляя расширенные данные
        по полю ingredients.

        Параметры
        ---------
        instance: dict

        Возвращаемое значение
        ---------------------
        dict
        """
        res = super().to_representation(instance)
        res['ingredients'] = (
            IngredientRecipeRepresentationSerializer(
                instance.recipe_ingredients.all(), many=True).data
        )
        return res

    @staticmethod
    def __create_or_update_obj(recipe, tags, ingredients):
        """
        Функция для корректного обновления или создания рецепта

        Параметры
        ---------
        recipe: Queryset[Recipe]
            обьект модели Recipe
        tags: list
            список тегов
        ingredients: list
            список ингридиентов

        Возвращаемое значение
        ---------------------
        Queryset[Recipe]
        """
        for tag in tags:
            recipe.tags.add(tag['id'])
        ingredients_in_recipe = []
        for ingredient in ingredients:
            ingredients_in_recipe.append(
                IngredientInRecipe(
                    ingredient=ingredient['id'],
                    recipe=recipe,
                    amount=ingredient['amount']
                )
            )
        recipe.recipe_ingredients.bulk_create(ingredients_in_recipe)
        return recipe

    @transaction.atomic
    def create(self, validated_data):
        """
        Функция создания рецепта.

        Параметры
        ---------
        validated_data: dict

        Возвращаемое значение
        ---------------------
        Queryset[Recipe]
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        return self.__create_or_update_obj(recipe, tags, ingredients)

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Функция обработки PATCH запроса

        Параметры
        ---------
        instance: Queryset[Recipe]
            рецепт
        validated_data: dict
            обновленные данные

        Возвращаемое значение
        ---------------------
        Queryset[Recipe]
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.ingredients.clear()
        recipe = super().update(instance, validated_data)
        return self.__create_or_update_obj(recipe, tags, ingredients)

    def validate(self, attrs):
        """
        Валидация уникальности имени рецепта и автора

        Параметры
        ---------
        attrs: dict
            атрибуты запроса

        Возвращаемое значение
        ---------------------
        dict
        """
        no_uniq_recipe = (
            self.context['request'].user.recipes.
            filter(name=attrs['name']).exists()
        )
        if self.context['request'].method == 'POST' and no_uniq_recipe:
            raise serializers.ValidationError(
                {'name': 'Вы уже создали такой рецепт'}
            )
        return attrs

    @staticmethod
    def validate_tags(attrs):
        """
        Функция валидации поля tags

        Параметры
        ---------
        attrs: dict
            атрибуты запроса

        Возвращаемое значение
        ---------------------
        dict
        """
        tags_id = []
        for tag in attrs:
            tag_id = tag['id'].id
            tags_id.append(tag_id)
        if len(attrs) == 0:
            raise serializers.ValidationError(
                {'errors': 'Поле не может быть пустым'}
            )
        if len(attrs) != len(set(tags_id)):
            raise serializers.ValidationError(
                {'errors': 'Теги не могут повторяться'}
            )
        return attrs

    @staticmethod
    def validate_ingredients(attrs):
        """
        Функция валидации поля ingredients

        Параметры
        ---------
        attrs: dict
            атрибуты запроса

        Возвращаемое значение
        ---------------------
        dict
        """
        ingredients_id = []
        for ingredient in attrs:
            ingredient_id = ingredient['id'].id
            ingredients_id.append(ingredient_id)
        if len(attrs) == 0:
            raise serializers.ValidationError(
                {'errors': 'Поле не может быть пустым'}
            )
        if len(attrs) != len(set(ingredients_id)):
            raise serializers.ValidationError(
                {'errors': 'Ингридиенты не могут повторяться'}
            )
        return attrs

    def get_is_favorited(self, obj):
        """
        Функция обработки поля is_favorited на основе
        связи пользователя и рецепта через модель FavoriteRecipes.

        Параметры
        ---------
        obj: int

        Возвращаемое значение
        ---------------------
        bool
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return user.favoriterecipes_set.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Функция обработки поля is_in_shopping_cart на основе
        связи пользователя и рецепта через модель ShoppingCart.

        Параметры
        ---------
        obj: int

        Возвращаемое значение
        ---------------------
        bool
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return user.shoppingcart_set.filter(recipe=obj).exists()
        return False


class SubscriptionsSerializer(SignUpSerializer):
    """
    Класс сериализации модели подписки, ролительский класс
    SignUpSerializer.

    ...

    Атрибуты
    --------
    recipes: list
        Список рецептов автора
    recipes_count: int
        Количество рецептов у автора

    Методы
    ------
    paginate_recipes(obj):
        Добавляет поджинацию при ответе на запрос.
    """
    recipes = serializers.SerializerMethodField(
        'paginate_recipes', read_only=True
    )
    recipes_count = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = User
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def paginate_recipes(self, obj):
        """
        Добавляет поджинацию при ответе на запрос.

        Параметры
        ---------
        obj: Queryset[User]
            автор

        Возвращаемое значение
        ---------------------
        dict

        """
        recipe = obj.recipes.all()
        paginator = paginations.CustomPageNumberPagination()
        paginator.page_size_query_param = 'recipes_limit'
        paginator.page_size = 3
        page = paginator.paginate_queryset(recipe, self.context['request'])
        serializer = RecipeMinifiedSerializer(
            page,
            many=True,
            context={'request': self.context['request']})
        return serializer.data


class SetPasswordSerializer(serializers.Serializer):
    """
    Класс сериализации запроса на смену пароля

    ...

    Атрибуты
    --------
    current_passwor: str
        Старый пароль
    new_password: str
        Новый пароль

    Методы
    ------
    validate(obj):
        Проверка ноого пароля на корректность.
    update(instance, validated_data):
        Обновление пароля


    """
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, obj):
        """
        Проверка ноого пароля на корректность.

        Параметры
        ---------
        obj: dict

        Возвращаемое значение
        ---------------------
        dict
        """
        try:
            validate_password(obj['new_password'])
        except ValidationError as error:
            raise serializers.ValidationError(
                {'new_password': list(error.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        """
        Обновление пароля

        Параметры
        ---------
        instance: Queryset[User]
            обьект модели User
        validated_data: dict
            проверенный пароль

        Возвращаемое значение
        ---------------------
        dict

        """
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        if (validated_data['current_password']
                == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data
