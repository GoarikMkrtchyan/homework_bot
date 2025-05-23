import logging
import os
import time
from contextlib import suppress

import requests
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.apihelper import ApiException

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# Настройка логирования
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s, %(levelname)s, %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(tokens)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug(f'Бот отправил сообщение: "{message}"')
    except ApiException as error:
        logging.error(f'Ошибка при отправке сообщения в Telegram: {error}')
        raise


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        )
        if response.status_code != requests.codes.ok:
            logging.error(
                f'API вернул неожиданный статус: {response.status_code}')
            raise requests.RequestException(
                f'API вернул неожиданный статус: {response.status_code}')
        return response.json()
    except requests.RequestException as error:
        logging.error(f'Сбой при запросе к эндпоинту: {error}')
        raise RuntimeError(f'Ошибка при запросе к API: {error}') from error
    except ValueError as json_error:
        logging.error(f'Ошибка декодирования JSON: {json_error}')
        raise requests.RequestException(
            f'Ошибка декодирования JSON: {json_error}')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарем')
    if 'homeworks' not in response or 'current_date' not in response:
        raise KeyError('Отсутствуют ожидаемые ключи в ответе API')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Поле homeworks не является списком')
    if not isinstance(response['current_date'], (int, float)):
        raise TypeError('Поле current_date не является числом')
    return response['homeworks']


def parse_status(homework):
    """Извлекает статус работы из информации о домашней работе."""
    if 'status' not in homework or 'homework_name' not in homework:
        raise KeyError(
            'Отсутствуют ожидаемые ключи в ответе о домашней работе')
    status = homework['status']
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус работы: {status}')
    return (f'Изменился статус проверки работы'
            f' "{homework["homework_name"]}". {HOMEWORK_VERDICTS[status]}')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Отсутствует обязательная переменная окружения')
        exit('Отсутствует обязательная переменная окружения.')

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_statuses = {}

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                for homework in homeworks:
                    id = homework['id']
                    new = homework['status']
                    if id not in last_statuses or last_statuses[id] != new:
                        status_message = parse_status(homework)
                        send_message(bot, status_message)
                        last_statuses[id] = new
            else:
                logging.debug('Нет новых домашних работ')
            timestamp = response.get('current_date', timestamp)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            with suppress(Exception):
                send_message(bot, message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
