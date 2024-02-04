from django_filters import rest_framework as filter

from recipes.models import Recipe, Tag


class RecipeFilter(filter.FilterSet):
    is_favorited = filter.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filter.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filter.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        )

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_recipe__user=self.request.user)
        return queryset
