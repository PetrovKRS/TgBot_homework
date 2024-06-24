import datetime
import time
import pytz
import logging
import os
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import ApiAnswer, RequestException, JsonError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID').split(',')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# Отображать время и дату в логах всегда по Москве
MOSCOW_TIME = datetime.datetime.now(pytz.timezone('Europe/Moscow'))

logging.basicConfig(
    format=f'{MOSCOW_TIME.strftime("%d-%m-%Y %H:%M:%S")}, %(levelname)s, %(funcName)s, %(message)s',
    level=logging.DEBUG,
    filename='main.log'
)


def check_tokens():
    """Проверяем доступность переменных окружения."""
    tokens = (
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    )
    if not all(tokens):
        logging.critical(
            'Отсутствует одна или несколько переменных окружения! '
            'Программа остановлена!'
        )
        raise ValueError


def send_message(bot, message):
    """Отправляем сообщение в телеграм."""
    try:
        for item in TELEGRAM_CHAT_ID:
            bot.send_message(item, message)
            logging.debug(
                'Бот отправил сообщение пользователю!'
            )
    except Exception as error:
        logging.error(
            f'Сообщение пользователю не отправлено: {error}'
        )


def get_api_answer(timestamp):
    """Проверяем доступность API сервиса Практикум.Домашка."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.RequestException as error:
        raise RequestException(
            f'Ответ от API сервиса не получен: {ENDPOINT}, {params}, {error}'
        )
    if response.status_code != HTTPStatus.OK:
        raise ApiAnswer(
            f'Ошибка обращения к API сервиса! {ENDPOINT}, {params}'
        )
    try:
        return response.json()
    except requests.RequestException as error:
        raise JsonError(
            f'Ответ API сервиса нельзя интерпретировать как json! {ENDPOINT}, {params}, {error}'
        )


def check_response(response):
    """Проверяем ответ API сервиса на валидность."""
    if not isinstance(response, dict):
        raise TypeError(
            'Ответ API сервиса не словарь!'
        )
    if 'homeworks' not in response:
        raise KeyError(
            'Отсутствует ключ homeworks в ответе сервиса!'
        )
    if 'current_date' not in response:
        raise KeyError(
            'Отсутствует ключ current_date в ответе сервиса!'
        )
    if not isinstance(response['homeworks'], list):
        raise TypeError(
            'Домашние работы не в виде списка!'
        )
    return response


def parse_status(homework):
    """Проверяем статус проверки домашнего задания."""
    if not isinstance(homework, dict):
        raise TypeError(
            'homework не словарь!'
        )
    if 'homework_name' not in homework:
        raise KeyError(
            'Отсутствует ключ homework_name в ответе сервиса!'
        )
    if 'status' not in homework:
        raise KeyError(
            'Отсутствует ключ status в ответе сервиса!'
        )
    if homework['status'] not in HOMEWORK_VERDICTS:
        raise KeyError(
            f'Неожиданный статус проверки работы: {homework["status"]}'
        )
    homework_name = homework['homework_name']
    status = homework['status']
    verdict = HOMEWORK_VERDICTS[status]
    return (
        f'Изменился статус проверки работы "{homework_name}". {verdict}'
    )


def hour_checker(hour_count):
    if (
            1 < hour_count <= 4
            or 21 < hour_count < 24
    ):
        hour = 'часа'
    elif (
            hour_count == 21
            or hour_count == 1
    ):
        hour = 'час'
    else:
        hour = 'часов'
    return hour


def days_checker(day_count, days_1, days_2, day=None):
    if (
            1 < day_count <= 4
            or day_count in days_2
    ):
        day = 'дня'
    elif (
            day_count == 0
            or 5 <= day_count <= 20
    ):
        day = 'дней'
    elif day_count in days_1:
        day = 'день'
    return day


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    prev_message = ''
    iteration_hour = [i for i in range(0, 127, 18)]
    iteration_count = 0
    day_count = 0
    hour_count = 0
    send_message(
        bot,
        f'Привет, Я включился!!!'
    )

    # Генератор чисел от 1 до 101 с шагом 10
    days_1 = [i for i in range(1, 101, 10)]
    # Кортеж с начальными данными для генератора days_2
    days_2_start = (22, 23, 24)
    # Генератор списка списков [[22, 23, 24], [32, 33, 34], ... [x, x, x]]
    days_2 = [[days_2_start[i] + j for i in range(0, 3)] for j in range(0, 90, 10)]

    while True:
        if iteration_count in iteration_hour:
            hour = hour_checker(hour_count)
            day = days_checker(day_count, days_1, days_2)
            send_message(
                bot,
                f'Я работаю {day_count} {day} и {hour_count} {hour}!'
            )
            logging.debug(
                f'Я работаю {day_count} {day} и {hour_count} {hour}!'
                          )
            if iteration_count == 144:
                hour_count = 0
                iteration_count = 0
                day_count += 1
            elif iteration_count in iteration_hour:
                hour_count += 3
        response = {}
        try:
            response = get_api_answer(timestamp)
            if (
                check_response(response)
                and response['homeworks']
            ):
                message = parse_status(response['homeworks'][0])
                if prev_message != message:
                    prev_message = message
                    send_message(bot, message)
            else:
                logging.debug(
                    'Новых работ нет!'
                )
            timestamp = response['current_date']
        except Exception as error:
            if not response.get('current_date'):
                timestamp = int(time.time())
            else:
                timestamp = response['current_date']
            send_message(bot, error)
            logging.error(
                f'Сбой в работе программы: {error}'
            )
        iteration_count += 1
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
