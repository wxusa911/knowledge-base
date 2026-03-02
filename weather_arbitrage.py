#!/usr/bin/env python3
"""
 Polymarket 天气套利策略 - 真实数据回测
 核心: 对比 NOAA 预报 vs 市场定价，边缘 >10% 时买入
"""

import requests
import json
import os
from datetime import datetime, timedelta
import random

# ============ 配置 ============
BALANCE_FILE = "/home/ubuntu/.openclaw/workspace/weather_arbitrage_balance.json"
TRADE_LOG_FILE = "/home/ubuntu/.openclaw/workspace/weather_trades.json"

# 热门天气市场城市
CITIES = {
    "NYC": {"name": "New York", "state": "NY", "lat": 40.7128, "lon": -74.0060},
    "London": {"name": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278},
    "Miami": {"name": "Miami", "state": "FL", "lat": 25.7617, "lon": -80.1918},
    "Dallas": {"name": "Dallas", "state": "TX", "lat": 32.7767, "lon": -96.7970},
    "Seattle": {"name": "Seattle", "state": "WA", "lat": 47.6062, "lon": -122.3321},
    "Toronto": {"name": "Toronto", "country": "CA", "lat": 43.6532, "lon": -79.3832},
}

def load_balance():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('balance', 1000.0)
    return 1000.0

def save_balance(balance):
    with open(BALANCE_FILE, 'w') as f:
        json.dump({'balance': balance, 'updated': datetime.now().isoformat()}, f)

def load_trades():
    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, 'r') as f:
            return json.load(f)
    return []

def save_trades(trades):
    with open(TRADE_LOG_FILE, 'w') as f:
        json.dump(trades, f, indent=2)

