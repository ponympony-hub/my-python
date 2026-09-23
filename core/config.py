"""
项目共享配置模块：存储股票列表、飞书机器人 Webhook 以及调度时间设置。
"""

# 股票列表配置
# 键 (Key): 报告中显示的名称
# 值 (Value): yfinance 使用的股票代码 (A股上证后缀 .SS, 深证后缀 .SZ, 港股后缀 .HK)
STOCKS = {
    "茅台": "600519.SS",
    "宇树🌲": "688836.SS",
    "长鑫": "688825.SS",
    "中芯": "688981.SS",
    "BYD": "002594.SZ",
    "宁德": "300750.SZ",
    "科创50": "000688.SS",
    "兆易": "603986.SS",
    "寒武": "688256.SS",
    "NVDA": "NVDA",
    "镁光": "MU",
    "闪迪": "SNDK",
    "海力士": "SKHY",
    "🍎": "AAPL",
    "三星": "SMSD",
    "🕷️": "MRVL",
    "🚗": "TSLA",
    "小米": "1810.HK",
    "CRCL": "CRCL",
    "⛽️": "CL=F",
    "🏅": "GC=F",
    "🥈": "SI=F",
    "🚀": "SPCX",
    "TSM": "TSM",
    "Mini": "0100.HK",
    "智谱": "2513.HK",
    "阿里": "9988.HK",
    "🐧": "0700.HK",
    "泡泡": "9992.HK",
    "建滔": "1888.HK",
    "BTC": "BTC",
}

# 飞书自定义机器人 Webhook（与 wealth-code 项目 COMMON_BOT 保持一致）
# 如需推送到不同群/机器人，可分别修改下面各任务的 Webhook
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/8e123b17-76ff-42ef-a8ea-c520b5fb0d7c"

# 各定时任务的推送目标，默认统一推到 FEISHU_WEBHOOK
DAILY_WEBHOOK = FEISHU_WEBHOOK
YEARLY_WEBHOOK = FEISHU_WEBHOOK
MARKET_CAP_WEBHOOK = FEISHU_WEBHOOK
EARNINGS_WEBHOOK = FEISHU_WEBHOOK
VOLUME_WEBHOOK = FEISHU_WEBHOOK
GREETING_WEBHOOK = FEISHU_WEBHOOK

# 活跃时间段设置 (24小时制)
# 程序仅在此时间范围内发送报告，避免深夜打扰
ACTIVE_START_HOUR = 7  # 开始时间：早上 7 点
ACTIVE_END_HOUR = 23    # 结束时间：晚上 11 点
