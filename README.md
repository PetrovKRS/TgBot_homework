# -- > Telegram - бот < --

### Общее описание
Бот для проверки статуса домашнего задания, с последующим уведомлением пользователя в Telegram. 
Производится опрос API сервиса учебного заведения с заданным интервалом времени, затем проверяется 
изменение статуса, если статус изменился, отправляется уведомление в telegram. Бот автоматически пишет логи
о каждом удачном/неудачном запросе.

### Основные функции
* Проверка доступности переменных окружения (.env)
* Уведомление пользователя в телеграм
* Проверка доступности API сервиса
* Проверка ответа API сервиса на валидность
* Проверка статуса ДЗ
* Логирование вышеперечисленных действий

### Подготовка проекта к запуску под Linux
  * в корне проекта создать файл .env с параметрами:
    ***
      - PRACTICUM_TOKEN= Ваш токен, полученный от API сервиса
      - TELEGRAM_TOKEN= ID Вашего telegram бота
      - TELEGRAM_CHAT_ID= ID Вашего telegram чата
    ***
  * клонируем репозиторий на пк
    ```
    git clone git@github.com:PetrovKRS/Telegram_bot_homework.git
    ```
  * переходим в рабочую папку склонированного проекта
  * разворачиваем виртуальное окружение
    ```
    python3 -m venv venv
    ```
    ```
    source venv/bin/activate
    ```
  * устанавливаем зависимости из файла requirements.txt
    ```
    pip install --upgrade pip
    ```
    ```
    pip install -r requirements.txt
    ```
  * запускаем бота
    ```
    python3 homework.py
    ```


***

### <b> Стек технологий: </b>

![Python](https://img.shields.io/badge/-Python_3.9-df?style=for-the-badge&logo=Python&labelColor=yellow&color=blue)
![Python Telegram bot](https://img.shields.io/badge/-Python_Telegram_bot-df?style=for-the-badge&logo=Telegram&labelColor=black&color=blue)
![DOTENV](https://img.shields.io/badge/-DotEnv-df?style=for-the-badge&logo=dotenv&labelColor=black&color=blue)
![GitHub](https://img.shields.io/badge/-GitHub-df?style=for-the-badge&logo=GitHub&labelColor=black&color=blue)
***
### Автор проекта: 
[![GitHub](https://img.shields.io/badge/-Андрей_Петров-df?style=for-the-badge&logo=GitHub&labelColor=black&color=blue)](https://github.com/PetrovKRS)
***