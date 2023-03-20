from colorfield.fields import ColorField

from django.core.validators import (MaxLengthValidator, MaxValueValidator,
                                    MinValueValidator)
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User


class Ingredients(models.Model):
    """
    Модель ингридиентов.

    ...

    Атрибуты
    --------
    name: str
        Название ингридиента
    measurement_unit: int
        Единица измерения
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name'
            ),
        ]

    def __str__(self):
        return f'{self.name},{self.measurement_unit}'


class Tags(models.Model):
    """
    Модель тегов.

    ...

    Атрибуты
    --------
    name: str
        Название тега
    color: str
        Цвет в HEX
    slug: str
        Уникальный слаг
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега'
    )
    color = ColorField(
        verbose_name='Цвет в HEX',
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Уникальный слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug',)
        constraints = [
            UniqueConstraint(
                fields=['name', 'color'],
                name='unique_tag'
            ),
        ]

    def __str__(self):
        return self.slug


class Recipes(models.Model):
    """
    Модель Рецептов.

    ...

    Атрибуты
    --------
    author: int
        Автор
    name: str
        Название рецепта
    text: str
        Описание рецепта
    cooking_time: int
        Время приготовления (в минутах)
    image: str
        Ссылка на картинку на сайте
    tags: int
        Тег
    pub_date: str
        Дата публикации
    ingredients: int
        Ингридиента в рецепте
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    text = models.TextField(
        validators=[MaxLengthValidator(1500)],
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1),
        ],
        error_messages={
            'max_value': 'Не стоит готовть сутками'
        }

    )
    image = models.ImageField(
        verbose_name='Ссылка на картинку на сайте',
        upload_to='api_foodgram/images/'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes',
        verbose_name='Тег',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='recipes',
        verbose_name='Ингридиента в рецепте',
        through='IngredientInRecipe',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe'
            ),
        ]

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """
    Модель связки ингридиентов и рецептов.

    ...

    Атрибуты
    --------
    ingredient: int
        Ингридиент
    recipe: int
        Рецепт
    amount: int
        Количество
    """
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.DO_NOTHING,
        verbose_name='Ингридиент',
        related_name='ingredient_in_recipe'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name = 'Количество ингридиента в рецепте'
        verbose_name_plural = 'Количество ингридиентов в рецепте'
        constraints = [
            UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_in_recipe'
            ),
        ]

    def __str__(self):
        return (f'{self.ingredient.name} '
                f'в количестве {self.amount} '
                f'{self.ingredient.measurement_unit}')


class UserRecipeAbstractModel(models.Model):
    """
    Абстрактная модель связки пользователя и
    рецепта.

    ...

    Атрибуты
    --------
    user: int
        Ингридиент
    recipe: int
        Рецепт
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Позователь',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True


class FavoriteRecipes(UserRecipeAbstractModel):
    """
    Модель подписки пользователя на рецепт.
    """

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            ),
        ]

    def __str__(self):
        return f'У {self.user} в избранном {self.recipe}.'


class ShoppingCart(UserRecipeAbstractModel):
    """
    Модель формирует список покупок и конкретного пользователя.
    """

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        ]
