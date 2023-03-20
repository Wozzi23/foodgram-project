from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscriptions, User


class AdminUser(admin.ModelAdmin):
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


admin.site.register(User, UserAdmin)
