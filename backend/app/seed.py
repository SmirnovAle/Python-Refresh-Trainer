import json

from sqlalchemy.orm import Session

from app.models import Exercise, ExerciseDifficulty, Topic, User, UserLevel

SOLUTION_EXPLANATIONS: dict[str, str] = {
    "reverse_text": """**`text[::-1]`** — срез строки с шагом `-1`: символы идут с конца к началу.""",
    "count_words": """- **`strip()`** — убирает пробелы по краям.
- **`split()`** без аргументов — режет по пробелам; лишние пробелы между словами схлопываются.
- **`len(...)`** — число получившихся фрагментов.""",
    "to_snake_case": """- **`char.isupper()`** — проверка заглавной буквы.
- **`char.lower()`** — перевод символа в нижний регистр.
- **`''.join(result)`** — склеивает список символов в строку.""",
    "is_palindrome": """- **`ch.isalnum()`** — буква или цифра (пробелы и знаки отбрасываем).
- **`ch.lower()`** — сравнение без учёта регистра.
- **`(ch.lower() for ch in text if ch.isalnum())`** — generator expression: ленивый перебор символов.
- **`''.join(...)`** — собирает генератор в строку `cleaned`.
- **`cleaned[::-1]`** — строка в обратном порядке; палиндром, если равна себе.""",
    "sum_list": """**`sum(items)`** — встроенная функция: суммирует элементы итерируемого объекта.""",
    "unique_items": """- **`set()`** — множество для O(1) проверки «уже видели».
- **`item not in seen`** — элемент новый.
- **`result.append(item)`** — сохраняем порядок первого появления.""",
    "flatten": """**List comprehension с двумя `for`**: `[item for sub in nested for item in sub]` — для каждого вложенного списка перебираем элементы.""",
    "invert_dict": """**Dict comprehension**: `{value: key for key, value in data.items()}` — новый словарь с переставленными ключами и значениями.""",
    "frequency_map": """- **`dict.get(key, 0)`** — значение по ключу или 0, если ключа нет.
- Цикл по символам увеличивает счётчик без `KeyError`.""",
    "even_squares": """**List comprehension**: `[x * x for x in numbers if x % 2 == 0]` — квадрат только для чётных (`x % 2 == 0`).""",
    "word_lengths": """**Dict comprehension**: `{word: len(word) for word in words}` — ключ слово, значение — длина.""",
    "first_letters": """**Set comprehension**: `{word[0] for word in words if word}` — уникальные первые буквы; пустые строки пропускаем.""",
    "sum_range": """Цикл **`for i in range(1, n + 1)`** — перебор чисел от 1 до n включительно; накопление суммы в переменной.""",
    "enumerate_pairs": """**`enumerate(items)`** — пары `(индекс, элемент)`; list(...) собирает в список.""",
    "zip_merge": """**`zip(a, b)`** — параллельный перебор двух списков; list comprehension склеивает элементы в строки.""",
    "unique_sorted": """**`set(items)`** — уникальные элементы; **`sorted(...)`** — сортированный список.""",
    "common_elements": """**`set(a) & set(b)`** — пересечение множеств; `sorted` для предсказуемого порядка.""",
    "symmetric_diff_sorted": """**`set(a) ^ set(b)`** — симметрическая разность; элементы, которые есть только в одном из множеств.""",
    "greet": """**Параметр по умолчанию** `greeting=\"Привет\"` — если аргумент не передан, используется значение по умолчанию.""",
    "sum_all": """**`*numbers`** — произвольное число позиционных аргументов, собранных в кортеж; `sum` их суммирует.""",
    "build_profile": """**`**fields`** — именованные аргументы собираются в словарь; `dict(fields)` возвращает копию.""",
    "safe_divide": """**`try/except ZeroDivisionError`** — перехват деления на ноль; возвращаем `None` вместо падения.""",
    "parse_int": """**`try/except ValueError`** — `int(text)` падает на нечисловой строке; возвращаем `None`.""",
    "safe_get": """**`try/except IndexError`** — безопасный доступ по индексу к списку.""",
    "count_lines": """**`str.splitlines()`** — разбиение текста на строки без символов перевода строки в результате.""",
    "non_empty_lines": """**`splitlines()` + generator** — отбираем непустые строки после `strip()`.""",
    "parse_key_value": """**`str.split('=')`** — разбиение по первому `=`; проверка, что получилось ровно две части.""",
    "count_with_counter": """**`collections.Counter`** — встроенный подсчёт частот элементов; `dict(counter)` для обычного словаря.""",
    "group_by_first_letter": """**`defaultdict(list)`** — словарь со списками по умолчанию; ключ — первая буква слова.""",
    "rotate_left": """**`collections.deque`** — двусторонняя очередь; **`rotate(-n)`** сдвигает элементы влево.""",
    "take_first": """**`itertools.islice(iterable, n)`** — первые n элементов без загрузки всего итерируемого в память.""",
    "chain_to_list": """**`itertools.chain(a, b)`** — ленивое объединение итерируемых; `list(...)` материализует.""",
    "pairwise_sums": """**`itertools.pairwise`** (Python 3.10+) — пары соседних элементов; суммируем каждую пару.""",
    "path_suffix": """**`pathlib.PurePath(path_str).suffix`** — расширение файла без обращения к диску.""",
    "path_stem": """**`PurePath.stem`** — имя файла без расширения.""",
    "join_posix_path": """**`PurePosixPath(*parts)`** — склейка частей POSIX-пути; `str(...)` для строки.""",
    "parse_iso_date": """**`datetime.fromisoformat(text).date()`** — разбор ISO-даты; **`.isoformat()`** обратно в строку.""",
    "add_days_iso": """**`timedelta(days=n)`** — смещение даты; **`date + delta`** даёт новую дату.""",
    "days_between_iso": """Разность двух **`date`** через `-` даёт **`timedelta`**; **`.days`** — число суток.""",
}


