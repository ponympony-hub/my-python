import yfinance as yf
import subprocess
import schedule
import time
from datetime import datetime

from Common import STOCKS


# 当前涨跌幅
# 1. 核心格式转换方法
def format_stock_report(stocks_dict):
    report_lines = ["📊 市值播报："]

    for name, code in stocks_dict.items():
        try:
            t = yf.Ticker(code)
            info = t.fast_info

            price = info.last_price
            prev_close = info.previous_close

            # 计算涨跌幅与日内振幅
            change = ((price - prev_close) / prev_close) * 100

            # 动态匹配涨跌图标与正负号
            change_emoji = "💹" if change >= 0 else "🔻"
            mkt_cap = t.info.get('marketCap', 0) / 1e12

            # 生成单行格式：名称:价格 💹+X.X% ↕️X.X%
            line = f"{name}:{price:.2f} {change_emoji}{change:.1f}% ↕️{mkt_cap:.2f}万亿"
            report_lines.append(line)

        except Exception as e:
            report_lines.append(f"{name}: 获取数据失败")

    return "\n".join(report_lines)

# 2. AppleScript 微信发送逻辑
def build_script(msg, groups):
    script_lines = [get_scr_pre()]
    step = ""
    for group in groups:
        step += f"""
        delay 1
        set the clipboard to "{group}"
        keystroke "f" using command down
        delay 1
        keystroke "v" using {{command down}}
        key code 36
        delay 1
        set the clipboard to "{msg}"
        key code 36
        key code 36
        delay 1
        keystroke "v" using {{command down}}
        key code 36
        """
    script_lines.append(step)
    script_lines.append("\nend tell")
    return "\n".join(script_lines)

def get_scr_pre():
    return """
    tell application "WeChat"
        activate
        delay 1
    end tell

    tell application "System Events" to tell process "WeChat"
        set frontmost to true
    """

def send_wechat_msg(contact, content):
    final_script = build_script(content, contact)
    subprocess.run(["osascript", "-e", final_script])

# 3. 定时任务配置
def job():
    now = datetime.now()
    # 修正了判断逻辑：7:00 到 22:59 之间执行
    if 0 <= now.hour < 23:
        # 您的原始股票与商品资产列表
        stocks = STOCKS

        report = format_stock_report(stocks)
        target_contact = ["wodejinrongqun", "shuanglang"]
        send_wechat_msg(target_contact, report)
    else:
        print(f"[{now}] 不在执行时间段（7-23点），跳过本次执行。")

# 每 30 分钟轮询一次
job()
schedule.every(130).minutes.do(job)

print("定时任务已启动...")

# 移除了死循环中直接触发的 job()，防止刚启动时瞬间并发，完全交由 schedule 的 30 分钟规则控制
while True:
    schedule.run_pending()
    time.sleep(1)

