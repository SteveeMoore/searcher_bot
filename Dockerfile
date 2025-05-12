FROM python:3.10-slim
WORKDIR /app

# Кэширование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

CMD ["python", "bot.py"]