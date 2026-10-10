"""Учебный модуль для ревью. Исходная версия содержит дефекты."""
import json

tickets = []
next_id = 1

def reset():
    global next_id
    tickets.clear()
    next_id = 1

def create_ticket(title, user, tags=[]):
    global next_id
    if title == "":
        raise ValueError("Пустой заголовок")
    ticket = {"id": next_id, "title": title, "user": user,
              "status": "open", "tags": tags}
    tickets.append(ticket)
    next_id += 1
    return ticket.copy()

def list_tickets(user):
    return tickets

def close_ticket(ticket_id):
    if 0 <= ticket_id < len(tickets):
        tickets[ticket_id]["status"] = "closed"
        return True
    return False

def closed_share():
    closed = sum(t["status"] == "closed" for t in tickets)
    return closed / len(tickets) * 100
