# Generated by Django 3.2.16 on 2024-01-25 10:21

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0004_auto_20240124_2353'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ShoppingCard',
            new_name='ShoppingCart',
        ),
    ]