def _prepare_exercise(data: dict) -> dict:
    prepared = dict(data)
    prepared["solution_explanation"] = SOLUTION_EXPLANATIONS[prepared["function_name"]]
    return prepared


def sync_exercise_explanations(db: Session) -> None:
    for function_name, explanation in SOLUTION_EXPLANATIONS.items():
        exercise = db.query(Exercise).filter(Exercise.function_name == function_name).first()
        if exercise is not None:
            exercise.solution_explanation = explanation
    db.commit()


def sync_topic_content(db: Session) -> None:
    for topic_data in _topics_data():
        data = dict(topic_data)
        exercises_data = data.pop("exercises")

        topic = db.query(Topic).filter(Topic.slug == data["slug"]).first()
        if topic is None:
            topic = Topic(**data)
            db.add(topic)
            db.flush()
        else:
            topic.title = data["title"]
            topic.theory_md = data["theory_md"]
            topic.min_user_level = data["min_user_level"]
            topic.sort_order = data["sort_order"]

        existing = {
            exercise.function_name: exercise
            for exercise in db.query(Exercise).filter(Exercise.topic_id == topic.id).all()
        }

        for exercise_data in exercises_data:
            prepared = _prepare_exercise(exercise_data)
            function_name = prepared["function_name"]
            if function_name in existing:
                exercise = existing[function_name]
                for field in (
                    "title",
                    "description",
                    "starter_code",
                    "hint",
                    "solution",
                    "tests_json",
                    "difficulty",
                    "min_user_level",
                    "sort_order",
                    "solution_explanation",
                ):
                    setattr(exercise, field, prepared[field])
            else:
                db.add(Exercise(topic_id=topic.id, **prepared))

    db.commit()


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
            db.add(Exercise(topic_id=topic.id, **_prepare_exercise(exercise_data)))

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

Неупорядоченные коллекции уникальных элементов.

## Операции
- `set(items)` — построить множество
- `a & b` — пересечение
- `a | b` — объединение
- `a ^ b` — симметрическая разность
""",
            "exercises": _sets_exercises(),
        },
        {
            "slug": "functions",
            "title": "Функции",
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 6,
            "theory_md": """# Функции

```python
def greet(name, greeting=\"Привет\"):
    return f\"{greeting}, {name}!\"

def total(*args):
    return sum(args)

def profile(**fields):
    return fields
```
""",
            "exercises": _functions_exercises(),
        },
        {
            "slug": "loops",
            "title": "Циклы",
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 7,
            "theory_md": """# Циклы

