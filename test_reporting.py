import unittest
from datetime import datetime
from types import SimpleNamespace

from reporting import daily_report, is_active_hour, market_cap_report, yearly_report


class FakeTicker:
    fast_info = SimpleNamespace(last_price=110, previous_close=100, day_high=115, day_low=95)
    info = {"fiftyTwoWeekHigh": 120, "fiftyTwoWeekLow": 80, "marketCap": 2_000_000_000_000}


class ReportingTests(unittest.TestCase):
    def test_daily_report_calculates_change_and_range(self):
        report = daily_report({"测试": "TEST"}, lambda _: FakeTicker())
        self.assertIn("测试:110.00 💹+10.0% ↕️20.0%", report)

    def test_yearly_and_market_cap_reports(self):
        factory = lambda _: FakeTicker()
        self.assertIn("测试:110.00 👆🏻120 🔻80 ↕️50%", yearly_report({"测试": "TEST"}, factory))
        self.assertIn("测试:110.00 💹+10.0% ↕️2.00万亿", market_cap_report({"测试": "TEST"}, factory))

    def test_active_hours_are_consistent(self):
        self.assertFalse(is_active_hour(datetime(2026, 1, 1, 6, 59)))
        self.assertTrue(is_active_hour(datetime(2026, 1, 1, 7)))
        self.assertFalse(is_active_hour(datetime(2026, 1, 1, 23)))


if __name__ == "__main__":
    unittest.main()
