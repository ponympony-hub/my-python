"""Backward-compatible entry point for the market-cap report.

Use ``S3Cur.py``, ``S4Year.py``, ``S5All.py``, or ``Common.py`` for new
automation.  This file no longer sends a stale report once per second.
"""

from S5All import main


if __name__ == "__main__":
    main()
