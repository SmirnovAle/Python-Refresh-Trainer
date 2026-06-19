import json

from sqlalchemy.orm import Session

from app.models import Exercise, ExerciseDifficulty, Topic, User, UserLevel


def seed_database(db: Session) -> None:
    if db.query(User).first():
        return

    default_user = User(name="default", level=UserLevel.BEGINNER)
    db.add(default_user)
    db.flush()

    topics_data = _topics_data()
    for topic_data in topics_data:
        exercises_data = topic_data.pop("exercises")
        topic = Topic(**topic_data)
        db.add(topic)
        db.flush()

        for exercise_data in exercises_data:
            db.add(Exercise(topic_id=topic.id, **exercise_data))

    db.commit()


def _topics_data() -> list[dict]:
    return [
        {
            "slug": "strings",
            "title": "Строки",
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 1,
            "theory_md": """# Строки в Python

Строки — неизменяемые последовательности символов.

## Полезные методы
- `split()`, `join()` — разбиение и склейка
- `strip()`, `replace()` — очистка и замена
- f-строки: `f\"{name}!\"`

## Срезы
```python
s = \"python\"
s[0:3]   # 'pyt'
s[::-1]  # 'nohtyp'
```
""",
            "exercises": _strings_exercises(),
        },
        {
            "slug": "lists",
            "title": "Списки",
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 2,
            "theory_md": """# Списки

Списки — изменяемые упорядоченные коллекции.

## Основное
- `append`, `extend`, `pop`, `insert`
- срезы возвращают новый список
- list comprehension: `[x * 2 for x in items if x > 0]`
""",
            "exercises": _lists_exercises(),
        },
        {
            "slug": "dictionaries",
            "title": "Словари",
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 3,
            "theory_md": """# Словари

Словарь хранит пары ключ-значение.

## Основное
- `dict.get(key, default)`
- `items()`, `keys()`, `values()`
- dict comprehension: `{k: v for k, v in pairs}`
""",
            "exercises": _dicts_exercises(),
        },
        {
            "slug": "comprehensions",
            "title": "Comprehensions",
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 4,
            "theory_md": """# Comprehensions

Короткий способ построить list/set/dict из итерируемого объекта.

```python
[x ** 2 for x in range(5) if x % 2]
{k: len(k) for k in [\"a\", \"bb\"]}
```
""",
            "exercises": _comprehensions_exercises(),
        },
        {
            "slug": "sets",
            "title": "Множества",
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 5,
            "theory_md": """# Множества

Неупорядоченные коллекции уникальных элементов. Скоро появятся задания.""",
            "exercises": [],
        },
        {
            "slug": "functions",
            "title": "Функции",
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 6,
            "theory_md": """# Функции

Определение функций, аргументы, `*args`, `**kwargs`. Скоро появятся задания.""",
            "exercises": [],
        },
        {
            "slug": "loops",
            "title": "Циклы",
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 7,
            "theory_md": """# Циклы

`for` и `while`, `enumerate`, `zip`. Скоро появятся задания.""",
            "exercises": [],
        },
        {
            "slug": "exceptions",
            "title": "Исключения",
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 8,
            "theory_md": """# Исключения

`try/except/finally`, собственные исключения. Скоро появятся задания.""",
            "exercises": [],
        },
        {
            "slug": "files",
            "title": "Файлы",
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 9,
            "theory_md": """# Работа с файлами

Чтение и запись текстовых файлов. Скоро появятся задания.""",
            "exercises": [],
        },
        {
            "slug": "collections",
            "title": "Collections",
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 10,
            "theory_md": """# Модуль collections

`Counter`, `defaultdict`, `deque`. Скоро появятся задания.""",
            "exercises": [],
        },
        {
            "slug": "itertools",
            "title": "itertools",
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 11,
            "theory_md": """# itertools

`groupby`, `chain`, `islice` и другие итераторы. Скоро появятся задания.""",
            "exercises": [],
        },
        {
            "slug": "pathlib",
            "title": "pathlib",
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 12,
            "theory_md": """# pathlib

Объектный API для путей. Скоро появятся задания.""",
            "exercises": [],
        },
        {
            "slug": "datetime",
            "title": "datetime",
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 13,
            "theory_md": """# datetime

`date`, `time`, `datetime`, `timedelta`. Скоро появятся задания.""",
            "exercises": [],
        },
    ]


