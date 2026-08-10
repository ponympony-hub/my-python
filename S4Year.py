"""Send the 52-week range report to WeChat."""

from datetime import datetime

from config import ACTIVE_END_HOUR, ACTIVE_START_HOUR, STOCKS, TARGET_CONTACTS
from reporting import is_active_hour, run_scheduler, send_wechat_message, yearly_report


def format_stock_report(stocks_dict):
    return yearly_report(stocks_dict)


def job() -> None:
    now = datetime.now()
    if not is_active_hour(now, ACTIVE_START_HOUR, ACTIVE_END_HOUR):
        print(f"[{now}] 不在执行时间段（7-23点），跳过本次执行。")
        return
    send_wechat_message(TARGET_CONTACTS, format_stock_report(STOCKS))


def main() -> None:
    run_scheduler(job, 123)


if __name__ == "__main__":
    main()
