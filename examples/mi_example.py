# 定义股票列表（注意：A股后缀 .SS 为上海，.SZ 为深圳）
stocks = {
    # "贵州茅台": "600519.SS",
    # "比亚迪": "002594.SZ",
    # "宁德时代": "300750.SZ",
    "科创50": "000688.SS",
    "长鑫": "688825.SS",
    "小米": "1810.HK"
}

def main() -> None:
    import json
    import yfinance as yf

    print(f"{'名称':<8} {'代码':<12} {'当前股价':<10} {'涨跌幅':<10} {'总市值 (亿元)':<12}")
    print("-" * 65)
    for name, code in stocks.items():
        try:
            ticker = yf.Ticker(code)
            # 转换为 JSON 字符串（注意：这里使用 .info 获取包含完整数据的字典）
            # ensure_ascii=False 可以让中文字符正常显示，而不是显示为 unicode 编码
            json_str = json.dumps(ticker.info, ensure_ascii=False, indent=4)
            print(json_str)

            info = ticker.fast_info

            current_price = info.last_price
            previous_close = info.previous_close
            change_pct = (current_price - previous_close) / previous_close * 100 if previous_close else 0.0
            market_cap = ticker.info.get("marketCap", 0) / 1e8
            print(f"{name:<8} {code:<12} {current_price:>8.2f} {change_pct:>+9.2f}% {market_cap:>14.2f} {info.currency}")
        except Exception as e:
            print(f"{name:<8} {code:<12} 获取数据失败: {e}")


if __name__ == "__main__":
    main()
