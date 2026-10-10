from helpdesk import reset, create_ticket, list_tickets
reset()
create_ticket("Не включается компьютер", "anna")
create_ticket("Не печатает принтер", "boris")
print("Заявки anna:", list_tickets("anna"))
