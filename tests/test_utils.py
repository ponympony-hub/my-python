import unittest
import os
import json
import shutil
from unittest.mock import MagicMock, patch
from core.utils import TickerExporter

class TestTickerExporter(unittest.TestCase):
    def setUp(self):
        # 测试用的股票列表
        self.test_stocks = {
            "TestStock": "TST"
        }
        # 测试输出目录
        self.test_dir = "test_tickers_output"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        # 清理测试目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('core.utils._ticker')
    def test_export_all_success(self, mock_ticker_factory):
        # 模拟 ticker 的各项数据
        mock_ticker = MagicMock()
        mock_ticker.info = {"symbol": "TST", "name": "Test Stock Data"}
        mock_ticker.news = [{"title": "News 1"}]
        mock_ticker.fast_info = {"last_price": 100.5}
        mock_ticker.calendar = None
        mock_ticker_factory.return_value = mock_ticker

        exporter = TickerExporter(stocks=self.test_stocks, output_dir=self.test_dir)
        exporter.export_all()

        # 检查文件是否生成
        expected_file = os.path.join(self.test_dir, "TestStock.json5")
        self.assertTrue(os.path.exists(expected_file))

        # 检查文件内容（处理注释）
        with open(expected_file, "r", encoding="utf-8") as f:
            content = f.read()
            # 验证包含中文注释
            self.assertIn("// 股票代码", content)
            self.assertIn("// 快速元数据", content)
            
            # 移除注释以便进行 JSON 解析验证数据
            import re
            clean_json = re.sub(r'//.*', '', content)
            data = json.loads(clean_json)
            
            self.assertEqual(data["info"]["symbol"], "TST")
            self.assertEqual(data["fast_info"]["last_price"], 100.5)
            self.assertEqual(data["news"][0]["title"], "News 1")

    @patch('core.utils._ticker')
    @patch('core.utils._log_failed_ticker')
    def test_export_all_failure(self, mock_log, mock_ticker_factory):
        # 模拟获取失败
        mock_ticker_factory.side_effect = Exception("Network error")

        exporter = TickerExporter(stocks=self.test_stocks, output_dir=self.test_dir)
        exporter.export_all()

        # 检查文件是否未生成
        expected_file = os.path.join(self.test_dir, "TestStock.json5")
        self.assertFalse(os.path.exists(expected_file))
        
        # 检查是否记录了错误日志
        mock_log.assert_called_once()

if __name__ == "__main__":
    unittest.main()
