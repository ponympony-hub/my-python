"""
核心业务逻辑模块：包含数据格式化、微信推送和调度工具。
本模块设计为无副作用导入，方便在各个任务脚本和测试中复用。
"""

from __future__ import annotations

import logging
import subprocess
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from typing import Any

# 配置日志系统，用于记录程序运行中的错误，特别是数据获取失败的情况
def _setup_logging() -> logging.Logger:
    """初始化日志配置，支持控制台和文件双重输出"""
    l = logging.getLogger(__name__)
    l.setLevel(logging.ERROR)
    
    # 避免重复添加处理器（Handler）
    if not any(isinstance(h, logging.FileHandler) for h in l.handlers):
        # 定义日志格式：时间 - 级别 - 消息
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        try:
            # 尝试创建日志文件，编码设为 utf-8 以支持中文
            file_handler = logging.FileHandler("report.log", encoding='utf-8')
            file_handler.setFormatter(formatter)
            l.addHandler(file_handler)
        except Exception:
            # 如果文件不可写（如权限问题），静默跳过
            pass
            
        # 同时输出到控制台，方便实时查看
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        l.addHandler(stream_handler)
    
    # 如果根日志记录器没有配置，进行基础配置，防止消息丢失
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.ERROR)
        
    return l

# 全局日志对象
logger = _setup_logging()

def _number(value: Any) -> float | None:
    """
    工具函数：将输入转换为浮点数。
    如果转换失败或输入是 NaN（非数字），则返回 None。
    这在处理不稳定的行情数据时非常重要。
    """
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    # 判断是否为 NaN (NaN != NaN)
    return result if result == result else None

def percent_change(current: Any, baseline: Any) -> float | None:
    """
    计算涨跌幅百分比。
    公式：(当前值 - 基准值) / 基准值 * 100
    """
    current_number = _number(current)
    baseline_number = _number(baseline)
    # 检查数据有效性，基准值不能为 0
    if current_number is None or baseline_number in (None, 0):
        return None
    return (current_number - baseline_number) / baseline_number * 100

def _ticker(symbol: str) -> Any:
    """
    获取 yfinance 股票对象的默认工厂函数。
    """
    import yfinance as yf
    return yf.Ticker(symbol)

def _log_failed_ticker(name: str, symbol: str, exc: Exception, ticker: Any = None) -> None:
    """
    当数据获取失败时，记录详细的原始数据上下文，便于排查问题。
    """
    raw = {}
    if ticker is not None:
        try:
            # .info 包含股票的详细元数据
            raw['info'] = ticker.info
        except Exception:
            raw['info'] = "Could not fetch .info"
        try:
            # .fast_info 包含实时价格等基础数据，访问速度较快
            fi = ticker.fast_info
            raw['fast_info'] = {
                "last_price": getattr(fi, "last_price", None),
                "previous_close": getattr(fi, "previous_close", None),
                "day_high": getattr(fi, "day_high", None),
                "day_low": getattr(fi, "day_low", None),
            }
        except Exception:
            raw['fast_info'] = "Could not fetch .fast_info"

    # 将错误信息和原始数据上下文写入日志
    logger.error(f"数据获取失败 [{name} ({symbol})]: {exc}\n原始数据上下文: {raw}")

def daily_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> str:
    """
    生成每日资产报告。
    按照当日涨幅从高到低排序。
    """
    results = []
    errors = []
    for name, symbol in stocks.items():
        ticker = None
        try:
            ticker = ticker_factory(symbol)
            info = ticker.fast_info
            price = _number(info.last_price)
            change = percent_change(price, info.previous_close)
            high_change = percent_change(info.day_high, info.previous_close)
            low_change = percent_change(info.day_low, info.previous_close)
            
            if price is None or change is None or high_change is None or low_change is None:
                raise ValueError("quote data incomplete")
            
            # 计算日内振幅
            intraday_amplitude = high_change - low_change
            
            results.append({
                "name": name,
                "price": price,
                "change": change,
                "intraday_amplitude": intraday_amplitude
            })
        except Exception as e:
            _log_failed_ticker(name, symbol, e, ticker)
            errors.append(f"{name}: 获取数据失败")

    # 排序：根据涨幅（change）降序排列
    results.sort(key=lambda x: x["change"], reverse=True)

    lines = ["📊 今日资产播报："]
    for r in results:
        # 根据涨跌选择图标
        icon = "💹" if r["change"] >= 0 else "🔻"
        # 格式化输出：名称:价格 图标 涨幅% ↕️振幅%
        lines.append(f"{r['name']}:{r['price']:.0f} {icon}{r['change']:.1f}%↕️{r['intraday_amplitude']:.0f}%")
    
    # 将错误信息追加在最后
    lines.extend(errors)
    return "\n".join(lines)

