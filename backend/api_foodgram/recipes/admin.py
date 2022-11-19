from django.contrib import admin
from django.db.models import Count

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipes.models import (FavoriteRecipes,
                            IngredientInRecipe,
                            Ingredients,
                            Recipes,
                            Tags)


class IngredientsResource(resources.ModelResource):
    """Класс для иморта ингридиентов"""
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit',)


@admin.register(Ingredients)
class IngredientsAdmin(ImportExportModelAdmin):
    """Класс, формирующий админ-панель сайта, раздел: Ингридиенты."""
    list_display = (
        'name', 'measurement_unit',
    )
    resource_classes = [IngredientsResource]
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '--пустое поле--'


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    """Класс, формирующий админ-панель сайта, раздел: Теги."""

    list_display = (
        'name', 'color', 'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)

    empty_value_display = '--пустое поле--'


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 0
    verbose_name = 'Ингридиент в рецепт'
    verbose_name_plural = 'Ингридиенты в рецепте'
    min_num = 1
    can_delete = False


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    """Класс, формирующий админ-панель сайта, раздел: Рецепты."""
    list_display = (
        'author',
        'name',
        'text',
        'cooking_time',
        'is_favorite'
    )
    inlines = (IngredientInRecipeInline,)
    filter_horizontal = ('tags',)
    list_filter = [
        'name',
        'author__username',
        'tags__name',
    ]

    def is_favorite(self, obj):
        result = (
            FavoriteRecipes.objects.
            filter(recipe=obj).
            aggregate(is_favorite=Count('recipe')))
        return result["is_favorite"]


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Класс, формирующий админ-панель сайта, раздел: Ингридиенты в рецепте."""
    list_display = (
        'ingredient',
        'recipe',
        'amount'
    )
