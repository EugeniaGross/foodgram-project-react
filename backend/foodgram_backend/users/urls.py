from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api_foodgram.views.users_views import UserViewSet

router = SimpleRouter()

router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
