import base64

from api import paginations

from django.core.files.base import ContentFile
from django.db import transaction

from recipes.models import (IngredientInRecipe,
                            Ingredients,
                            Recipes,
                            Tags)

from rest_framework import serializers

from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели User. Поле is_subscribed вычисляется
    вхождения в модель Subscriptions пользователя сделавшего запрос
    и автора рецепта.
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
        Функция обработки поля is_subscribed на основе
        связи пользователя и автора через модель Subscriptions.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return user.subscribe_user.filter(
                author=obj).exists()
        return False

    def to_representation(self, instance):
        """
        Функция убирает из POST запроса на адрес /api/users/
        поле is_subscribed для соответсвия ответа техзаданию.
        """
        res = super().to_representation(instance)
        if (self.context['request'].method == 'POST'
                and self.context['request'].path == '/api/users/'):
            res.pop('is_subscribed')
        return res

    def create(self, validated_data):
        """
        Метод обработки POST запроса длч создания модели User.
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
    Сериализатор модели Ingredients.
    """

    class Meta:
        model = Ingredients
        read_only_fields = ('name', 'measurement_unit')
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeRepresentationSerializer(IngredientsSerializer):
    """
    Сериализатор модели Ingredients в выдачу добавлено поле
    amount для реализации количества ингридиента в конкретном
    рецепте
    """

    def to_representation(self, instance):
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount
        }


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор связующей модели между Recipes и Ingredients.
    Добавляет поле amount для рецепта.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        error_messages={'does_not_exist': 'Ингридиента нет в базе'})
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class TagsSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Tags.
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
        Для POST запросов через модель рецепта через поле id
        приводим выдачу к валидным значениям для избежания
        ошибок и не писать второй сериализатор для модели.
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
    Сериализатор модели Recipes. Изпользуется для вложенных полей
    других сериализаторов, является родительским к RecipesSerializer
    """
    name = serializers.CharField(
        min_length=2,
        max_length=200
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=1,
        max_value=1440,
        error_messages={
            'max_value': 'Не стоит готовть сутками'
        }
    )

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
    Сериализатор модели Recipes. Часть полей наследуется от
    модели RecipeMinifiedSerializer и новыми полями расширяем
    модель для соответсвия выдачи ожиданиям.
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
        """
        res = super().to_representation(instance)
        res['ingredients'] = (
            IngredientRecipeRepresentationSerializer(
                instance.recipe_ingredients.all(), many=True).data
        )
        return res

    @staticmethod
    def __create_or_update_obj(recipe, tags, ingredients):
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
        IngredientInRecipe.objects.bulk_create(ingredients_in_recipe)
        return recipe

    @transaction.atomic
    def create(self, validated_data):
        """
        Функция обработки POST запроса
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        return self.__create_or_update_obj(recipe, tags, ingredients)

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Функция обработки PATCH запроса
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.ingredients.clear()
        recipe = super().update(instance, validated_data)
        return self.__create_or_update_obj(recipe, tags, ingredients)

    def validate(self, attrs):
        """
        Валидация уникальности имени рецепта и автора для исключения
        попадания нескольких одинаковых рецептов в модели.
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
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return user.favoriterecipes_set.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Функция обработки поля is_in_shopping_cart на основе
        связи пользователя и рецепта через модель ShoppingCart.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return user.shoppingcart_set.filter(recipe=obj).exists()
        return False


class SubscriptionsSerializer(SignUpSerializer):
    """
    Класс сериализации модели подписки ролительский класс
    SignUpSerializer в выдачу добавлены связанные с
    автором рецепты и их общее количество.
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
        Функция добавляет поджинацию при ответе на запрос.
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
