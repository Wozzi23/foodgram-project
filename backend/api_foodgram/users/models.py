from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

ADMIN = 'admin'
USER = 'user'

LIST_OF_ROLES = [
    (ADMIN, ADMIN),
    (USER, USER),
]


class User(AbstractUser):
    """
    Модель для управления пользователями. Модель расширена
    ролью (админ, пользователь).
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
        verbose_name='Логин'
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
        null=False,
    )
    permissions = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=LIST_OF_ROLES,
        default=USER,
    )

    @property
    def is_admin(self):
        return self.permissions == ADMIN

    @property
    def is_user(self):
        return self.permissions == USER

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user')
        ]
        ordering = ('username',)
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """
    Модель подписки пользователя на авторов.
    Уникальность связки author и user.
    Добавлена проверка на запрет подписки на
    самого себя.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецептов',
        related_name='subscribe_author'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscribe_user'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscribe',
            )
        ]
        ordering = ('author',)
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'Пользователь {self.user.username} '
                f'подписан на {self.author.username}.')

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.author == self.user:
            raise ValidationError('Нельзя подписаться на самого себя')

    def save(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        if self.author == self.user:
            raise ValidationError('Нельзя подписаться на самого себя')
        super().save(*args, **kwargs)
