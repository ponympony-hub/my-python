# 股票资产自动播报项目

这是一个专门为 Python 新手设计的股票资产自动监控与播报系统。它可以通过微信（MacOS 版）自动发送每日行情、年度波动和市值排行的报告。

## 📁 项目结构说明

优化的目录结构如下，旨在帮助你理解模块化开发的思想：

```text
my-python/
├── core/                # 核心逻辑文件夹
│   ├── config.py        # 配置文件：包含股票列表、微信联系人和时间设置
│   ├── reporting.py     # 核心功能：数据抓取、格式化、微信发送逻辑
│   └── utils.py         # 辅助工具：数据导出等通用类
├── jobs/                # 定时任务文件夹（独立脚本）
│   ├── daily_job.py     # 每日价格播报任务
│   ├── yearly_job.py    # 年度资产播报任务
│   ├── market_cap_job.py # 市值排行播报任务
│   └── export_tickers_job.py # 批量导出股票数据任务
├── tests/               # 测试文件夹
│   ├── test_reporting.py # 单元测试
│   └── test_utils.py    # 工具类测试
├── examples/            # 示例与旧代码存根（学习参考）
├── main.py              # 项目总入口：同时运行所有定时任务
├── requirements.txt     # 项目依赖列表
└── README.md            # 项目说明文档（本文件）
```

## 🚀 如何开始

1. **安装依赖**：
   在终端运行以下命令安装所需的库：
   ```bash
   pip install -r requirements.txt
   ```

2. **配置信息**：
   打开 `core/config.py`，按照注释说明修改你的股票列表和微信联系人。

3. **运行程序**：
   - 如果你想运行**完整系统**（包含所有任务）：
     ```bash
     python main.py
     ```
   - 如果你只想运行**某个特定任务**（例如今日播报）：
     ```bash
     python jobs/daily_job.py
     ```
   - 如果你想**批量导出所有股票数据**为 JSON5 文件：
     ```bash
     python jobs/export_tickers_job.py
     ```

## 📚 学习要点

本项目中包含了一些 Python 基础知识的实际应用，你可以通过阅读代码中的注释来学习：

- **模块导入**：如何使用 `import` 和路径管理。
- **错误处理**：使用 `try...except` 捕获异常，保证程序不因某只股票数据缺失而崩溃。
- **数据结构**：如何使用 `dict` (字典) 存储股票信息，使用 `list` (列表) 存储报告行。
- **自动化控制**：通过 AppleScript 控制桌面端软件。
- **定时调度**：使用 `schedule` 库管理周期性任务。

## ⚠️ 注意事项

- **微信版本**：本项目的自动发送功能基于 MacOS 的 AppleScript，需要 MacOS 环境并登录桌面版微信。
- **数据源**：使用 `yfinance` 获取行情，可能因网络环境需要科学上网或有一定的延迟。
