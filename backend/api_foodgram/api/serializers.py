import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Ingredients, Tags, Recipes, IngredientInRecipe
from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели User.
    """

    class Meta:
        model = User
        read_only_fields = ('id',)
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
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
        fields = ('id',)

    def to_representation(self, instance):
        instances = {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount
        }
        return instances


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


class RecipesListSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Recipes.
    """
    tags = TagsSerializer(many=True)
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        write_only=True
    )
    author = SignUpSerializer(read_only=True)
    image = Base64ImageField()
    name = serializers.CharField(
        min_length=2,
        max_length=200
    )
    text = serializers.CharField(min_length=5)
    cooking_time = serializers.IntegerField(
        min_value=1,
        max_value=1440,
        error_messages={
            'max_value': 'Не стоит готовть сутками'
        }
    )

    class Meta:
        model = Recipes
        read_only_fields = ('id', 'author',)
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res['ingredients'] = IngredientsSerializer(instance.recipe_ingredients.all(), many=True).data
        return res

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag['id'])
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.ingredients.clear()
        recipe = super().update(instance, validated_data)
        for tag in tags:
            recipe.tags.add(tag['id'])
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            )
        return instance

    def validate(self, attrs):
        if self.context['request'].method == 'POST':
            if Recipes.objects.filter(author=self.context.get('request').user, name=attrs['name']).exists():
                raise serializers.ValidationError({'name': 'Вы уже создали такой рецепт'})
        return attrs


    @staticmethod
    def validate_tags(attrs):
        tags_id = []
        for tag in attrs:
            tag_id = tag['id'].id
            tags_id.append(tag_id)
        if len(attrs) == 0:
            raise serializers.ValidationError('Поле не может быть пустым')
        elif len(attrs) != len(set(tags_id)):
            raise serializers.ValidationError('Теги не могут повторяться')
        return attrs

    @staticmethod
    def validate_ingredients(attrs):
        ingredients_id = []
        for ingredient in attrs:
            ingredient_id = ingredient['id'].id
            ingredients_id.append(ingredient_id)
        if len(attrs) == 0:
            raise serializers.ValidationError('Поле не может быть пустым')
        elif len(attrs) != len(set(ingredients_id)):
            raise serializers.ValidationError('Ингридиенты не могут повторяться')
        return attrs