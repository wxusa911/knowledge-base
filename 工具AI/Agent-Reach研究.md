# Agent-Reach 研究

## 项目简介

**给AI Agent装上互联网能力** - 让AI能读Twitter、Reddit、YouTube、小红书、抖音等

- ⭐ 3K+ Stars
- Python
- 完全免费（除了服务器代理~$1/月）
- 开源

---

## 核心功能

| 平台 | 装好即用 | 配置后解锁 |
|------|---------|-----------|
| 网页 | ✅ 任意网页阅读 | - |
| YouTube | ✅ 字幕提取+搜索 | - |
| RSS | ✅ 任意RSS源 | - |
| 全网搜索 | - | ✅ Exa免费搜索 |
| GitHub | ✅ 公开仓库 | ✅ 私有仓库/PR |
| Twitter/X | ✅ 读单条推文 | ✅ 搜索/发推 |
| B站 | ✅ 字幕+搜索 | ✅ (服务器也能用) |
| Reddit | - | ✅ 搜索+读帖子 |
| 小红书 | - | ✅ 阅读/搜索/评论 |
| 抖音 | - | ✅ 视频解析+无水印下载 |
| LinkedIn | - | ✅ Profile详情 |
| Boss直聘 | - | ✅ 职位搜索+打招呼 |

---

## 为什么有用

让AI Agent能：
- "帮我看看这个YouTube视频讲了什么" → 获取字幕+总结
- "搜一下推特上大家怎么评价这个产品" → 免费搜索
- "去Reddit看看有没有同样bug" → 读取帖子
- "看看小红书上这个品口碑" → 读取+搜索
- "帮我下这个抖音视频" → 无水印下载

---

## 当前技术选型

| 场景 | 工具 | 为什么 |
|------|------|--------|
| 读网页 | Jina Reader | 免费，无需API Key |
| 读推特 | xreach | Cookie登录，免费 |
| 视频字幕 | yt-dlp | 148K Stars，YouTube+B站通吃 |
| 全网搜索 | Exa (MCP) | AI语义搜索，免费 |
| GitHub | gh CLI | 官方工具 |
| RSS | feedparser | Python标准库 |
| 小红书 | xiaohongshu-mcp | Go，Docker一键部署 |
| 抖音 | douyin-mcp-server | MCP服务，无需登录 |

---

## 安装

```bash
# 一键安装
pip install agent-reach

# 或让AI Agent安装
帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

---

## 使用

不需要记命令，告诉Agent就行：
- "帮我看看这个链接" → 自动读取网页
- "这个视频讲了什么" → 提取字幕
- "搜一下GitHub上LLM框架" → 搜索仓库

---

## 对我们有什么用

1. **研究Polymarket** - 让AI直接搜Twitter/X上的讨论
2. **抖音运营** - 分析小红书、抖音内容
3. **竞品分析** - 追踪各平台舆情

---

## 参考

- GitHub: https://github.com/Panniantong/Agent-Reach
- 文档: https://github.com/Panniantong/Agent-Reach/blob/main/docs/README_en.md
