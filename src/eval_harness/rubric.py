from __future__ import annotations

import ast


WEIGHTS = {
    "parseable": 5,
    "line_length": 6,
    "docstrings": 8,
    "no_todo": 6,
    "no_bare_except": 5,
}


def score_maintainability(
    source: str,
    config: dict[str, object] | None = None,
) -> dict[str, object]:
    """Return a transparent maintainability score for Python source."""
    config = config or {}
    max_line_length = int(config.get("max_line_length", 100))
    checks: list[dict[str, object]] = []

    def add_check(name: str, passed: bool, detail: str) -> None:
        checks.append(
            {
                "name": name,
                "passed": passed,
                "points_awarded": WEIGHTS[name] if passed else 0,
                "possible_points": WEIGHTS[name],
                "detail": detail,
            }
        )

    long_lines = [
        number
        for number, line in enumerate(source.splitlines(), start=1)
        if len(line) > max_line_length
    ]
    add_check(
        "line_length",
        not long_lines,
        (
            f"No lines exceed {max_line_length} characters."
            if not long_lines
            else f"Lines exceeding {max_line_length} characters: {long_lines}"
        ),
    )

    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        tree = None
        add_check(
            "parseable",
            False,
            f"Syntax error at line {error.lineno}: {error.msg}",
        )
    else:
        add_check("parseable", True, "Source parses as Python.")

    if tree is None:
        add_check(
            "docstrings",
            False,
            "Functions could not be inspected because parsing failed.",
        )
        add_check(
            "no_bare_except",
            False,
            "Exception handlers could not be inspected because parsing failed.",
        )
    else:
        functions = [
            node
            for node in ast.walk(tree)
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )
        ]
        missing_docstrings = [
            function.name
            for function in functions
            if not ast.get_docstring(function)
        ]
        add_check(
            "docstrings",
            not missing_docstrings,
            (
                "Every function has a docstring."
                if not missing_docstrings
                else f"Functions without docstrings: {missing_docstrings}"
            ),
        )

        bare_except_lines = [
            handler.lineno
            for handler in ast.walk(tree)
            if isinstance(handler, ast.ExceptHandler)
            and handler.type is None
        ]
        add_check(
            "no_bare_except",
            not bare_except_lines,
            (
                "No bare except clauses found."
                if not bare_except_lines
                else f"Bare except clauses on lines: {bare_except_lines}"
            ),
        )

    todo_lines = [
        number
        for number, line in enumerate(source.splitlines(), start=1)
        if "TODO" in line.upper()
    ]
    add_check(
        "no_todo",
        not todo_lines,
        (
            "No TODO markers found."
            if not todo_lines
            else f"TODO markers on lines: {todo_lines}"
        ),
    )

    return {
        "points_awarded": sum(
            int(check["points_awarded"])
            for check in checks
        ),
        "possible_points": sum(WEIGHTS.values()),
        "checks": checks,
    }