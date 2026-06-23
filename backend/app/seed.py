import json

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Exercise, ExerciseDifficulty, Topic, User, UserLevel
from app.services.auth_service import hash_password

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
    "remove_spaces": """**`str.replace(' ', '')`** — удаляет все пробелы из строки.""",
    "starts_with_vowel": """**`text[0].lower() in 'aeiou'`** — проверка первой буквы на гласную.""",
    "max_item": """**`max(items)`** — максимум списка; проверка на пустой список перед вызовом.""",
    "chunk_pairs": """**Срез с шагом 2**: `[items[i:i+2] for i in range(0, len(items), 2)]` — пары подряд.""",
    "double_values": """**List comprehension**: `[x * 2 for x in items]` — удвоение каждого элемента.""",
    "count_matches": """**`sum(1 for x in items if x == target)`** — подсчёт совпадений без явного цикла с append.""",
    "merge_dicts": """**`{**first, **second}`** — объединение; ключи из второго словаря перезаписывают первый.""",
    "filter_positive": """**`[x for x in numbers if x > 0]`** или **`filter(lambda x: x > 0, numbers)`** — только положительные.""",
    "map_lengths": """**`map(len, words)`** — применяет `len` к каждому элементу; `list(...)` для списка.""",
    "all_even": """**`all(x % 2 == 0 for x in numbers)`** — True, если все элементы чётные; пустой список даёт True.""",
    "sort_words": """**`sorted(words)`** — новый отсортированный список, исходный не меняется.""",
    "sort_by_length": """**`sorted(words, key=len)`** — сортировка по длине строки.""",
    "swap_pair": """**Распаковка кортежа**: `a, b = pair; return (b, a)` — обмен двух значений.""",
    "parse_json_list": """**`json.loads(text)`** — строка JSON в Python-объект; для массива чисел — `sum(...)`.""",
    "dumps_sorted": """**`json.dumps(data, sort_keys=True)`** — сериализация с сортировкой ключей.""",
    "json_get_name": """**`json.loads` + `.get('name')`** — безопасное чтение поля из объекта JSON.""",
    "find_digits": """**`re.findall(r'\\d+', text)`** — все группы цифр в строке.""",
    "normalize_spaces": """**`re.sub(r'\\s+', ' ', text).strip()`** — схлопывание пробелов.""",
    "is_valid_word": """**`re.fullmatch(r'[A-Za-z]+', word)`** — проверка, что строка целиком из букв.""",
    "product_reduce": """**`functools.reduce`** — свёртка списка: `reduce(lambda a, b: a * b, numbers, 1)`.""",
    "cached_square": """**`@lru_cache`** — кеш результатов функции; повторные вызовы с тем же аргументом мгновенны.""",
    "sum_reduce": """**`functools.reduce`** с начальным значением 0: `reduce(lambda a, b: a + b, numbers, 0)`.""",
    "iso_weekday": """**`date.fromisoformat(...).isoweekday()`** — день недели: 1=понедельник, 7=воскресенье.""",
}

