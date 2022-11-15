from django.contrib import admin

from .models import User, Subscriptions


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс, формирующий админ-панель сайта, раздел: пользователи."""
    list_display = (
        'username', 'email', 'first_name',
        'last_name', 'permissions',
    )
    search_fields = ('username', 'permissions',)
    list_filter = ('username', 'email')
    empty_value_display = '--пустое поле--'


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Класс, формирующий админ-панель сайта, раздел: Подписки."""
    list_display = (
        'author', 'user',
    )
    empty_value_display = '--пустое поле--'
