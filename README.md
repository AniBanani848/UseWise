# UseWISE

UseWISE е Django уеб приложение за отдаване и наемане на вещи, които не се използват често: инструменти, къмпинг екипировка, домашни уреди и други полезни предмети. Идеята е хората да споделят достъп, вместо всеки да купува нещо, което ще ползва рядко.

Проектът е изграден като хакатон MVP с реален потребителски flow:
- регистрация, вход и профил
- публикуване и разглеждане на вещи
- заявки за наем с периоди и статуси
- директен чат между потребители
- отзиви след приключил наем

## Технологии

- Python 3.13
- Django 6
- Django Channels
- SQLite
- Django templates

## Структура

Основният код е в директорията `UseWISE/`.

Приложения:
- `accounts` - custom user model, signup, login, профил
- `items` - каталог, публикуване, детайли и отзиви
- `rentals` - заявки за наем, одобряване, отказ и табло
- `chat` - контакти, чатове и websocket съобщения

Ключови файлове:
- `UseWISE/manage.py`
- `UseWISE/UseWISE/settings.py`
- `requirements.txt`

## Стартиране локално

### 1. Създай и активирай virtual environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Инсталирай зависимостите

```bash
pip install -r requirements.txt
```

### 3. Влез в проекта и приложи миграциите

```bash
cd UseWISE
python manage.py migrate
```

### 4. Стартирай development server

```bash
python manage.py runserver
```

Отвори `http://127.0.0.1:8000`.

## Тестове

От директорията `UseWISE/`:

```bash
python manage.py test
```

## Какво работи в момента

- регистрация и вход с email
- custom user model с допълнителни полета
- редакция на профил
- добавяне на вещ
- списък и детайл на вещ
- подаване на заявка за наем
- одобряване, отказ и отказване на заявка
- директен чат между потребители
- оставяне на отзив след приключил наем

## Основни маршрути

- `/` - начална страница
- `/accounts/signup/` - регистрация
- `/accounts/login/` - вход
- `/accounts/profile/` - профил
- `/items/` - каталог
- `/items/add/` - добавяне на вещ
- `/rentals/` - табло за наеми
- `/chat/` - чатове

## Бележки за разработка

- Използва се custom user model: `accounts.User`
- Базата по подразбиране е SQLite файлът `UseWISE/db.sqlite3`
- Проектът е server-rendered и няма frontend build pipeline
- Realtime чатът минава през Django Channels и ASGI
- `DEBUG`, `SECRET_KEY` и `ALLOWED_HOSTS` могат да се подават през environment variables