HINT_SIGNATURES: dict[str, str] = {
    "reverse_text": "text[::-1]",
    "count_words": "len(text.strip().split())",
    "to_snake_case": "''.join(...); char.isupper(); char.lower()",
    "is_palindrome": "''.join(ch.lower() for ch in text if ch.isalnum())",
    "remove_spaces": "text.replace(' ', '')",
    "starts_with_vowel": "text[0].lower() in 'aeiou'",
    "sum_list": "sum(items)",
    "unique_items": "set(); item not in seen",
    "flatten": "[item for sub in nested for item in sub]",
    "max_item": "max(items)",
    "chunk_pairs": "[items[i:i + 2] for i in range(0, len(items), 2)]",
    "invert_dict": "{value: key for key, value in data.items()}",
    "frequency_map": "result.get(char, 0) + 1",
    "merge_dicts": "{**first, **second}",
    "even_squares": "[x * x for x in numbers if x % 2 == 0]",
    "word_lengths": "{word: len(word) for word in words}",
    "first_letters": "{word[0] for word in words if word}",
    "sum_range": "for i in range(1, n + 1)",
    "enumerate_pairs": "enumerate(items)",
    "zip_merge": "[x + y for x, y in zip(a, b)]",
    "double_values": "[x * 2 for x in items]",
    "count_matches": "sum(1 for x in items if x == target)",
    "unique_sorted": "sorted(set(items))",
    "common_elements": "sorted(set(a) & set(b))",
    "symmetric_diff_sorted": "sorted(set(a) ^ set(b))",
    "greet": 'f"{greeting}, {name}!"',
    "sum_all": "sum(numbers)",
    "build_profile": "dict(fields)",
    "safe_divide": "try: ... except ZeroDivisionError",
    "parse_int": "try: int(text) except ValueError",
    "safe_get": "try: items[index] except IndexError",
    "count_lines": "text.splitlines()",
    "non_empty_lines": "[line.strip() for line in text.splitlines() if line.strip()]",
    "parse_key_value": "line.split('=')",
    "count_with_counter": "Counter(items)",
    "group_by_first_letter": "defaultdict(list)",
    "rotate_left": "deque(items); deque.rotate(-n)",
    "take_first": "islice(iterable, n)",
    "chain_to_list": "list(chain(a, b))",
    "pairwise_sums": "pairwise(items)",
    "path_suffix": "PurePath(path_str).suffix",
    "path_stem": "PurePath(path_str).stem",
    "join_posix_path": "PurePosixPath(*parts)",
    "parse_iso_date": "date.fromisoformat(text).isoformat()",
    "add_days_iso": "date.fromisoformat(iso_date) + timedelta(days=days)",
    "days_between_iso": "(date.fromisoformat(end) - date.fromisoformat(start)).days",
    "iso_weekday": "date.fromisoformat(iso_date).isoweekday()",
    "filter_positive": "[x for x in numbers if x > 0]",
    "map_lengths": "list(map(len, words))",
    "all_even": "all(x % 2 == 0 for x in numbers)",
    "sort_words": "sorted(words)",
    "sort_by_length": "sorted(words, key=len)",
    "swap_pair": "a, b = pair; return (b, a)",
    "parse_json_list": "sum(json.loads(text))",
    "dumps_sorted": "json.dumps(data, sort_keys=True)",
    "json_get_name": "json.loads(text).get('name')",
    "find_digits": "re.findall(r'\\d+', text)",
    "normalize_spaces": "re.sub(r'\\s+', ' ', text).strip()",
    "is_valid_word": "re.fullmatch(r'[A-Za-z]+', word)",
    "product_reduce": "reduce(lambda a, b: a * b, numbers, 1)",
    "cached_square": "@lru_cache",
    "sum_reduce": "reduce(lambda a, b: a + b, numbers, 0)",
}


def _prepare_exercise(data: dict) -> dict:
    prepared = dict(data)
    function_name = prepared["function_name"]
    prepared["solution_explanation"] = SOLUTION_EXPLANATIONS[function_name]
    prepared["hint_signature"] = HINT_SIGNATURES[function_name]
    return prepared


