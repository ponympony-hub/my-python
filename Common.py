"""Run all reports from one scheduler without circular imports or duplicate loops."""

import time

from S3Cur import job as current_price_job
from S4Year import job as yearly_job
from S5All import job as market_cap_job


def main() -> None:
    import schedule

    schedule.every(120).minutes.do(current_price_job)
    schedule.every(123).minutes.do(yearly_job)
    schedule.every(130).minutes.do(market_cap_job)
    print("定时任务已成功注册，正在等待首轮触发...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
