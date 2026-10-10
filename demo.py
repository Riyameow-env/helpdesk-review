"""Демонстрация работы helpdesk.py с проверками по R1–R8.

При нарушении любого требования скрипт падает с AssertionError.
"""
from helpdesk import (
    reset, create_ticket, list_tickets, close_ticket, closed_share
)

reset()

# R1: id с 1, статус open
t1 = create_ticket("anna", "Не включается компьютер")
t2 = create_ticket("boris", "Не печатает принтер")
assert t1["id"] == 1, "R1: первый id должен быть 1"
assert t2["id"] == 2, "R1: второй id должен быть 2"
assert t1["status"] == "open", "R1: статус должен быть open"

# R2/R3: strip и валидация
t3 = create_ticket("  anna  ", "  Сбой VPN  ")
assert t3["title"] == "Сбой VPN", "R2: title не очищен"
assert t3["user"] == "anna", "R3: user не очищен"

# R4: фильтр по user
anna = list_tickets("anna")
assert len(anna) == 2, "R4: у anna должно быть 2 заявки"
assert all(x["user"] == "anna" for x in anna), "R4: утечка чужих заявок"

# R5: закрытие по id
assert close_ticket(t1["id"]) is True, "R5: закрытие существующей"
assert close_ticket(t1["id"]) is True, "R5: повторное закрытие"
assert close_ticket(999) is False, "R5: отсутствующий id"

# R6: процент
share = closed_share()
assert isinstance(share, float), "R6: тип должен быть float"
assert 0.0 <= share <= 100.0, "R6: процент вне диапазона"

# R7: изоляция tags
src = ["hardware"]
t4 = create_ticket("anna", "Шум вентилятора", src)
src.append("urgent")
assert t4["tags"] == ["hardware"], "R7: входной список не скопирован"
t4["tags"].append("hack")
assert list_tickets("anna")[-1]["tags"] == ["hardware"], "R7: утечка tags"

# R8: reset
reset()
assert list_tickets("anna") == [], "R8: reset не очистил заявки"
assert create_ticket("anna", "Новая")["id"] == 1, "R8: счётчик не сброшен"

print("demo: OK — все проверки R1–R8 пройдены")