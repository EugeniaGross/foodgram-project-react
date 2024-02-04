from django.shortcuts import get_object_or_404
from djoser import views
from djoser.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_foodgram.pagination import UserRecipePagination
from api_foodgram.serializers.users_serializers import (
    SubscriptionCreateSerializer, SubscriptionsSerializer)
from users.models import Subscription, User


class UserViewSet(views.UserViewSet):
    pagination_class = UserRecipePagination

    def permission_denied(self, request, **kwargs):
        if (
            settings.HIDE_USERS
            and request.user.is_authenticated
            and self.action in [
                'update',
                'partial_update',
                'destroy'
            ]
        ):
            raise NotFound()
        super().permission_denied(request, **kwargs)

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = settings.PERMISSIONS.user_retrieve
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return settings.SERIALIZERS.user_create
        if self.action == 'set_password':
            return settings.SERIALIZERS.set_password
        elif (self.action == 'me' or self.action == 'list'
              or self.action == 'retrieve'):
            return settings.SERIALIZERS.user
        return self.serializer_class

    def get_queryset(self):
        return User.objects.all()

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

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
        Subscription.objects.create(user=user, author=author)
        return Response(
            SubscriptionsSerializer(
                author,
                context={'request': request}
            ).data,
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
