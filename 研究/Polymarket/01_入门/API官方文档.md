# Polymarket API 官方文档

> 更新: 2026-03-03
> 来源: https://docs.polymarket.com/api-reference

---

## 三大API

| API | 用途 | 认证 |
|-----|------|------|
| **Gamma API** | 市场数据、搜索、事件 | 无需 |
| **Data API** | 用户持仓、交易、活动 | 无需 |
| **CLOB API** | 订单簿、交易下单 | 需要 |

---

## API 端点

### Gamma API (公开)
```
https://gamma-api.polymarket.com
- /markets - 市场列表
- /events - 事件列表
- /markets/{slug} - 市场详情
```

### Data API (公开)
```
https://data-api.polymarket.com
- /positions - 用户持仓
- /trades - 交易记录
- /activity - 用户活动
```

### CLOB API (需认证)
```
https://clob.polymarket.com
- /orderbook - 订单簿
- /order - 下单
- /orders/{id} - 订单管理
```

---

## 认证机制 (L1 + L2)

### L1: 私钥认证
- 使用钱包私钥签名 EIP-712 消息
- 用于: 创建API凭证、派生密钥、下单签名

### L2: API Key认证
- 使用生成的 apiKey + secret + passphrase
- 用于: 查询持仓、撤单、管理订单

---

## SDK 安装

### Python
```bash
pip install py-clob-client
```

### 使用示例
```python
from py_clob_client.client import ClobClient

client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137  # Polygon
)

# 创建/派生API凭证
creds = client.create_or_derive_api_creds()
```

---

## 下单流程

1. **获取市场** - Gamma API
2. **获取Token ID** - 市场详情
3. **创建订单** - 使用SDK签名
4. **发送订单** - CLOB API

---

## 相关链接

- 文档: https://docs.polymarket.com
- Python SDK: github.com/Polymarket/py-clob-client
- TypeScript SDK: github.com/Polymarket/clob-client

---

*持续更新*
