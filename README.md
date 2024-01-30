# Проект Foodgram
Foodgram - это сайт с рецептами, где любой пользователь может поделиться самыми любимыми и вкусными блюдами. Опубликованные рецепты можно добавлять и избранное, если в скором времени вы собирайтесь их приготовить, можно добавить в список покупок, а затем скачать список всх ингредиентов в необходимый момент. Так же можно подписаться на любого пользователя, рецепты которых наиболее интересны.
# На даннном этапе разработки развернуть проект можно следующим образом
1. Склонировать проект на свой компьютер
   ```
   git clone git@github.com:EugeniaGross/foodgram-project-react.git
   ```
2. Перейти в папку из корневой директории infra
   ```
   cd infra
   ```
3. Запустить оркестр контейнеров
   ```
   docker compose up
   ```
4. Cобрать и копировать статику бэкенда, выполнить миграции, наполнить базу данных ингредиентами
   ```
   docker compose exec backend python manage.py collectstatic
   ```
   ```
   docker compose exec backend cp -r /app/static/. /backend_static/static/
   ```
   ```
   docker compose exec backend python manage.py migrate
   ```
   ```
   docker compose exec backend python manage.py load_ingredients
   ```
