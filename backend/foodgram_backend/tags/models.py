from django.db import models

from foodgram_backend.constants import MAX_LENGTH_TAG, MAX_LENGTH_TAG_COLOR

from .validators import validate_hex_color


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_TAG,
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=MAX_LENGTH_TAG_COLOR,
        validators=[
            validate_hex_color
        ]
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=MAX_LENGTH_TAG,
        unique=True,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
