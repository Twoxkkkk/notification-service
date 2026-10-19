FROM python:3.12-slim

# Устанавливаем uv напрямую в финальный образ
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Оптимизация сборки (компиляция в байт-код)
ENV UV_COMPILE_BYTECODE=1

# Сначала копируем только файлы зависимостей для кэширования слоев Docker
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости в .venv (без самого кода проекта)
RUN uv sync --frozen --no-install-project --no-dev

# Копируем весь остальной код проекта
COPY . .

# Синхронизируем проект окончательно, чтобы uv зафиксировал структуру приложения
RUN uv sync --frozen --no-dev

# Запуск приложения через uv на последнем этапе
CMD ["uv", "run", "python", "main.py"]
