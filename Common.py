
import time
import random
import schedule
import S3Cur
import S4Year
import S5All


STOCKS = {
    "茅台": "600519.SS",
    "BYD": "002594.SZ",
    "宁德": "300750.SZ",
    "NVDA": "NVDA",
    "苹果": "AAPL",
    "TSLA": "TSLA",
    "小米": "1810.HK",
    "寒武": "688256.SS",
    "CRCL": "CRCL",
    "原油": "CL=F",
    "黄金": "GC=F",
    "白银": "SI=F",

    # --- 新追加的资产 ---
    "Mini": "0100.HK",      # 港股大模型新星
    "智谱": "2513.HK",         # 港股AI大模型
    "SPCX": "SPCX",            # 美股特殊目的收购ETF
    "TSM": "TSM",              # 台积电美股ADR
    "长鑫": "688825.SS",       # 长鑫存储
    "中芯": "688981.SS",     # 中芯国际 (A股科创板)
    "阿里": "9988.HK",       # 阿里巴巴 (港股)
    "腾讯": "0700.HK",         # 腾讯控股 (港股)
    "科创50": "588000.SS",      # 华夏科创50ETF (代表科创50指数)
    "泡泡": "9992.HK",       # 泡泡玛特 (港股)
    "兆易": "603986.SS",     # 兆易创新 (A股)
    "建滔": "1888.HK"      # 建滔积层板 (港股)
}

# 包装函数：增加随机时间延迟（0-15秒），彻底避免 API 并发锁死
def run_with_delay(job_func):
    delay = random.randint(0, 15)
    time.sleep(delay)
    job_func()

# 注册定时任务 (注意：do() 内部必须传函数名，不能带括号)
schedule.every(120).minutes.do(run_with_delay, S3Cur.job)
schedule.every(123).minutes.do(run_with_delay, S4Year.job)
schedule.every(130).minutes.do(run_with_delay, S5All.job)

print("定时任务已成功注册，正在等待首轮触发...")

while True:
    schedule.run_pending()
    time.sleep(1)