def sync_exercise_explanations(db: Session) -> None:
    for function_name, explanation in SOLUTION_EXPLANATIONS.items():
        exercise = db.query(Exercise).filter(Exercise.function_name == function_name).first()
        if exercise is not None:
            exercise.solution_explanation = explanation
            exercise.hint_signature = HINT_SIGNATURES[function_name]
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
                    "hint_signature",
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

    default_user = User(
        name="admin",
        email=settings.admin_email,
        password_hash=hash_password(settings.admin_password) if settings.admin_password else None,
        level=UserLevel.BEGINNER,
    )
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
        {
            "slug": "builtins",
            "title": "Встроенные функции",
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 14,
            "theory_md": """# map, filter, all

```python
list(map(len, words))
[x for x in nums if x > 0]
all(x > 0 for x in nums)
any(x == 0 for x in nums)
```
""",
            "exercises": _builtins_exercises(),
        },
        {
            "slug": "sorting",
            "title": "Сортировка и кортежи",
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 15,
            "theory_md": """# sorted и key

```python
sorted(words)
sorted(words, key=len)
a, b = pair
```

`sorted` не меняет исходный список.
""",
            "exercises": _sorting_exercises(),
        },
        {
            "slug": "json",
            "title": "JSON",
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 16,
            "theory_md": """# json

```python
import json

json.loads('{"a": 1}')
json.dumps(data, sort_keys=True)
```
""",
            "exercises": _json_exercises(),
        },
        {
            "slug": "regex",
            "title": "Регулярные выражения",
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 17,
            "theory_md": """# re

```python
import re

re.findall(r"\\d+", text)
re.sub(r"\\s+", " ", text)
re.fullmatch(r"[A-Za-z]+", word)
```
""",
            "exercises": _regex_exercises(),
        },
        {
            "slug": "functools",
            "title": "functools",
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 18,
            "theory_md": """# functools

- **`reduce(func, iterable, start)`** — свёртка списка в одно значение
- **`@lru_cache`** — мемоизация результатов функции
""",
            "exercises": _functools_exercises(),
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
        {
            "title": "Убрать пробелы",
            "description": "Функция `remove_spaces(text)` удаляет все пробелы из строки.",
            "starter_code": "def remove_spaces(text: str) -> str:\n    pass\n",
            "hint": "Метод replace(' ', '').",
            "solution": "def remove_spaces(text: str) -> str:\n    return text.replace(' ', '')\n",
            "function_name": "remove_spaces",
            "tests_json": json.dumps(
                [
                    {"args": ["a b c"], "expected": "abc"},
                    {"args": ["hello"], "expected": "hello"},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 5,
        },
        {
            "title": "Начинается с гласной",
            "description": "Функция `starts_with_vowel(text)` возвращает True, если первая буква — гласная (a,e,i,o,u).",
            "starter_code": "def starts_with_vowel(text: str) -> bool:\n    pass\n",
            "hint": "text[0].lower() in 'aeiou'",
            "solution": (
                "def starts_with_vowel(text: str) -> bool:\n"
                "    if not text:\n"
                "        return False\n"
                "    return text[0].lower() in 'aeiou'\n"
            ),
            "function_name": "starts_with_vowel",
            "tests_json": json.dumps(
                [
                    {"args": ["apple"], "expected": True},
                    {"args": ["banana"], "expected": False},
                    {"args": [""], "expected": False},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 6,
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
        {
            "title": "Максимум списка",
            "description": "Функция `max_item(items)` возвращает максимальный элемент или None для пустого списка.",
            "starter_code": "def max_item(items: list[int]) -> int | None:\n    pass\n",
            "hint": "if not items: return None; иначе max(items).",
            "solution": (
                "def max_item(items: list[int]) -> int | None:\n"
                "    if not items:\n"
                "        return None\n"
                "    return max(items)\n"
            ),
            "function_name": "max_item",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 5, 3]], "expected": 5},
                    {"args": [[]], "expected": None},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 4,
        },
        {
            "title": "Пары элементов",
            "description": "Функция `chunk_pairs(items)` разбивает список на пары: `[1,2,3,4]` → `[[1,2],[3,4]]`.",
            "starter_code": "def chunk_pairs(items: list) -> list[list]:\n    pass\n",
            "hint": "Срез items[i:i+2] в цикле range(0, len(items), 2).",
            "solution": (
                "def chunk_pairs(items: list) -> list[list]:\n"
                "    return [items[i:i + 2] for i in range(0, len(items), 2)]\n"
            ),
            "function_name": "chunk_pairs",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 3, 4]], "expected": [[1, 2], [3, 4]]},
                    {"args": [[1, 2, 3]], "expected": [[1, 2], [3]]},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 5,
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
        {
            "title": "Объединить словари",
            "description": "Функция `merge_dicts(first, second)` объединяет словари; ключи из second перезаписывают first.",
            "starter_code": "def merge_dicts(first: dict, second: dict) -> dict:\n    pass\n",
            "hint": "{**first, **second}",
            "solution": "def merge_dicts(first: dict, second: dict) -> dict:\n    return {**first, **second}\n",
            "function_name": "merge_dicts",
            "tests_json": json.dumps(
                [
                    {"args": [{"a": 1}, {"b": 2}], "expected": {"a": 1, "b": 2}},
                    {"args": [{"a": 1}, {"a": 2}], "expected": {"a": 2}},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 3,
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
        {
            "title": "Удвоить элементы",
            "description": "Функция `double_values(items)` возвращает список с удвоенными значениями.",
            "starter_code": "def double_values(items: list[int]) -> list[int]:\n    pass\n",
            "hint": "[x * 2 for x in items]",
            "solution": "def double_values(items: list[int]) -> list[int]:\n    return [x * 2 for x in items]\n",
            "function_name": "double_values",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 3]], "expected": [2, 4, 6]},
                    {"args": [[]], "expected": []},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.BEGINNER,
            "sort_order": 4,
        },
        {
            "title": "Сколько раз встретился",
            "description": "Функция `count_matches(items, target)` считает, сколько раз target встречается в списке.",
            "starter_code": "def count_matches(items: list, target) -> int:\n    pass\n",
            "hint": "sum(1 for x in items if x == target)",
            "solution": "def count_matches(items: list, target) -> int:\n    return sum(1 for x in items if x == target)\n",
            "function_name": "count_matches",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 1, 3, 1], 1], "expected": 3},
                    {"args": [["a", "b"], "x"], "expected": 0},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 5,
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
        {
            "title": "День недели ISO",
            "description": "Функция `iso_weekday(iso_date)` возвращает номер дня недели: 1=понедельник, 7=воскресенье.",
            "starter_code": "def iso_weekday(iso_date: str) -> int:\n    pass\n",
            "hint": "date.fromisoformat(iso_date).isoweekday()",
            "solution": (
                "from datetime import date\n\n"
                "def iso_weekday(iso_date: str) -> int:\n"
                "    return date.fromisoformat(iso_date).isoweekday()\n"
            ),
            "function_name": "iso_weekday",
            "tests_json": json.dumps(
                [
                    {"args": ["2024-06-03"], "expected": 1},
                    {"args": ["2024-06-09"], "expected": 7},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 4,
        },
    ]


def _builtins_exercises() -> list[dict]:
    return [
        {
            "title": "Только положительные",
            "description": "Функция `filter_positive(numbers)` возвращает список положительных чисел.",
            "starter_code": "def filter_positive(numbers: list[int]) -> list[int]:\n    pass\n",
            "hint": "[x for x in numbers if x > 0]",
            "solution": "def filter_positive(numbers: list[int]) -> list[int]:\n    return [x for x in numbers if x > 0]\n",
            "function_name": "filter_positive",
            "tests_json": json.dumps(
                [
                    {"args": [[-1, 2, 0, 3]], "expected": [2, 3]},
                    {"args": [[-5, -1]], "expected": []},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 1,
        },
        {
            "title": "Длины через map",
            "description": "Функция `map_lengths(words)` возвращает список длин слов через map().",
            "starter_code": "def map_lengths(words: list[str]) -> list[int]:\n    pass\n",
            "hint": "list(map(len, words))",
            "solution": "def map_lengths(words: list[str]) -> list[int]:\n    return list(map(len, words))\n",
            "function_name": "map_lengths",
            "tests_json": json.dumps(
                [
                    {"args": [["hi", "hey", "a"]], "expected": [2, 3, 1]},
                    {"args": [[]], "expected": []},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 2,
        },
        {
            "title": "Все чётные",
            "description": "Функция `all_even(numbers)` возвращает True, если все числа чётные.",
            "starter_code": "def all_even(numbers: list[int]) -> bool:\n    pass\n",
            "hint": "all(x % 2 == 0 for x in numbers)",
            "solution": "def all_even(numbers: list[int]) -> bool:\n    return all(x % 2 == 0 for x in numbers)\n",
            "function_name": "all_even",
            "tests_json": json.dumps(
                [
                    {"args": [[2, 4, 6]], "expected": True},
                    {"args": [[2, 3]], "expected": False},
                    {"args": [[]], "expected": True},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 3,
        },
    ]


def _sorting_exercises() -> list[dict]:
    return [
        {
            "title": "Отсортировать слова",
            "description": "Функция `sort_words(words)` возвращает новый отсортированный список слов.",
            "starter_code": "def sort_words(words: list[str]) -> list[str]:\n    pass\n",
            "hint": "sorted(words)",
            "solution": "def sort_words(words: list[str]) -> list[str]:\n    return sorted(words)\n",
            "function_name": "sort_words",
            "tests_json": json.dumps(
                [
                    {"args": [["banana", "apple", "cherry"]], "expected": ["apple", "banana", "cherry"]},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 1,
        },
        {
            "title": "Сортировка по длине",
            "description": "Функция `sort_by_length(words)` сортирует слова по длине.",
            "starter_code": "def sort_by_length(words: list[str]) -> list[str]:\n    pass\n",
            "hint": "sorted(words, key=len)",
            "solution": "def sort_by_length(words: list[str]) -> list[str]:\n    return sorted(words, key=len)\n",
            "function_name": "sort_by_length",
            "tests_json": json.dumps(
                [
                    {"args": [["aaa", "b", "cc"]], "expected": ["b", "cc", "aaa"]},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.INTERMEDIATE,
            "sort_order": 2,
        },
        {
            "title": "Поменять местами",
            "description": "Функция `swap_pair(pair)` принимает кортеж из двух элементов и возвращает их в обратном порядке.",
            "starter_code": "def swap_pair(pair: tuple) -> tuple:\n    pass\n",
            "hint": "a, b = pair; return (b, a)",
            "solution": "def swap_pair(pair: tuple) -> tuple:\n    a, b = pair\n    return (b, a)\n",
            "function_name": "swap_pair",
            "tests_json": json.dumps(
                [
                    {"args": [(1, 2)], "expected": [2, 1]},
                    {"args": [("x", "y")], "expected": ["y", "x"]},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 3,
        },
    ]


def _json_exercises() -> list[dict]:
    return [
        {
            "title": "Сумма JSON-массива",
            "description": "Функция `parse_json_list(text)` парсит JSON-массив чисел и возвращает их сумму.",
            "starter_code": "def parse_json_list(text: str) -> int:\n    pass\n",
            "hint": "sum(json.loads(text))",
            "solution": (
                "import json\n\n"
                "def parse_json_list(text: str) -> int:\n"
                "    return sum(json.loads(text))\n"
            ),
            "function_name": "parse_json_list",
            "tests_json": json.dumps(
                [
                    {"args": ["[1, 2, 3]"], "expected": 6},
                    {"args": ["[]"], "expected": 0},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 1,
        },
        {
            "title": "JSON с сортировкой ключей",
            "description": "Функция `dumps_sorted(data)` сериализует словарь в JSON с sort_keys=True.",
            "starter_code": "def dumps_sorted(data: dict) -> str:\n    pass\n",
            "hint": "json.dumps(data, sort_keys=True)",
            "solution": (
                "import json\n\n"
                "def dumps_sorted(data: dict) -> str:\n"
                "    return json.dumps(data, sort_keys=True)\n"
            ),
            "function_name": "dumps_sorted",
            "tests_json": json.dumps(
                [
                    {"args": [{"b": 2, "a": 1}], "expected": '{"a": 1, "b": 2}'},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 2,
        },
        {
            "title": "Имя из JSON",
            "description": "Функция `json_get_name(text)` парсит JSON-объект и возвращает поле `name` или None.",
            "starter_code": "def json_get_name(text: str) -> str | None:\n    pass\n",
            "hint": "json.loads(text).get('name')",
            "solution": (
                "import json\n\n"
                "def json_get_name(text: str) -> str | None:\n"
                "    return json.loads(text).get('name')\n"
            ),
            "function_name": "json_get_name",
            "tests_json": json.dumps(
                [
                    {"args": ['{"name": "Ann", "age": 30}'], "expected": "Ann"},
                    {"args": ['{"age": 30}'], "expected": None},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]


def _regex_exercises() -> list[dict]:
    return [
        {
            "title": "Найти числа",
            "description": "Функция `find_digits(text)` возвращает список групп цифр из строки.",
            "starter_code": "def find_digits(text: str) -> list[str]:\n    pass\n",
            "hint": "re.findall(r'\\d+', text)",
            "solution": (
                "import re\n\n"
                "def find_digits(text: str) -> list[str]:\n"
                "    return re.findall(r'\\d+', text)\n"
            ),
            "function_name": "find_digits",
            "tests_json": json.dumps(
                [
                    {"args": ["order 12 and 345"], "expected": ["12", "345"]},
                    {"args": ["no digits"], "expected": []},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 1,
        },
        {
            "title": "Схлопнуть пробелы",
            "description": "Функция `normalize_spaces(text)` заменяет повторяющиеся пробелы одним и убирает края.",
            "starter_code": "def normalize_spaces(text: str) -> str:\n    pass\n",
            "hint": "re.sub(r'\\s+', ' ', text).strip()",
            "solution": (
                "import re\n\n"
                "def normalize_spaces(text: str) -> str:\n"
                "    return re.sub(r'\\s+', ' ', text).strip()\n"
            ),
            "function_name": "normalize_spaces",
            "tests_json": json.dumps(
                [
                    {"args": ["  hello   world  "], "expected": "hello world"},
                    {"args": ["a\t\tb"], "expected": "a b"},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.ADVANCED,
            "sort_order": 2,
        },
        {
            "title": "Только буквы",
            "description": "Функция `is_valid_word(word)` возвращает True, если слово состоит только из латинских букв.",
            "starter_code": "def is_valid_word(word: str) -> bool:\n    pass\n",
            "hint": "re.fullmatch(r'[A-Za-z]+', word) is not None",
            "solution": (
                "import re\n\n"
                "def is_valid_word(word: str) -> bool:\n"
                "    return re.fullmatch(r'[A-Za-z]+', word) is not None\n"
            ),
            "function_name": "is_valid_word",
            "tests_json": json.dumps(
                [
                    {"args": ["Hello"], "expected": True},
                    {"args": ["Hello1"], "expected": False},
                    {"args": [""], "expected": False},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]


def _functools_exercises() -> list[dict]:
    return [
        {
            "title": "Произведение через reduce",
            "description": "Функция `product_reduce(numbers)` возвращает произведение чисел через functools.reduce.",
            "starter_code": "def product_reduce(numbers: list[int]) -> int:\n    pass\n",
            "hint": "reduce(lambda a, b: a * b, numbers, 1)",
            "solution": (
                "from functools import reduce\n\n"
                "def product_reduce(numbers: list[int]) -> int:\n"
                "    return reduce(lambda a, b: a * b, numbers, 1)\n"
            ),
            "function_name": "product_reduce",
            "tests_json": json.dumps(
                [
                    {"args": [[2, 3, 4]], "expected": 24},
                    {"args": [[]], "expected": 1},
                ]
            ),
            "difficulty": ExerciseDifficulty.MEDIUM,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 1,
        },
        {
            "title": "Кеш квадрата",
            "description": "Функция `cached_square(n)` возвращает n*n с lru_cache на внутренней функции.",
            "starter_code": "def cached_square(n: int) -> int:\n    pass\n",
            "hint": "Вложенная функция с @lru_cache.",
            "solution": (
                "from functools import lru_cache\n\n"
                "def cached_square(n: int) -> int:\n"
                "    @lru_cache\n"
                "    def _square(value: int) -> int:\n"
                "        return value * value\n"
                "    return _square(n)\n"
            ),
            "function_name": "cached_square",
            "tests_json": json.dumps(
                [
                    {"args": [5], "expected": 25},
                    {"args": [0], "expected": 0},
                ]
            ),
            "difficulty": ExerciseDifficulty.HARD,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 2,
        },
        {
            "title": "Сумма через reduce",
            "description": "Функция `sum_reduce(numbers)` возвращает сумму списка через reduce.",
            "starter_code": "def sum_reduce(numbers: list[int]) -> int:\n    pass\n",
            "hint": "reduce(lambda a, b: a + b, numbers, 0)",
            "solution": (
                "from functools import reduce\n\n"
                "def sum_reduce(numbers: list[int]) -> int:\n"
                "    return reduce(lambda a, b: a + b, numbers, 0)\n"
            ),
            "function_name": "sum_reduce",
            "tests_json": json.dumps(
                [
                    {"args": [[1, 2, 3]], "expected": 6},
                    {"args": [[]], "expected": 0},
                ]
            ),
            "difficulty": ExerciseDifficulty.EASY,
            "min_user_level": UserLevel.EXPERT,
            "sort_order": 3,
        },
    ]
