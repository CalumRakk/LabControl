import unittest
from cloudAuto.paquetes.aws.lab_aws_utils import (
    ReadyLabSessionRegex,
    StoppedLabSessionRegex,
    regex_lab_status,
)


class Test_ReadyLabSessionRegex(unittest.TestCase):

    def test_remaining_time(self):
        sample_text = "Remaining session time: 03:43:00(223 minutes)"
        match = ReadyLabSessionRegex.remaining_time.value.search(sample_text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), sample_text)

    def test_session_started(self):
        sample_text = "Session started at: 2024-08-20T18:18:55-0700"
        match = ReadyLabSessionRegex.session_started.value.search(sample_text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), sample_text)

    def test_session_ended(self):
        sample_text = "Session to end&nbsp; at: 2024-08-21T07:23:23-0700"
        match = ReadyLabSessionRegex.session_ended.value.search(sample_text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), sample_text)

    def test_accumulated_lab_time(self):
        # 3 days : Los días aparece cuando se ha acomulado más de 24 horas.
        sample_text = "Accumulated lab time: 3 days 05:58:00 (4678 minutes)"
        match = ReadyLabSessionRegex.accumulated_lab_time.value.search(sample_text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), sample_text)

    def test_accumulated_lab_time2(self):
        # No aparecen los días porque no se ha acomulado más de 24 horas.
        sample_text = "Accumulated lab time: 05:58:00 (4678 minutes)"
        match = ReadyLabSessionRegex.accumulated_lab_time.value.search(sample_text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), sample_text)


class Test_StoppedLabSessionRegex(unittest.TestCase):
    def test_session_started(self):
        sample_text = "Session started at: -0001-11-30T00:00:00-0752"
        match = StoppedLabSessionRegex.session_started.value.search(sample_text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), sample_text)

    def test_session_stoped(self):
        sample_text = "Session stopped at 2024-08-20T01:23:56-0700"
        match = StoppedLabSessionRegex.session_stopped.value.search(sample_text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), sample_text)

    def test_accumulated_lab_time(self):
        # 3 days : Los días aparece cuando se ha acomulado más de 24 horas.
        sample_text = "Accumulated lab time: 3 days 05:58:00 (4678 minutes)"
        match = StoppedLabSessionRegex.accumulated_lab_time.value.search(sample_text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), sample_text)

    def test_accumulated_lab_time2(self):
        # No aparecen los días porque no se ha acomulado más de 24 horas.
        sample_text = "Accumulated lab time: 05:58:00 (4678 minutes)"
        match = ReadyLabSessionRegex.accumulated_lab_time.value.search(sample_text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), sample_text)


class Test_others(unittest.TestCase):
    def get_lab_status(self):
        sample_text = "Lab status: stopped<br>"
        match = regex_lab_status.search(sample_text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), "stopped")

        sample_text2 = "Lab status: in creation<br>"
        match = regex_lab_status.search(sample_text2)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), "stopped")


if __name__ == "__main__":
    unittest.main()
