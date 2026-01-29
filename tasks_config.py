# tasks_config.py
TASKS = {
    1: {
        "title": "Задание 1",
        "key": 7360,
        "input_fields": ["code"],  # одно поле с именем "code"
        "expected": {"code": 'HELLOW_WORLD'},
        "error_message": "В доступе отказано: пароль не верный",
        "can_pass":False

    },
    2: {
    "input_fields": ["selected_id"],
    "expected": {"selected_id": "0"},
    "error_message": "Тревога! Высока опасность обнаружения.",
    "key": 1123,
    "can_pass":False,
    "SYMBOLS":[{"image": "/static/images/phone1.png", "message": "Сообщение 1", "id": "0"},
    {"image": "/static/images/phone2.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone3.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone1.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone2.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone3.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone1.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone2.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone3.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone1.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone2.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone3.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone1.png", "message": "Сообщение 1", "id": "1"},
    {"image": "/static/images/phone2.png", "message": "Сообщение 1", "id": "1"}]
    },


    3: {
        "title": "Задание 3",
        "key": 2430,
        "input_fields": [],  
        "expected": {},
        "error_message": "wrong answer",
        "can_pass":False,
    },
    4: {
        "title": "Задание 4",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "ESCAPE"},
        "error_message": "Ошибка активации. Тебуется верный код",
        "can_pass":False,
        "SYMBOLS":[{"image": "/static/images/phone1.png", "message": "Это отдел полиции. Представьтесь и назовите цель вызова.", "id": "0"},
    {"image": "/static/images/phone2.png", "message": "Здравствуйте! Вы позвонили в службу доставки “Быстрый Бит”. Оставьте сообщение после сигнала.", "id": "1"},
    {"image": "/static/images/phone3.png", "message": "Внимание: уровень доступа недостаточен. Повторите попытку с авторизацией.", "id": "1"},
    {"image": "/static/images/phone1.png", "message": "Привет! Это голосовой помощник Тим. Я сейчас в оффлайне. Оставьте координаты — я найду вас.", "id": "1"},
    {"image": "/static/images/phone2.png", "message": "Звонок отклонён. Причина: “слишком много вопросов”.", "id": "1"},
    {"image": "/static/images/phone3.png", "message": "Сигнал получен. Ожидайте подтверждения… Подтверждение не пришло. Соединение разорвано.", "id": "1"},
    {"image": "/static/images/phone1.png", "message": "Код активации: ESCAPE. Повторяю: ESCAPE. Система готова к следующему этапу.", "id": "1"},
    {"image": "/static/images/phone2.png", "message": "Ошибка 404: голос не найден. Попробуйте говорить громче или молчать умнее.", "id": "1"},
    {"image": "/static/images/phone3.png", "message": "Это автоответчик агента Морфея. Оставьте имя, уровень угрозы и цвет своей таблетки.", "id": "1"},
    {"image": "/static/images/phone1.png", "message": "Ваш звонок важен для нас! Сейчас все операторы заняты борьбой с системой. Подождите…", "id": "1"},
    {"image": "/static/images/phone2.png", "message": "Система распознала ваш голос. Доступ разрешён… Нет, шучу. Доступ запрещён.", "id": "1"},
    {"image": "/static/images/phone3.png", "message": "Тишина — тоже ответ. Но не сегодня. Сегодня — код.", "id": "1"},
    {"image": "/static/images/phone1.png", "message": "Это служба безопасности банка. На вашем счету была обнаружена подозрительная активность. Продиктуйте 6-ти значный код из СМС для...", "id": "1"},
    {"image": "/static/images/phone2.png", "message": "Голосовая почта переполнена. Удалите старые иллюзии, чтобы принять новые.", "id": "1"},
    {"image": "/static/images/phone1.png", "message": "Связь установлена. Передаю данные… Данные зашифрованы. Ключ утерян.", "id": "1"},
    {"image": "/static/images/phone2.png", "message": "Это не телефон. Это портал. Но сегодня он сломан. Звоните завтра.", "id": "1"},
    ],
    },
    5: {
        "title": "Задание 5",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "COLLISION"},
        "error_message": "Ты ошибся, но ошибки делают нас сильнее...",
        "can_pass":False,
    },
    6: {
        "title": "Задание 6",
        "key": 2430,
        "input_fields": [],  
        "expected": {},
        "error_message": "wrong answer",
        "can_pass":False,
    },
    7: {
        "title": "Задание 7",
        "key": 2430,
        "input_fields": [],  
        "expected": {},
        "error_message": "wrong answer",
        "can_pass":False,
    },
    8: {
        "title": "Задание 8",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "Обнаружен робот! Одна ошибка и ты ошибся. Человек человеку человек",
        "can_pass":False,
    },
    9: {
        "title": "Задание 9",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },
    10: {
        "title": "Задание 10",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },
    11: {
        "title": "Задание 11",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },

    12: {
        "title": "Задание 12",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },

    12: {
        "title": "Задание 12",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },

    13: {
        "title": "Задание 13",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },

    14: {
        "title": "Задание 14",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },

    15: {
        "title": "Задание 15",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },

    16: {
        "title": "Задание 16",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },


}


"""
2: {
        "title": "Задание 2",
        "key": 5666,
        "input_fields": ["part1", "part2"],  # два поля
        "expected": {"part1": "HELLO", "part2": "WORLD"},
        "error_message": "wrong answer"
    },
    3: {
        "title": "Задание 3",
        "key": 2430,
        "input_fields": [],  # без полей — автоматический переход
        "expected": {},
        "error_message": "wrong answer"
    }



    5: {
        "input_fields": ["choice"],  # обязательно — иначе success = True всегда
        "expected": {"choice": "omega"},  # значение правильной кнопки
        "error_message": "Неверный выбор. Система заблокирована на 5 секунд.",
        "can_pass": True,
        "key": "MATRIX_OMEGA"
    }
"""