- `for item in items` — перебор
- `enumerate(items)` — индекс + элемент
- `zip(a, b)` — параллельный перебор
- `range(n)` — числа от 0 до n-1
""",
            "exercises": _loops_exercises(),
        },
        {
            "slug": "exceptions",
            "title": "Исключения",
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 8,
            "theory_md": """# Исключения

```python
try:
    risky()
except ValueError:
    handle()
except ZeroDivisionError:
    handle()
```

Перехват позволяет не падать на ожидаемых ошибках.
""",
            "exercises": _exceptions_exercises(),
        },
        {
            "slug": "files",
            "title": "Файлы",
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 9,
            "theory_md": """# Работа с текстом как с файлом

Здесь упражнения работают со **строкой-содержимым**, без реального `open()`.

- `splitlines()` — строки файла
- `strip()` — очистка краёв
- разбор строк `ключ=значение`
""",
            "exercises": _files_exercises(),
        },
        {
            "slug": "collections",
            "title": "Collections",
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 10,
            "theory_md": """# Модуль collections

- **`Counter`** — частоты элементов
- **`defaultdict(list)`** — словарь с умолчанием
- **`deque`** — очередь с rotate
""",
            "exercises": _collections_exercises(),
        },
        {
            "slug": "itertools",
            "title": "itertools",
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 11,
            "theory_md": """# itertools

- `islice(iterable, n)` — первые n элементов
- `chain(a, b)` — склеить итерируемые
- `pairwise(iterable)` — соседние пары (3.10+)
""",
            "exercises": _itertools_exercises(),
        },
        {
            "slug": "pathlib",
            "title": "pathlib",
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 12,
            "theory_md": """# pathlib

**PurePath** — работа с путями без диска.

- `.suffix` — расширение
- `.stem` — имя без расширения
- `PurePosixPath(a, b, c)` — склейка частей
""",
            "exercises": _pathlib_exercises(),
        },
        {
            "slug": "datetime",
            "title": "datetime",
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 13,
            "theory_md": """# datetime

