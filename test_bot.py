import tempfile
import unittest
from pathlib import Path

import bot


class FakeMessage:
    def __init__(self) -> None:
        self.edits = []
        self.answers = []

    async def edit_text(self, text, reply_markup=None) -> None:
        self.edits.append((text, reply_markup))

    async def answer(self, text, reply_markup=None, **kwargs) -> None:
        self.answers.append((text, reply_markup))


class FakeCallback:
    def __init__(self, action: str, user_id: int = 42) -> None:
        self.data = f"menu:{action}"
        self.from_user = type("User", (), {"id": user_id})()
        self.message = FakeMessage()
        self.answered = False

    async def answer(self) -> None:
        self.answered = True


class MenuTests(unittest.TestCase):
    def test_main_menu_has_all_customer_sections(self) -> None:
        labels = [button.text for row in bot.main_menu_keyboard().inline_keyboard for button in row]
        self.assertEqual(
            labels,
            [
                "💬 Общение",
                "📅 Дела",
                "💰 Финансы",
                "🎓 Обучение",
                "🧠 Память",
                "⚙️ Настройки",
                "❓ Возможности и помощь",
            ],
        )

    def test_all_callbacks_fit_telegram_limit(self) -> None:
        keyboards = [
            bot.main_menu_keyboard(),
            bot.chat_menu_keyboard(),
            bot.planning_menu_keyboard(),
            bot.finance_menu_keyboard(),
            bot.learning_menu_keyboard(),
            bot.memory_menu_keyboard(),
            bot.settings_menu_keyboard(),
        ]
        callbacks = [
            button.callback_data
            for keyboard in keyboards
            for row in keyboard.inline_keyboard
            for button in row
        ]
        self.assertTrue(all(callbacks))
        self.assertTrue(all(len(value.encode("utf-8")) <= 64 for value in callbacks if value))

    def test_dispatcher_registers_callback_navigation(self) -> None:
        dispatcher = bot.build_dispatcher(None, None, None, None)
        self.assertGreater(len(dispatcher.message.handlers), 0)
        self.assertEqual(len(dispatcher.callback_query.handlers), 1)


class MemoryTests(unittest.TestCase):
    def test_input_flow_is_saved_and_can_be_cancelled(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = bot.MemoryStore(str(Path(directory) / "memory.sqlite3"))
            store.start_input_flow(42, "task")
            self.assertEqual(store.active_input_flow(42), "task")
            store.clear_input_flow(42)
            self.assertEqual(store.active_input_flow(42), "")
            store.close()

    def test_clear_all_removes_every_user_area(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = bot.MemoryStore(str(Path(directory) / "memory.sqlite3"))
            user_id = 42
            store.add_profile_fact(user_id, "Живу в Екатеринбурге")
            store.save_exchange(user_id, "Привет", "Привет!")
            store.add_task(user_id, "Купить продукты")
            store.add_expense(user_id, 750, "продукты", "молоко")
            store.ensure_assistant(user_id, 100)
            store.start_english_test(user_id)
            store.start_input_flow(user_id, "task")

            store.clear_all(user_id)

            self.assertEqual(store.profile(user_id), [])
            self.assertEqual(store.history(user_id), [])
            self.assertEqual(store.open_tasks(user_id), [])
            self.assertEqual(store.expense_summary(user_id)[0], 0)
            self.assertEqual(store.english_profile(user_id)["level"], "")
            self.assertEqual(store.active_input_flow(user_id), "")
            store.close()


class CallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_add_task_button_starts_plain_text_flow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = bot.MemoryStore(str(Path(directory) / "memory.sqlite3"))
            dispatcher = bot.build_dispatcher(None, store, None, None)
            callback_handler = dispatcher.callback_query.handlers[0].callback

            await callback_handler(FakeCallback("task_help"))

            self.assertEqual(store.active_input_flow(42), "task")
            store.close()

    async def test_navigation_edits_existing_menu_message(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = bot.MemoryStore(str(Path(directory) / "memory.sqlite3"))
            dispatcher = bot.build_dispatcher(None, store, None, None)
            callback_handler = dispatcher.callback_query.handlers[0].callback
            callback = FakeCallback("planning")

            await callback_handler(callback)

            self.assertTrue(callback.answered)
            self.assertEqual(len(callback.message.edits), 1)
            self.assertIn("Дела и напоминания", callback.message.edits[0][0])
            store.close()

    async def test_delete_requires_second_confirmed_callback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = bot.MemoryStore(str(Path(directory) / "memory.sqlite3"))
            store.add_profile_fact(42, "Тестовый факт")
            dispatcher = bot.build_dispatcher(None, store, None, None)
            callback_handler = dispatcher.callback_query.handlers[0].callback

            await callback_handler(FakeCallback("forget_confirm"))
            self.assertEqual(store.profile(42), ["Тестовый факт"])

            await callback_handler(FakeCallback("forget_do"))
            self.assertEqual(store.profile(42), [])
            store.close()


class RoutingTests(unittest.TestCase):
    def test_current_information_uses_search(self) -> None:
        self.assertTrue(bot.needs_web_search("Какая сегодня погода?", False, True))

    def test_bot_self_question_does_not_use_search(self) -> None:
        self.assertFalse(bot.needs_web_search("Кто ты?", False, True))

    def test_relative_reminder_is_parsed(self) -> None:
        parsed = bot.parse_reminder("через 20 минут проверить духовку", 5)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed[1], "проверить духовку")

    def test_natural_monthly_reminder_is_parsed(self) -> None:
        parsed = bot.parse_reminder(
            "Добавь напоминание напоминать каждое 27 число об оплате домашнего интернета", 5
        )
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed[1], "об оплате домашнего интернета")
        self.assertEqual(parsed[2], "monthly:27:5")


if __name__ == "__main__":
    unittest.main()