def _strings_exercises() -> list[dict]:
    return [
        {
            "title": "Разворот строки",
            "description": "Напишите функцию `reverse_text`, которая возвращает строку в обратном порядке.",
            "starter_code": "def reverse_text(text: str) -> str:\n    pass\n",
            "hint": "Используйте срез с шагом -1.",
            "solution": "def reverse_text(text: str) -> str:\n    return text[::-1]\n",
            "function_name": "reverse_text",
            "tests_json": json.dumps(
                [
                    {"args": ["python"], "expected": "nohtyp"},
                    {"args": [""], "expected": ""},
                    {"args": ["ab"], "expected": "ba"},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 1,
        },
        {
            "title": "Подсчёт слов",
            "description": "Функция `count_words` принимает строку и возвращает количество слов (разделитель — пробел).",
            "starter_code": "def count_words(text: str) -> int:\n    pass\n",
            "hint": "Метод split() без аргументов разбивает по пробелам.",
            "solution": "def count_words(text: str) -> int:\n    text = text.strip()\n    if not text:\n        return 0\n    return len(text.split())\n",
            "function_name": "count_words",
            "tests_json": json.dumps(
                [
                    {"args": ["hello world"], "expected": 2},
                    {"args": ["  one   two  "], "expected": 2},
                    {"args": [""], "expected": 0},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 2,
        },
        {
            "title": "CamelCase в snake_case",
            "description": "Реализуйте `to_snake_case`: переводит `HelloWorld` в `hello_world`.",
            "starter_code": "def to_snake_case(text: str) -> str:\n    pass\n",
            "hint": "Пройдитесь по символам и вставляйте `_` перед заглавными буквами.",
            "solution": (
                "def to_snake_case(text: str) -> str:\n"
                "    result = []\n"
                "    for char in text:\n"
                "        if char.isupper():\n"
                "            if result:\n"
                "                result.append('_')\n"
                "            result.append(char.lower())\n"
                "        else:\n"
                "            result.append(char)\n"
                "    return ''.join(result)\n"
            ),
            "function_name": "to_snake_case",
            "tests_json": json.dumps(
                [
                    {"args": ["HelloWorld"], "expected": "hello_world"},
                    {"args": ["HTTPResponse"], "expected": "h_t_t_p_response"},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 3,
        },
        {
            "title": "Палиндром",
            "description": "Функция `is_palindrome` игнорирует регистр и пробелы.",
            "starter_code": "def is_palindrome(text: str) -> bool:\n    pass\n",
            "hint": "Очистите строку и сравните с reversed.",
            "solution": (
                "def is_palindrome(text: str) -> bool:\n"
                "    cleaned = ''.join(ch.lower() for ch in text if ch.isalnum())\n"
                "    return cleaned == cleaned[::-1]\n"
            ),
            "function_name": "is_palindrome",
            "tests_json": json.dumps(
                [
                    {"args": ["A man a plan a canal Panama"], "expected": True},
                    {"args": ["hello"], "expected": False},
                ]
            ),
            "difficulty": ExerciseDifficulty.HARD,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 4,
        },
    ]


def _lists_exercises() -> list[dict]:
    return [
        {
            "title": "Сумма списка",
            "description": "Функция `sum_list` возвращает сумму чисел в списке.",
            "starter_code": "def sum_list(items: list[int]) -> int:\n    pass\n",
            "hint": "Используйте встроенную sum().",
            "solution": "def sum_list(items: list[int]) -> int:\n    return sum(items)\n",
            "function_name": "sum_list",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 3]], "expected": 6},
                    {"args": [[]], "expected": 0},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 1,
        },
        {
            "title": "Уникальные элементы",
            "description": "Функция `unique_items` сохраняет порядок первого появления.",
            "starter_code": "def unique_items(items: list) -> list:\n    pass\n",
            "hint": "set для проверки, list для результата.",
            "solution": (
                "def unique_items(items: list) -> list:\n"
                "    seen = set()\n"
                "    result = []\n"
                "    for item in items:\n"
                "        if item not in seen:\n"
                "            seen.add(item)\n"
                "            result.append(item)\n"
                "    return result\n"
            ),
            "function_name": "unique_items",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 2, 3, 1]], "expected": [1, 2, 3]},
                    {"args": [["a", "b", "a"]], "expected": ["a", "b"]},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 2,
        },
        {
            "title": "Плоский список",
            "description": "Функция `flatten` принимает список списков и возвращает одномерный список.",
            "starter_code": "def flatten(nested: list[list]) -> list:\n    pass\n",
            "hint": "List comprehension с двумя циклами.",
            "solution": "def flatten(nested: list[list]) -> list:\n    return [item for sub in nested for item in sub]\n",
            "function_name": "flatten",
            "tests_json": json.dumps(
                [
                    {"args": [[[1, 2], [3]]], "expected": [1, 2, 3]},
                    {"args": [[[]]], "expected": []},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 3,
        },
    ]


def _dicts_exercises() -> list[dict]:
    return [
        {
            "title": "Инвертировать словарь",
            "description": "Функция `invert_dict` меняет ключи и значения местами.",
            "starter_code": "def invert_dict(data: dict) -> dict:\n    pass\n",
            "hint": "Dict comprehension: {v: k for k, v in data.items()}",
            "solution": "def invert_dict(data: dict) -> dict:\n    return {value: key for key, value in data.items()}\n",
            "function_name": "invert_dict",
            "tests_json": json.dumps(
                [
                    {"args": [{"a": "1", "b": "2"}], "expected": {"1": "a", "2": "b"}},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 1,
        },
        {
            "title": "Подсчёт частот",
            "description": "Функция `frequency_map` возвращает словарь частот символов строки.",
            "starter_code": "def frequency_map(text: str) -> dict[str, int]:\n    pass\n",
            "hint": "Пройдитесь по символам и увеличивайте счётчик.",
            "solution": (
                "def frequency_map(text: str) -> dict[str, int]:\n"
                "    result = {}\n"
                "    for char in text:\n"
                "        result[char] = result.get(char, 0) + 1\n"
                "    return result\n"
            ),
            "function_name": "frequency_map",
            "tests_json": json.dumps(
                [
                    {"args": ["aab"], "expected": {"a": 2, "b": 1}},
                    {"args": [""], "expected": {}},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 2,
        },
    ]


def _comprehensions_exercises() -> list[dict]:
    return [
        {
            "title": "Квадраты чётных",
            "description": "Функция `even_squares` возвращает квадраты чётных чисел из списка.",
            "starter_code": "def even_squares(numbers: list[int]) -> list[int]:\n    pass\n",
            "hint": "[x * x for x in numbers if x % 2 == 0]",
            "solution": "def even_squares(numbers: list[int]) -> list[int]:\n    return [x * x for x in numbers if x % 2 == 0]\n",
            "function_name": "even_squares",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 3, 4]], "expected": [4, 16]},
                    {"args": [[1, 3]], "expected": []},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 1,
        },
        {
            "title": "Длины слов",
            "description": "Функция `word_lengths` возвращает словарь {слово: длина}.",
            "starter_code": "def word_lengths(words: list[str]) -> dict[str, int]:\n    pass\n",
            "hint": "{word: len(word) for word in words}",
            "solution": "def word_lengths(words: list[str]) -> dict[str, int]:\n    return {word: len(word) for word in words}\n",
            "function_name": "word_lengths",
            "tests_json": json.dumps(
                [
                    {"args": [["hi", "hey"]], "expected": {"hi": 2, "hey": 3}},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 2,
        },
        {
            "title": "Уникальные первые буквы",
            "description": "Функция `first_letters` возвращает set первых букв слов.",
            "starter_code": "def first_letters(words: list[str]) -> set[str]:\n    pass\n",
            "hint": "{word[0] for word in words if word}",
            "solution": "def first_letters(words: list[str]) -> set[str]:\n    return {word[0] for word in words if word}\n",
            "function_name": "first_letters",
            "tests_json": json.dumps(
                [
                    {"args": [["apple", "apricot", "banana"]], "expected": ["a", "b"]},
                ]
            ),
            "difficulty": ExerciseDifficulty.HARD,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]
