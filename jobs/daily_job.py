"""
今日价格播报任务脚本。
"""

import sys
import os
from datetime import datetime

# 将项目根目录添加到 Python 路径，确保可以导入 core 模块
# 这对于从命令行直接运行脚本非常有用
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import ACTIVE_END_HOUR, ACTIVE_START_HOUR, STOCKS, TARGET_CONTACTS
from core.reporting import daily_report, is_active_hour, run_scheduler, send_wechat_message

def job() -> None:
    """定义单次执行的任务逻辑"""
    now = datetime.now()
    # 检查是否在允许的时间段内
    if not is_active_hour(now, ACTIVE_START_HOUR, ACTIVE_END_HOUR):
        print(f"[{now}] 当前不在执行时间段（{ACTIVE_START_HOUR}-{ACTIVE_END_HOUR}点），跳过。")
        return
    
    # 生成报告内容
    report_content = daily_report(STOCKS)
    # 发送微信消息
    send_wechat_message(TARGET_CONTACTS, report_content)

def main() -> None:
    """主入口：启动调度器，每 30 分钟运行一次"""
    print("启动今日价格播报任务调度器...")
    run_scheduler(job, 30)

if __name__ == "__main__":
    main()
