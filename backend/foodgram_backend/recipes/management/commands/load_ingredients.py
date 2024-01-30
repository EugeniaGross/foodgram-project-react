import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Создает ингредиенты в БД из JSON документа'

    def handle(self, *args, **options):
        with open('data/ingredients.json', encoding='utf-8') as file:
            ingredients_list = json.load(file)
            for ingredient in ingredients_list:
                Ingredient.objects.create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit'])
        self.stdout.write('Записи созданы')
