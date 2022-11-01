from django.db import models
from django.db.models import UniqueConstraint


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название ингридиента')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
        constraints = [
            UniqueConstraint(
                fields=['name', ],
                name='unique_name'
            ),
        ]

    def __str__(self):
        return self.name

