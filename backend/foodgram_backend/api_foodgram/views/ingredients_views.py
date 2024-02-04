from rest_framework import filters, viewsets

from api_foodgram.serializers.ingredients_serializers import \
    IngredientsSerializer
from ingredients.models import Ingredient


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )
