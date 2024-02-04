import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api_foodgram.filters import RecipeFilter
from api_foodgram.mixins import UpdateModelMixin
from api_foodgram.pagination import UserRecipePagination
from api_foodgram.permissions import IsAuthorOrAuthenticated
from api_foodgram.serializers.recipe_serializers import (
    FavoriteCreateSerializer, RecipeCreateSerializer,
    RecipeInFavoriteOrCartSerializer, RecipeSerializer,
    ShoppingCartCreateSerializer)
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

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
        Favorite.objects.create(user=user, recipe=recipe)
        return Response(
            RecipeInFavoriteOrCartSerializer(
                recipe,
                context={'request': request}).data,
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
        ShoppingCart.objects.create(user=user, recipe=recipe)
        return Response(RecipeInFavoriteOrCartSerializer(
            recipe,
            context={'request': request}
        ).data,
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
            string = (ingredient['ingredient__name']
                      + ' - ' + str(ingredient['amount__sum'])
                      + ' ' + ingredient['ingredient__measurement_unit'])
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
