import ast
import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from app.config import settings
from app.schemas import SubmitCodeResponse, TestResult

FORBIDDEN_IMPORTS = frozenset({"os", "sys", "subprocess", "socket", "shutil", "ctypes", "importlib"})
FORBIDDEN_CALLS = frozenset({"eval", "exec", "compile", "__import__", "open"})


class CodeValidationError(Exception):
    pass


def _validate_ast(source: str) -> None:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise CodeValidationError(f"Синтаксическая ошибка: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise CodeValidationError(f"Импорт '{alias.name}' запрещён")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise CodeValidationError(f"Импорт '{node.module}' запрещён")
        elif isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in FORBIDDEN_CALLS:
                raise CodeValidationError(f"Вызов '{name}' запрещён")
            if isinstance(func, ast.Attribute) and func.attr == "unlink":
                raise CodeValidationError("Вызов 'unlink' запрещён")


def _build_runner_script(user_code: str, function_name: str, tests: list[dict]) -> str:
    tests_literal = json.dumps(tests, ensure_ascii=False)
    return textwrap.dedent(
        f"""
        import json
        import traceback

        USER_CODE = {json.dumps(user_code)}

        ns = {{}}
        try:
            exec(USER_CODE, ns)
        except Exception:
            print(json.dumps({{"error": "Ошибка при загрузке кода", "traceback": traceback.format_exc()}}))
            raise SystemExit(0)

        fn = ns.get({json.dumps(function_name)})
        if fn is None or not callable(fn):
            print(json.dumps({{"error": "Функция '{function_name}' не найдена"}}))
            raise SystemExit(0)

        tests = {tests_literal}
        results = []
        stdout_parts = []

        for index, test in enumerate(tests):
            args = test.get("args", [])
            kwargs = test.get("kwargs", {{}})
            expected = test.get("expected")
            try:
                actual = fn(*args, **kwargs)
                if isinstance(actual, set) and isinstance(expected, list):
                    passed = actual == set(expected)
                else:
                    passed = actual == expected
                message = "OK" if passed else f"Ожидалось {{expected!r}}, получено {{actual!r}}"
                results.append({{"index": index, "passed": passed, "message": message}})
            except Exception as exc:
                results.append({{"index": index, "passed": False, "message": f"Исключение: {{type(exc).__name__}}: {{exc}}"}})

        print(json.dumps({{"results": results}}))
        """
    )


def run_user_code(user_code: str, function_name: str, tests_json: str) -> SubmitCodeResponse:
    _validate_ast(user_code)

    try:
        tests = json.loads(tests_json)
    except json.JSONDecodeError:
        return SubmitCodeResponse(
            success=False,
            stdout="",
            stderr="",
            tests=[],
            error="Некорректные тесты на сервере",
        )

    script = _build_runner_script(user_code, function_name, tests)

    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = Path(tmp_dir) / "runner.py"
        script_path.write_text(script, encoding="utf-8")

        try:
            completed = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=settings.code_timeout_seconds,
                cwd=tmp_dir,
            )
        except subprocess.TimeoutExpired:
            return SubmitCodeResponse(
                success=False,
                stdout="",
                stderr="",
                tests=[],
                error=f"Превышен лимит времени ({settings.code_timeout_seconds} с)",
            )

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""

    if not stdout.strip():
        return SubmitCodeResponse(
            success=False,
            stdout=stdout,
            stderr=stderr,
            tests=[],
            error=stderr.strip() or "Пустой ответ от runner",
        )

    lines = [line for line in stdout.strip().splitlines() if line.strip()]
    payload_line = lines[-1]

    try:
        payload = json.loads(payload_line)
    except json.JSONDecodeError:
        return SubmitCodeResponse(
            success=False,
            stdout=stdout,
            stderr=stderr,
            tests=[],
            error="Не удалось разобрать результат выполнения",
        )

    if "error" in payload:
        return SubmitCodeResponse(
            success=False,
            stdout=stdout,
            stderr=stderr,
            tests=[],
            error=payload["error"],
        )

    test_results = [
        TestResult(index=item["index"], passed=item["passed"], message=item["message"])
        for item in payload.get("results", [])
    ]
    success = bool(test_results) and all(item.passed for item in test_results)

    return SubmitCodeResponse(
        success=success,
        stdout=stdout,
        stderr=stderr,
        tests=test_results,
        error=None if success else "Не все тесты пройдены",
    )
