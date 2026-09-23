"""
核心业务逻辑模块：包含数据格式化、飞书消息推送和调度工具。
本模块设计为无副作用导入，方便在各个任务脚本和测试中复用。
"""

from __future__ import annotations

import json
import logging
import sys
import time
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
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

# ==================== 结构化报告 ====================

@dataclass
class Report:
    """
    结构化报告：标题 + 表格列定义 + 数据行。
    用于渲染成飞书表格卡片。
    """
    title: str
    columns: list[dict]
    rows: list[dict] = field(default_factory=list)


def _col(name: str, display: str, data_type: str = "text", width: int = 100) -> dict:
    """表格列定义（data_type 用 lark_md 可渲染加粗/彩色，width 单位为像素）"""
    return {"name": name, "display_name": display, "data_type": data_type, "width": width}


def _pct(v: float, digits: int = 1) -> str:
    """百分数字符串，带正负号，例如 +10.0% / -3.0%"""
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.{digits}f}%"


def _icon(v: float) -> str:
    """涨跌图标：涨=💹 跌=🔻"""
    return "💹" if v >= 0 else "🔻"


def daily_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> Report:
    """
    生成每日资产报告（结构化表格）。
    按照当日涨幅从高到低排序。
    """
    results = []
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

    # 排序：根据涨幅（change）降序排列
    results.sort(key=lambda x: x["change"], reverse=True)

    columns = [
        _col("name", "名称", "lark_md", 90),
        _col("price", "现价", "text", 90),
        _col("change", "涨跌幅", "lark_md", 110),
        _col("amplitude", "振幅", "text", 90),
    ]
    rows = []
    for r in results:
        rows.append({
            "name": f"**{r['name']}**",
            "price": f"{r['price']:.0f}",
            "change": f"{_icon(r['change'])}{_pct(r['change'])}",
            "amplitude": f"{r['intraday_amplitude']:.0f}%",
        })
    return Report("📊 今日资产播报", columns, rows)


def yearly_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> Report:
    """
    生成年度（52周）资产报告（结构化表格）。
    按照 52 周振幅从高到低排序。
    """
    results = []
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

    # 排序：根据年度振幅（amplitude）降序排列
    results.sort(key=lambda x: x["amplitude"], reverse=True)

    columns = [
        _col("name", "名称", "lark_md", 90),
        _col("high", "52周高", "text", 100),
        _col("price", "现价", "text", 90),
        _col("low", "52周低", "text", 100),
        _col("amplitude", "振幅", "text", 90),
    ]
    rows = []
    for r in results:
        rows.append({
            "name": f"**{r['name']}**",
            "high": f"{r['high']:.0f}",
            "price": f"{r['price']:.0f}",
            "low": f"{r['low']:.0f}",
            "amplitude": f"{r['amplitude']:.0f}%",
        })
    return Report("📊 年度资产播报", columns, rows)


def market_cap_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> Report:
    """
    生成市值报告（结构化表格）。
    按照市值从大到小排序。
    """
    results = []
    for name, symbol in stocks.items():
        ticker = None
        try:
            ticker = ticker_factory(symbol)
            price = _number(ticker.fast_info.last_price)
            change = percent_change(price, ticker.fast_info.previous_close)
            market_cap = _number(ticker.info.get("nonDilutedMarketCap"))

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

    # 排序：根据市值（market_cap）降序排列
    results.sort(key=lambda x: x["market_cap"], reverse=True)

    columns = [
        _col("name", "名称", "lark_md", 90),
        _col("price", "现价", "text", 90),
        _col("change", "涨跌幅", "lark_md", 110),
        _col("market_cap", "市值(万亿)", "text", 110),
    ]
    rows = []
    for r in results:
        rows.append({
            "name": f"**{r['name']}**",
            "price": f"{r['price']:.0f}",
            "change": f"{_icon(r['change'])}{_pct(r['change'])}",
            "market_cap": f"{r['market_cap'] / 1e12:.2f}",
        })
    return Report("📊 市值播报", columns, rows)


