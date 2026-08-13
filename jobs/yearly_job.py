"""
年度资产播报任务脚本。
"""

import sys
import os
from datetime import datetime

# 将项目根目录添加到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import ACTIVE_END_HOUR, ACTIVE_START_HOUR, STOCKS, TARGET_CONTACTS
from core.reporting import yearly_report, is_active_hour, run_scheduler, send_wechat_message

def job() -> None:
    """定义单次执行的任务逻辑"""
    now = datetime.now()
    if not is_active_hour(now, ACTIVE_START_HOUR, ACTIVE_END_HOUR):
        print(f"[{now}] 当前不在执行时间段，跳过年度报告。")
        return
    
    report_content = yearly_report(STOCKS)
    send_wechat_message(TARGET_CONTACTS, report_content)

def main() -> None:
    """启动调度器，每 60 分钟检查一次"""
    print("启动年度资产播报任务调度器...")
    # 注意：这里可以根据需要调整频率
    run_scheduler(job, 60)

if __name__ == "__main__":
    main()
