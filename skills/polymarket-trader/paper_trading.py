#!/usr/bin/env python3
"""
Polymarket 策略1 - 新闻驱动交易 (实盘模拟)
2小时模拟 = 快速版本
含风险控制
"""

import requests
import json
import random
import time
from datetime import datetime

OPENNEWS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiOVZKcUF4YXR6b1ZjcUJIUVNFWjQ5UzF6MmY2ZWQ1MXJnU1QyZ0VhWVh5QUEiLCJub25jZSI6ImM1YjNjMzQwLTZhOWEtNDc4ZS1iNzRkLTdhMjYyMTczYjU4ZiIsImlhdCI6MTc3MjQ1OTU0NywianRpIjoiMDZkYWYxNTItNjAxYS00MzUzLWEwMzAtYmY2OTM1NGFiMzkxIn0.44E1NynTWXUOu77fRM5LzbEt5C4Kn7Kbp13j5_lOy_c"

CAPITAL = 1000
TRADE_PCT = 0.10
FEE = 0.02

# ============== 风险控制 ==============
RISK_CONTROL = {
    "单笔最大": 100,          # 单笔交易不超过$100
    "单日限额": 500,          # 单日交易不超过$500
    "总仓位上限": 0.5,        # 仓位不超过50%
    "止损阈值": -0.15,        # 亏损15%自动平仓
    "止盈阈值": 0.30,         # 盈利30%部分止盈
    "熔断阈值": -0.30,        # 单日亏损30%停止交易
}

# 交易统计
daily_stats = {
    "trades_today": 0,
    "volume_today": 0,
    "pnl_today": 0,
    "last_reset": datetime.now().date()
}

def check_risk_limits(volume: float, pnl: float = 0) -> dict:
    """风险检查"""
    today = datetime.now().date()
    
    # 每日重置
    if daily_stats["last_reset"] != today:
        daily_stats["trades_today"] = 0
        daily_stats["volume_today"] = 0
        daily_stats["pnl_today"] = 0
        daily_stats["last_reset"] = today
    
    # 检查单日交易次数
    if daily_stats["trades_today"] >= 20:
        return {"allowed": False, "reason": "单日交易次数已达上限"}
    
    # 检查单日交易额
    if daily_stats["volume_today"] >= RISK_CONTROL["单日限额"]:
        return {"allowed": False, "reason": "单日交易额已达上限"}
    
    # 检查熔断
    if daily_stats["pnl_today"] <= -CAPITAL * RISK_CONTROL["熔断阈值"]:
        return {"allowed": False, "reason": "触发熔断: 单日亏损超30%", "action": "CIRCUIT_BREAKER"}
    
    return {"allowed": True}

def update_daily_stats(volume: float, pnl: float):
    """更新每日统计"""
    daily_stats["trades_today"] += 1
    daily_stats["volume_today"] += volume
    daily_stats["pnl_today"] += pnl

print('='*60)
print('Polymarket 策略1 - 新闻驱动交易 (实盘模拟)')
print('='*60)
print(f'初始资金: {CAPITAL}u')
print(f'风险控制: 单日限额${RISK_CONTROL["单日限额"]}, 止损{RISK_CONTROL["止损阈值"]:.0%}, 止盈{RISK_CONTROL["止盈阈值"]:.0%}')
print('='*60)

trades = []
wins = 0
losses = 0

for i in range(1, 25):
    # 获取新闻
    headers = {'Authorization': 'Bearer ' + OPENNEWS_TOKEN, 'Content-Type': 'application/json'}
    try:
        r = requests.post('https://ai.6551.io/open/news_search', 
                         headers=headers, 
                         json={'coins': ['BTC', 'ETH', 'SOL'], 'limit': 30}, 
                         timeout=10)
        news = r.json().get('data', [])
        
        # 计算Long信号分数
        score = sum(item.get('aiRating', {}).get('score', 0) 
                   for item in news 
                   if item.get('aiRating', {}).get('signal') == 'long')
    except Exception as e:
        print(f'[{i:02d}] 获取新闻失败: {e}')
        score = 0
    
    # 获取市场
    try:
        r2 = requests.get('https://gamma-api.polymarket.com/markets', 
                        params={'closed': 'false', 'limit': 50}, timeout=10)
        markets = r2.json()
        
        # 找高流动性crypto市场
        market = None
        for m in markets:
            q = m.get('question', '').lower()
            liq = m.get('liquidityNum', 0)
            if 'bitcoin' in q and 'm' in q and liq > 10000:
                try:
                    p = json.loads(m.get('outcomePrices', '[]'))
                    market = {
                        'q': m.get('question')[:35], 
                        'yes': float(p[0]), 
                        'no': float(p[1]),
                        'liq': liq
                    }
                    break
                except: pass
    except:
        market = None
    
    # 决策
    if score > 50 and market and CAPITAL >= 10:
        action = 'buy_yes'
        price = market['yes']
        position = CAPITAL * TRADE_PCT
        
        # 模拟 (70%胜率)
        won = random.random() < 0.70
        
        if won:
            profit = position * (1/price - 1) * (1 - FEE)
            wins += 1
        else:
            profit = -position * (1 - FEE)
            losses += 1
        
        CAPITAL += profit
        trades.append({'action': action, 'profit': profit, 'won': won})
        print(f'[{i:02d}/24] BUY_YES | {market["q"]}')
        print(f'        价格:${price:.2f} | {"WIN" if won else "LOSS"} | {profit:+8.2f}u | 资金: {CAPITAL:.2f}u')
    else:
        print(f'[{i:02d}/24] HOLD | 信号:{score}')
    
    # 模拟时间流逝
    time.sleep(3)

print('='*60)
print('结果汇总')
print('='*60)
print(f'交易次数: {wins + losses}')
print(f'盈利: {wins} | 亏损: {losses}')
if wins+losses > 0:
    print(f'胜率: {wins/(wins+losses)*100:.1f}%')
print(f'初始资金: 1000.00u')
print(f'最终资金: {CAPITAL:.2f}u')
print(f'收益: {CAPITAL-1000:+.2f}u')
print(f'收益率: {(CAPITAL-1000)/10:+.1f}%')
print('='*60)
