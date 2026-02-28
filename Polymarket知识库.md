# Polymarket 知识库 - 工具、策略与研究

> 持续更新中...

## 一、核心概念

### Polymarket 是什么
- 基于 Polygon 区块链的去中心化预测市场
- 使用 USDC 交易
- **免交易手续费**（只赚流动性）
- 不需要 KYC

### 基础机制
- 每个事件 = 一个市场
- 每个市场 = Yes/No 两种代币
- 价格 = 市场认为事件发生的概率
- 买入 = 买概率，赔率 = 1/价格

---

## 二、免费 API 接口

### 1. Gamma API（市场数据）
```
基础URL: https://gamma-api.polymarket.com

获取市场:
curl "https://gamma-api.polymarket.com/markets?active=true&limit=10"

获取事件:
curl "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=10"

按交易量排序:
curl "https://gamma-api.polymarket.com/events?active=true&order=volume_24hr&ascending=false&limit=10"

搜索:
curl "https://gamma-api.polymarket.com/public-search?query=bitcoin"
```

### 2. CLOB API（价格与订单簿）
```
基础URL: https://clob.polymarket.com

实时价格:
curl "https://clob.polymarket.com/prices?token_id=TOKEN_ID"

订单簿:
curl "https://clob.polymarket.com/orderbook?token_id=TOKEN_ID"
```

### 3. Data API（交易数据）
```
基础URL: https://data-api.polymarket.com

用户持仓:
curl "https://data-api.polymarket.com/positions?address=WALLET_ADDRESS"

交易历史:
curl "https://data-api.polymarket.com/trades?address=WALLET_ADDRESS"
```

### 4. WebSocket（实时推送）
```
URL: wss://clob.polymarket.com/ws

连接后可订阅:
- orderbook 更新
- 价格变动
- 成交记录
```

---

## 三、推荐工具

### 🐋 跟单工具

| 工具 | 特点 | 费用 |
|------|------|------|
| PolySight | Telegram机器人，实时跟单 | 付费 |
| polymarket-mcp-server | 开源，连接Claude | 免费 |
| 0x1979 Whale Bot | 追踪鲸鱼 | 免费/付费 |

### 📊 数据分析

| 工具 | 特点 |
|------|------|
| **Polyterm** | 终端版全方位工具，支持鲸鱼追踪 |
| **Bitquery** | GraphQL查询链上数据 |
| **The Graph** | 去中心化索引 |

### 🤖 交易机器人

| 工具 | 语言 | 特点 |
|------|------|------|
| polymarket-trading-bot | Python | 入门友好 |
| polymarket-spike-bot | Python | 监测价格波动 |
| poly-based-sdk | Python | 完整SDK |
| Polymarket/agents | Python | 官方AI Agent框架 |

---

## 四、策略研究

### 1. 跟单（Copy Trading）
**原理**: 复制成功交易者的订单

**步骤**:
1. 找到靠谱的"鲸鱼"钱包
2. 监测他们的交易
3. 自动复制他们的订单

**工具**: PolySight, 手动跟踪

### 2. 套利（Arbitrage）
**原理**: 当市场效率低时，买低卖高

**例子**:
- Polymarket 价格 = 60%
- 另一个市场 = 65%
- 买入便宜的，卖出贵的

**难点**: 需要速度快，资金大

### 3. 鲸鱼追踪（Whale Tracking）
**原理**: 跟着大资金走

**信号**:
- 多个大钱包同时买入
- 沉默钱包突然活跃
- 某个钱包的历史胜率高

**工具**: Polyterm, Bitquery

### 4. 事件分析（Manual Edge）
**原理**: 利用信息优势

**方向**:
- 你擅长的领域（体育、政治、商业）
- 新闻前的预判
- 长期趋势

---

## 五、关键资源

### 官方文档
- https://docs.polymarket.com

### GitHub 仓库
- https://github.com/Polymarket/agents
- https://github.com/NYTEMODEONLY/polyterm
- https://github.com/olliegrimes123/polybased-sdk
- https://github.com/discountry/polymarket-trading-bot

### 社区
- Polymarket Discord
- r/polymarketkalshi (Reddit)
- Twitter #Polymarket

---

## 六、小而精路线建议

### 适合新手的策略

1. **数据监控**
   - 用 Polyterm 监控特定市场
   - 不用真钱交易，只学习

2. **小额跟单**
   - 找到胜率高的钱包
   - 每次只跟 1-5 U

3. **信息差**
   - 利用你擅长的领域知识
   - 只买你真正懂的

### 风险控制

| 规则 | 说明 |
|------|------|
| 只用闲钱 | 最多 10-20 U |
| 设止损 | 到点就跑 |
| 不梭哈 | 分散风险 |
| 记录复盘 | 每次交易写原因 |

---

## 七、待研究

- [ ] 你的Twitter收藏链接
- [ ] 具体跟单工具使用
- [ ] 鲸鱼钱包筛选标准
- [ ] 最佳市场筛选方法

---

*更新时间: 2026-02-28*
