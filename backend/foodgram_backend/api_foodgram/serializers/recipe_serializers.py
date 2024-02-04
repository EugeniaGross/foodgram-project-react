import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from ingredients.models import Ingredient
from recipes.models import Favorite, IngredientsinRecipe, Recipe, ShoppingCart
from tags.models import Tag

from .tag_serializers import TagSerializer
from .users_serializers import UserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsinRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientsinRecipe
        fields = (
            'id',
            'amount'
            )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = data['ingredients']
        tags = data['tags']
        unique_ingredients = []
        unique_tags = []
        for ingredient in ingredients:
            if ingredient['id'] in unique_ingredients:
                raise serializers.ValidationError(
                    'Вы не можете в рецепте использовать один '
                    'и тот же ингредиент больше одного раза'
                )
            else:
                unique_ingredients.append(ingredient['id'])
        for tag in tags:
            if tag in unique_tags:
                raise serializers.ValidationError(
                    'Вы не можете использовать в рецепте один '
                    'и тот же тег больше одного раза'
                )
            else:
                unique_tags.append(tag)
        return super().validate(data)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        instance.tags.clear()
        instance.ingredients.clear()
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        self.add_ingredients(ingredients, recipe)
        return super().update(instance, validated_data)

    def add_ingredients(self, ingredients, recipe):
        IngredientsinRecipe.objects.bulk_create(
            [
                IngredientsinRecipe(
                    recipe=recipe,
                    ingredient=ingredient.pop('id'),
                    amount=ingredient.pop('amount')
                )
                for ingredient in ingredients
            ]
        )

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={'request': self.context.get('request')}).data


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = IngredientsinRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=self.context.get(
                'request').user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        return Favorite.objects.filter(user=self.context.get(
                'request').user, recipe=obj).exists()


class RecipeInFavoriteOrCartSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ShoppingCartCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, attrs):
        ending = self.context.get('ending')
        if self.context.get('request').method == 'POST':
            if self.Meta.model.objects.filter(
                user=attrs['user'],
                recipe=attrs['recipe']
            ).exists():
                raise serializers.ValidationError(
                    f'Этот рецепт уже находится в {ending}'
                )
            return attrs
        if self.context.get('request').method == 'DELETE':
            if not self.Meta.model.objects.filter(
                user=attrs['user'],
                recipe=attrs['recipe']
            ).exists():
                raise serializers.ValidationError(
                    f'Этого рецепта нет в {ending}'
                )
            return attrs


class FavoriteCreateSerializer(ShoppingCartCreateSerializer):
    class Meta(ShoppingCartCreateSerializer.Meta):
        model = Favorite
