"""
项目总入口脚本。
同时启动多个不同频率的定时报告任务。
"""

import time
import schedule
from jobs.daily_job import job as daily_job
from jobs.yearly_job import job as yearly_job
from jobs.market_cap_job import job as market_cap_job
from jobs.earnings_job import job as earnings_job
from jobs.volume_job import job as volume_job

def main() -> None:
    """
    统一注册所有定时任务并进入循环执行状态。
    """
    print("正在初始化所有定时报告任务...")
    
    # 立即执行一次首轮任务，确保程序启动时就有输出
    earnings_job()
    volume_job()
    market_cap_job()
    daily_job()
    yearly_job()

    # 注册不同频率的定时任务
    # 使用 schedule 库提供的 DSL (领域特定语言) 风格
    schedule.every(120).minutes.do(daily_job)      # 每 120 分钟播报今日行情
    schedule.every(123).minutes.do(yearly_job)     # 每 123 分钟播报年度行情
    schedule.every(130).minutes.do(market_cap_job) # 每 130 分钟播报市值排行
    schedule.every(150).minutes.do(volume_job)     # 每 150 分钟播报成交额排行
    schedule.every(240).minutes.do(earnings_job)  # 每 分钟播报财报日历
    
    print("✅ 定时任务已成功注册，程序正在后台运行中...")
    print("提示：按 Ctrl+C 可以停止程序。")
    
    # 进入死循环，持续检查并运行任务
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
