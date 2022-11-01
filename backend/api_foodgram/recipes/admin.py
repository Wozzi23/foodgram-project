from django.contrib import admin

from recipes.models import Ingredients


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """Класс, формирующий админ-панель сайта, раздел: Ингридиенты."""
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '--пустое поле--'
