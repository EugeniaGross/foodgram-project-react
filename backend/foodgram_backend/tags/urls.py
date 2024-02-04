from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api_foodgram.views.tags_views import TagViewSet

router = SimpleRouter()

router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]
