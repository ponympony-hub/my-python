"""
单元测试模块：验证报告生成逻辑和工具函数的正确性。
"""

import unittest
import sys
import os
from datetime import datetime
from types import SimpleNamespace

# 将项目根目录添加到 Python 路径，以便导入 core 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.reporting import daily_report, is_active_hour, market_cap_report, yearly_report

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
        "marketCap": 2_000_000_000_000
    }

class ReportingTests(unittest.TestCase):
    """测试用例集"""

    def test_daily_report_calculates_change_and_range(self):
        """测试每日报告的涨跌幅和振幅计算"""
        # 使用 lambda 表达式创建一个简单的工厂函数返回模拟对象
        report = daily_report({"测试": "TEST"}, lambda _: FakeTicker())
        # 验证输出中是否包含预期的格式化字符串
        self.assertIn("测试:110 💹10.0%↕️20%", report)

    def test_yearly_and_market_cap_reports(self):
        """测试年度报告和市值报告"""
        factory = lambda _: FakeTicker()
        # 验证年度报告格式
        self.assertIn("测试:👆120📢110 🔻80 ↕️50%", yearly_report({"测试": "TEST"}, factory))
        # 验证市值报告格式 (2万亿)
        self.assertIn("测试:110 💹10% ↕️2.00万亿", market_cap_report({"测试": "TEST"}, factory))

    def test_active_hours_are_consistent(self):
        """测试活跃时间段检查函数"""
        # 测试临界点：6:59 不活跃
        self.assertFalse(is_active_hour(datetime(2026, 1, 1, 6, 59)))
        # 7:00 活跃
        self.assertTrue(is_active_hour(datetime(2026, 1, 1, 7)))
        # 23:00 不活跃
        self.assertFalse(is_active_hour(datetime(2026, 1, 1, 23)))

if __name__ == "__main__":
    # 运行所有测试
    unittest.main()
