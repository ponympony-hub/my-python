"""Data formatting, WeChat delivery, and scheduling utilities.

This module has no import-time side effects so it is safe to reuse from each
report entry point and from tests.
"""

from __future__ import annotations

import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from typing import Any


def _number(value: Any) -> float | None:
    """Return a finite numeric value, or ``None`` for missing market data."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result == result else None  # NaN is not usable data.


def percent_change(current: Any, baseline: Any) -> float | None:
    current_number = _number(current)
    baseline_number = _number(baseline)
    if current_number is None or baseline_number in (None, 0):
        return None
    return (current_number - baseline_number) / baseline_number * 100


def _ticker(symbol: str) -> Any:
    import yfinance as yf

    return yf.Ticker(symbol)


def daily_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> str:
    lines = ["📊 今日资产播报："]
    for name, symbol in stocks.items():
        try:
            info = ticker_factory(symbol).fast_info
            price = _number(info.last_price)
            change = percent_change(price, info.previous_close)
            amplitude = percent_change(info.day_high, info.previous_close)
            low_change = percent_change(info.day_low, info.previous_close)
            if price is None or change is None or amplitude is None or low_change is None:
                raise ValueError("incomplete quote data")
            intraday_amplitude = amplitude - low_change
            icon = "💹" if change >= 0 else "🔻"
            lines.append(f"{name}:{price:.2f} {icon}{change:+.1f}% ↕️{intraday_amplitude:.1f}%")
        except Exception:
            lines.append(f"{name}: 获取数据失败")
    return "\n".join(lines)


def yearly_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> str:
    lines = ["📊 年度资产播报："]
    for name, symbol in stocks.items():
        try:
            ticker = ticker_factory(symbol)
            price = _number(ticker.fast_info.last_price)
            info = ticker.info
            high = _number(info.get("fiftyTwoWeekHigh"))
            low = _number(info.get("fiftyTwoWeekLow"))
            if price is None or high is None or low is None or low <= 0:
                raise ValueError("incomplete 52-week data")
            amplitude = (high - low) / low * 100
            lines.append(f"{name}:{price:.2f} 👆🏻{high:.0f} 🔻{low:.0f} ↕️{amplitude:.0f}%")
        except Exception:
            lines.append(f"{name}: 获取数据失败")
    return "\n".join(lines)


def market_cap_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> str:
    lines = ["📊 市值播报："]
    for name, symbol in stocks.items():
        try:
            ticker = ticker_factory(symbol)
            price = _number(ticker.fast_info.last_price)
            change = percent_change(price, ticker.fast_info.previous_close)
            market_cap = _number(ticker.info.get("marketCap"))
            if price is None or change is None or market_cap is None:
                raise ValueError("incomplete market-cap data")
            icon = "💹" if change >= 0 else "🔻"
            lines.append(f"{name}:{price:.2f} {icon}{change:+.1f}% ↕️{market_cap / 1e12:.2f}万亿")
        except Exception:
            lines.append(f"{name}: 获取数据失败")
    return "\n".join(lines)


_APPLESCRIPT = '''on run argv
    set targetName to item 1 of argv
    set messageText to item 2 of argv
    tell application "WeChat" to activate
    delay 1
    tell application "System Events" to tell process "WeChat"
        set frontmost to true
        keystroke "f" using command down
        delay 1
        set the clipboard to targetName
        keystroke "v" using command down
        key code 36
        delay 1
        set the clipboard to messageText
        key code 36
        key code 36
        delay 1
        keystroke "v" using command down
        key code 36
    end tell
end run'''


def send_wechat_message(contacts: Sequence[str], content: str) -> None:
    """Send the same message to each contact without interpolating AppleScript."""
    for contact in contacts:
        subprocess.run(["osascript", "-e", _APPLESCRIPT, contact, content], check=True)


def is_active_hour(now: datetime | None = None, start: int = 7, end: int = 23) -> bool:
    return start <= (now or datetime.now()).hour < end


def run_scheduler(job: Callable[[], None], interval_minutes: int, *, run_now: bool = True) -> None:
    """Run one job serially; executing this function is the only blocking action."""
    import schedule

    if run_now:
        job()
    schedule.every(interval_minutes).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
