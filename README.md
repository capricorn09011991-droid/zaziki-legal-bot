# ZAZIKI Legal Bot — Инструкция по запуску

## Файлы проекта
- `bot.py` — основной код бота
- `requirements.txt` — зависимости
- `Procfile` — инструкция для Railway

## Деплой на Railway

### 1. Создай репозиторий на GitHub
- Зайди на github.com
- Нажми "New repository"
- Назови `zaziki-legal-bot`
- Нажми "Create repository"

### 2. Загрузи файлы
- Нажми "uploading an existing file"
- Перетащи все 3 файла: bot.py, requirements.txt, Procfile
- Нажми "Commit changes"

### 3. Подключи к Railway
- Зайди на railway.app
- "New Project" → "GitHub Repository"
- Выбери `zaziki-legal-bot`

### 4. Добавь переменные окружения
В Railway → твой проект → Variables → добавь:

| Переменная | Значение |
|-----------|---------|
| TELEGRAM_TOKEN | токен от @BotFather |
| ANTHROPIC_API_KEY | твой Claude API ключ (sk-ant-...) |

### 5. Запусти
Railway автоматически установит зависимости и запустит бота.

## Что умеет бот
- Принимает PDF и Word документы
- Анализирует договоры: риски, проблемные пункты, рекомендации
- Отвечает на юридические вопросы текстом
- Работает в групповом чате и личке
