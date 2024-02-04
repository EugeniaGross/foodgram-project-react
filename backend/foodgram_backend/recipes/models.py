from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram_backend.constants import MAX_LENGTH_RECIPE
from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipe',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsinRecipe',
        verbose_name='Ингредиенты',
        related_name='recipe',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
    )
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_RECIPE
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images'
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                1,
                message='Значение не может быть меньше единицы'
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name


class IngredientsinRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_in_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов',
        validators=[
            MinValueValidator(
                1,
                message='Значение не может быть меньше единицы'
            )
        ]
    )

    class Meta:
        verbose_name = 'количество ингредиентов в рецепте'
        verbose_name_plural = 'Количество ингредиентов  в рецепте'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite_recipe'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избраннoе'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorite'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_recipe'
    )

    class Meta:
        verbose_name = 'покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_card'
            )
        ]
