from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser import views
from djoser.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_foodgram.pagination import UserRecipePagination
from api_foodgram.users.serializers import (SubscriptionCreateSerializer,
                                            SubscriptionsSerializer)
from users.models import Subscription

User = get_user_model()


class UserViewSet(views.UserViewSet):
    pagination_class = UserRecipePagination

    def get_permissions(self):
        # для retrieve в djoser пермишен не прописан
        if self.action == 'retrieve':
            self.permission_classes = settings.PERMISSIONS.user_retrieve
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return settings.SERIALIZERS.user_create
        elif self.action == 'set_password':
            return settings.SERIALIZERS.set_password
        elif self.action == 'me':
            return settings.SERIALIZERS.current_user
        elif self.action == 'list':
            return settings.SERIALIZERS.user_list
        if self.action == 'retrieve':
            return settings.SERIALIZERS.user
        return self.serializer_class

    def get_queryset(self):
        return User.objects.all()

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscription__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializer(
            queryset, many=True, context={
                'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        serializer = SubscriptionCreateSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        serializer = SubscriptionCreateSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Subscription.objects.filter(
            user=user, author=author).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
