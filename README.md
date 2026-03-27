# UseWise
Проект- Hack tues 12
ME.md
# UseWise
Проект- Hack tues 12
# UseWISE

UseWISE е Django уеб приложение за отдаване и наемане на вещи, които не се използват често, като инструменти, къмпинг екипировка и домашни уреди.

Проектът е започнат като хакатон MVP и в момента включва:
- регистрация, вход и профил на потребители
- публикуване и разглеждане на вещи
- заявки за наем с периоди и статуси
- директен чат между потребители



Cancel
Comment
## Технологии

- Python 3.13
- Django 6
- Django Channels
- SQLite
- Server-rendered Django templates

## Структура

Основният код е в [`UseWISE/`](/Users/dimitar.sariiski/Desktop/sasss-stuff/UseWise/UseWISE).

Приложения:
- `accounts` - custom user model, signup, login, профил
- `items` - вещи, публикуване, списък и детайли
- `rentals` - заявки за наем, одобряване, отказ, табло
- `chat` - контакти, чатове и websocket съобщения

Ключови файлове:
- [`UseWISE/manage.py`](/Users/dimitar.sariiski/Desktop/sasss-stuff/UseWise/UseWISE/manage.py)
- [`UseWISE/UseWISE/settings.py`](/Users/dimitar.sariiski/Desktop/sasss-stuff/UseWise/UseWISE/UseWISE/settings.py)
- [`requirements.txt`](/Users/dimitar.sariiski/Desktop/sasss-stuff/UseWise/requirements.txt)

## Стартиране локално

### 1. Влез в директорията

```bash
cd /Users/dimitar.sariiski/Desktop/sasss-stuff/UseWise
```

### 2. Активирай virtual environment

Ако вече имаш `.venv`:

```bash
source .venv/bin/activate
```

Ако нямаш:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Инсталирай зависимостите

```bash
pip install -r requirements.txt
```

Забележка: в момента `requirements.txt` изглежда по-широк от нуждите на проекта и вероятно съдържа пакети, които не се използват директно от приложението.

### 4. Приложи миграциите

```bash
python UseWISE/manage.py migrate
```

### 5. Стартирай development server

```bash
python UseWISE/manage.py runserver
```

После отвори:

- [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Тестове

За да пуснеш тестовете:

```bash
python UseWISE/manage.py test
```

Важно: в текущото състояние на локалната среда тестовете не тръгват, ако Django не е инсталиран във `.venv`.

## Какво работи в момента

- регистрация и вход с email
- custom user model с допълнителни полета
- редакция на профил
- добавяне на вещ
- списък и детайл на вещ
- подаване на заявка за наем
- одобряване, отказ и отказване на заявка
- директен чат между потребители

## Какво още е в ранен етап

- README и developer onboarding все още се доизчистват
- production конфигурацията не е готова
- `SECRET_KEY` и `DEBUG` са в settings файла и трябва да се изнесат в environment variables
- няма достатъчно тестове за `items`
- UI е MVP и е основно с inline/template стилове

## Основни маршрути

- `/` - начална страница
- `/accounts/signup/` - регистрация
- `/accounts/login/` - вход
- `/accounts/profile/` - профил
- `/items/` - всички вещи
- `/items/add/` - добавяне на вещ
- `/rentals/` - табло за наеми
- `/chat/` - чатове

## Бележки за разработка

- Използва се custom user model: `accounts.User`
- Базата по подразбиране е SQLite файлът [`UseWISE/db.sqlite3`](/Users/dimitar.sariiski/Desktop/sasss-stuff/UseWise/UseWISE/db.sqlite3)
- Проектът е server-rendered и няма frontend build pipeline
- Realtime чатът минава през Django Channels и ASGI

## Следващи добри стъпки

- да се изчисти `requirements.txt`
- да се добавят още тестове за `items` и integration flow-ове
- да се въведе env-based configuration
- да се подобри UX на каталога и детайла на вещите
- да се доразвие rental lifecycle