"""Backward-compatible entry point for the market-cap report.

Use ``jobs/daily_job.py``, ``jobs/yearly_job.py``, ``jobs/market_cap_job.py``, or ``main.py`` for new
automation.  This file no longer sends a stale report once per second.
"""

import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from jobs.market_cap_job import main


if __name__ == "__main__":
    main()
