
"""Учебный модуль учёта заявок.

Хранение — в памяти процесса. Публичный контракт — R1–R8 из REQUIREMENTS.md.
"""

tickets = []
_next_id = 1


def reset():
    """Очищает все заявки и сбрасывает нумерацию с 1."""
    global _next_id
    tickets.clear()
    _next_id = 1


def create_ticket(user, title, tags=None):
    """Создаёт заявку со статусом open.

    user:  непустая строка, очищается strip
    title: строка длиной 1..80 после strip
    tags:  список строк или None
    Возвращает независимую копию заявки.
    Raises:
        ValueError: если user пуст или title вне диапазона 1..80.
    """
    global _next_id

    user = user.strip()
    title = title.strip()

    if not user:
        raise ValueError("user: непустой после strip")
    if not (1 <= len(title) <= 80):
        raise ValueError("title: длина после strip 1..80")

    if tags is None:
        tags = []

    ticket = {
        "id": _next_id,
        "title": title,
        "user": user,
        "status": "open",
        "tags": list(tags),
    }
    tickets.append(ticket)
    _next_id += 1

    return _copy_ticket(ticket)


def list_tickets(user):
    """Возвращает независимые копии заявок указанного пользователя.

    user сравнивается после strip. Если заявок нет — возвращает [].
    """
    user = user.strip()
    return [_copy_ticket(t) for t in tickets if t["user"] == user]


def close_ticket(ticket_id):
    """Закрывает заявку по полю id.

    Возвращает True при успехе и при повторном закрытии.
    Возвращает False, если заявки с таким id нет; состояние не меняется.
    """
    for t in tickets:
        if t["id"] == ticket_id:
            t["status"] = "closed"
            return True
    return False


def closed_share():
    """Процент закрытых заявок от 0 до 100.

    При пустом списке возвращает 0.0 (float).
    """
    if not tickets:
        return 0.0
    closed = sum(t["status"] == "closed" for t in tickets)
    return closed / len(tickets) * 100


def _copy_ticket(ticket):
    """Возвращает копию заявки с независимым списком tags."""
    copy = ticket.copy()
    copy["tags"] = list(ticket["tags"])
    return copy
