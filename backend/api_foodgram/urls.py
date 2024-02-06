from django.urls import include, path

extra_patterns = [
    path('', include('api_foodgram.tags.urls')),
    path('', include('api_foodgram.ingredients.urls')),
    path('', include('api_foodgram.users.urls')),
    path('', include('api_foodgram.recipes.urls')),
]

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(extra_patterns)),
]
