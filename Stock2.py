import yfinance as yf
import subprocess
import schedule
import time
from datetime import datetime

def get_crypto_data():
    """获取以太坊(ETH-USD)的最新价格、涨跌幅和日内振幅"""
    try:
        t = yf.Ticker("ETH-USD")
        info = t.fast_info

        price = info.last_price
        prev_close = info.previous_close
        day_high = info.day_high
        day_low = info.day_low

        # 计算涨跌幅
        change = ((price - prev_close) / prev_close) * 100
        # 计算日内振幅 (最高价 - 最低价) / 昨收价
        amplitude = ((day_high - day_low) / prev_close) * 100

        # 动态匹配正负号符号
        change_emoji = "💹" if change >= 0 else "🔻"
        change_sign = "+" if change > 0 else ""

        return f"ETH:{price:.2f} {change_emoji}{change_sign}{change:.1f}% ↕️{amplitude:.1f}%"
    except Exception as e:
        return f"ETH数据获取失败: {str(e)}"

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

def job():
    now = datetime.now()
    # 限制在 7:00 至 23:00 之间执行
    if 7 <= now.hour < 23:
        report = get_crypto_data()
        target_contact = ["wodejinrongqun", "shuanglang"]
        send_wechat_msg(target_contact, report)
    else:
        print(f"[{now}] 不在执行时间段（7-23点），跳过本次执行。")

# 每 30 分钟定时执行一次
schedule.every(30).minutes.do(job)

print("定时任务已启动...")

# 移除主循环中直接触发的 job() 以免启动时瞬间并发，完全交由 schedule 管理
while True:
    schedule.run_pending()
    time.sleep(1)
