"""Автотесты для helpdesk.py по R1-R8 и критериям сопровождения.

На исходной версии helpdesk.py часть тестов ПАДАЕТ — это ожидаемо,
так как модуль содержит намеренные дефекты. После исправлений (День 3)
все тесты должны проходить.
"""
import unittest

from helpdesk import (
    reset,
    create_ticket,
    list_tickets,
    close_ticket,
    closed_share,
)


class R1Tests(unittest.TestCase):
    """R1: id с 1, уникальны, сброс в reset."""

    def setUp(self):
        reset()

    def test_r1_1_first_id_is_one(self):
        t = create_ticket("u", "t")
        self.assertEqual(t["id"], 1)

    def test_r1_2_ids_sequential(self):
        ids = [create_ticket("u", "t")["id"] for _ in range(3)]
        self.assertEqual(ids, [1, 2, 3])

    def test_r1_3_reset_resets_ids(self):
        create_ticket("u", "t")
        reset()
        self.assertEqual(create_ticket("u", "t")["id"], 1)

    def test_r1_4_status_is_open(self):
        t = create_ticket("u", "t")
        self.assertEqual(t["status"], "open")

    def test_r1_5_id_is_int(self):
        t = create_ticket("u", "t")
        self.assertIsInstance(t["id"], int)


class R2Tests(unittest.TestCase):
    """R2: title — strip, длина 1..80, атомарность."""

    def setUp(self):
        reset()

    def test_r2_1_title_stripped(self):
        t = create_ticket("u", "  hi  ")
        self.assertEqual(t["title"], "hi")

    def test_r2_2_min_length_ok(self):
        t = create_ticket("u", "x")
        self.assertEqual(t["title"], "x")

    def test_r2_3_max_length_ok(self):
        t = create_ticket("u", "x" * 80)
        self.assertEqual(len(t["title"]), 80)

    def test_r2_4_too_long_raises(self):
        with self.assertRaises(ValueError):
            create_ticket("u", "x" * 81)

    def test_r2_5_empty_raises(self):
        with self.assertRaises(ValueError):
            create_ticket("u", "")

    def test_r2_6_spaces_only_raises(self):
        with self.assertRaises(ValueError):
            create_ticket("u", "   ")

    def test_r2_7_state_unchanged_after_error(self):
        with self.assertRaises(ValueError):
            create_ticket("u", "")
        self.assertEqual(list_tickets("u"), [])

    def test_r2_8_counter_unchanged_after_error(self):
        with self.assertRaises(ValueError):
            create_ticket("u", "")
        self.assertEqual(create_ticket("u", "ok")["id"], 1)


class R3Tests(unittest.TestCase):
    """R3: user — strip, непустой, сохраняется очищенным."""

    def setUp(self):
        reset()

    def test_r3_1_user_stripped_findable(self):
        create_ticket("  bob  ", "t")
        self.assertEqual(len(list_tickets("bob")), 1)

    def test_r3_2_empty_user_raises(self):
        with self.assertRaises(ValueError):
            create_ticket("", "t")

    def test_r3_3_spaces_only_user_raises(self):
        with self.assertRaises(ValueError):
            create_ticket("   ", "t")

    def test_r3_4_user_saved_stripped(self):
        t = create_ticket("  bob  ", "t")
        self.assertEqual(t["user"], "bob")


class R4Tests(unittest.TestCase):
    """R4: list_tickets — фильтр по user."""

    def setUp(self):
        reset()

    def test_r4_1_filter_by_user(self):
        create_ticket("anna", "a")
        create_ticket("boris", "b")
        self.assertEqual(len(list_tickets("anna")), 1)

    def test_r4_2_empty_for_unknown_user(self):
        create_ticket("anna", "a")
        self.assertEqual(list_tickets("nobody"), [])

    def test_r4_3_user_compared_stripped(self):
        create_ticket("anna", "a")
        self.assertEqual(len(list_tickets("  anna  ")), 1)

    def test_r4_4_result_is_new_list(self):
        create_ticket("anna", "a")
        r1 = list_tickets("anna")
        r1.clear()
        self.assertEqual(len(list_tickets("anna")), 1)


