# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

AI Signal Board - 高质量 AI/科技新闻聚合项目，支持静态网页展示、24h 增量更新、WaytoAGI 更新日志、OPML RSS 批量接入。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行新闻抓取（本地）
python scripts/update_news.py --output-dir data --window-hours 24 --rss-opml feeds/follow.opml

# 本地预览网页
python -m http.server 8080

# 运行测试
python -m unittest discover tests
```

## 架构说明

### 核心组件

- **数据抓取**: `scripts/update_news.py` - 从 10+ 个新闻源抓取内容，支持 RSS OPML 订阅
- **前端展示**: 纯静态页面（HTML + CSS + Vanilla JS），无框架依赖
- **自动化**: `.github/workflows/update-news.yml` - 每 30 分钟定时抓取并提交到 `data/`

### 数据流

1. `update_news.py` 从多个源抓取新闻 → 生成 `data/latest-24h.json`
2. 归档数据存入 `data/archive.json`
3. `index.html` 读取 JSON 在浏览器展示

### 关键文件

| 文件 | 用途 |
|------|------|
| `scripts/update_news.py` | 核心抓取逻辑 |
| `index.html` | 前端页面入口 |
| `assets/app.js` | 前端状态管理和渲染 |
| `data/*.json` | 抓取输出的数据文件 |
| `feeds/follow.example.opml` | OPML 订阅模板 |

### 环境配置

- 代理（可选）: `HTTP_PROXY` / `HTTPS_PROXY` 环境变量
- 私有 RSS: Base64 编码后存入 GitHub Secret `FOLLOW_OPML_B64`

### 测试

测试文件位于 `tests/` 目录，使用 `unittest` 框架。导入从 `scripts.update_news` 直接引用内部函数进行单元测试。
