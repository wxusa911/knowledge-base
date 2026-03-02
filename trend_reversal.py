#!/usr/bin/env python3
"""
 Polymarket 趋势反转策略 - 历史回测
 核心: 买入被市场过度定价的相反方向
"""

import requests
import json
import os
from datetime import datetime, timedelta
import random

BALANCE_FILE = "/home/ubuntu/.openclaw/workspace/trend_reversal_balance.json"
TRADES_FILE = "/home/ubuntu/.openclaw/workspace/trend_reversal_trades.json"

def load_balance():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, 'r') as f:
            return json.load(f).get('balance', 1000.0)
    return 1000.0

def save_balance(b):
    with open(BALANCE_FILE, 'w') as f:
        json.dump({'balance': b}, f)

def load_trades():
    if os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_trades(t):
    with open(TRADES_FILE, 'w') as f:
        json.dump(t, f, indent=2)

# ============ 获取市场历史数据 ============
def get_market_history(condition_id):
    """获取市场历史价格数据"""
    try:
        # 获取历史K线
        url = f"https://gamma-api.polymarket.com/markets/{condition_id}/candles"
        params = {
            "condition": condition_id,
            "interval": "15m",  # 15分钟K线
            "limit": 100
        }
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def get_markets():
    """获取所有市场"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {"closed": "false", "limit": 50}
    
    try:
        r = requests.get(url, params=params, timeout=10)
        markets = r.json()
        
        result = []
        for m in markets:
            try:
                prices = json.loads(m.get('outcomePrices', '[]'))
                if len(prices) >= 2:
                    result.append({
                        "question": m.get('question')[:50],
                        "condition_id": m.get('conditionId'),
                        "yes": float(prices[0]),
                        "no": float(prices[1]),
                        "volume": m.get('volumeNum', 0),
                        "liquidity": m.get('liquidityNum', 0),
                    })
            except:
                continue
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []

# ============ 趋势反转策略 ============
def analyze_trend_reversal(market):
    """
    趋势反转策略:
    1. 极端价格 (YES < 0.15 或 YES > 0.85) 
    2. 反向买入等回归
    3. 止损线: -20%
    4. 止盈线: +50%
    """
    yes_price = market['yes']
    no_price = market['no']
    
    # 只做极端价格
    if yes_price < 0.15:
        # YES 被严重低估，可能反弹
        return {
            "action": "BUY_YES",
            "entry": yes_price,
            "target": 0.30,  # 目标价格
            "stop": yes_price * 0.8,  # 止损
            "edge": 0.15 - yes_price,
            "strategy": "极端低估反弹"
        }
    elif yes_price > 0.85:
        # YES 被严重高估，可能下跌
        return {
            "action": "SELL_YES",
            "entry": yes_price,
            "target": 0.70,
            "stop": yes_price * 1.2,
            "edge": yes_price - 0.85,
            "strategy": "极端高估反转"
        }
    elif no_price < 0.15:
        return {
            "action": "BUY_NO",
            "entry": no_price,
            "target": 0.30,
            "stop": no_price * 0.8,
            "edge": 0.15 - no_price,
            "strategy": "NO极端低估"
        }
    elif no_price > 0.85:
        return {
            "action": "SELL_NO",
            "entry": no_price,
            "target": 0.70,
            "stop": no_price * 1.2,
            "edge": no_price - 0.85,
            "strategy": "NO极端高估"
        }
    
    return None

# ============ 模拟交易 ============
def simulate_trade(market, signal, balance):
    """模拟交易"""
    # Kelly 20%
    position = balance * 0.20
    
    entry = signal['entry']
    action = signal['action']
    
    # 模拟未来价格变动
    # 简化模型: 基于历史波动
    volatility = 0.15  # 15%日波动
    
    # 随机生成结果
    # 假设极端价格有70%概率反转
    edge = signal['edge']
    reversal_prob = 0.5 + edge * 2  # 边缘越大，反转概率越高
    
    won = random.random() < min(reversal_prob, 0.85)
    
    if won:
        # 达到目标
        profit = position * (signal['target'] - entry) / entry
    else:
        # 止损
        profit = position * (signal['stop'] - entry) / entry
    
    return {
        "market": market['question'],
        "action": action,
        "entry": entry,
        "target": signal['target'],
        "position": position,
        "won": won,
        "profit": profit,
        "date": datetime.now().isoformat()
    }

# ============ 回测系统 ============
def backtest():
    balance = load_balance()
    trades = load_trades()
    
    print(f"\n{'='*75}")
    print(f"📈 Polymarket 趋势反转策略 - 回测")
    print(f"   策略: 极端价格反向买入，等待回归")
    print(f"   阈值: 价格 < 0.15 或 > 0.85")
    print(f"{'='*75}")
    print(f"💵 初始余额: ${balance:.2f}")
    
    markets = get_markets()
    
    if not markets:
        print("❌ 无法获取市场数据")
        return
    
    print(f"\n🔍 扫描 {len(markets)} 个市场...\n")
    
    # 找信号
    signals = []
    for m in markets:
        # 跳过低流动性市场
        if m['liquidity'] < 1000:
            continue
            
        signal = analyze_trend_reversal(m)
        if signal:
            signals.append((m, signal))
    
    print(f"📊 发现 {len(signals)} 个信号\n")
    
    # 执行交易
    new_trades = []
    for m, s in signals[:5]:
        print(f"  🎯 {m['question'][:45]}")
        print(f"     价格: ${s['entry']:.2f} → 目标: ${s['target']:.2f}")
        print(f"     策略: {s['strategy']}")
        
        result = simulate_trade(m, s, balance)
        balance += result['profit']
        new_trades.append(result)
        
        status = "✅" if result['won'] else "❌"
        print(f"     {status} {'盈利 +$' if result['won'] else '亏损 -$'}{abs(result['profit']):.2f}\n")
    
    # 保存
    trades.extend(new_trades)
    save_trades(trades)
    save_balance(balance)
    
    # 统计
    print(f"{'='*75}")
    print(f"📈 策略统计:")
    print(f"   总交易次数: {len(trades)}")
    
    if trades:
        wins = sum(1 for t in trades if t['won'])
        total = len(trades)
        win_rate = wins / total * 100 if total > 0 else 0
        total_profit = sum(t['profit'] for t in trades)
        
        print(f"   胜率: {wins}/{total} = {win_rate:.1f}%")
        print(f"   总盈亏: ${total_profit:+,.2f}")
        print(f"   当前余额: ${balance:,.2f}")
        
        # 按策略分类
        by_strategy = {}
        for t in trades:
            strat = t.get('action', 'unknown')
            if strat not in by_strategy:
                by_strategy[strat] = {'wins': 0, 'total': 0, 'profit': 0}
            by_strategy[strat]['total'] += 1
            if t['won']:
                by_strategy[strat]['wins'] += 1
            by_strategy[strat]['profit'] += t['profit']
        
        print(f"\n   📊 分策略统计:")
        for strat, stats in by_strategy.items():
            wr = stats['wins'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"      {strat}: {stats['wins']}/{stats['total']} ({wr:.0f}%) | ${stats['profit']:+,.2f}")
    
    print(f"{'='*75}\n")

if __name__ == "__main__":
    backtest()
