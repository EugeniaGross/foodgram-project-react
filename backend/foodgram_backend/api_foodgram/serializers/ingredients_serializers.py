from rest_framework import serializers

from ingredients.models import Ingredient


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
