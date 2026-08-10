import yfinance as yf
import subprocess
import schedule
import time
from datetime import datetime
from Common import STOCKS

# 1. 核心格式转换方法
def format_stock_report(stocks_dict):
    report_lines = ["📊 年度资产播报："]

    for name, code in stocks_dict.items():
        try:
            t = yf.Ticker(code)

            # 使用 fast_info 获取最新价
            price = t.fast_info.last_price

            # 使用 t.info 获取52周（近一年）的最高价和最低价
            info = t.info
            year_high = info.get('fiftyTwoWeekHigh', price)
            year_low = info.get('fiftyTwoWeekLow', price)

            # 计算年内总振幅: (最高 - 最低) / 最低 * 100
            if year_low and year_low > 0:
                amplitude_year = ((year_high - year_low) / year_low) * 100
            else:
                amplitude_year = 0.0

            # 生成新格式：小米集团:27.62 今年最高👆🏻50 最低🔻20 ↕️60%
            line = f"{name}:{price:.2f} 👆🏻{year_high:.0f} 🔻{year_low:.0f} ↕️{amplitude_year:.0f}%"
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
    # 限制在 7:00 到 22:59 之间执行
    if 0 <= now.hour < 23:
        # 您的股票与商品资产列表
        stocks = STOCKS

        report = format_stock_report(stocks)
        target_contact = ["wodejinrongqun", "shuanglang"]
        send_wechat_msg(target_contact, report)
    else:
        print(f"[{now}] 不在执行时间段（7-23点），跳过本次执行。")

# 每 30 分钟轮询一次
# ⚠️ 注意：请确保当前运行目录下没有名为 "schedule.py" 的干扰文件！
job()
schedule.every(123).minutes.do(job)

print("定时任务已启动...")

while True:
    schedule.run_pending()
    time.sleep(1)
