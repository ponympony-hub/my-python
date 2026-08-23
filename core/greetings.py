"""小红书风格的每日早安问候生成器。"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import requests


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "stealth/ox-alpha"
REQUEST_TIMEOUT_SECONDS = 100


_OPENINGS = (
    "早安☀️",
    "早呀🌤️",
    "新的一天✨",
)

_BODIES = (
    "把闹钟调成期待，把清晨过成小确幸",
    "阳光已上线，好心情也要准时营业",
    "今天也请慢慢发光，温柔又有力量",
    "风很轻，光很好，适合重新出发",
)

_CLOSINGS = (
    "#早安 #今日份元气 #治愈日常",
    "#早起打卡 #生活碎片 #元气满满",
    "#早安日记 #小确幸 #热爱生活",
)


def xiaohongshu_morning_greeting(now: datetime | None = None) -> str:
    """生成约 30 个汉字的小红书样式早安文案。"""
    current = now or datetime.now()
    weekday = current.weekday()
    rng = random.Random(current.date().toordinal())
    body = _BODIES[(rng.randrange(len(_BODIES)) + weekday) % len(_BODIES)]
    return f"{rng.choice(_OPENINGS)} {body}\n{rng.choice(_CLOSINGS)}"


def _load_env_file() -> None:
    """读取项目根目录的 .env，已存在的环境变量优先。"""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def generate_ai_morning_greeting(now: datetime | None = None) -> str:
    """通过 OpenRouter 实时生成一条不重复的正能量早安问候。"""
    _load_env_file()
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("缺少 OPENROUTER_API_KEY")

    current = now or datetime.now()
    weekdays = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")
    prompt = (
        "请为微信群写一条今天早上发送的微信早安问候。"
        "要求：中文、开心温暖、正能量、像小红书风格+两个换行+英文翻译；"
        "包含 2 个合适 emoji 和 2 个话题标签；"
        "正文约 20 个汉字；只输出问候语本身，不要解释或引号。"
        f"今天是 {current:%Y-%m-%d} "
        # f"{weekdays[current.weekday()]}，"
        "请结合今天日子和清晨氛围创作一条全新的内容。"
    )
    print(prompt)
    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            # "temperature": 1.15,
            # "max_tokens": 180,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"].strip()
    if not content:
        raise ValueError("AI 返回内容为空")
    return content


def tomorrow_morning(hour: int = 8, minute: int = 0) -> datetime:
    """返回下一个指定早晨时间。"""
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target