def yearly_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> str:
    """
    生成年度（52周）资产报告。
    按照 52 周振幅从高到低排序。
    """
    results = []
    errors = []
    for name, symbol in stocks.items():
        ticker = None
        try:
            ticker = ticker_factory(symbol)
            price = _number(ticker.fast_info.last_price)
            info = ticker.info
            high = _number(info.get("fiftyTwoWeekHigh"))
            low = _number(info.get("fiftyTwoWeekLow"))
            
            if price is None or high is None or low is None or low <= 0:
                raise ValueError("52-week data incomplete")
            
            # 计算 52 周振幅
            amplitude = (high - low) / low * 100
            
            results.append({
                "name": name,
                "price": price,
                "high": high,
                "low": low,
                "amplitude": amplitude
            })
        except Exception as e:
            _log_failed_ticker(name, symbol, e, ticker)
            errors.append(f"{name}: 获取数据失败")

    # 排序：根据年度振幅（amplitude）降序排列
    results.sort(key=lambda x: x["amplitude"], reverse=True)

    lines = ["📊 年度资产播报："]
    for r in results:
        # 格式化输出：名称:👆最高📢当前 🔻最低 ↕️振幅%
        lines.append(f"{r['name']}:👆{r['high']:.0f}📢{r['price']:.0f} 🔻{r['low']:.0f} ↕️{r['amplitude']:.0f}%")
    lines.extend(errors)
    return "\n".join(lines)

def market_cap_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> str:
    """
    生成市值报告。
    按照市值从大到小排序。
    """
    results = []
    errors = []
    for name, symbol in stocks.items():
        ticker = None
        try:
            ticker = ticker_factory(symbol)
            price = _number(ticker.fast_info.last_price)
            change = percent_change(price, ticker.fast_info.previous_close)
            market_cap = _number(ticker.info.get("marketCap"))
            
            if price is None or change is None or market_cap is None:
                raise ValueError("market cap data incomplete")
                
            results.append({
                "name": name,
                "price": price,
                "change": change,
                "market_cap": market_cap
            })
        except Exception as e:
            _log_failed_ticker(name, symbol, e, ticker)
            errors.append(f"{name}: 获取数据失败")

    # 排序：根据市值（market_cap）降序排列
    results.sort(key=lambda x: x["market_cap"], reverse=True)

    lines = ["📊 市值播报："]
    for r in results:
        icon = "💹" if r["change"] >= 0 else "🔻"
        # 格式化输出：名称:价格 图标 涨幅% ↕️市值（万亿）
        lines.append(f"{r['name']}:{r['price']:.0f} {icon}{r['change']:.0f}% ↕️{r['market_cap'] / 1e12:.2f}万亿")
    lines.extend(errors)
    return "\n".join(lines)

# AppleScript 脚本模板：用于在 MacOS 上控制微信发送消息
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
    """
    调用系统 osascript 命令执行 AppleScript，实现微信自动发消息。
    """
    for contact in contacts:
        try:
            subprocess.run(["osascript", "-e", _APPLESCRIPT, contact, content], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"微信消息发送失败 [{contact}]: {e}")

def is_active_hour(now: datetime | None = None, start: int = 7, end: int = 23) -> bool:
    """
    检查当前时间是否在活跃时间段内（默认 7点 到 23点）。
    """
    return start <= (now or datetime.now()).hour < end

def run_scheduler(job: Callable[[], None], interval_minutes: int, *, run_now: bool = True) -> None:
    """
    通用的简单调度器，按照指定分钟间隔运行任务。
    """
    import schedule

    if run_now:
        # 如果需要立即运行一次
        job()
    
    # 注册定时任务
    schedule.every(interval_minutes).minutes.do(job)
    
    # 循环检查并运行待处理的任务
    while True:
        schedule.run_pending()
        time.sleep(1)
