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
        # retrieve должен быть доступен всем, при изменении перимишена
        # user на AllowAny открылся доступ для всех к me
        if self.action == 'me':
            self.permission_classes = settings.PERMISSIONS.current_user
        return super().get_permissions()

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
