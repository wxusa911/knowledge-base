# Polymarket 天气预测策略 - Reddit调研

> 更新日期: 2026-03-01

---

## ⚠️ Reddit 访问问题

Reddit API 需要登录才能访问，直接请求被阻止。

**替代方案**: 通过 Twitter 获取 Reddit 相关讨论热点，或使用 NWS/NOAA API 获取天气数据。

---

## ✅ NOAA/NWS API 实测可用

测试结果：NWS API 可以正常调用！

```bash
# 获取城市天气信息
curl "https://api.weather.gov/points/40.7128,-74.0060"

# 纽约天气预报示例 (需先获取 forecastOffice URL)
```

**API 特点**:
- 免费，无需API Key
- 美国城市覆盖全面
- 数据更新及时

---

## 📊 策略核心：数据源对比

| 数据源 | 用途 | 状态 |
|--------|------|------|
| NWS/NOAA | 官方天气预报 | ✅ 可用 |
| Open-Meteo | GFS Ensemble | ✅ 免费 |
| Polymarket | 市场定价 | ✅ API |
| Kalshi | 跨市场套利 | ✅ |

---

## 🔄 策略流程

```
1. 从 NWS API 获取官方预报
2. 对比 Polymarket 市场定价
3. 计算偏差 = 模型概率 - 市场概率
4. 偏差 > 8% 时买入
5. 目标收益 10-50% 退出
```

---

## 📁 相关文档

- `01_Twitter调研.md` - 成功案例
- `02_策略详细分析.md` - 策略框架
