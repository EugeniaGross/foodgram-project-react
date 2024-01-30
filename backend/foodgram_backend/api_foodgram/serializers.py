import base64

from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientsinRecipe, Recipe,
                            ShoppingCart, Tag, TagRecipe)
from users.models import Subscription, User


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
        ) + tuple(User.REQUIRED_FIELDS) + (
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if isinstance(self.context.get('request').user, AnonymousUser):
            return False
        if Subscription.objects.filter(user=self.context.get(
                'request').user, subscription=obj).exists():
            return True
        return False


class UserPostSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        fields = (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            "password",
        ) + tuple(User.REQUIRED_FIELDS)


class IngredientRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsinRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientsinRecipe
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipePostSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())

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
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.tags.clear()
        instance.ingredients.clear()
        tags = validated_data.get('tags')
        self.add_tags(tags, recipe)
        ingredients = validated_data.get('ingredients')
        IngredientsinRecipe.objects.filter(recipe=recipe).delete()
        self.add_ingredients(ingredients, recipe)
        return instance

    def add_tags(self, tags, recipe):
        for tag in tags:
            TagRecipe.objects.create(recipe=recipe, tag=tag)

    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            current_ingredient = ingredient.pop('id')
            amount = ingredient.pop('amount')
            IngredientsinRecipe.objects.create(
                recipe=recipe, ingredient=current_ingredient, amount=amount)

    def to_internal_value(self, data):
        image = data.get('image')
        if isinstance(image, str) and image.startswith('data:image'):
            format, imgstr = image.split(';base64,')
            ext = format.split('/')[-1]
            image = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
        data['image'] = image
        return super().to_internal_value(data)

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance, context={'request': self.context.get('request')}).data


class RecipeGetSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UserGetSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField(use_url=True)

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
        return IngredientRecipeGetSerializer(ingredients, many=True).data

    def get_is_in_shopping_cart(self, obj):
        if isinstance(self.context.get('request').user, AnonymousUser):
            return False
        if ShoppingCart.objects.filter(user=self.context.get(
                'request').user, recipe=obj).exists():
            return True
        return False

    def get_is_favorited(self, obj):
        if isinstance(self.context.get('request').user, AnonymousUser):
            return False
        if Favorite.objects.filter(user=self.context.get(
                'request').user, recipe=obj).exists():
            return True
        return False


class RecipeInFavoriteOrCartSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipe.count()

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipe_limit')
        if limit:
            return RecipeInFavoriteOrCartSerializer(
                obj.recipe.all()[: int(limit)],
                many=True,
                context={'request': self.context.get('request')}
            ).data
        return RecipeInFavoriteOrCartSerializer(
            obj.recipe.all(),
            many=True,
            context={'request': self.context.get('request')}
        ).data

    def get_is_subscribed(self, obj):
        return True
