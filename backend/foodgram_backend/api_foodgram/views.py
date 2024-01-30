import io

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import signals, utils
from djoser.compat import get_user_email
from djoser.conf import settings
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientsinRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User

from .filters import RecipeFilter
from .mixins import UpdateModelMixin
from .pagination import FoodGramPagination
from .permissions import IsAuthorOrAuthenticated
from .serializers import (IngredientsSerializer, RecipeGetSerializer,
                          RecipeInFavoriteOrCartSerializer,
                          RecipePostSerializer, SubscriptionsSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = settings.SERIALIZERS.user
    queryset = User.objects.all()
    permission_classes = settings.PERMISSIONS.user
    pagination_class = FoodGramPagination
    token_generator = default_token_generator
    lookup_field = settings.USER_ID_FIELD

    def permission_denied(self, request, **kwargs):
        if (
            settings.HIDE_USERS
            and request.user.is_authenticated
            and self.action in ['update', 'partial_update', 'destroy']
        ):
            raise NotFound()
        super().permission_denied(request, **kwargs)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == 'list':
            self.permission_classes = settings.PERMISSIONS.user_list
        elif self.action == 'retrieve':
            self.permission_classes = settings.PERMISSIONS.user_retrieve
        elif self.action == 'set_password':
            self.permission_classes = settings.PERMISSIONS.set_password
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return settings.SERIALIZERS.user_create
        elif self.action == 'set_password':
            return settings.SERIALIZERS.set_password
        elif (self.action == 'me' or self.action == 'list'
              or self.action == 'retrieve'):
            return settings.SERIALIZERS.user
        return self.serializer_class

    def get_instance(self):
        return self.request.user

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )
        context = {'user': user}
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            settings.EMAIL.activation(self.request, context).send(to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            settings.EMAIL.confirmation(self.request, context).send(to)

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(['post'], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {'user': self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(
                self.request,
                context
            ).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscription__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializer(
            queryset, many=True, context={
                'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        print(id, user.id, author.id)
        if request.method == 'POST':
            if user == author:
                return Response(
                    'Вы не можете подписаться сами на себя',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                    user=user, subscription=author).exists():
                return Response(
                    'Вы уже подписаны на этого пользователя',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=user, subscription=author)
            return Response(
                SubscriptionsSerializer(
                    author,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if Subscription.objects.filter(
                    user=user, subscription=author).exists():
                Subscription.objects.filter(
                    user=user, subscription=author).delete()
                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                'Вы не подписаны на этого пользователя',
                status=status.HTTP_400_BAD_REQUEST
            )


class RecipeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Recipe.objects.all()
    pagination_class = FoodGramPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny, )
        elif self.action in (
            'partial_update',
            'destroy',
            'create',
            'favorite',
            'shopping_cart',
            'download_shopping_cart'
        ):
            self.permission_classes = (IsAuthorOrAuthenticated, )
        return super().get_permissions()

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Этот рецепт уже находится в избранном',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeInFavoriteOrCartSerializer(
                    recipe,
                    context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                Favorite.objects.filter(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Этого рецепта нет в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Этот рецепт уже находится в корзине',
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(RecipeInFavoriteOrCartSerializer(
                recipe,
                context={'request': request}
            ).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Этого рецепта нет в корзине',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['get'],
        detail=False,
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientsinRecipe.objects.filter(
            recipe__shopping_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(Sum('amount'))
        buf = io.BytesIO()
        p = canvas.Canvas(buf)
        pdfmetrics.registerFont(TTFont('Arial', 'arialmt.ttf'))
        p.setFillColorRGB(0, 0, 1)
        p.rect(150, 780, 300, 30, fill=True)
        p.setFillColorRGB(255, 255, 255)
        p.setFont('Arial', 20)
        p.drawString(253, 787, 'FoodGram')
        p.setFillColorRGB(0, 0, 0)
        text = p.beginText()
        text.setTextOrigin(inch * 2 + 6, inch * 10 + 15)
        text.setFont('Arial', 16)
        for ingredient in ingredients:
            string = (ingredient['ingredient__name'] +
                      ' - ' + str(ingredient['amount__sum']) +
                      ' ' + ingredient['ingredient__measurement_unit'])
            text.textLine(string)
        p.drawText(text)
        p.showPage()
        p.save()
        buf.seek(0)
        return FileResponse(
            buf,
            as_attachment=True,
            filename='ingredients.pdf'
        )
