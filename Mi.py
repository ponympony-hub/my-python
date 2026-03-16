import yfinance as yf

# 定义股票列表（注意：A股后缀 .SS 为上海，.SZ 为深圳）
stocks = {
    "贵州茅台": "600519.SS",
    "比亚迪": "002594.SZ",
    "宁德时代": "300750.SZ",
    "小米": "1810.HK"
}

# 打印表头
print(f"{'名称':<8} {'代码':<12} {'当前股价':<10} {'涨跌幅':<10} {'总市值 (亿元)':<12}")
print("-" * 65)

for name, code in stocks.items():
    ticker = yf.Ticker(code)

    # 1. 获取基本价格信息 (使用 fast_info 速度最快)
    info = ticker.fast_info
    current_price = info.last_price         # 当前价
    previous_close = info.previous_close   # 昨日收盘价

    # 2. 计算涨跌幅
    if previous_close:
        change_pct = (current_price - previous_close) / previous_close * 100
    else:
        change_pct = 0.0

    # 3. 获取市值并转换单位
    market_cap = ticker.info.get('marketCap', 0) / 1e8
    currency = info.currency

    # 4. 格式化输出 (根据涨跌正负添加符号)
    change_str = f"{'+' if change_pct > 0 else ''}{change_pct:.2f}%"

    print(f"{name:<8} {code:<12} {current_price:>8.2f} {change_str:>10} {market_cap:>14.2f} {currency}")
