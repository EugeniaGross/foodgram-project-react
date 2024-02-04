# Проект Foodgram
Foodgram - это сайт с рецептами, где любой пользователь может поделиться самыми любимыми и вкусными блюдами. Опубликованные рецепты можно добавлять и избранное, если в скором времени вы собирайтесь их приготовить, можно добавить в список покупок, а затем скачать список всх ингредиентов в необходимый момент. Так же можно подписаться на любого пользователя, рецепты которых наиболее интересны. Сайт - <https://foodgramrecipes.sytes.net/>
# Запуск проекта через docker compose на локальной машине
1. Склонировать проект на свой компьютер
   ```
   git clone git@github.com:EugeniaGross/foodgram-project-react.git
   ```
2. В папке foodgram_backend создать .env со следующими данными
   ```
   POSTGRES_USER = postgres # пользователь
   POSTGRES_PASSWORD = postgres # пароль
   POSTGRES_DB = postgres # имя базы данных
   DB_HOST = db # название контейнера, отвечающего за базу данных
   DB_PORT = 5432 # порт
   SEKRET_KEY = # секретный ключ Django-проекта
   DEBUG = # режим отладки (True или False)
   ALLOWED_HOSTS = [] # разрешенные хосты
   DB = django.db.backends.postgresql # используемая база данных
   ```
2. Перейти в папку из корневой директории infra
   ```
   cd infra/
   ```
3. Запустить оркестр контейнеров
   ```
   docker compose up
   ```
4. Cобрать и копировать статику бэкенда, выполнить миграции, наполнить базу данных ингредиентами
   ```
   docker compose exec backend python manage.py collectstatic

   docker compose exec backend cp -r /app/static/. /backend_static/static/

   docker compose exec backend python manage.py migrate

   docker compose exec backend python manage.py load_ingredients
   ```
# Запуск backend части
1. Склонировать проект на свой компьютер
   ```
   git clone git@github.com:EugeniaGross/foodgram-project-react.git
   ```
2. В папке foodgram_backend создать .env со следующими данными
   ```
   POSTGRES_USER = postgres # пользователь
   POSTGRES_PASSWORD = postgres # пароль
   POSTGRES_DB = postgres # имя базы данных
   DB_HOST = db # название контейнера, отвечающего за базу данных
   DB_PORT = 5432 # порт
   SEKRET_KEY = # секретный ключ Django-проекта
   DEBUG = # режим отладки (True или False)
   ALLOWED_HOSTS = [] # разрешенные хосты
   DB = django.db.backends.postgresql # используемая база данных
   ```
3. Запустить базу данных
4. Выполнить миграции, наполнить базу данных ингредиентами, запустить сервер
   ```
   python manage.py migrate

   python manage.py load_ingredients

   python manage.py runserver
   ```
# Работа с API
Не авторизованным пользователям предоставляется возможность получения списка рецептов, кокретного рецепта, списка тегов, конкретного тега, списка ингредиентов, конкретного ингредиента. <br>
Документация API: <https://foodgramrecipes.sytes.net/api/docs/>
Примеры запросов:
### https://foodgramrecipes.sytes.net/api/recipes/
```
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 4,
            "tags": [
                {
                    "id": 1,
                    "name": "Завтрак",
                    "color": "#FFFF00",
                    "slug": "breakfast"
                }
            ],
            "author": {
                "email": "grum@yandex.ru",
                "id": 3,
                "username": "grum_91",
                "first_name": "Александр",
                "last_name": "Грюм",
                "is_subscribed": false
            },
            "ingredients": [
                {
                    "id": 1036,
                    "name": "молоко 3,2%",
                    "measurement_unit": "г",
                    "amount": 150
                },
                {
                    "id": 2171,
                    "name": "ягоды",
                    "measurement_unit": "г",
                    "amount": 30
                },
                {
                    "id": 1136,
                    "name": "овсяные хлопья быстрого приготовления",
                    "measurement_unit": "г",
                    "amount": 50
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false,
            "name": "Каша овсяная",
            "image": "http://foodgramrecipes.sytes.net/media/recipes/images/image_dnQNwzi.jpeg",
            "text": "Нагреть молоко до 90 градусов. Овсянку выложить в миску и залить молоком. Накрыть крышкой. Подождать 10 минут. Открыть крышку. Насыпать ягоды.",
            "cooking_time": 20
        },
        ...
    ]
}
```
### https://foodgramrecipes.sytes.net/api/recipes/4/
```
{
    "id": 4,
    "tags": [
        {
            "id": 1,
            "name": "Завтрак",
            "color": "#FFFF00",
            "slug": "breakfast"
        }
    ],
    "author": {
        "email": "grum@yandex.ru",
        "id": 3,
        "username": "grum_91",
        "first_name": "Александр",
        "last_name": "Грюм",
        "is_subscribed": false
    },
    "ingredients": [
        {
            "id": 1036,
            "name": "молоко 3,2%",
            "measurement_unit": "г",
            "amount": 150
        },
        {
            "id": 2171,
            "name": "ягоды",
            "measurement_unit": "г",
            "amount": 30
        },
        {
            "id": 1136,
            "name": "овсяные хлопья быстрого приготовления",
            "measurement_unit": "г",
            "amount": 50
        }
    ],
    "is_favorited": false,
    "is_in_shopping_cart": false,
    "name": "Каша овсяная",
    "image": "http://foodgramrecipes.sytes.net/media/recipes/images/image_dnQNwzi.jpeg",
    "text": "Нагреть молоко до 90 градусов. Овсянку выложить в миску и залить молоком. Накрыть крышкой. Подождать 10 минут. Открыть крышку. Насыпать ягоды.",
    "cooking_time": 20
}
```
### https://foodgramrecipes.sytes.net/api/tags/
```
[
    {
        "id": 1,
        "name": "Завтрак",
        "color": "#FFFF00",
        "slug": "breakfast"
    },
    {
        "id": 2,
        "name": "Обед",
        "color": "#FF0000",
        "slug": "dinner"
    },
    {
        "id": 3,
        "name": "Ужин",
        "color": "#0000FF",
        "slug": "evening_meal"
    }
]
```
### https://foodgramrecipes.sytes.net/api/tags/1/
```
{
    "id": 1,
    "name": "Завтрак",
    "color": "#FFFF00",
    "slug": "breakfast"
}
```
### https://foodgramrecipes.sytes.net/api/ingredients/
```
[
    {
        "id": 1,
        "name": "абрикосовое варенье",
        "measurement_unit": "г"
    },
    {
        "id": 2,
        "name": "абрикосовое пюре",
        "measurement_unit": "г"
    },
    ...
]
```
### https://foodgramrecipes.sytes.net/api/ingredients/1/
```
{
    "id": 1,
    "name": "абрикосовое варенье",
    "measurement_unit": "г"
}
```
# Технологии
Django, Django restframework, React, Gunicorn, Nginx, Docker, Docker compose
# Автор бэкенда
Евгения Гросс<br>
GitHub: <https://github.com/EugeniaGross/><br>
Email: <eug.gross@yandex.ru>