def earnings_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> Report:
    """
    生成财报时间报告（结构化表格）。
    按照财报时间从近到远排序，格式化为 UTC+8 可读时间，精确到分钟。
    """
    results = []
    # 定义 UTC+8 时区 (东八区)
    tz_utc8 = timezone(timedelta(hours=8))

    # 获取当前 Unix 时间戳
    now_ts = time.time()

    for name, symbol in stocks.items():
        ticker = None
        try:
            ticker = ticker_factory(symbol)
            # 获取财报时间戳 (earningsTimestampStart)
            ts = ticker.info.get("earningsTimestampStart")

            if ts is None:
                raise ValueError("earnings timestamp not found")

            # 过滤掉早于当前时间的时间点
            if ts < now_ts:
                continue

            # 将 Unix 时间戳转换为 UTC+8 格式的 datetime 对象
            dt = datetime.fromtimestamp(ts, tz=tz_utc8)
            # 格式化为可读字符串，精确到分钟
            formatted_time = dt.strftime("%Y-%m-%d %H:%M")

            results.append({
                "name": name,
                "timestamp": ts,
                "time": formatted_time
            })
        except Exception as e:
            _log_failed_ticker(name, symbol, e, ticker)

    # 排序：按照时间戳从小到大排列（最近的财报时间在前面）
    results.sort(key=lambda x: x["timestamp"])

    columns = [
        _col("name", "名称", "lark_md", 120),
        _col("time", "财报时间", "text", 160),
    ]
    rows = [{"name": f"**{r['name']}**", "time": r["time"]} for r in results]
    return Report("📅 财报日历播报", columns, rows)


def volume_report(stocks: Mapping[str, str], ticker_factory: Callable[[str], Any] = _ticker) -> Report:
    """
    生成成交额报告（结构化表格）。
    成交额 = 当前价格 * 当日成交量。
    按照成交额从大到小排序。
    """
    results = []
    for name, symbol in stocks.items():
        ticker = None
        try:
            ticker = ticker_factory(symbol)
            fast_info = ticker.fast_info
            price = _number(fast_info.last_price)
            # 优先尝试从 fast_info 获取当日成交量
            volume = _number(getattr(fast_info, "day_volume", None))

            # 兜底：尝试从 info 获取成交量
            if volume is None:
                volume = _number(ticker.info.get("volume"))

            avg_vol_10d = _number(ticker.info.get("averageDailyVolume10Day"))
            prev_close = _number(fast_info.previous_close)

            if price is None or volume is None or avg_vol_10d is None or prev_close is None:
                raise ValueError("volume or price data incomplete")

            # 计算成交额
            amount = price * volume
            # 计算10日平均成交额
            avg_amount_10d = price * avg_vol_10d
            # 计算涨跌幅，用于选择图标
            change = percent_change(price, prev_close)

            results.append({
                "name": name,
                "amount": amount,
                "avg_amount_10d": avg_amount_10d,
                "change": change
            })
        except Exception as e:
            _log_failed_ticker(name, symbol, e, ticker)

    # 排序：根据成交额（amount）降序排列
    results.sort(key=lambda x: x["amount"], reverse=True)

    columns = [
        _col("name", "名称", "lark_md", 100),
        _col("amount", "成交额(亿)", "text", 110),
        _col("avg_amount", "10日均额(亿)", "text", 120),
        _col("change", "涨跌", "lark_md", 80),
    ]
    rows = []
    for r in results:
        rows.append({
            "name": f"**{r['name']}**",
            "amount": f"{r['amount'] / 1e8:.2f}",
            "avg_amount": f"{r['avg_amount_10d'] / 1e8:.2f}",
            "change": _icon(r["change"]),
        })
    return Report("📊 今日成交额排行", columns, rows)


# ==================== 飞书消息推送 ====================

def build_table_card(report: Report) -> dict:
    """构建飞书 interactive 表格卡片（内容居中、列宽固定紧凑）。"""
    table = {
        "tag": "table",
        "page_size": 50,
        "row_height": "low",
        "text_align": "center",
        "header_style": {"text_align": "center", "background_style": "grey", "bold": True, "lines": 1},
        "columns": report.columns,
        "rows": report.rows,
    }
    card = {
        "schema": "2.0",
        "header": {"template": "blue", "title": {"tag": "plain_text", "content": report.title}},
        "body": {"elements": [table, {"tag": "markdown", "content": "🔗 数据来源：yfinance 行情"}]},
    }
    return {"msg_type": "interactive", "card": card}


def send_feishu_table_message(webhook: str, report: Report) -> bool:
    """发送飞书表格卡片到指定 Webhook。返回 True 表示发送成功。"""
    return _post_feishu(webhook, build_table_card(report))


def send_feishu_text_message(webhook: str, title: str, content: str) -> bool:
    """发送飞书文本卡片（非表格内容，如早安问候）到指定 Webhook。"""
    card = {
        "schema": "2.0",
        "header": {"template": "blue", "title": {"tag": "plain_text", "content": title}},
        "body": {"elements": [{"tag": "markdown", "content": content}]},
    }
    return _post_feishu(webhook, {"msg_type": "interactive", "card": card})


def _post_feishu(webhook: str, payload: dict) -> bool:
    """向飞书自定义机器人 Webhook 发送 JSON 消息。"""
    try:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            webhook,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
        ok = '"code":0' in body
        logger.info(f"飞书消息发送{'成功' if ok else '失败'}: {body}")
        return ok
    except Exception as e:
        logger.error(f"飞书消息发送失败: {e}")
        return False


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
