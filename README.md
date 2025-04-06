![workflow](https://github.com/mvrogozov/foodgram-project-react/actions/workflows/main.yml/badge.svg)
# Проект TF-IDF.
***
Задание: Реализовать веб-приложение. В качестве интерфейса сделать страницу с формой для загрузки текстового файла, после загрузки и обработки файла отображается таблица с 50 словами с колонками:

слово
tf, сколько раз это слово встречается в тексте
idf, обратная частота документа
Вывод упорядочить по уменьшению idf.
***


## Установка.
***
Клонировать репозиторий и перейти в него в командной строке.

```
git clone git@github.com:mvrogozov/tf-idf-django.git
```
Перейти в папку infra.
```
sudo docker compose up
```
Для выполнения миграций и сбора статики выполнить:
```
./migrate
```
Переменные окружения, необходимые для запуска:

* DB_ENGINE - настройка ENGINE для БД в django.settings
* DB_HOST - имя хоста с БД
* POSTGRES_DB - имя БД
* DB_PORT - порт для БД
* POSTGRES_PASSWORD - пароль БД
* POSTGRES_USER - пользователь БД
* DJANGO_SECRET_KEY - секретный ключ для django

***
Автор:
* Рогозов Михаил