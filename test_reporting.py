import unittest
from datetime import datetime
from types import SimpleNamespace

from reporting import daily_report, is_active_hour, market_cap_report, yearly_report


class FakeTicker:
    fast_info = SimpleNamespace(last_price=110, previous_close=100, day_high=115, day_low=95)
    info = {"fiftyTwoWeekHigh": 120, "fiftyTwoWeekLow": 80, "marketCap": 2_000_000_000_000}


def ticker(last_price, previous_close, day_high, day_low, year_high, year_low, market_cap):
    return SimpleNamespace(
        fast_info=SimpleNamespace(
            last_price=last_price,
            previous_close=previous_close,
            day_high=day_high,
            day_low=day_low,
        ),
        info={
            "fiftyTwoWeekHigh": year_high,
            "fiftyTwoWeekLow": year_low,
            "marketCap": market_cap,
        },
    )


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

    def test_reports_sort_by_requested_metric(self):
        quotes = {
            "GAIN": ticker(120, 100, 125, 95, 110, 100, 1_000_000_000_000),
            "RANGE": ticker(95, 100, 105, 90, 200, 100, 3_000_000_000_000),
            "CAP": ticker(100, 100, 110, 90, 150, 100, 2_000_000_000_000),
        }
        factory = quotes.__getitem__
        stocks = {name: name for name in quotes}

        self.assertLess(daily_report(stocks, factory).index("GAIN:"), daily_report(stocks, factory).index("CAP:"))
        self.assertLess(yearly_report(stocks, factory).index("RANGE:"), yearly_report(stocks, factory).index("CAP:"))
        self.assertLess(market_cap_report(stocks, factory).index("RANGE:"), market_cap_report(stocks, factory).index("CAP:"))


if __name__ == "__main__":
    unittest.main()
