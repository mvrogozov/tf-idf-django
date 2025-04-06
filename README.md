# Проект TF-IDF.
***
Задание: Реализовать веб-приложение. В качестве интерфейса сделать страницу с формой для загрузки текстового файла, после загрузки и обработки файла отображается таблица с 50 словами с колонками:

слово
tf, сколько раз это слово встречается в тексте
idf, обратная частота документа
Вывод упорядочить по уменьшению idf.
***
## Примечания.
***
Для подсчета TF в тексте оставляются только слова определенной длины (для игнорирования предлогов).
Этот параметр можно настроить в файле settings.py - параметр ANALYZER_MIN_WORD_LENGTH.
IDF расчитывается на основе всех загруженных в базу документов.
Дополнительно в таблицу выведен параметр TF-IDF
***

## Установка.
***
Клонировать репозиторий и перейти в него в командной строке.

```
git clone git@github.com:mvrogozov/tf-idf-django.git
```
Перейти в папку infra.
Создать файл .env и заполнить его необходимыми переменными окружения(см.ниже)
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