# OpenClaw + Polymarket 自动交易机器人搭建指南

> 来源: dashen.wang 初级指南

---

## 🎯 系统架构

三大核心组件：

| 组件 | 功能 |
|------|------|
| **OpenClaw** | 机器人的大脑和办公室 |
| **Polymarket CLI** | 机器人的双手 (交易执行) |
| **Simmer** | 安全护栏 + AI量化分析 |

---

## 📋 搭建步骤

### 1. 安装基础工具

```bash
# 安装 OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# 安装 Polymarket CLI  
curl -L https://raw.githubusercontent.com/polymarket/polymarket-cli/main/install.sh | bash
```

### 2. 配置钱包

- 创建新钱包 (只放测试资金)
- 需要两种币:
  - USDC.e (交易筹码)
  - POL (Gas费)

```bash
# 授权
polymarket approve set

# 检查余额
polymarket clob balance
```

### 3. 注册 Simmer API

```bash
# 注册机器人
curl -X POST https://api.simmer.markets/api/sdk/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "My-Auto-Profit-Agent"}'

# 配置到 OpenClaw
echo "SIMMER_API_KEY=sk_live_xxx" >> ~/.openclaw/.env
```

### 4. 安装 Skills

```bash
# 基础数据查询
clawhub install polymarket

# 复制跟单 (巨鲸追踪)
clawhub install polymarket-copytrading

# AI价格偏差套利
clawhub install polymarket-ai-divergence
```

---

## ⚙️ 自动任务配置

### 任务1: 高频市场扫描 (每30分钟)

编辑 `HEARTBEAT.md`:
```markdown
# 30分钟高频扫描任务
1. 调用 Simmer briefing 接口
2. 检查止盈/止损
3. 检查高偏差套利机会
4. 如果正常，回复 HEARTBEAT_OK
```

### 任务2: 每日流动性奖励 (每天凌晨2点)

```bash
openclaw cron add \
  --name "Daily_Reward_Farming" \
  --cron "0 2 * * *" \
  --message "领取流动性奖励，热门市场双向挂单5USDC" \
  --session-target isolated
```

### 任务3: 追踪巨鲸 (每4小时)

```bash
openclaw cron add \
  --name "Whale_Copytrading" \
  --every 14400000 \
  --message "追踪胜率>75%的大佬，跟随买入不超过20USDC"
```

---

## 💰 赚钱逻辑

1. **套利**: Simmer AI计算"真实概率"，与市场价格偏差>10%时下单
2. **跟单**: 自动复制高胜率钱包
3. **流动性奖励**: 每天自动领取平台发放的奖励

---

## ⚠️ 安全提示

- 创建专门测试钱包，不要用主力钱包
- 设置单日交易限额 (建议$500)
- 开启自动风控 (暴跌50%自动斩仓)

---

## 📚 相关资源

- OpenClaw: https://openclaw.ai
- Polymarket CLI: github.com/polymarket/polymarket-cli
- Simmer: https://simmer.markets

---

*最后更新: 2026-03-02*
