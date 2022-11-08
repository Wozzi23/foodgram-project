from django.contrib import admin

from recipes.models import Ingredients, Tags, IngredientInRecipe, Recipes


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """Класс, формирующий админ-панель сайта, раздел: Ингридиенты."""
    list_display = (
        'name', 'measurement_unit',
    )
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
    list_display = (
        'author',
        'name',
        'text',
        'cooking_time',

    )
    inlines = (IngredientInRecipeInline,)
    filter_horizontal = ('tags',)
