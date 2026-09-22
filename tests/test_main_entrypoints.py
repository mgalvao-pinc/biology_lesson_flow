import inspect
import unittest

from biology_lesson_flow.main import kickoff, plot, run_with_trigger, sanitize_filename


class TestMainEntrypoints(unittest.TestCase):
    def test_entrypoints_exist(self):
        self.assertTrue(callable(kickoff))
        self.assertTrue(callable(plot))
        self.assertTrue(callable(run_with_trigger))

    def test_kickoff_accepts_topic_without_interactive_input(self):
        topic_parameter = inspect.signature(kickoff).parameters["topic"]
        self.assertIsNone(topic_parameter.default)

    def test_filename_sanitization_removes_accents_and_invalid_chars(self):
        self.assertEqual(sanitize_filename("Fotossíntese"), "Fotossintese")
        self.assertEqual(sanitize_filename("Células & tecidos"), "Celulas_tecidos")


if __name__ == "__main__":
    unittest.main()
