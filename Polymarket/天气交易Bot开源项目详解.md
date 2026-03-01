# Polymarket 天气交易 Bot 深入研究

> 更新日期: 2026-03-01
> 来源: 飞书文档 + GitHub + Twitter

---

## 🎯 核心发现

根据飞书文档研究，**天气预测是 Polymarket 最隐秘但有效的赛道**：

| 指标 | 数据 |
|------|------|
| 成功率 | 73%+ |
| ROI | 100%-2000%+ |
| 竞争者 | 极少 (GitHub 仅 15 stars) |

---

## 🔥 成功案例汇总

### 案例 1: 伦敦温度区间
- **本金**: $204
- **收益**: ~$24,000
- **交易数**: 1,300+
- **胜率**: 73%
- **策略**: 伦敦每日最高温度区间

### 案例 2: 实验性天气 Bot
- **本金**: $100
- **收益**: $1,400 (30天)
- **收益%**: +1400%
- **预测数**: 1,500+

### 案例 3: 精准温度狩猎
- **本金**: $48
- **收益**: $1,000+
- **收益%**: 2022%

---

## 🛠️ 推荐开源项目

### 1. 天气预测 Bot (重点!)

**项目**: [suislanchez/polymarket-kalshi-weather-bot](https://github.com/suislanchez/polymarket-kalshi-weather-bot)

| 属性 | 值 |
|------|-----|
| Stars | 15 |
| 语言 | Python |
| 数据源 | Open-Meteo (免费) |
| 支持 | Polymarket + Kalshi |

**核心功能**:
- ✅ 31成员 GFS Ensemble 天气预报
- ✅ Kelly 仓位管理
- ✅ 边缘检测 (偏差 >8% 触发)
- ✅ 3D 地球仪表盘
- ✅ 模拟交易模式

**架构**:
```
数据层:
├── Open-Meteo (31成员GFS)
├── NWS API (美国天气)
├── Polymarket Gamma API
└── Kalshi API

分析层:
├── 概率计算
├── 边缘检测
└── Kelly优化

交易层:
├── 市场监控
└── 订单执行
```

### 2. 套利全家桶

**项目**: [PolyScripts/polymarket-arbitrage-trading-bot-pack](https://github.com/PolyScripts/polymarket-arbitrage-trading-bot-pack)

| 属性 | 值 |
|------|-----|
| Stars | 244 |
| 语言 | TypeScript/Rust |
| 特点 | 套利策略集合 |

---

## 📊 策略核心逻辑

### 1. 数据获取

```python
# 天气数据 - Open-Meteo (免费!)
response = requests.get(
    "https://api.open-meteo.com/v1/ensemble",
    params={
        "latitude": 40.7128,
        "longitude": -74.0060,
        "temperature_2m": ["40", "50", "60"]  # 温度阈值
    }
)
# 返回31个ensemble成员的预测

# 市场数据 - Polymarket Gamma API
response = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={"conditionTitle": "weather"}
)
```

### 2. 边缘检测

```python
# 计算边缘
model_prob = ensemble_member_agree_count / 31  # 模型概率
market_prob = float(market.get('bestAsk'))     # 市场概率
edge = model_prob - market_prob

if edge > 0.08:  # 8% 阈值
    generate_signal(direction="YES", edge=edge)
```

### 3. Kelly 仓位

```python
# Quarter-Kelly
kelly = (edge * win_rate - loss_rate) / edge
position_size = bankroll * (kelly * 0.25)  # 四分之一Kelly
```

---

## 🗺️ 热门交易城市

| 城市 | 国家 | 温度区间 | 特点 |
|------|------|----------|------|
| NYC | 美国 | ≥46°F | 流动性好 |
| London | 英国 | 高温区间 | 稳定 |
| Toronto | 加拿大 | 0°C | 波动大 |
| Seattle | 美国 | 50-51°F | 精准区间 |

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/suislanchez/polymarket-kalshi-weather-bot.git
cd polymarket-kalshi-weather-bot

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制配置
cp config.example.yaml config.yaml

# 编辑配置
# - 添加私钥
# - 设置API
# - 选择市场
```

### 3. 运行

```bash
# 后端
uvicorn api.main:app --reload --port 8000

# 前端 (可选)
cd frontend && npm run dev
```

---

## 💰 预期收益

| 投入 | 保守收益 | 正常收益 | 乐观收益 |
|------|----------|----------|----------|
| $10 | $20 | $50 | $100+ |
| $100 | $200 | $500 | $1,000+ |

---

## ⚠️ 风险提示

1. **气象模型风险**: NOAA 预报也有不准的时候
2. **流动性风险**: 低温区间可能流动性差
3. **时间风险**: 快到期时难退出
4. **技术风险**: 执行延迟

---

## 🏆 Raspberry Pi 案例 (最新!)

**推文**: "My Polymarket bot is still running on my Raspberry Pi"

| 指标 | 数据 |
|------|------|
| 设备 | Raspberry Pi |
| 交易数 | 42 笔触发 |
| 胜率 | **100%** (42胜 0负) |
| 策略 | 保守型 |

> "I could change the parameters to increase the number of triggered orders, but that would make it less conservative"

---

## 🐋 鲸鱼扫描器 (额外发现)

**项目**: C++ 终端扫描 Polymarket 自动交易钱包

| 案例 | 收益 |
|------|------|
| Account88888 | $152K/周, 99%胜率, 11,000+交易 |
| 另一个钱包 | -$500 → $106K (3周), 95%胜率 |

---

## 📁 相关文档

- `01_Twitter调研.md` - Twitter 案例
- `02_策略详细分析.md` - 策略框架
- `03_Reddit调研.md` - 风险提示

---

## 🔗 关键链接

- GitHub: github.com/suislanchez/polymarket-kalshi-weather-bot
- Open-Meteo: open-meteo.com
- NWS API: api.weather.gov

---

*持续更新中...*
