from rest_framework import permissions


class ReadAnyOrAuthorOnly(permissions.BasePermission):
    """
    Переопределенный класс BasePermission
    для проверки доступа у пользователя сделавшего запрос.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or bool(request.user and request.user.is_authenticated))

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