```python
from datetime import date, timedelta

d = date.fromisoformat(\"2024-06-01\")
d + timedelta(days=7)
(d2 - d1).days
```
""",
            "exercises": _datetime_exercises(),
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


def _loops_exercises() -> list[dict]:
    return [
        {
            "title": "Сумма от 1 до n",
            "description": "Функция `sum_range(n)` возвращает сумму чисел от 1 до n включительно.",
            "starter_code": "def sum_range(n: int) -> int:\n    pass\n",
            "hint": "Цикл for и range(1, n + 1).",
            "solution": (
                "def sum_range(n: int) -> int:\n"
                "    total = 0\n"
                "    for i in range(1, n + 1):\n"
                "        total += i\n"
                "    return total\n"
            ),
            "function_name": "sum_range",
            "tests_json": json.dumps(
                [
                    {"args": [5], "expected": 15},
                    {"args": [1], "expected": 1},
                    {"args": [0], "expected": 0},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 1,
        },
        {
            "title": "Пары с индексом",
            "description": "Функция `enumerate_pairs(items)` возвращает список `[индекс, элемент]`.",
            "starter_code": "def enumerate_pairs(items: list) -> list[list]:\n    pass\n",
            "hint": "Используйте enumerate().",
            "solution": (
                "def enumerate_pairs(items: list) -> list[list]:\n"
                "    return [[index, item] for index, item in enumerate(items)]\n"
            ),
            "function_name": "enumerate_pairs",
            "tests_json": json.dumps(
                [
                    {"args": [["a", "b"]], "expected": [[0, "a"], [1, "b"]]},
                    {"args": [[]], "expected": []},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 2,
        },
        {
            "title": "Склейка через zip",
            "description": "Функция `zip_merge(a, b)` склеивает два списка строк в список `a[i]+b[i]`.",
            "starter_code": "def zip_merge(a: list[str], b: list[str]) -> list[str]:\n    pass\n",
            "hint": "zip(a, b) и list comprehension.",
            "solution": "def zip_merge(a: list[str], b: list[str]) -> list[str]:\n    return [x + y for x, y in zip(a, b)]\n",
            "function_name": "zip_merge",
            "tests_json": json.dumps(
                [
                    {"args": [["a", "b"], ["1", "2"]], "expected": ["a1", "b2"]},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 3,
        },
    ]


def _sets_exercises() -> list[dict]:
    return [
        {
            "title": "Уникальные и отсортированные",
            "description": "Функция `unique_sorted(items)` возвращает отсортированный список уникальных элементов.",
            "starter_code": "def unique_sorted(items: list) -> list:\n    pass\n",
            "hint": "sorted(set(items)).",
            "solution": "def unique_sorted(items: list) -> list:\n    return sorted(set(items))\n",
            "function_name": "unique_sorted",
            "tests_json": json.dumps(
                [
                    {"args": [[3, 1, 2, 2, 1]], "expected": [1, 2, 3]},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 1,
        },
        {
            "title": "Общие элементы",
            "description": "Функция `common_elements(a, b)` возвращает отсортированный список общих элементов.",
            "starter_code": "def common_elements(a: list, b: list) -> list:\n    pass\n",
            "hint": "set(a) & set(b).",
            "solution": "def common_elements(a: list, b: list) -> list:\n    return sorted(set(a) & set(b))\n",
            "function_name": "common_elements",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 3], [2, 3, 4]], "expected": [2, 3]},
                    {"args": [[1], [2]], "expected": []},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 2,
        },
        {
            "title": "Симметрическая разность",
            "description": "Функция `symmetric_diff_sorted(a, b)` — отсортированные элементы, которые есть только в одном списке.",
            "starter_code": "def symmetric_diff_sorted(a: list, b: list) -> list:\n    pass\n",
            "hint": "set(a) ^ set(b).",
            "solution": "def symmetric_diff_sorted(a: list, b: list) -> list:\n    return sorted(set(a) ^ set(b))\n",
            "function_name": "symmetric_diff_sorted",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 3], [3, 4]], "expected": [1, 2, 4]},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]


def _functions_exercises() -> list[dict]:
    return [
        {
            "title": "Приветствие",
            "description": "Функция `greet(name, greeting=\"Привет\")` возвращает строку `\"{greeting}, {name}!\"`.",
            "starter_code": "def greet(name: str, greeting: str = \"Привет\") -> str:\n    pass\n",
            "hint": "f-string и аргумент по умолчанию.",
            "solution": "def greet(name: str, greeting: str = \"Привет\") -> str:\n    return f\"{greeting}, {name}!\"\n",
            "function_name": "greet",
            "tests_json": json.dumps(
                [
                    {"args": ["Анна"], "expected": "Привет, Анна!"},
                    {"args": ["Bob", "Hello"], "expected": "Hello, Bob!"},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 1,
        },
        {
            "title": "Сумма произвольных аргументов",
            "description": "Функция `sum_all(*numbers)` возвращает сумму всех переданных чисел.",
            "starter_code": "def sum_all(*numbers: int) -> int:\n    pass\n",
            "hint": "*numbers собирает аргументы в кортеж.",
            "solution": "def sum_all(*numbers: int) -> int:\n    return sum(numbers)\n",
            "function_name": "sum_all",
            "tests_json": json.dumps(
                [
                    {"args": [1, 2, 3], "expected": 6},
                    {"args": [], "expected": 0},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 2,
        },
        {
            "title": "Профиль из kwargs",
            "description": "Функция `build_profile(**fields)` возвращает словарь переданных полей.",
            "starter_code": "def build_profile(**fields) -> dict:\n    pass\n",
            "hint": "**fields — именованные аргументы как словарь.",
            "solution": "def build_profile(**fields) -> dict:\n    return dict(fields)\n",
            "function_name": "build_profile",
            "tests_json": json.dumps(
                [
                    {"args": [], "kwargs": {"name": "Ann", "age": 30}, "expected": {"name": "Ann", "age": 30}},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]


def _exceptions_exercises() -> list[dict]:
    return [
        {
            "title": "Безопасное деление",
            "description": "Функция `safe_divide(a, b)` возвращает `a/b` или `None` при делении на ноль.",
            "starter_code": "def safe_divide(a: float, b: float) -> float | None:\n    pass\n",
            "hint": "try/except ZeroDivisionError.",
            "solution": (
                "def safe_divide(a: float, b: float) -> float | None:\n"
                "    try:\n"
                "        return a / b\n"
                "    except ZeroDivisionError:\n"
                "        return None\n"
            ),
            "function_name": "safe_divide",
            "tests_json": json.dumps(
                [
                    {"args": [10, 2], "expected": 5.0},
                    {"args": [1, 0], "expected": None},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 1,
        },
        {
            "title": "Безопасный int",
            "description": "Функция `parse_int(text)` возвращает int или `None`, если преобразование невозможно.",
            "starter_code": "def parse_int(text: str) -> int | None:\n    pass\n",
            "hint": "try/except ValueError вокруг int(text).",
            "solution": (
                "def parse_int(text: str) -> int | None:\n"
                "    try:\n"
                "        return int(text)\n"
                "    except ValueError:\n"
                "        return None\n"
            ),
            "function_name": "parse_int",
            "tests_json": json.dumps(
                [
                    {"args": ["42"], "expected": 42},
                    {"args": ["abc"], "expected": None},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 2,
        },
        {
            "title": "Безопасный доступ",
            "description": "Функция `safe_get(items, index)` возвращает элемент или `None` при IndexError.",
            "starter_code": "def safe_get(items: list, index: int):\n    pass\n",
            "hint": "try/except IndexError.",
            "solution": (
                "def safe_get(items: list, index: int):\n"
                "    try:\n"
                "        return items[index]\n"
                "    except IndexError:\n"
                "        return None\n"
            ),
            "function_name": "safe_get",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 3], 1], "expected": 2},
                    {"args": [[1], 5], "expected": None},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 3,
        },
    ]


def _files_exercises() -> list[dict]:
    return [
        {
            "title": "Количество строк",
            "description": "Функция `count_lines(text)` считает строки в тексте (как содержимое файла).",
            "starter_code": "def count_lines(text: str) -> int:\n    pass\n",
            "hint": "splitlines().",
            "solution": "def count_lines(text: str) -> int:\n    return len(text.splitlines())\n",
            "function_name": "count_lines",
            "tests_json": json.dumps(
                [
                    {"args": ["a\nb\nc"], "expected": 3},
                    {"args": [""], "expected": 0},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 1,
        },
        {
            "title": "Непустые строки",
            "description": "Функция `non_empty_lines(text)` возвращает список непустых строк после strip().",
            "starter_code": "def non_empty_lines(text: str) -> list[str]:\n    pass\n",
            "hint": "splitlines + фильтр после strip.",
            "solution": (
                "def non_empty_lines(text: str) -> list[str]:\n"
                "    return [line.strip() for line in text.splitlines() if line.strip()]\n"
            ),
            "function_name": "non_empty_lines",
            "tests_json": json.dumps(
                [
                    {"args": ["a\n\n b \n"], "expected": ["a", "b"]},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 2,
        },
        {
            "title": "Разбор key=value",
            "description": "Функция `parse_key_value(line)` парсит строку `key=value` в список `[key, value]` или возвращает None.",
            "starter_code": "def parse_key_value(line: str) -> list[str] | None:\n    pass\n",
            "hint": "split('=') и проверка длины.",
            "solution": (
                "def parse_key_value(line: str) -> list[str] | None:\n"
                "    parts = line.split('=')\n"
                "    if len(parts) != 2:\n"
                "        return None\n"
                "    return [parts[0], parts[1]]\n"
            ),
            "function_name": "parse_key_value",
            "tests_json": json.dumps(
                [
                    {"args": ["name=Ann"], "expected": ["name", "Ann"]},
                    {"args": ["bad"], "expected": None},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]


def _collections_exercises() -> list[dict]:
    return [
        {
            "title": "Counter",
            "description": "Функция `count_with_counter(items)` возвращает словарь частот через Counter.",
            "starter_code": "def count_with_counter(items: list) -> dict:\n    pass\n",
            "hint": "from collections import Counter",
            "solution": (
                "from collections import Counter\n\n"
                "def count_with_counter(items: list) -> dict:\n"
                "    return dict(Counter(items))\n"
            ),
            "function_name": "count_with_counter",
            "tests_json": json.dumps(
                [
                    {"args": [["a", "b", "a"]], "expected": {"a": 2, "b": 1}},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 1,
        },
        {
            "title": "Группировка по первой букве",
            "description": "Функция `group_by_first_letter(words)` группирует слова по первой букве.",
            "starter_code": "def group_by_first_letter(words: list[str]) -> dict[str, list[str]]:\n    pass\n",
            "hint": "defaultdict(list).",
            "solution": (
                "from collections import defaultdict\n\n"
                "def group_by_first_letter(words: list[str]) -> dict[str, list[str]]:\n"
                "    groups = defaultdict(list)\n"
                "    for word in words:\n"
                "        groups[word[0]].append(word)\n"
                "    return dict(groups)\n"
            ),
            "function_name": "group_by_first_letter",
            "tests_json": json.dumps(
                [
                    {"args": [["ant", "axe", "boy"]], "expected": {"a": ["ant", "axe"], "b": ["boy"]}},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 2,
        },
        {
            "title": "Сдвиг влево",
            "description": "Функция `rotate_left(items, n)` сдвигает список влево на n позиций.",
            "starter_code": "def rotate_left(items: list, n: int) -> list:\n    pass\n",
            "hint": "collections.deque и rotate(-n).",
            "solution": (
                "from collections import deque\n\n"
                "def rotate_left(items: list, n: int) -> list:\n"
                "    d = deque(items)\n"
                "    d.rotate(-n)\n"
                "    return list(d)\n"
            ),
            "function_name": "rotate_left",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 3, 4], 1], "expected": [2, 3, 4, 1]},
                    {"args": [[1, 2, 3], 0], "expected": [1, 2, 3]},
                ]
            ),
            "difficulty": ExerciseDifficulty.HARD,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]


def _itertools_exercises() -> list[dict]:
    return [
        {
            "title": "Первые n элементов",
            "description": "Функция `take_first(n, iterable)` возвращает список первых n элементов.",
            "starter_code": "def take_first(n: int, iterable) -> list:\n    pass\n",
            "hint": "itertools.islice.",
            "solution": (
                "from itertools import islice\n\n"
                "def take_first(n: int, iterable) -> list:\n"
                "    return list(islice(iterable, n))\n"
            ),
            "function_name": "take_first",
            "tests_json": json.dumps(
                [
                    {"args": [2, [10, 20, 30]], "expected": [10, 20]},
                    {"args": [0, [1, 2]], "expected": []},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 1,
        },
        {
            "title": "Склеить списки",
            "description": "Функция `chain_to_list(a, b)` объединяет два списка через itertools.chain.",
            "starter_code": "def chain_to_list(a: list, b: list) -> list:\n    pass\n",
            "hint": "from itertools import chain",
            "solution": (
                "from itertools import chain\n\n"
                "def chain_to_list(a: list, b: list) -> list:\n"
                "    return list(chain(a, b))\n"
            ),
            "function_name": "chain_to_list",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2], [3]], "expected": [1, 2, 3]},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 2,
        },
        {
            "title": "Суммы соседей",
            "description": "Функция `pairwise_sums(numbers)` возвращает суммы каждой пары соседних элементов.",
            "starter_code": "def pairwise_sums(numbers: list[int]) -> list[int]:\n    pass\n",
            "hint": "itertools.pairwise (Python 3.10+).",
            "solution": (
                "from itertools import pairwise\n\n"
                "def pairwise_sums(numbers: list[int]) -> list[int]:\n"
                "    return [a + b for a, b in pairwise(numbers)]\n"
            ),
            "function_name": "pairwise_sums",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 3, 4]], "expected": [3, 5, 7]},
                    {"args": [[5]], "expected": []},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]


def _pathlib_exercises() -> list[dict]:
    return [
        {
            "title": "Расширение файла",
            "description": "Функция `path_suffix(path_str)` возвращает расширение пути (с точкой).",
            "starter_code": "def path_suffix(path_str: str) -> str:\n    pass\n",
            "hint": "PurePath(path_str).suffix",
            "solution": (
                "from pathlib import PurePath\n\n"
                "def path_suffix(path_str: str) -> str:\n"
                "    return PurePath(path_str).suffix\n"
            ),
            "function_name": "path_suffix",
            "tests_json": json.dumps(
                [
                    {"args": ["/tmp/data.csv"], "expected": ".csv"},
                    {"args": ["readme"], "expected": ""},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 1,
        },
        {
            "title": "Имя без расширения",
            "description": "Функция `path_stem(path_str)` возвращает имя файла без расширения.",
            "starter_code": "def path_stem(path_str: str) -> str:\n    pass\n",
            "hint": "PurePath.stem",
            "solution": (
                "from pathlib import PurePath\n\n"
                "def path_stem(path_str: str) -> str:\n"
                "    return PurePath(path_str).stem\n"
            ),
            "function_name": "path_stem",
            "tests_json": json.dumps(
                [
                    {"args": ["/tmp/report.final.pdf"], "expected": "report.final"},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 2,
        },
        {
            "title": "POSIX-путь",
            "description": "Функция `join_posix_path(*parts)` склеивает части в POSIX-путь.",
            "starter_code": "def join_posix_path(*parts: str) -> str:\n    pass\n",
            "hint": "PurePosixPath(*parts)",
            "solution": (
                "from pathlib import PurePosixPath\n\n"
                "def join_posix_path(*parts: str) -> str:\n"
                "    return str(PurePosixPath(*parts))\n"
            ),
            "function_name": "join_posix_path",
            "tests_json": json.dumps(
                [
                    {"args": ["home", "user", "file.txt"], "expected": "home/user/file.txt"},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]


def _datetime_exercises() -> list[dict]:
    return [
        {
            "title": "Разбор ISO-даты",
            "description": "Функция `parse_iso_date(text)` принимает `YYYY-MM-DD` и возвращает ту же строку (проверка парсинга).",
            "starter_code": "def parse_iso_date(text: str) -> str:\n    pass\n",
            "hint": "date.fromisoformat(text).isoformat()",
            "solution": (
                "from datetime import date\n\n"
                "def parse_iso_date(text: str) -> str:\n"
                "    return date.fromisoformat(text).isoformat()\n"
            ),
            "function_name": "parse_iso_date",
            "tests_json": json.dumps(
                [
                    {"args": ["2024-06-01"], "expected": "2024-06-01"},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 1,
        },
        {
            "title": "Прибавить дни",
            "description": "Функция `add_days_iso(iso_date, days)` возвращает ISO-дату через days суток.",
            "starter_code": "def add_days_iso(iso_date: str, days: int) -> str:\n    pass\n",
            "hint": "timedelta(days=days)",
            "solution": (
                "from datetime import date, timedelta\n\n"
                "def add_days_iso(iso_date: str, days: int) -> str:\n"
                "    start = date.fromisoformat(iso_date)\n"
                "    return (start + timedelta(days=days)).isoformat()\n"
            ),
            "function_name": "add_days_iso",
            "tests_json": json.dumps(
                [
                    {"args": ["2024-06-01", 10], "expected": "2024-06-11"},
                    {"args": ["2024-12-25", 7], "expected": "2025-01-01"},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 2,
        },
        {
            "title": "Дней между датами",
            "description": "Функция `days_between_iso(start, end)` возвращает число суток между датами.",
            "starter_code": "def days_between_iso(start: str, end: str) -> int:\n    pass\n",
            "hint": "(end_date - start_date).days",
            "solution": (
                "from datetime import date\n\n"
                "def days_between_iso(start: str, end: str) -> int:\n"
                "    start_date = date.fromisoformat(start)\n"
                "    end_date = date.fromisoformat(end)\n"
                "    return (end_date - start_date).days\n"
            ),
            "function_name": "days_between_iso",
            "tests_json": json.dumps(
                [
                    {"args": ["2024-01-01", "2024-01-11"], "expected": 10},
                    {"args": ["2024-06-01", "2024-06-01"], "expected": 0},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]
