# homework_bot
python telegram bot
О проекте:
Homework_Bot - это Telegram-бот

Проект построен с использованием следующих технологий:

- Python
- requests
- python-dotenv
- pyTelegramBotAPI
- logging

Следуйте этим шагам, чтобы развернуть проект локально:

Клонируйте репозиторий:

git clone git@github.com:GoarikMkrtchyan/homework_bot.git
cd homework_bot

Создайте и активируйте виртуальное окружение:

python -m venv venv
source venv\Scripts\activate

Установите зависимости:

pip install -r requirements.txt

Создайте файл .env в корне проекта и добавьте в него следующие строки, заменив значения на ваши реальные токены и ID чата:

PRACTICUM_TOKEN=ваш_токен_практикума
TELEGRAM_TOKEN=ваш_токен_телеграм
TELEGRAM_CHAT_ID=ваш_чат_айди

Запустите скрипт:

python main.py

Проект разработан [Goarik](https://github.com/GoarikMkrtchyan).
