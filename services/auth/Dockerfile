FROM python:3.12-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала копируем только зависимости — Docker кэширует этот слой.
# Если изменился только код (main.py), pip install не перезапустится.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Теперь копируем код
COPY . .

# Запускаем uvicorn на порту 8000 внутри контейнера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# --host 0.0.0.0 — слушать все интерфейсы, не только localhost
# --reload       — перезапускать при изменении файлов (удобно в разработке)
