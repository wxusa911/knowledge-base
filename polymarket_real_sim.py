#!/usr/bin/env python3
"""
Polymarket 真实数据模拟
从 API 获取真实市场数据，基于真实价格模拟
"""

import requests
import json
import os
from datetime import datetime

BALANCE_FILE = "/home/ubuntu/.openclaw/workspace/real_sim_balance.json"

def load_balance():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('balance', 10.0)
    return 10.0

def save_balance(balance):
    with open(BALANCE_FILE, 'w') as f:
        json.dump({'balance': balance, 'updated': datetime.now().isoformat()}, f)

def get_markets():
    """获取真实市场数据"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        "closed": "false",
        "limit": "20",
        "sortBy": "volume24hr"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        markets = r.json()
        
        # 解析市场数据
        result = []
        for m in markets[:10]:  # 取前10个
            try:
                prices = json.loads(m.get('outcomePrices', '[]'))
                if len(prices) >= 2:
                    result.append({
                        "question": m.get('question', 'Unknown')[:40],
                        "yes": float(prices[0]),
                        "no": float(prices[1]),
                        "volume": m.get('volumeNum', 0),
                        "liquidity": m.get('liquidityNum', 0),
                        "endDate": m.get('endDate', '')
                    })
            except:
                continue
        return result
    except Exception as e:
        print(f"API错误: {e}")
        return []

def simulate_trade(market, balance):
    """模拟一笔交易"""
    # 策略: 找边缘 >5% 的机会
    # 假设模型预测: 如果YES价格 < 0.5，则模型认为概率更高
    
    # 简单策略: 如果YES价格低，买YES等涨
    if market['yes'] < 0.5:
        model_prob = market['yes'] + 0.15  # 模型认为会涨15%
    else:
        model_prob = market['yes']
    
    edge = abs(model_prob - market['yes'])
    
    if edge > 0.05:  # 边缘 > 5%
        # Kelly 仓位
        position = balance * 0.1  # 10%
        
        # 模拟结果: 基于真实价格
        # 如果买YES赢了，价格应该 > 买入价
        # 简化: 50%概率赢
        import random
        won = random.random() < market['yes']  # 用真实价格概率
        
        if won:
            profit = position * (1/market['yes'] - 1)
        else:
            profit = -position
        
        return {
            "market": market['question'],
            "action": "YES",
            "price": market['yes'],
            "position": position,
            "won": won,
            "profit": profit
        }
    return None

def run_simulation():
    balance = load_balance()
    
    print(f"\n{'='*65}")
    print(f"📈 Polymarket 真实数据模拟")
    print(f"   数据源: Polymarket API (实时)")
    print(f"{'='*65}")
    print(f"💵 初始余额: ${balance:.2f}")
    
    # 获取真实市场
    markets = get_markets()
    
    if not markets:
        print("❌ 无法获取市场数据")
        return
    
    print(f"\n🔍 扫描 {len(markets)} 个热门市场...\n")
    
    trades = []
    for m in markets:
        result = simulate_trade(m, balance)
        if result:
            balance += result['profit']
            trades.append(result)
            
            status = "✅" if result['won'] else "❌"
            print(f"  {status} {result['market']}")
            print(f"      买入: YES @ ${result['price']:.2f} | 仓位: ${result['position']:.2f}")
            print(f"      结果: {'盈利 +$' if result['won'] else '亏损 -$'}{abs(result['profit']):.2f}")
    
    save_balance(balance)
    
    print(f"\n{'='*65}")
    print(f"📊 交易统计:")
    print(f"   交易次数: {len(trades)}")
    wins = sum(1 for t in trades if t['won'])
    print(f"   胜率: {wins}/{len(trades)} = {wins*100//max(len(trades),1)}%")
    total_profit = sum(t['profit'] for t in trades)
    print(f"   总盈亏: ${total_profit:+.2f}")
    print(f"   当前余额: ${balance:.2f}")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    run_simulation()
