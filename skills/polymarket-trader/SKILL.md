---
name: polymarket-trader
description: Polymarket自动交易策略，基于新闻信号决策。获取6551新闻→分析AI信号→匹配市场→执行交易
user-invocable: true
metadata:
  openclaw:
    requires:
      env:
        - OPENNEWS_TOKEN
        - POLYMARKET_PRIVATE_KEY
        - POLYGON_RPC_URL
      bins:
        - curl
        - python3
      pip:
        - requests
        - py-clob-client
    primaryEnv: OPENNEWS_TOKEN
    emoji: "📈"
    install:
      - id: curl
        kind: brew
        formula: curl
        label: curl
      - id: python3
        kind: brew
        formula: python3
        label: Python 3
    os:
      - darwin
      - linux
    version: 1.0.0
---

# Polymarket Trader Skill

基于6551新闻API的自动交易策略。

## 功能

1. **获取新闻信号** - 从6551 API获取加密货币新闻和AI评分
2. **分析市场** - 获取Polymarket活跃市场数据
3. **主题匹配** - 将新闻主题与相关市场匹配
4. **信号决策** - 基于信号强度决定买入/卖出/观望
5. **模拟交易** - 支持模拟模式测试策略

## 使用方法

### 1. 获取新闻信号

```bash
# 获取BTC相关新闻
curl -X POST "https://ai.6551.io/open/news_search" \
  -H "Authorization: Bearer $OPENNEWS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"coins": ["BTC"], "limit": 20}'

# 获取高分新闻 (score >= 80)
curl -X POST "https://ai.6551.io/open/news_search" \
  -H "Authorization: Bearer $OPENNEWS_TOKEN" \
  -d '{"limit": 50}' | jq '[.data[] | select(.aiRating.score >= 80)]'
```

### 2. 获取Polymarket市场

```bash
# 获取活跃市场
curl -s "https://gamma-api.polymarket.com/markets?closed=false&limit=50"
```

### 3. 运行交易策略

```bash
python3 ~/polymarket-trader/trader.py --mode simulate --days 7
```

## 配置

设置环境变量:
```bash
export OPENNEWS_TOKEN="your-token"
export POLYMARKET_PRIVATE_KEY="your-private-key"
export POLYGON_RPC_URL="your-rpc-url"
```

## 策略逻辑

1. **信号收集**: 获取新闻，计算各主题(Long/Short/Neutral)得分
2. **市场匹配**: 根据主题匹配相关Polymarket市场
3. **决策**: 
   - 信号强度 > 50 → buy_yes
   - 信号强度 < -50 → buy_no  
   - 其他 → hold
4. **风控**: 每次交易不超过总资金10%

## 优化技巧 (节省80% Token)

1. **缓存系统** - 5分钟TTL，避免重复API调用
2. **增量更新** - 只获取新数据
3. **精简数据** - 只保留必要字段，截断长文本
4. **指定Coin** - 用coins参数过滤，减少无效数据
5. **批量处理** - 一次获取多条
6. **简化逻辑** - 减少条件分支
