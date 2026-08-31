"""
财报时间播报任务脚本。
"""

import os
import sys
from datetime import datetime

# 将项目根目录添加到 Python 路径，确保可以导入 core 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import ACTIVE_END_HOUR, ACTIVE_START_HOUR, STOCKS, FINANCIAL_REPORT_CONTACTS
from core.reporting import earnings_report, is_active_hour, run_scheduler, send_wechat_message

def job() -> None:
    """定义单次执行的任务逻辑"""
    now = datetime.now()
    # 检查是否在允许的时间段内
    if not is_active_hour(now, ACTIVE_START_HOUR, ACTIVE_END_HOUR):
        print(f"[{now}] 当前不在执行时间段（{ACTIVE_START_HOUR}-{ACTIVE_END_HOUR}点），跳过。")
        return
    
    print(f"[{now}] 正在生成财报时间报告...")
    # 生成报告内容
    report_content = earnings_report(STOCKS)
    # 发送微信消息
    send_wechat_message(FINANCIAL_REPORT_CONTACTS, report_content)

def main() -> None:
    """主入口：启动调度器，每天运行一次 (或者按需调整频率)"""
    # 财报时间变动不频繁，这里设置为每 480 分钟 (8小时) 运行一次
    print("启动财报时间播报任务调度器...")
    run_scheduler(job, 480)

if __name__ == "__main__":
    main()
