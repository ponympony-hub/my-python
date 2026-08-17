"""
辅助工具模块：包含数据导出、文件处理等通用工具类。
"""

import json
import os
import re
from typing import Mapping, Any, Dict
from datetime import datetime
from core.config import STOCKS
from core.reporting import _ticker, _log_failed_ticker

# 股票字段中文注释映射表，用于增强导出的 json5 文件的可读性
COMMENT_MAP = {
    "address1": "地址1",
    "address2": "地址2",
    "city": "城市",
    "zip": "邮编",
    "country": "国家",
    "phone": "电话",
    "website": "官方网站",
    "industry": "行业",
    "industryKey": "行业键",
    "industryDisp": "行业显示名称",
    "sector": "板块",
    "sectorKey": "板块键",
    "sectorDisp": "板块显示名称",
    "longBusinessSummary": "公司业务摘要",
    "fullTimeEmployees": "全职员工人数",
    "companyOfficers": "公司高管",
    "maxAge": "数据最大有效时长",
    "name": "姓名",
    "age": "年龄",
    "title": "职位",
    "yearBorn": "出生年份",
    "fiscalYear": "财年",
    "exercisedValue": "已行权价值",
    "unexercisedValue": "未行权价值",
    "auditRisk": "审计风险",
    "boardRisk": "董事会风险",
    "compensationRisk": "薪酬风险",
    "shareHolderRightsRisk": "股东权益风险",
    "overallRisk": "综合风险",
    "governanceEpochDate": "治理数据时间戳",
    "compensationAsOfEpochDate": "薪酬数据截止时间戳",
    "executiveTeam": "执行团队",
    "priceHint": "价格小数位提示",
    "previousClose": "昨日收盘价",
    "open": "今日开盘价",
    "dayLow": "当日最低价",
    "dayHigh": "当日最高价",
    "regularMarketPreviousClose": "常规市场昨日收盘价",
    "regularMarketOpen": "常规市场今日开盘价",
    "regularMarketDayLow": "常规市场当日最低价",
    "regularMarketDayHigh": "常规市场当日最高价",
    "payoutRatio": "股利支付率",
    "beta": "贝塔系数",
    "trailingPE": "滚动市盈率 (TTM)",
    "forwardPE": "预测市盈率",
    "volume": "成交量",
    "regularMarketVolume": "常规市场成交量",
    "averageVolume": "平均成交量",
    "averageVolume10days": "10日平均成交量",
    "averageDailyVolume10Day": "10日日均成交量",
    "bid": "买入价",
    "ask": "卖出价",
    "bidSize": "买盘量",
    "askSize": "卖盘量",
    "marketCap": "总市值",
    "nonDilutedMarketCap": "非稀释市值",
    "fiftyTwoWeekLow": "52周最低价",
    "fiftyTwoWeekHigh": "52周最高价",
    "allTimeHigh": "历史最高价",
    "allTimeLow": "历史最低价",
    "priceToSalesTrailing12Months": "市销率 (TTM)",
    "fiftyDayAverage": "50日均价",
    "twoHundredDayAverage": "200日均价",
    "trailingAnnualDividendRate": "年度股息率",
    "trailingAnnualDividendYield": "年度股息收益率",
    "currency": "交易货币",
    "tradeable": "是否可交易",
    "enterpriseValue": "企业价值 (EV)",
    "profitMargins": "利润率",
    "floatShares": "流通股本",
    "sharesOutstanding": "发行在外股份总数",
    "heldPercentInsiders": "内部人士持股比例",
    "heldPercentInstitutions": "机构持股比例",
    "impliedSharesOutstanding": "隐含发行在外股份",
    "bookValue": "每股净资产",
    "priceToBook": "市净率 (P/B)",
    "lastFiscalYearEnd": "上个财年结束日",
    "nextFiscalYearEnd": "下个财年结束日",
    "mostRecentQuarter": "最近一个季度日",
    "earningsQuarterlyGrowth": "季度盈利增长",
    "netIncomeToCommon": "归属于普通股股东的净利润",
    "trailingEps": "滚动每股收益 (EPS TTM)",
    "forwardEps": "预测每股收益",
    "pegRatio": "PEG比率",
    "enterpriseToRevenue": "企业价值/营收比",
    "enterpriseToEbitda": "企业价值/EBITDA比",
    "52WeekChange": "52周价格变动",
    "SandP52WeekChange": "标普500指数52周变动",
    "quoteType": "报价类型",
    "currentPrice": "当前价格",
    "targetHighPrice": "目标最高价",
    "targetLowPrice": "目标最低价",
    "targetMeanPrice": "目标平均价",
    "targetMedianPrice": "目标中位价",
    "recommendationMean": "建议平均值",
    "recommendationKey": "推荐评级",
    "numberOfAnalystOpinions": "分析师人数",
    "totalCash": "现金总额",
    "totalCashPerShare": "每股现金",
    "ebitda": "EBITDA",
    "totalDebt": "总债务",
    "quickRatio": "速动比率",
    "currentRatio": "流动比率",
    "totalRevenue": "总营收",
    "debtToEquity": "债务权益比",
    "revenuePerShare": "每股营收",
    "returnOnAssets": "资产回报率 (ROA)",
    "returnOnEquity": "权益回报率 (ROE)",
    "grossProfits": "毛利润",
    "freeCashflow": "自由现金流",
    "operatingCashflow": "经营现金流",
    "earningsGrowth": "盈利增长",
    "revenueGrowth": "营收增长",
    "grossMargins": "毛利率",
    "ebitdaMargins": "EBITDA利润率",
    "operatingMargins": "营业利润率",
    "financialCurrency": "财务报表货币",
    "symbol": "股票代码",
    "language": "语言",
    "region": "地区",
    "typeDisp": "资产类型显示",
    "quoteSourceName": "报价来源",
    "triggerable": "是否可触发",
    "customPriceAlertConfidence": "自定义价格警报信心度",
    "exchange": "交易所代码",
    "messageBoardId": "留言板ID",
    "exchangeTimezoneName": "交易所时区",
    "exchangeTimezoneShortName": "时区简称",
    "gmtOffSetMilliseconds": "GMT偏移毫秒",
    "market": "市场类别",
    "esgPopulated": "是否填充ESG数据",
    "hasPrePostMarketData": "是否有盘前盘后数据",
    "firstTradeDateMilliseconds": "首次交易日期时间戳",
    "regularMarketChange": "常规市场价格变动",
    "regularMarketDayRange": "常规市场当日价格范围",
    "fullExchangeName": "交易所全称",
    "averageDailyVolume3Month": "3个月日均成交量",
    "fiftyTwoWeekLowChange": "较52周低点的变动",
    "fiftyTwoWeekLowChangePercent": "较52周低点的变动百分比",
    "fiftyTwoWeekRange": "52周价格范围",
    "fiftyTwoWeekHighChange": "较52周高点的变动",
    "fiftyTwoWeekHighChangePercent": "较52周高点的变动百分比",
    "fiftyTwoWeekChangePercent": "52周价格变动百分比",
    "longName": "公司正式名称",
    "regularMarketChangePercent": "常规市场变动百分比",
    "regularMarketPrice": "常规市场当前价格",
    "shortName": "公司简称",
    "earningsTimestamp": "财报时间戳",
    "earningsTimestampStart": "财报发布起始时间戳",
    "earningsTimestampEnd": "财报发布截止时间戳",
    "earningsCallTimestampStart": "财报电话会议起始时间戳",
    "earningsCallTimestampEnd": "财报电话会议截止时间戳",
    "isEarningsDateEstimate": "财报日期是否为估计值",
    "epsTrailingTwelveMonths": "过去12个月每股收益",
    "epsForward": "预测每股收益",
    "epsCurrentYear": "本年度每股收益",
    "priceEpsCurrentYear": "本年度股价/EPS比",
    "fiftyDayAverageChange": "50日均价变动",
    "fiftyDayAverageChangePercent": "50日均价变动百分比",
    "twoHundredDayAverageChange": "200日均价变动",
    "twoHundredDayAverageChangePercent": "200日均价变动百分比",
    "sourceInterval": "数据源更新间隔",
    "exchangeDataDelayedBy": "交易所数据延迟（分钟）",
    "averageAnalystRating": "平均分析师评级",
    "cryptoTradeable": "是否支持加密货币交易",
    "marketState": "市场状态",
    "corporateActions": "公司行为",
    "regularMarketTime": "常规市场时间戳",
    "trailingPegRatio": "滚动PEG比率",
    # 额外模块字段
    "fast_info": "快速元数据",
    "calendar": "财报日历",
    "news": "最新相关新闻",
    "actions": "分红及拆股历史",
    "major_holders": "主要持股人信息",
    "institutional_holders": "机构持股人信息",
    "recommendations": "机构推荐建议",
    "last_price": "最新价格",
    "change": "涨跌幅",
    "year_high": "52周最高点",
    "year_low": "52周最低点",
    "year_change": "年度变动"
}

