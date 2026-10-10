import unittest
from helpdesk import reset, create_ticket

class SmokeTests(unittest.TestCase):
    def setUp(self):
        reset()

    def test_create_regular_ticket(self):
        ticket = create_ticket("Принтер", "anna")
        self.assertEqual(ticket["title"], "Принтер")
        self.assertEqual(ticket["status"], "open")

if __name__ == "__main__":
    unittest.main()
