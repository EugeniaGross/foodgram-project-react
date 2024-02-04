from django.db import models

from foodgram_backend.constants import MAX_LENGTH_INGREDIENT


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_INGREDIENT,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=MAX_LENGTH_INGREDIENT,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name
