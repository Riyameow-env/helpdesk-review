# Карта проекта «Учёт заявок»

## 1. Структура файлов

| Файл | Назначение |
|---|---|
| `README.md` | Инструкция по практике, порядок 4 дней |
| `REQUIREMENTS.md` | Контракт R1–R8 и критерии сопровождения |
| `helpdesk.py` | Модуль учёта заявок (содержит дефекты) |
| `demo.py` | Демонстрационный запуск |
| `test_smoke.py` | Минимальный smoke-тест |
| `MAP.md` | Карта проекта (этот файл) |

## 2. Публичный API helpdesk.py

| Функция | Аргументы (факт) | Аргументы (по контракту) | Возвращает | Назначение |
|---|---|---|---|---|
| `reset()` | — | — | None | Очищает заявки, сбрасывает нумерацию |
| `create_ticket` | `title, user, tags=[]` | `user, title, tags=None` | dict | Создаёт заявку |
| `list_tickets` | `user` (позиц., обяз.) | `user` | list[dict] | Возвращает заявки пользователя |
| `close_ticket` | `ticket_id` (позиц., обяз.) | `id` | bool | Закрывает заявку по id |
| `closed_share()` | — | — | float | Процент закрытых заявок |

## 3. Внутреннее состояние (не публичное по R8)

| Переменная | Тип | Назначение |
|---|---|---|
| `tickets` | list[dict] | Список всех заявок |
| `next_id` | int | Следующий id для новой заявки |

## 4. Поля заявки

| Поле | Тип | Значение |
|---|---|---|
| `id` | int | Уникальный, с 1 |
| `title` | str | Заголовок |
| `user` | str | Идентификатор пользователя |
| `status` | str | `open` / `closed` |
| `tags` | list[str] | Метки заявки |

## 5. Точки входа

- `demo.py` — вызывает `reset`, `create_ticket`, `list_tickets`
- `test_smoke.py` — вызывает `reset`, `create_ticket`

## 6. Связи

```text
demo.py ──► helpdesk.reset
        ──► helpdesk.create_ticket
        ──► helpdesk.list_tickets

test_smoke.py ──► helpdesk.reset
              ──► helpdesk.create_ticket

helpdesk.py ──► tickets (list)
            ──► next_id (int)
```

## 7. Наблюдения (без выводов)

Зафиксировано на этапе составления карты:

- `create_ticket` принимает `title` первым, `user` вторым — порядок отличается от контракта R2/R3.
- `create_ticket` использует `tags=[]` — изменяемый аргумент по умолчанию.
- `create_ticket` сохраняет `tags` в заявку по ссылке и возвращает `ticket.copy()` — поверхностную копию.
- `create_ticket` проверяет только `title == ""`, без `strip` и без верхней границы.
- `create_ticket` не проверяет `user` ни на пустоту, ни на `strip`.
- `list_tickets` возвращает `tickets` напрямую, без фильтра и без копии.
- `close_ticket` ищет заявку по индексу списка, не по полю `id`.
- `close_ticket` использует границу `0`, хотя id начинаются с 1.
- `closed_share` делит на `len(tickets)` без проверки на пустой список.
- `reset` использует `global next_id` и `tickets.clear()` — счётчик сбрасывается, список очищается.
- `import json` в `helpdesk.py` не используется.
- `demo.py` и `test_smoke.py` вызывают `create_ticket` в том же порядке, что и модуль — расхождение с контрактом сохраняется во всех файлах.