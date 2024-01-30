from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientsinRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('name', )
    list_per_page = 20


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', )
    list_filter = ('name', )
    list_per_page = 20


class TagRecipeInLine(admin.StackedInline):
    model = TagRecipe
    extra = 1


class IngredientsinRecipeInLine(admin.StackedInline):
    model = IngredientsinRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (TagRecipeInLine, IngredientsinRecipeInLine)
    list_display = (
        'name',
        'text',
        'image',
        'cooking_time',
        'author',
        'get_tags',
        'get_ingredients',
        'get_count',
        'pub_date')
    list_filter = ('name', 'author', 'tags')
    list_per_page = 20

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ', '.join([
            tag.name for tag in obj.tags.all()
        ])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join([
            ingredient.name for ingredient in obj.ingredients.all()
        ])

    @admin.display(description='Число добавлений в избранное')
    def get_count(self, obj):
        return obj.favorite_recipe.count()


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'recipe')
    list_filter = ('tag', )
    list_per_page = 20


@admin.register(IngredientsinRecipe)
class IngredientsinRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe', )
    list_per_page = 20


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    list_per_page = 20


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    list_per_page = 20
