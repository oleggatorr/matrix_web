# tasks_config.py
TASKS = {
    1: {
        "title": "Задание 1",
        "key": 7360,
        "input_fields": ["code"],  # одно поле с именем "code"
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False

    },
    2: {
    "input_fields": ["selected_id"],
    "expected": {"selected_id": "0"},
    "error_message": "Тревога! Неправильная кнопка.",
    "key": 1123,
    "can_pass":False
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
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },
    5: {
        "title": "Задание 5",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
        "error_message": "wrong answer",
        "can_pass":False,
    },
    6: {
        "title": "Задание 6",
        "key": 2430,
        "input_fields": ["code"],  
        "expected": {"code": "12345"},
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
        "error_message": "wrong answer",
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