"""
导出股票数据任务脚本。
该脚本手动调用 TickerExporter 工具类，将 config.py 中所有股票的最新元数据导出为 json5 文件。
"""

import sys
import os

# 将项目根目录添加到 Python 路径，确保可以导入 core 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils import TickerExporter

def main() -> None:
    """
    主入口：实例化导出器并执行批量导出。
    文件将被保存在项目根目录的 'json' 文件夹下，包含完整数据和中文注释。
    """
    # 指定输出目录为 'json'
    output_directory = "json"
    
    print(f"🚀 开始执行增强版批量导出任务...")
    print(f"📁 目标目录: {output_directory}")
    
    # 创建导出器实例
    exporter = TickerExporter(output_dir=output_directory)
    
    # 执行导出
    exporter.export_all()
    
    print(f"\n✅ 导出任务已完成！请在 '{output_directory}' 文件夹中查看生成的 .json5 文件。")

if __name__ == "__main__":
    main()