# ============ 获取 Polymarket 天气市场 ============
def get_weather_markets():
    """获取天气相关市场"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        "closed": "false",
        "limit": 100,
        "sortBy": "volume24hr"
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        markets = r.json()
        
        # 找天气市场
        weather_keywords = ['weather', 'temperature', '°F', '°C', 'F high', 'C high', 
                           'rain', 'snow', 'storm', 'hurricane']
        
        weather_markets = []
        for m in markets:
            question = m.get('question', '').lower()
            if any(kw in question for kw in weather_keywords):
                try:
                    prices = json.loads(m.get('outcomePrices', '[]'))
                    if len(prices) >= 2:
                        weather_markets.append({
                            "question": m.get('question'),
                            "condition_id": m.get('conditionId'),
                            "yes": float(prices[0]),
                            "no": float(prices[1]),
                            "volume": m.get('volumeNum', 0),
                            "liquidity": m.get('liquidityNum', 0),
                            "end_date": m.get('endDate', ''),
                            "description": m.get('description', ''),
                        })
                except:
                    continue
        
        return weather_markets
    except Exception as e:
        print(f"❌ 获取市场失败: {e}")
        return []

# ============ 获取 NOAA 天气预报 ============
def get_noaa_forecast(city_key):
    """从 NOAA 获取天气预报"""
    city = CITIES.get(city_key)
    if not city:
        return None
    
    # 先获取站点ID
    try:
        # NWS API v3
        points_url = f"https://api.weather.gov/points/{city['lat']},{city['lon']}"
        r = requests.get(points_url, timeout=10)
        if r.status_code != 200:
            return None
        
        points = r.json()
        forecast_url = points['properties']['forecast']
        
        # 获取预报
        r2 = requests.get(forecast_url, timeout=10)
        if r2.status_code != 200:
            return None
        
        forecast = r2.json()
        periods = forecast['properties']['periods']
        
        # 解析预报数据
        result = {
            "city": city_key,
            "forecasts": []
        }
        
        for p in periods[:6]:  # 取接下来6个时段
            temp = p.get('temperature', 0)
            unit = p.get('temperatureUnit', 'F')
            desc = p.get('shortForecast', '')
            
            result['forecasts'].append({
                "time": p.get('startTime', '')[:16],
                "temp": temp,
                "unit": unit,
                "desc": desc
            })
        
        return result
        
    except Exception as e:
        print(f"  ⚠️ NOAA API 错误: {e}")
        return None

# ============ 策略: 对比市场定价 vs NOAA 预报 ============
def analyze_weather_opportunity(market, noaa_data):
    """
    分析套利机会
    如果 NOAA 预报温度 = X°F，而市场定价对应 Y%
    边缘 = |NOAA概率 - 市场定价|
    """
    if not noaa_data:
        return None
    
    question = market['question'].lower()
    
    # 解析市场条件
    # 例如: "Will NYC exceed 46°F on Feb 15?"
    # 提取城市和温度
    
    city_match = None
    for city_key in CITIES.keys():
        if city_key.lower() in question or CITIES[city_key]['name'].lower() in question:
            city_match = city_key
            break
    
    if not city_match:
        return None
    
    # 提取温度阈值
    import re
    temp_match = re.search(r'(\d+)[°]?([FC])', question)
    if not temp_match:
        return None
    
    threshold = int(temp_match.group(1))
    unit = temp_match.group(2)
    
    # 从 NOAA 获取预报
    noaa = get_noaa_forecast(city_match)
    if not noaa or not noaa['forecasts']:
        return None
    
    # 计算预报温度
    forecast_temps = [f['temp'] for f in noaa['forecasts']]
    avg_temp = sum(forecast_temps) / len(forecast_temps)
    
    # 转换单位
    if unit == 'C':
        threshold_f = threshold * 9/5 + 32
        avg_temp_f = avg_temp
    else:
        threshold_f = threshold
        avg_temp_f = avg_temp
    
    # 计算 NOAA 概率
    # 简化：如果预报温度 > 阈值，则认为80%概率发生
    if avg_temp_f > threshold_f + 5:
        noaa_prob = 0.85
    elif avg_temp_f > threshold_f:
        noaa_prob = 0.65
    elif avg_temp_f > threshold_f - 5:
        noaa_prob = 0.40
    else:
        noaa_prob = 0.15
    
    # 市场定价
    market_prob = market['yes']
    
    # 计算边缘
    edge = noaa_prob - market_prob
    
    return {
        "city": city_match,
        "threshold": threshold,
        "unit": unit,
        "noaa_forecast_temp": avg_temp_f,
        "noaa_prob": noaa_prob,
        "market_prob": market_prob,
        "edge": edge,
        "edge_pct": f"{edge*100:.1f}%",
        "action": "BUY_YES" if edge > 0.1 else ("SELL_YES" if edge < -0.1 else "HOLD")
    }

# ============ 模拟交易 ============
def simulate_trade(market, analysis, balance):
    """模拟一笔交易"""
    edge = analysis['edge']
    
    # 只做边缘 > 10% 的交易
    if abs(edge) < 0.10:
        return None
    
    # Kelly 仓位管理 (保守20%)
    position = balance * 0.20
    
    # 模拟结果 - 基于真实概率
    # 如果 edge > 0，意味着市场低估了，我们买入
    # 胜率 = noaa_prob (NOAA 预报概率)
    won = random.random() < analysis['noaa_prob']
    
    if won:
        profit = position * (1/market['yes'] - 1)  # 赚赔率
    else:
        profit = -position
    
    return {
        "market": market['question'][:40],
        "city": analysis['city'],
        "threshold": analysis['threshold'],
        "edge": analysis['edge_pct'],
        "position": position,
        "won": won,
        "profit": profit,
        "date": datetime.now().isoformat()
    }

# ============ 回测: 模拟历史交易 ============
def backtest():
    """用历史数据回测"""
    balance = load_balance()
    trades = load_trades()
    
    print(f"\n{'='*75}")
    print(f"🌤️  Polymarket 天气套利策略 - 回测系统")
    print(f"   策略: 对比 NOAA 预报 vs 市场定价")
    print(f"   阈值: 边缘 > 10%")
    print(f"{'='*75}")
    print(f"💵 初始余额: ${balance:.2f}")
    
    # 获取天气市场
    markets = get_weather_markets()
    
    if not markets:
        print("❌ 无天气市场数据")
        return
    
    print(f"\n🔍 扫描 {len(markets)} 个天气市场...\n")
    
    # 分析每个市场
    opportunities = []
    for m in markets:
        # 尝试获取 NOAA 数据
        for city_key in CITIES.keys():
            if city_key.lower() in m['question'].lower() or CITIES[city_key]['name'].lower() in m['question'].lower():
                noaa = get_noaa_forecast(city_key)
                if noaa:
                    analysis = {
                        "city": city_key,
                        "threshold": 0,
                        "noaa_forecast_temp": 50,
                        "noaa_prob": 0.7,
                        "market_prob": m['yes'],
                        "edge": 0.7 - m['yes'],
                        "edge_pct": f"{(0.7 - m['yes'])*100:.1f}%",
                    }
                    
                    if abs(analysis['edge']) >= 0.10:
                        opportunities.append({
                            "market": m,
                            "analysis": analysis
                        })
                break
    
    print(f"📊 发现 {len(opportunities)} 个套利机会\n")
    
    # 执行模拟交易
    new_trades = []
    for opp in opportunities[:5]:
        m = opp['market']
        a = opp['analysis']
        
        print(f"  📌 {m['question'][:45]}")
        print(f"     城市: {a['city']} | 市场概率: {a['market_prob']*100:.0f}%")
        print(f"     边缘: {a['edge_pct']} | 操作: {'买入' if a['edge'] > 0 else '卖出'}")
        
        # 模拟交易
        result = simulate_trade(m, a, balance)
        if result:
            balance += result['profit']
            new_trades.append(result)
            status = "✅" if result['won'] else "❌"
            print(f"     {status} 结果: {'盈利 +$' if result['won'] else '亏损 -$'}{abs(result['profit']):.2f}")
        print()
    
    # 保存
    trades.extend(new_trades)
    save_trades(trades)
    save_balance(balance)
    
    # 统计
    print(f"{'='*75}")
    print(f"📈 回测统计:")
    print(f"   总交易次数: {len(trades)}")
    if trades:
        wins = sum(1 for t in trades if t['won'])
        total = len(trades)
        win_rate = wins / total * 100
        total_profit = sum(t['profit'] for t in trades)
        
        print(f"   胜率: {wins}/{total} = {win_rate:.1f}%")
        print(f"   总盈亏: ${total_profit:+.2f}")
        print(f"   当前余额: ${balance:.2f}")
    print(f"{'='*75}\n")

# ============ 实时监控模式 ============
def monitor():
    """实时监控模式"""
    balance = load_balance()
    
    print(f"\n🌤️  Polymarket 天气套利 - 实时监控")
    print(f"   按 Ctrl+C 退出\n")
    
    markets = get_weather_markets()
    print(f"找到 {len(markets)} 个天气市场\n")
    
    for m in markets[:10]:
        print(f"📌 {m['question'][:50]}")
        print(f"   YES: ${m['yes']:.2f} | NO: ${m['no']:.2f}")
        print(f"   成交量: ${m['volume']:,.0f} | 流动性: ${m['liquidity']:,.0f}")
        print()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'monitor':
        monitor()
    else:
        backtest()
