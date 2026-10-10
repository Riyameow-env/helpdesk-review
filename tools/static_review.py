"""Статический анализатор для helpdesk.py.

Ищет типовые дефекты по R1–R8 и критериям сопровождения.
Внешних зависимостей нет — только стандартная библиотека.
"""
import ast
import sys


class Review(ast.NodeVisitor):
    """Собирает замечания по исходному коду."""

    def __init__(self):
        self.issues = []

    # --- Импорты ---
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            if not self._name_used(name, node):
                self.issues.append(
                    f"L{node.lineno}: неиспользуемый импорт '{alias.name}'"
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            if not self._name_used(name, node):
                self.issues.append(
                    f"L{node.lineno}: неиспользуемый импорт "
                    f"'{node.module}.{alias.name}'"
                )
        self.generic_visit(node)

    # --- Функции ---
    def visit_FunctionDef(self, node):
        # Мутабельные дефолты
        for d in node.args.defaults:
            if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                self.issues.append(
                    f"L{node.lineno}: мутабельный аргумент по умолчанию "
                    f"в '{node.name}' — риск R7"
                )

        # Отсутствие докстринга
        if not ast.get_docstring(node):
            self.issues.append(
                f"L{node.lineno}: у функции '{node.name}' нет докстринга "
                f"— критерий сопровождения"
            )

        # Сравнение с пустой строкой без strip
        for child in ast.walk(node):
            if isinstance(child, ast.Compare):
                for op, comparator in zip(child.ops, child.comparators):
                    if isinstance(op, ast.Eq) and isinstance(comparator, ast.Constant):
                        if comparator.value == "":
                            self.issues.append(
                                f"L{child.lineno}: сравнение с пустой строкой "
                                f"без strip — риск R2/R3"
                            )

        # Деление на len(...)
        for child in ast.walk(node):
            if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Div):
                if isinstance(child.right, ast.Call):
                    func = child.right.func
                    if isinstance(func, ast.Name) and func.id == "len":
                        self.issues.append(
                            f"L{child.lineno}: деление на len(...) без проверки "
                            f"на ноль — риск R6"
                        )

        # Доступ по индексу списка tickets
        for child in ast.walk(node):
            if isinstance(child, ast.Subscript):
                value = child.value
                if isinstance(value, ast.Name) and value.id == "tickets":
                    self.issues.append(
                        f"L{child.lineno}: доступ к tickets по индексу — "
                        f"риск R5 (нужен поиск по полю id)"
                    )

        self.generic_visit(node)

    # --- Return ---
    def visit_Return(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == "tickets":
            self.issues.append(
                f"L{node.lineno}: return tickets — утечка внутреннего "
                f"списка, риск R4/R7"
            )
        self.generic_visit(node)

    # --- .copy() без глубокого копирования ---
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "copy":
            self.issues.append(
                f"L{node.lineno}: .copy() — поверхностная копия, "
                f"проверьте вложенные структуры (R7)"
            )
        self.generic_visit(node)

    # --- Вспомогательное ---
    def _name_used(self, name, node):
        """Проверяет, встречается ли имя где-то, кроме импорта."""
        tree = getattr(node, "_module_tree", None)
        if tree is None:
            return True  # без дерева не можем проверить — пропускаем
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and n.id == name:
                return True
            if isinstance(n, ast.Attribute):
                if isinstance(n.value, ast.Name) and n.value.id == name:
                    return True
        return False


def analyze(path):
    """Читает файл, строит AST, собирает замечания."""
    with open(path, encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=path)

    # Привязываем дерево к каждому узлу для проверки использования имён
    for node in ast.walk(tree):
        node._module_tree = tree

    review = Review()
    review.visit(tree)
    return review.issues


def main(argv):
    if len(argv) < 2:
        print("Использование: python tools/static_review.py <файл.py>")
        return 1

    path = argv[1]
    issues = analyze(path)

    if not issues:
        print(f"{path}: замечаний нет")
        return 0

    print(f"{path}: найдено замечаний: {len(issues)}")
    for issue in issues:
        print(f"  {issue}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))