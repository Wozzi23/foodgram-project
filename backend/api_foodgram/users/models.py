from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.models import UniqueConstraint

ADMIN = 'admin'
USER = 'user'

LIST_OF_ROLES = [
    (ADMIN, ADMIN),
    (USER, USER),
]


class User(AbstractBaseUser):
    """
    Модель для управления пользователями. Модель расширена
    ролью (админ, пользователь) и подтверждающим кодом.
    """
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Адрес электронной почты'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Уникальный юзернейм'
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
        null=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
        null=False,
    )
    user_permissions = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=LIST_OF_ROLES,
        default=USER,
        blank=True,
    )
    auth_token = models.CharField(
        verbose_name='Токен',
        max_length=200,
        null=True,
        blank=False,
        default='null'
    )

    @property
    def is_admin(self):
        return self.user_permissions == ADMIN

    @property
    def is_user(self):
        return self.user_permissions == USER

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user')
        ]
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
