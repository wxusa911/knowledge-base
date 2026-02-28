# Polymarket 交易机器人 - 完整设置指南 (v2)

## 核心架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  发现层     │ →  │  执行层     │ →  │  链上结算   │
│ Gamma API   │    │ CLOB Client │    │ Polygon     │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 必需物品

| 物品 | 说明 |
|------|------|
| Polygon钱包 | 需要私钥 |
| USDC.e | 交易本金 |
| POL | 支付Gas |
| RPC节点 | Quicknode或其他 |

---

## API 端点总览

### 市场数据 (Gamma API) - 无需认证
```
GET https://gamma-api.polymarket.com/markets
GET https://gamma-api.polymarket.com/events
GET https://gamma-api.polymarket.com/markets/{slug}
```

### 交易 (CLOB API) - 需要签名
```
POST https://clob.polymarket.com/order
GET  https://clob.polymarket.com/orderbook
```

### 价格历史
```
GET https://gamma-api.polymarket.com/markets/{id}/history
```

---

## 完整Python代码示例

### Step 1: 获取市场数据

```python
import requests

# 获取活跃市场
response = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={
        "active": "true",
        "closed": "false", 
        "limit": 10,
        "order": "volume_24hr"  # 按24小时成交量排序
    }
)
markets = response.json()

for m in markets[:5]:
    print(f"问题: {m['question']}")
    print(f"ID: {m['id']}")
    print(f"TokenIDs: {m['clobTokenIds']}")  # [Yes, No]
    print(f"当前价格: {m.get('bestBid')} / {m.get('bestAsk')}")
    print("---")
```

### Step 2: 安装SDK并初始化

```bash
pip install py-clob-client
```

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
import os

host = "https://clob.polymarket.com"
chain_id = 137  # Polygon mainnet
private_key = os.getenv("PRIVATE_KEY")

# 方式1: 使用私钥直接创建
client = ClobClient(
    host,
    key=private_key,
    chain_id=chain_id,
)

# 派生API凭证
api_creds = client.create_or_derive_api_creds()
client.set_api_creds(api_creds)

print(f"钱包地址: {client.address}")
```

### Step 3: 获取Token ID

```python
# 方式A: 通过市场查询
markets = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={"question": "Will BTC be above $100k by June 2025?", "limit": 1}
).json()

if markets:
    token_id = markets[0]['clobTokenIds'][0]  # Yes token
    condition_id = markets[0]['conditionId']
    print(f"Token ID: {token_id}")
    print(f"Condition ID: {condition_id}")
```

### Step 4: 下单

```python
# 买单 (限价单)
order = OrderArgs(
    token_id="TOKEN_ID_HERE",
    price=0.55,        # 愿意买的价格
    size=10,          # 数量 (必须整数!)
    side=BUY,
    order_type=OrderType.GTC,  # Good Till Cancel
)

signed = client.create_order(order)
resp = client.post_order(signed, OrderType.GTC)
print(resp)

# 市价单 (FOK - Fill or Kill)
market_order = MarketOrderArgs(
    token_id="TOKEN_ID_HERE",
    amount=10.0,      # 金额
    side=BUY,
    order_type=OrderType.FOK,
)
signed_mo = client.create_market_order(market_order)
resp_mo = client.post_order(signed_mo, OrderType.FOK)
```

### Step 5: 查看持仓

```python
# 获取当前持仓
positions = client.get_positions()
print(positions)

# 获取某个市场的持仓
market_positions = client.get_positions(condition_id="CONDITION_ID")
```

---

## 重要规则 (必须记住!)

| 规则 | 说明 |
|------|------|
| **最小订单** | size × price ≥ $1 |
| **价格精度** | ≤ 2位小数（价格<0.04或>0.96时3位）|
| **数量必须整数** | size必须是int，不能是float |
| **签名类型0** | EOA模式，自己付Gas |
| **链ID** | 137 (Polygon) |
| **货币** | USDC: `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |

---

## 订单类型

| 类型 | 说明 |
|------|------|
| GTC | Good Till Cancel - 取消前一直有效 |
| FOK | Fill or Kill - 立即全部成交，否则取消 |
| GTC | Good Till Cancel |
| FAK | Fill or Kill |

---

## 跟单策略 (最简单)

### 原理
复制成功交易者的钱包地址

### 工具
- **Polywhaler**: https://polymarket.com/polywhaler - 追踪鲸鱼
- **Quicknode跟单教程**: 有完整TypeScript代码

### 鲸鱼地址示例
- `0x1e1f17412069c0736adfaadf8ee7f46e5612c855` - Top 0.01%

### 跟单配置 (.env)
```bash
TARGET_WALLET=0x要跟单的钱包地址
PRIVATE_KEY=你的私钥
RPC_URL=https://polygon-mainnet.quiknode.pro/YOUR_KEY
POSITION_MULTIPLIER=0.1    # 跟单比例 (10%)
MAX_TRADE_SIZE=100         # 最大交易额
MIN_TRADE_SIZE=1           # 最小交易额
USE_WEBSOCKET=true         # 使用WebSocket
```

---

## 高频策略 (5分钟市场)

### 为什么需要机器人
- 5分钟市场变化太快
- 手动操作来不及
- WebSocket实时数据

### 核心逻辑
```python
# WebSocket监听
import websocket

ws = websocket.WebSocketApp(
    "wss://ws-subscriptions-clob.polymarket.com/ws",
    on_message=on_message,
)
ws.run_forever()
```

### 策略类型
1. **均值回归**: 价格偏离均值时入场
2. **突破交易**: 价格突破关键点位
3. **套利**: 不同市场间价差

---

## 常见错误排错

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `insufficient balance` | 用了EOA地址而不是proxy | 检查钱包地址 |
| `Order silently rejected` | 价格小数位太多 | round到2位 |
| `Order value error` | size × price < $1 | 增加金额 |
| Positions empty | 查询的是EOA而不是proxy | 用proxy地址 |
| WebSocket无数据 | 订阅格式错误 | 检查JSON格式 |

---

## 数据API (无需认证)

```python
# 获取用户活动
requests.get(
    "https://data-api.polymarket.com/activity",
    params={
        "user": "钱包地址",
        "type": "TRADE",
        "limit": 100
    }
)

# 获取历史价格
requests.get(
    "https://gamma-api.polymarket.com/markets/{id}/history",
    params={
        "interval": 60,  # 分钟
        "start": "2025-01-01T00:00:00Z",
        "end": "2025-01-02T00:00:00Z"
    }
)
```

---

## 参考资源

| 资源 | 链接 |
|------|------|
| 官方文档 | https://docs.polymarket.com |
| Quicknode跟单教程 | https://www.quicknode.com/guides/defi/polymarket-copy-trading-bot |
| Python SDK | https://github.com/Polymarket/py-clob-client |
| 追踪鲸鱼 | https://polymarket.com/polywhaler |
| Discord | https://discord.gg/polymarket |

---

## 下一步行动

1. [ ] 准备钱包私钥
2. [ ] 部署测试网络练习
3. [ ] 实现简单跟单策略
4. [ ] 逐步增加复杂度
