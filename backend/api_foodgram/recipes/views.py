from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_foodgram.filters import RecipeFilter
from api_foodgram.mixins import UpdateModelMixin
from api_foodgram.pagination import UserRecipePagination
from api_foodgram.permissions import IsAuthorOrReadOnly
from api_foodgram.recipes.serializers import (FavoriteCreateSerializer,
                                              RecipeCreateSerializer,
                                              RecipeSerializer,
                                              ShoppingCartCreateSerializer)
from api_foodgram.utils import get_pdf
from recipes.models import Favorite, IngredientsinRecipe, Recipe, ShoppingCart


class RecipeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Recipe.objects.all()
    pagination_class = UserRecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        methods=['post'],
        detail=True,
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteCreateSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request, 'ending': 'избранном'}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteCreateSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request, 'ending': 'избранном'}
        )
        serializer.is_valid(raise_exception=True)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post'],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShoppingCartCreateSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request, 'ending': 'корзине'}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShoppingCartCreateSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request, 'ending': 'корзине'}
        )
        serializer.is_valid(raise_exception=True)
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientsinRecipe.objects.filter(
            recipe__shopping_recipes__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(Sum('amount'))
        return FileResponse(
            get_pdf(ingredients),
            as_attachment=True,
            filename='ingredients.pdf'
        )
