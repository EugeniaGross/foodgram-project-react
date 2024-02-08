import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = (
        'Удаляет все ингредиенты и создает '
        'ингредиенты в БД из JSON документа'
    )

    def handle(self, *args, **options):
        with open('data/ingredients.json', encoding='utf-8') as file:
            ingredients_list = json.load(file)
            Ingredient.objects.all().delete()
            Ingredient.objects.bulk_create(
                Ingredient(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )
                for ingredient in ingredients_list
            )
        self.stdout.write('Записи созданы')
