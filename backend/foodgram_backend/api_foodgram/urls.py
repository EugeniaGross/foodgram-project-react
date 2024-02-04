from django.urls import include, path

extra_patterns = [
    path('', include('tags.urls')),
    path('', include('ingredients.urls')),
    path('', include('users.urls')),
    path('', include('recipes.urls')),
]

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('re/', include('rest_framework.urls')),
    path('', include(extra_patterns)),
]
