from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api_foodgram.ingredients.views import IngredientViewSet

router = SimpleRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
