# YaMDb

![Yamdb Workflow Status](https://github.com/aoamosova/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master&event=push)

Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории: «Книги», «Фильмы», «Музыка».
Произведению может быть присвоен жанр. Новые жанры может создавать только администратор.
Читатели оставляют к произведениям текстовые отзывы и выставляют произведению рейтинг (оценку в диапазоне от одного до десяти).
Cредняя оценка произведения высчитывается автоматически.

Аутентификация по JWT-токену

Поддерживает методы GET, POST, PUT, PATCH, DELETE

Предоставляет данные в формате JSON

Cоздан в команде из трёх человек с использованим Git в рамках учебного курса Яндекс.Практикум.

## Стек технологий
- проект написан на Python с использованием Django REST Framework
- библиотека Simple JWT - работа с JWT-токеном
- библиотека django-filter - фильтрация запросов
- базы данны - SQLite3
- автоматическое развертывание проекта - Docker, docker-compose
- система управления версиями - git
- настроен непрерывный процесс разработки, тестирования и деплоя кода на боевой сервер CI/CD

## Шаблон наполнения env-файла

```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=secretkey
```

## Запуск приложения в контейнерах

Запуск docker-compose:

```bash
docker-compose up -d
```

Выполнить миграции:

```bash
docker-compose exec web python manage.py migrate
```

Создать суперюзера:

```bash
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:

```bash
docker-compose exec web python manage.py collectstatic --no-input
```

## Заполнение базы данными

```bash
docker-compose exec web python manage.py loaddata fixtures.json
```
## Страница приложения:

```
 http://localhost/admin/
```

## Алгоритм регистрации пользователей
- Пользователь отправляет запрос с параметрами *email* и *username* на */auth/email/*.
- YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на адрес *email* .
- Пользователь отправляет запрос с параметрами *email* и *confirmation_code* на */auth/token/*, в ответе на запрос ему приходит token (JWT-токен).

## Ресурсы API YaMDb

- Ресурс AUTH: аутентификация.
- Ресурс USERS: пользователи.
- Ресурс TITLES: произведения, к которым пишут отзывы (определённый фильм, книга или песня).
- Ресурс CATEGORIES: категории (типы) произведений («Фильмы», «Книги», «Музыка»).
- Ресурс GENRES: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
- Ресурс REVIEWS: отзывы на произведения. Отзыв привязан к определённому произведению.
- Ресурс COMMENTS: комментарии к отзывам. Комментарий привязан к определённому отзыву.

## Документация (запросы для работы с API):

```
 http://localhost/redoc/
```