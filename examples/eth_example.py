"""Send a periodic ETH price report to WeChat."""

from datetime import datetime

import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import ACTIVE_END_HOUR, ACTIVE_START_HOUR, TARGET_CONTACTS
from core.reporting import daily_report, is_active_hour, run_scheduler, send_wechat_message


def get_crypto_data() -> str:
    return daily_report({"ETH": "ETH-USD"}).replace("📊 今日资产播报：\n", "")


def job() -> None:
    now = datetime.now()
    if not is_active_hour(now, ACTIVE_START_HOUR, ACTIVE_END_HOUR):
        print(f"[{now}] 不在执行时间段（7-23点），跳过本次执行。")
        return
    send_wechat_message(TARGET_CONTACTS, get_crypto_data())


def main() -> None:
    run_scheduler(job, 30, run_now=False)


if __name__ == "__main__":
    main()
