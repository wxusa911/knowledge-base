# Polymarket AI Agent 官方框架详解

> 更新时间: 2026-03-01
> 来源: Twitter/X 英文社区 + GitHub

---

## 🎯 什么是 Polymarket Agents

Polymarket 官方发布的 **AI Agent 框架**，让你的 AI 可以自动交易预测市场。

> "Autonomous AI agents are now trading on Polymarket in an attempt to subsidize their token costs."

---

## 🔥 热点案例

| 案例 | 收益 | 说明 |
|------|------|------|
| AI Agent 交易实验 | $10 → ? | 官方实验项目 |
| AI 概率模型交易 | $2.2M (2个月) | 完全自动化 |
| Claude Code 交易 bot | $195K (1个月) | 500笔/周 |

---

## 🛠️ 官方资源

### GitHub 仓库

| 仓库 | 说明 |
|------|------|
| [Polymarket/agents](https://github.com/Polymarket/agents) | **AI Agent 框架** - 官方 |
| [Polymarket/py-clob-client](https://github.com/Polymarket/py-clob-client) | Python SDK - 交易用 |
| [polymarket-websocket-client](https://github.com/polymarket/polymarket-websocket-client) | 实时 WebSocket 数据 |

### 文档
- https://docs.polymarket.com

---

## 🤖 AI Agent 交易原理

### 架构

```
AI Agent (GPT/Claude)
    ↓
决策层 (分析市场数据)
    ↓
执行层 (py-clob-client)
    ↓
Polymarket CLOB API
```

### 典型工作流

1. **市场分析**: AI 分析新闻、数据、情绪
2. **策略决策**: 判断买入 YES 还是 NO
3. **自动执行**: 调用 SDK 下单
4. **风险管理**: 设置止盈止损

---

## 💻 快速开始

### 1. 安装 SDK

```bash
pip install py-clob-client
```

### 2. 初始化客户端

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType

client = ClobClient(
    host="https://clob.polymarket.com",
    key="你的私钥",
    chain_id=137  # Polygon
)

# 派生 API 凭证
api_creds = client.create_or_derive_api_creds()
client.set_api_creds(api_creds)
```

### 3. 基本交易

```python
# 买入 YES
order = OrderArgs(
    token_id="TOKEN_ID",
    price=0.55,
    size=10,
    side=BUY,
    order_type=OrderType.GTC
)

signed = client.create_order(order)
resp = client.post_order(signed, OrderType.GTC)
```

---

## 🧠 AI Agent 示例提示词

```
你是一个 Polymarket 交易 Agent。

任务：
1. 扫描当前热门市场
2. 分析新闻和数据
3. 找出定价错误的市场
4. 执行交易

规则：
- 每笔最大 $10
- 胜率 >60% 时加仓
- 亏损 >10% 止损
- 每天最多 5 笔交易
```

---

## 📈 成功案例分析

### 案例 1: $2.2M (2个月)

- **策略**: AI 概率模型
- **特点**: 完全自动化
- **盈利方式**: 套利 + 趋势预测

### 案例 2: Claude Code Bot ($195K/月)

```
• 交易品种: BTC/ETH 15分钟涨跌
• 交易频率: ~500笔/周
• 胜率: 55%
• 策略: 小额多次复利
```

### 案例 3: $10 实验账户

- 官方发起的 AI 自主交易实验
- 目标: 测试 AI 能否通过交易赚回 token 成本

---

## ⚠️ 常见问题

### 1. 为什么 AI 交易会失败？

根据社区反馈：
> "you don't have a clear strategy"
> "you don't follow simple math formulas"
> "you make emotional decisions"

**解决方案**: 
- 设定明确策略
- 遵循数学公式
- 排除情绪

### 2. 需要多少资金？

| 目标 | 建议资金 |
|------|----------|
| 实验 | $10-100 |
| 稳定收益 | $500-1000 |
| 专业交易 | $5000+ |

### 3. Gas 成本

- Polygon Gas 便宜
- 但高频交易仍需考虑 Gas 成本

---

## 🔗 相关链接

- GitHub: github.com/Polymarket
- 官方文档: docs.polymarket.com
- Discord: discord.gg/polymarket
- 生态地图: 260+ 项目

---

*持续更新中...*
