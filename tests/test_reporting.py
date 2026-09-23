"""
单元测试模块：验证报告生成逻辑和工具函数的正确性。
"""

import unittest
from unittest.mock import MagicMock
import sys
import os
from datetime import datetime
from types import SimpleNamespace

# 将项目根目录添加到 Python 路径，以便导入 core 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.reporting import daily_report, is_active_hour, market_cap_report, yearly_report, earnings_report, volume_report

class FakeTicker:
    """
    模拟 yfinance Ticker 对象的类，用于测试。
    这样测试就不需要联网获取真实数据，运行速度快且结果可控。
    """
    fast_info = SimpleNamespace(
        last_price=110,
        previous_close=100,
        day_high=115,
        day_low=95
    )
    info = {
        "fiftyTwoWeekHigh": 120,
        "fiftyTwoWeekLow": 80,
        "marketCap": 2_000_000_000_000,
        "nonDilutedMarketCap": 2_000_000_000_000
    }

class ReportingTests(unittest.TestCase):
    """测试用例集"""

    def test_daily_report_calculates_change_and_range(self):
        """测试每日报告的涨跌幅和振幅计算"""
        # 使用 lambda 表达式创建一个简单的工厂函数返回模拟对象
        report = daily_report({"测试": "TEST"}, lambda _: FakeTicker())
        self.assertEqual(report.title, "📊 今日资产播报")
        self.assertEqual(len(report.rows), 1)
        row = report.rows[0]
        # 现价 110；涨幅 (110-100)/100=10.0%；振幅 15-(-5)=20%
        self.assertIn("测试", row["name"])
        self.assertEqual(row["price"], "110")
        self.assertEqual(row["change"], "💹+10.0%")
        self.assertEqual(row["amplitude"], "20%")

    def test_yearly_and_market_cap_reports(self):
        """测试年度报告和市值报告"""
        factory = lambda _: FakeTicker()

        # 年度报告：52周高120 / 现价110 / 52周低80 / 振幅 (120-80)/80=50%
        yearly = yearly_report({"测试": "TEST"}, factory)
        self.assertEqual(yearly.title, "📊 年度资产播报")
        yrow = yearly.rows[0]
        self.assertEqual(yrow["high"], "120")
        self.assertEqual(yrow["price"], "110")
        self.assertEqual(yrow["low"], "80")
        self.assertEqual(yrow["amplitude"], "50%")

        # 市值报告：市值 2e12 = 2.00 万亿
        cap = market_cap_report({"测试": "TEST"}, factory)
        self.assertEqual(cap.title, "📊 市值播报")
        crow = cap.rows[0]
        self.assertEqual(crow["change"], "💹+10.0%")
        self.assertEqual(crow["market_cap"], "2.00")

    def test_active_hours_are_consistent(self):
        """测试活跃时间段检查函数"""
        # 测试临界点：6:59 不活跃
        self.assertFalse(is_active_hour(datetime(2026, 1, 1, 6, 59)))
        # 7:00 活跃
        self.assertTrue(is_active_hour(datetime(2026, 1, 1, 7)))
        # 23:00 不活跃
        self.assertFalse(is_active_hour(datetime(2026, 1, 1, 23)))

    def test_earnings_report_filtering_and_sorting(self):
        """测试财报时间报告的过滤（忽略过去时间）和排序"""
        import time
        now = time.time()
        # 准备数据：两个将来，一个过去
        future_ts_1 = now + 10000
        future_ts_2 = now + 20000
        past_ts = now - 10000

        data_map = {
            "T1": {"earningsTimestampStart": future_ts_2},
            "T2": {"earningsTimestampStart": past_ts},
            "T3": {"earningsTimestampStart": future_ts_1},
        }

        def factory(symbol):
            mock = MagicMock()
            mock.info = data_map.get(symbol, {})
            return mock

        report = earnings_report({"公司A": "T1", "公司B": "T2", "公司C": "T3"}, factory)
        self.assertEqual(report.title, "📅 财报日历播报")

        names = [r["name"] for r in report.rows]
        # 验证过滤：公司B (过去时间) 应该被忽略
        self.assertNotIn("公司B", "".join(names))
        # 验证排序：公司C (较近将来) 应该在 公司A (较远将来) 之前
        self.assertIn("公司C", names[0])
        self.assertIn("公司A", names[1])

    def test_volume_report_sorting_and_formatting(self):
        """测试成交额报告的计算、排序和单位格式化（包含10日均额和涨跌标识）"""
        class VolTicker:
            def __init__(self, price, prev_close, vol, avg_vol):
                # 模拟 fast_info 属性
                self.fast_info = SimpleNamespace(
                    last_price=price,
                    previous_close=prev_close,
                    day_volume=vol
                )
                self.info = {"averageDailyVolume10Day": avg_vol}

        data_map = {
            "V1": VolTicker(100, 90, 1_000_000, 800_000),    # 额:1亿, 均额:0.8亿, 涨 💹
            "V2": VolTicker(200, 210, 2_000_000, 3_000_000), # 额:4亿, 均额:6.0亿, 跌 🔻
        }

        report = volume_report({"股1": "V1", "股2": "V2"}, lambda s: data_map[s])
        self.assertEqual(report.title, "📊 今日成交额排行")

        # 验证排序：股2 (4亿) 应该排在 股1 (1亿) 前面
        self.assertEqual(len(report.rows), 2)
        self.assertIn("股2", report.rows[0]["name"])
        self.assertEqual(report.rows[0]["amount"], "4.00")
        self.assertEqual(report.rows[0]["avg_amount"], "6.00")
        self.assertEqual(report.rows[0]["change"], "🔻")

        self.assertIn("股1", report.rows[1]["name"])
        self.assertEqual(report.rows[1]["amount"], "1.00")
        self.assertEqual(report.rows[1]["avg_amount"], "0.80")
        self.assertEqual(report.rows[1]["change"], "💹")

if __name__ == "__main__":
    # 运行所有测试
    unittest.main()
