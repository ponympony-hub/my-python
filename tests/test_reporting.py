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
        # 验证输出中是否包含预期的格式化字符串
        self.assertIn("测试:110 💹10.0%↕️20%", report)

    def test_yearly_and_market_cap_reports(self):
        """测试年度报告和市值报告"""
        factory = lambda _: FakeTicker()
        # 验证年度报告格式
        self.assertIn("测试:120👆110🔻80↕️50%", yearly_report({"测试": "TEST"}, factory))
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
        
        # 验证过滤：公司B (过去时间) 应该被忽略，不出现在报告中
        self.assertNotIn("公司B", report)
        self.assertIn("公司A", report)
        self.assertIn("公司C", report)
        
        # 验证排序：公司C (较近将来) 应该在 公司A (较远将来) 之前
        lines = [line for line in report.split("\n") if line.strip()]
        # lines[0] 为标题 "📅 财报日历播报："
        self.assertIn("公司C", lines[1])
        self.assertIn("公司A", lines[2])

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
        
        # 验证排序：股2 (4亿) 应该排在 股1 (1亿) 前面
        lines = [line for line in report.split("\n") if line.strip()]
        # 股2: 4.00亿 (10日均:6.00亿)🔻
        self.assertIn("股2: 4.00亿 (10日均:6.00亿)🔻", lines[1])
        # 股1: 1.00亿 (10日均:0.80亿)💹
        self.assertIn("股1: 1.00亿 (10日均:0.80亿)💹", lines[2])

if __name__ == "__main__":
    # 运行所有测试
    unittest.main()
