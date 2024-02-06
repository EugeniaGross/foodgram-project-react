from rest_framework import viewsets

from api_foodgram.tags.serializers import TagSerializer
from tags.models import Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
