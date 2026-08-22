"""小红书早安问候测试。"""

from unittest import mock
import os

import unittest
from datetime import datetime

import core.greetings
from core.greetings import generate_ai_morning_greeting, xiaohongshu_morning_greeting
from jobs.greeting_job import job


class GreetingTests(unittest.TestCase):
    def test_same_day_is_stable(self):
        time_point = datetime(2026, 8, 21, 8, 30)
        self.assertEqual(
            xiaohongshu_morning_greeting(time_point),
            xiaohongshu_morning_greeting(time_point),
        )

    def test_contains_xiaohongshu_tags(self):
        text = xiaohongshu_morning_greeting(datetime(2026, 8, 21, 8, 30))
        self.assertTrue(any(tag.startswith("#早") for tag in text.split()))
        self.assertIn("\n#", text)

    def test_ai_greeting_is_used_when_available(self):
        with mock.patch.object(core.greetings.requests, "post") as request:
            request.return_value.json.return_value = {
                "choices": [{"message": {"content": "早安☀️ 今天也要闪闪发光"}}]
            }
            request.return_value.raise_for_status.return_value = None
            self.assertEqual(
                generate_ai_morning_greeting(datetime(2026, 8, 22, 9, 30)),
                "早安☀️ 今天也要闪闪发光",
            )

    def test_ai_greeting_requires_api_key(self):
        with (
            mock.patch.object(core.greetings.Path, "exists", return_value=False),
            mock.patch.dict(os.environ, {}, clear=False),
        ):
            del os.environ["OPENROUTER_API_KEY"]
            with self.assertRaises(RuntimeError):
                generate_ai_morning_greeting()

    def test_job_falls_back_to_template(self):
        with (
            mock.patch("jobs.greeting_job.generate_ai_morning_greeting", side_effect=OSError("network unavailable")) as ai_mock,
            mock.patch("jobs.greeting_job.send_wechat_message") as send,
        ):
            job()

        send.assert_called_once()


if __name__ == "__main__":
    unittest.main()
