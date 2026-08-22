"""每天早上发送小红书风格问候的定时任务。"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config import XIAOHONGSHU_CONTACTS
from core.greetings import (
    generate_ai_morning_greeting,
    tomorrow_morning,
    xiaohongshu_morning_greeting,
)
from core.reporting import send_wechat_message

GREETING_HOUR = 9
GREETING_MINUTE = 30

def job() -> None:
    """生成并立即发送当天问候。"""
    try:
        content = generate_ai_morning_greeting(datetime.now())
        print("已通过 AI 实时生成今日早安问候。")
    except Exception as exc:
        print(f"AI 问候生成失败，已改用本地模板：{exc}")
        content = xiaohongshu_morning_greeting(datetime.now())
    send_wechat_message(XIAOHONGSHU_CONTACTS, content)


def run_daily_greeting_job(task) -> None:
    """按下一个固定早晨时间调度，并在每次发送后滚动到明天。"""
    while True:
        target_time = tomorrow_morning(GREETING_HOUR, GREETING_MINUTE)
        delay_seconds = max(0.0, (target_time - datetime.now()).total_seconds())
        print(f"下一次早安问候将在 {target_time:%Y-%m-%d %H:%M} 发送。")
        time.sleep(delay_seconds)
        try:
            task()
        except Exception as exc:
            print(f"早安任务执行失败：{exc}")


if __name__ == "__main__":
    print("启动小红书早安问候任务...")
    job()
