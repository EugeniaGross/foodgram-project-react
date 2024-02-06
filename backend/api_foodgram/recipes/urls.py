from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api_foodgram.recipes.views import RecipeViewSet

router = SimpleRouter()

router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
