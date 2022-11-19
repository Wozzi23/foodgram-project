from rest_framework import permissions


class ReadAnyOrAuthorOnly(permissions.BasePermission):
    """
    Собственный метод проверки доступа к модели,
    безопасные методы доступны всем пользователям,
    остальные только автору рецепта.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
