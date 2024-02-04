from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

from foodgram_backend.constants import MAX_LENGTH_USER


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=MAX_LENGTH_USER)
    last_name = models.CharField(_('last name'), max_length=MAX_LENGTH_USER)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.CheckConstraint(
                check=~Q(username__iexact='me'),
                name='not_me'
            )
        ]

    def clean(self):
        if (self.username == 'me'
                or self.username == 'Me'
                or self.username == 'ME'
                or self.username == 'mE'):
            raise ValidationError(
                {
                    'username': _('Нельзя использовать me')
                }
            )


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='user'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписка',
        related_name='subscription'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                name='not_same',
                check=~Q(user=F('author'))
            )
        ]

    def clean(self):
        if self.author == self.user:
            raise ValidationError(
                {
                    'author': _(
                        'Пользователь не может подписаться сам на себя'
                    )
                }
            )
