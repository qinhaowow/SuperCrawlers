# SuperCrawler

SuperCrawler是一个多平台社交媒体爬虫系统，支持爬取小红书、抖音、快手等多个平台的内容。

## 功能特性

- **多平台支持**：支持小红书、抖音、快手等11个平台
- **异步编程**：使用asyncio实现异步爬取，提高效率
- **多存储方式**：支持文件、SQLite、MongoDB存储
- **代理管理**：支持代理池管理和轮换
- **监控系统**：实时监控系统状态和爬虫性能
- **调度系统**：支持定时任务和重复任务
- **浏览器自动化**：使用Playwright实现浏览器自动化
- **RESTful API**：提供Web API接口
- **命令行接口**：支持命令行操作

## 安装

### 依赖项

- Python 3.7+
- aiohttp
- asyncio
- playwright
- psutil
- fastapi
- uvicorn
- pymongo (可选，用于MongoDB存储)

### 安装步骤

1. 克隆仓库
2. 安装依赖
3. 安装Playwright浏览器驱动

```bash
# 克隆仓库
git clone <repository-url>

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器驱动
playwright install
```

## 使用方法

### 命令行使用

```bash
# 搜索小红书内容
python -m src.supercrawler --platform xhs --crawler-type search --query "美食"

# 获取内容详情
python -m src.supercrawler --platform xhs --crawler-type detail --content-id <content-id>

# 获取用户信息
python -m src.supercrawler --platform xhs --crawler-type creator --user-id <user-id>
```

### Web API使用

启动Web API服务：

```bash
python -m src.api.web.app
```

然后访问：
- API文档：http://localhost:8000/docs
- 平台列表：http://localhost:8000/platforms
- 爬虫执行：POST http://localhost:8000/crawl
- 系统统计：http://localhost:8000/stats
- 健康检查：http://localhost:8000/health

## 配置

配置文件位于 `src/config/base_config.py`，可以根据需要修改配置参数。

## 支持的平台

| 平台代码 | 平台名称 | 支持的功能 |
|---------|---------|-----------|
| xhs     | 小红书   | 搜索、内容详情、评论、用户资料、用户内容 |
| dy      | 抖音     | 搜索、内容详情、评论、用户资料、用户内容 |
| ks      | 快手     | 搜索、内容详情、评论、用户资料、用户内容 |

## 项目结构

```
src/
├── api/            # API模块
│   ├── cli/        # 命令行接口
│   └── web/        # Web API
├── browser/        # 浏览器管理
├── config/         # 配置
├── core/           # 核心模块
├── monitoring/     # 监控系统
├── proxy/          # 代理管理
├── scheduler/      # 调度系统
├── spiders/        # 爬虫实现
│   └── platforms/  # 平台爬虫
├── storage/        # 存储系统
└── utils/          # 工具函数
```

## 贡献

欢迎贡献代码，提交问题和功能请求。

## 许可证

本项目使用非商业学习许可证 1.1