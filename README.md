# searcher\_bot

## Описание

**searcher\_bot** — это Telegram-бот на базе [aiogram 3.20+](https://docs.aiogram.dev/) для быстрого поиска проектов по названию и синонимам из базы PostgreSQL. Администраторы могут добавлять и удалять проекты через Telegram-меню.

---

## Возможности

* ⚡ Поиск проектов по названию и синонимам (через Telegram)
* 🛠 Админ-панель (добавление/удаление проектов)
* 📦 Асинхронная работа с PostgreSQL (через `asyncpg`)
* 🧩 Простая конфигурация через `.env`
* 🚀 Запуск в Docker или локально

---

## Требования

* Python 3.9+
* PostgreSQL (локально или в Docker)
* Docker, Docker Compose (для контейнеризации)

---

## Установка

1. **Клонирование репозитория**

   ```bash
   git clone https://github.com/your-repo/searcher_bot.git
   cd searcher_bot
   ```

2. **Создайте файл `.env`** (пример содержимого):

   ```dotenv
   BOT_TOKEN=ваш_telegram_token
   ADMIN_IDS=123456789,987654321
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=your_db
   DOCKER_MODE=true    # true — если используете docker-compose, иначе false
   ```

3. **Установка зависимостей**

   ```bash
   pip install -r requirements.txt
   ```

---

## Запуск

### Локально

```bash
python bot.py
```

### В Docker

```bash
docker-compose up --build
```

---

## Настройка базы данных

```sql
CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL
);

CREATE TABLE synonyms (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  synonym TEXT NOT NULL
);
```

---

## Переменные окружения

| Переменная          | Назначение                                       |
| ------------------- | ------------------------------------------------ |
| `BOT_TOKEN`         | Токен Telegram-бота                              |
| `ADMIN_IDS`         | ID администраторов (через запятую)               |
| `POSTGRES_USER`     | Пользователь PostgreSQL                          |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL                                |
| `POSTGRES_DB`       | Имя базы данных PostgreSQL                       |
| `DOCKER_MODE`       | true/false — использовать ли docker-контейнер БД |

---

## Логирование

Используется библиотека [loguru](https://github.com/Delgan/loguru) для вывода логов в консоль и файл (`debug.log`).

---

## Структура проекта

```
searcher_bot/
├── bot.py
├── database.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Быстрый старт для разработчика

1. Проверьте версию Python (>= 3.9)
2. Проверьте работоспособность PostgreSQL (или используйте Docker)
3. Заполните .env
4. Установите зависимости
5. Запустите бота

---

## Использование (примеры команд)

* `/start` — приветствие
* `/admin` — вход в админ-панель (только для указанных админов)
* Введите любое название проекта для поиска
* Кнопки "Добавить проект" и "Удалить проект" доступны администратору

---

## Совместимость

* **Бот полностью совместим с aiogram >= 3.20.0**
* Для фильтрации текста используйте только:

  ```python
  from aiogram import F

  @dp.message(F.text == "Добавить проект")
  async def add_project_start(...):
      ...
  ```
* Фильтры `Text` больше не поддерживаются с версии 3.20!

---

## Важно

**По просьбе заказчика любые дальнейшие коммиты, новые фичи и доработки не выкладываются в общий (публичный) доступ.
Дальнейшее развитие — только в приватных репозиториях.**

---