class R5Tests(unittest.TestCase):
    """R5: close_ticket — поиск по полю id."""

    def setUp(self):
        reset()

    def test_r5_1_close_existing_returns_true(self):
        t = create_ticket("u", "t")
        self.assertTrue(close_ticket(t["id"]))

    def test_r5_2_other_tickets_untouched(self):
        t1 = create_ticket("u", "1")
        t2 = create_ticket("u", "2")
        close_ticket(t2["id"])
        tickets = list_tickets("u")
        self.assertEqual(tickets[0]["status"], "open")
        self.assertEqual(tickets[1]["status"], "closed")

    def test_r5_3_missing_id_returns_false(self):
        create_ticket("u", "t")
        self.assertFalse(close_ticket(999))

    def test_r5_4_repeat_close_returns_true(self):
        t = create_ticket("u", "t")
        close_ticket(t["id"])
        self.assertTrue(close_ticket(t["id"]))

    def test_r5_5_close_by_id_not_index(self):
        # Закрываем вторую заявку по её id (2), не по индексу 1
        create_ticket("u", "1")
        t2 = create_ticket("u", "2")
        close_ticket(t2["id"])
        tickets = list_tickets("u")
        self.assertEqual(tickets[0]["status"], "open")
        self.assertEqual(tickets[1]["status"], "closed")

    def test_r5_6_close_nonzero_id(self):
        create_ticket("u", "1")
        create_ticket("u", "2")
        create_ticket("u", "3")
        close_ticket(3)
        tickets = list_tickets("u")
        self.assertEqual(tickets[0]["status"], "open")
        self.assertEqual(tickets[1]["status"], "open")
        self.assertEqual(tickets[2]["status"], "closed")


class R6Tests(unittest.TestCase):
    """R6: closed_share — процент 0..100."""

    def setUp(self):
        reset()

    def test_r6_1_empty_returns_zero_float(self):
        self.assertEqual(closed_share(), 0.0)
        self.assertIsInstance(closed_share(), float)

    def test_r6_2_half_closed(self):
        t1 = create_ticket("u", "1")
        create_ticket("u", "2")
        close_ticket(t1["id"])
        self.assertEqual(closed_share(), 50.0)

    def test_r6_3_all_closed(self):
        t1 = create_ticket("u", "1")
        t2 = create_ticket("u", "2")
        close_ticket(t1["id"])
        close_ticket(t2["id"])
        self.assertEqual(closed_share(), 100.0)

    def test_r6_4_none_closed(self):
        create_ticket("u", "1")
        create_ticket("u", "2")
        self.assertEqual(closed_share(), 0.0)

    def test_r6_5_type_is_float(self):
        create_ticket("u", "1")
        self.assertIsInstance(closed_share(), float)


class R7Tests(unittest.TestCase):
    """R7: tags — изоляция."""

    def setUp(self):
        reset()

    def test_r7_1_input_tags_copied(self):
        src = ["a"]
        t = create_ticket("u", "t", src)
        src.append("b")
        self.assertEqual(t["tags"], ["a"])

    def test_r7_2_result_tags_isolated_create(self):
        t = create_ticket("u", "t", ["a"])
        t["tags"].append("hack")
        self.assertEqual(list_tickets("u")[0]["tags"], ["a"])

    def test_r7_3_result_tags_isolated_list(self):
        create_ticket("u", "t", ["a"])
        r = list_tickets("u")
        r[0]["tags"].append("hack")
        self.assertEqual(list_tickets("u")[0]["tags"], ["a"])

    def test_r7_4_two_results_independent(self):
        create_ticket("u", "t", ["a"])
        a = list_tickets("u")
        b = list_tickets("u")
        self.assertIsNot(a[0], b[0])
        self.assertIsNot(a[0]["tags"], b[0]["tags"])

    def test_r7_5_default_tags_not_shared(self):
        t1 = create_ticket("u", "1")
        t2 = create_ticket("u", "2")
        t1["tags"].append("x")
        self.assertEqual(t2["tags"], [])


class R8Tests(unittest.TestCase):
    """R8: reset — очистка и сброс нумерации."""

    def setUp(self):
        reset()

    def test_r8_1_reset_clears_tickets(self):
        create_ticket("u", "t")
        reset()
        self.assertEqual(list_tickets("u"), [])

    def test_r8_2_reset_resets_counter(self):
        create_ticket("u", "t")
        reset()
        self.assertEqual(create_ticket("u", "t")["id"], 1)

    def test_r8_3_closed_share_zero_after_reset(self):
        t = create_ticket("u", "t")
        close_ticket(t["id"])
        reset()
        self.assertEqual(closed_share(), 0.0)


if __name__ == "__main__":
    unittest.main()