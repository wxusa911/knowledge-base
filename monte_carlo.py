#!/usr/bin/env python3
"""
 Polymarket 统计套利策略 - 基于价格分布规律
 核心: 分析价格分布，找到高胜率入场点
"""

import requests
import json
import os
import random
from datetime import datetime
from collections import defaultdict

def get_markets():
    """获取市场数据"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {"closed": "false", "limit": 100}
    
    r = requests.get(url, params=params, timeout=10)
    markets = r.json()
    
    result = []
    for m in markets:
        try:
            prices = json.loads(m.get('outcomePrices', '[]'))
            if len(prices) >= 2:
                result.append({
                    "question": m.get('question'),
                    "yes": float(prices[0]),
                    "no": float(prices[1]),
                    "volume": float(m.get('volume', 0)),
                    "liquidity": float(m.get('liquidity', 0)),
                })
        except:
            continue
    return result

# ============ 策略: 统计回归 ============
def get_strategy_signal(market):
    """
    基于统计规律的策略:
    
    策略1: 50%回归 - 价格在0.45-0.55区间时，买两端
    策略2: 极端低买 - YES<0.20时，买YES等反弹
    策略3: 流动性高概率 - 高流动性市场，价格>0.70则更可靠
    """
    yes = market['yes']
    no = market['no']
    volume = market['volume']
    liquidity = market['liquidity']
    
    signals = []
    
    # 策略1: 50%回归
    if 0.40 <= yes <= 0.60:
        # 接近50%，两边都可能
        # 统计: 50%价格最终会偏向某一方
        # 但我们不知道方向，所以观望
        pass
    
    # 策略2: 极端低买 YES
    if yes < 0.15:
        # 极端低价，可能反弹
        signals.append({
            "strategy": "EXTREME_LOW_YES",
            "action": "BUY_YES",
            "edge": 0.15 - yes,
            "confidence": 0.25  # 低信心
        })
    
    # 策略3: 极端高卖 YES  
    if yes > 0.85:
        signals.append({
            "strategy": "EXTREME_HIGH_YES",
            "action": "BUY_NO",  # 买NO等价于卖YES
            "edge": yes - 0.85,
            "confidence": 0.30
        })
    
    # 策略4: 极端低买 NO
    if no < 0.15:
        signals.append({
            "strategy": "EXTREME_LOW_NO",
            "action": "BUY_NO",
            "edge": 0.15 - no,
            "confidence": 0.25
        })
    
    # 策略5: 极端高卖 NO
    if no > 0.85:
        signals.append({
            "strategy": "EXTREME_HIGH_NO",
            "action": "BUY_YES",
            "edge": no - 0.85,
            "confidence": 0.30
        })
    
    # 策略6: 高流动性市场趋势
    if liquidity > 50000 and 0.60 <= yes <= 0.80:
        # 高流动性市场，价格相对可靠
        # 假设趋势会继续
        if yes > 0.70:
            signals.append({
                "strategy": "LIQUID_TREND_YES",
                "action": "BUY_YES",
                "edge": yes - 0.50,
                "confidence": 0.60
            })
    
    return signals

# ============ 模拟交易 ============
def simulate(signals, balance, fee=0.02):
    """模拟交易"""
    results = []
    
    for s in signals:
        # 仓位 = 余额 * 信心度
        position = balance * s['confidence']
        
        # 真实概率需要模拟
        # 基于边缘计算预期胜率
        edge = s['edge']
        
        # 简化模型: 极端价格反转概率
        if "EXTREME_LOW" in s['strategy']:
            # 极端低价，反弹概率 ~40%
            win_prob = 0.40
        elif "EXTREME_HIGH" in s['strategy']:
            # 极端高价，反转概率 ~45%
            win_prob = 0.45
        elif "LIQUID_TREND" in s['strategy']:
            # 高流动性趋势，概率 ~55%
            win_prob = 0.55
        else:
            win_prob = 0.50
        
        # 模拟结果
        won = random.random() < win_prob
        
        if won:
            if "YES" in s['action']:
                profit = position * edge * (1 - fee)
            else:
                profit = position * edge * (1 - fee)
        else:
            profit = -position * (1 - fee)
        
        results.append({
            "strategy": s['strategy'],
            "action": s['action'],
            "edge": edge,
            "win_prob": win_prob,
            "won": won,
            "profit": profit
        })
        
        balance += profit
    
    return results, balance

# ============ Monte Carlo 模拟 ============
def monte_carlo_simulation(n_runs=1000):
    """蒙特卡洛模拟"""
    markets = get_markets()
    
    # 收集所有信号
    all_signals = []
    for m in markets:
        if m['liquidity'] < 1000:
            continue
        signals = get_strategy_signal(m)
        all_signals.extend(signals)
    
    print(f"\n{'='*75}")
    print(f"🎲 Polymarket 策略 Monte Carlo 模拟")
    print(f"   策略: 极端价格 + 流动性趋势")
    print(f"   运行: {n_runs} 次模拟")
    print(f"{'='*75}")
    print(f"📊 发现 {len(all_signals)} 个信号\n")
    
    # 按策略分类统计
    strategy_stats = defaultdict(lambda: {'wins': 0, 'total': 0, 'profit': 0})
    
    all_results = []
    
    for run in range(n_runs):
        balance = 1000.0
        for s in all_signals[:10]:  # 每次最多10笔
            edge = s['edge']
            
            # 根据策略计算胜率
            if "EXTREME_LOW" in s['strategy']:
                win_prob = 0.40
            elif "EXTREME_HIGH" in s['strategy']:
                win_prob = 0.45
            elif "LIQUID_TREND" in s['strategy']:
                win_prob = 0.55
            else:
                win_prob = 0.50
            
            position = balance * s['confidence']
            won = random.random() < win_prob
            
            if won:
                profit = position * edge * 0.98
            else:
                profit = -position * 0.98
            
            balance += profit
            
            key = s['strategy']
            strategy_stats[key]['total'] += 1
            if won:
                strategy_stats[key]['wins'] += 1
            strategy_stats[key]['profit'] += profit
        
        all_results.append(balance)
    
    # 统计结果
    print(f"📈 策略统计:")
    print(f"{'='*75}")
    
    for strategy, stats in sorted(strategy_stats.items()):
        win_rate = stats['wins'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"📌 {strategy}:")
        print(f"   交易: {stats['total']} | 胜率: {win_rate:.1f}% | 盈亏: ${stats['profit']:+,.2f}")
    
    # 总体
    total_trades = sum(s['total'] for s in strategy_stats.values())
    total_wins = sum(s['wins'] for s in strategy_stats.values())
    overall_win_rate = total_wins / total_trades * 100 if total_trades > 0 else 0
    
    avg_balance = sum(all_results) / len(all_results)
    win_count = sum(1 for r in all_results if r > 1000)
    win_pct = win_count / len(all_results) * 100
    
    print(f"\n{'='*75}")
    print(f"🏆 总体结果 ({n_runs} 次模拟):")
    print(f"   总交易: {total_trades}")
    print(f"   总体胜率: {overall_win_rate:.1f}%")
    print(f"   平均余额: ${avg_balance:,.2f}")
    print(f"   盈利概率: {win_pct:.1f}%")
    
    if overall_win_rate >= 75:
        print(f"\n✅ 胜率 >= 75%，策略可用于实盘!")
    else:
        print(f"\n⚠️ 胜率 < 75%，需要优化策略")
    
    print(f"{'='*75}\n")

if __name__ == "__main__":
    monte_carlo_simulation(1000)
