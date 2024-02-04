from djoser.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from users.models import Subscription, User

from .recipe_serializers import RecipeInFavoriteOrCartSerializer


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
        ) + tuple(User.REQUIRED_FIELDS) + (
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=self.context.get('request').user,
            author=obj
        ).exists()


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            "password",
        ) + tuple(User.REQUIRED_FIELDS)

    def validate(self, attrs):
        if attrs['username'] == 'me':
            raise serializers.ValidationError(
                'Вы не можете использовать me как имя пользователя'
            )
        return super().validate(attrs)


class SubscriptionsSerializer(UserSerializer):
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
        return obj.recipes.count()

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipe_limit')
        if limit:
            return RecipeInFavoriteOrCartSerializer(
                obj.recipes.all()[: int(limit)],
                many=True,
                context={'request': self.context.get('request')}
            ).data
        return RecipeInFavoriteOrCartSerializer(
            obj.recipes.all(),
            many=True,
            context={'request': self.context.get('request')}
        ).data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, attrs):
        if self.context.get('request').method == 'POST':
            if attrs['user'] == attrs['author']:
                raise serializers.ValidationError(
                    'Вы не можете подписаться сами на себя'
                )
            if Subscription.objects.filter(
                user=attrs['user'], author=attrs['author']
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя'
                )
            return attrs
        if self.context.get('request').method == 'DELETE':
            if not Subscription.objects.filter(
                user=attrs['user'], author=attrs['author']
            ).exists():
                raise serializers.ValidationError(
                    'Вы не подписаны на этого пользователя'
                )
            return attrs