class TickerExporter:
    """
    股票数据导出工具类。
    功能：实现将配置文件中所有股票的完整数据导出为带中文注释的 JSON5 格式文件。
    """

    def __init__(self, stocks: Mapping[str, str] = STOCKS, output_dir: str = "json"):
        """
        初始化导出器。
        :param stocks: 股票名称与代码的映射字典，默认为 config.py 中的 STOCKS。
        :param output_dir: 文件保存的目录，默认为项目根目录下的 'json' 文件夹。
        """
        self.stocks = stocks
        self.output_dir = output_dir

    def _convert_to_serializable(self, obj: Any) -> Any:
        """
        将不可序列化的对象（如 DataFrame, Timestamp）转换为标准 Python 类型。
        同时保留 int, float, bool 等基本类型。
        """
        if isinstance(obj, (int, float, bool, str)) or obj is None:
            return obj
        
        import pandas as pd
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        if isinstance(obj, pd.Series):
            return obj.to_dict()
        if hasattr(obj, "to_pydatetime"): # 处理 pandas Timestamp
            return obj.isoformat()
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        # 兜底处理：尝试转换为字符串
        try:
            return str(obj)
        except:
            return None

    def _add_comments(self, json_str: str) -> str:
        """
        逐行解析 JSON 字符串，并根据字段名添加对应的中文注释。
        """
        lines = json_str.split("\n")
        new_lines = []
        for line in lines:
            # 使用正则表达式提取字段键名 (例如 "symbol":)
            match = re.search(r'"(\w+)":', line)
            if match:
                key = match.group(1)
                if key in COMMENT_MAP:
                    # 在行尾直接追加注释
                    line = line + f" // {COMMENT_MAP[key]}"
            new_lines.append(line)
        return "\n".join(new_lines)

    def export_all(self) -> None:
        """
        遍历所有股票，获取完整数据并逐个生成带注释的 json5 文件。
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建目录: {self.output_dir}")

        for name, symbol in self.stocks.items():
            print(f"--- 正在处理: {name} ({symbol}) ---")
            ticker = None
            try:
                ticker = _ticker(symbol)
                
                # 整合多项数据源
                full_data = {
                    "info": ticker.info,
                    "news": ticker.news,
                }

                # 尝试获取 fast_info (包含实时性较强的数据)
                try:
                    fi = ticker.fast_info
                    full_data["fast_info"] = {k: self._convert_to_serializable(v) for k, v in fi.items()}
                except:
                    pass

                # 尝试获取日历信息
                try:
                    cal = ticker.calendar
                    if cal is not None:
                        full_data["calendar"] = self._convert_to_serializable(cal)
                except:
                    pass

                # 尝试获取公司动作 (分红/拆股)
                try:
                    actions = ticker.actions
                    if not actions.empty:
                        full_data["actions"] = self._convert_to_serializable(actions)
                except:
                    pass

                if not full_data["info"]:
                    raise ValueError("获取到的核心 info 为空")

                # 生成文件名
                filename = f"{name}.json5"
                file_path = os.path.join(self.output_dir, filename)

                # 序列化为 JSON 字符串
                # 使用 default 参数处理可能遗漏的复杂类型
                json_content = json.dumps(
                    full_data, 
                    indent=2, 
                    ensure_ascii=False, 
                    default=self._convert_to_serializable
                )

                # 添加中文注释
                annotated_content = self._add_comments(json_content)

                # 写入文件
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(annotated_content)
                
                print(f"成功导出: {file_path}")
            
            except Exception as e:
                _log_failed_ticker(name, symbol, e, ticker)
                print(f"❌ 导出 {name} 失败: {e}")

if __name__ == "__main__":
    exporter = TickerExporter()
    exporter.export_all()
