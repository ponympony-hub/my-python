import yfinance as yf
import subprocess
import schedule
import time
from datetime import datetime

# 方法在前
def build_script(msg, groups):
    # 假设 get_scr_pre() 返回 "tell application \"System Events\"" 之类的启动语句
    script_lines = [get_scr_pre()]
    for group in groups:
        # 使用 f-string 填充变量
        step = f"""
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

    # 将所有列表元素合并为一个长字符串
    return "\n".join(script_lines)

def job():
    now = datetime.now()
    # 检查当前小时是否在 7:00 到 23:00 之间
    if 7 <= now.hour <= 23:
        # 执行你的发送任务
        target_contact = ["小助手", "shuanglang"]  # <--- 改成你想发送的人名
        send_wechat_msg(target_contact, report)
    else:
        print(f"[{now}] 不在执行时间段（7-23点），跳过本次执行。")

# 获取前置脚本：微信
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
    """通过 AppleScript 将消息发送给微信"""
    final_script = build_script(content, contact)
    subprocess.run(["osascript", "-e", final_script])


# 1. 抓取数据
stocks = {
    "贵州茅台": "600519.SS",
    "比亚迪": "002594.SZ",
    "宁德时代": "300750.SZ",
    "英伟达": "NVDA",
    "苹果": "AAPL",
    "特斯拉": "TSLA",
    "小米集团": "1810.HK",
    "寒武纪": "688256.SS",
    "CRCL": "CRCL",
    "原油 (WTI期货)": "CL=F",
    "黄金 (现货/主力期货)": "GC=F",
    "白银 (现货/主力期货)": "SI=F"
}
report = "📊 今日股价播报：\n"

for name, code in stocks.items():
    t = yf.Ticker(code)
    info = t.fast_info
    price = info.last_price
    change = (price - info.previous_close) / info.previous_close * 100
    mkt_cap = t.info.get('marketCap', 0) / 1e8

    change_str = f"{'+' if change > 0 else ''}{change:.2f}%"
    report += f"{name}: {price:.2f} ({change_str}), 市值:{mkt_cap:.0f}亿\n"

# 2. 执行发送（确保你的微信已登录）
# 每 30 分钟执行一次 job 函数
# schedule.every(30).minutes.do(job)
#
# print("定时任务已启动...")
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

job()