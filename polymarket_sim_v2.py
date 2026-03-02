#!/usr/bin/env python3
"""
Polymarket NO-Maxi 策略 - 修正版
目标: 小资金稳定收益 > 手续费
"""

import requests
import json
import random

def get_markets():
    url = "https://gamma-api.polymarket.com/markets"
    r = requests.get(url, params={"closed": "false", "limit": 100}, timeout=10)
    return r.json()

def find_opportunities(markets):
    """找 NO-Maxi 机会"""
    ops = []
    for m in markets:
        try:
            prices = json.loads(m.get('outcomePrices', '[]'))
            if len(prices) < 2:
                continue
            yes = float(prices[0])
            no = float(prices[1])
            liq = m.get('liquidityNum', 0)
            
            if liq < 1000:
                continue
            
            # NO-Maxi: 买被高估那一边
            # 如果 YES > 0.70, 市场高估YES, 买NO
            # 如果 NO > 0.70, 市场高估NO, 买YES
            if yes > 0.70:
                ops.append({
                    "action": "BUY_NO",
                    "price": no,
                    "win_prob": no,  # NO赢的概率
                    "question": m.get('question', '')[:45],
                    "liq": liq
                })
            elif no > 0.70:
                ops.append({
                    "action": "BUY_YES",
                    "price": yes,
                    "win_prob": yes,  # YES赢的概率
                    "question": m.get('question', '')[:45],
                    "liq": liq
                })
        except:
            continue
    return ops

def simulate_trade(opp, capital):
    """单笔交易模拟"""
    position = capital * 0.10  # 10%仓位
    fee = 0.02  # 2%手续费
    
    price = opp['price']
    win_prob = opp['win_prob']
    
    # 计算收益
    # 买入: position / price = 股数
    # 赢了: 股数 * $1 - 手续费
    # 输了: -position - 手续费
    
    shares = position / price
    
    won = random.random() < win_prob
    
    if won:
        profit = shares * 1.0 * (1 - fee) - position
    else:
        profit = -position * (1 + fee)
    
    return won, profit

def run_sim():
    markets = get_markets()
    ops = find_opportunities(markets)
    
    print("="*70)
    print("🎯 Polymarket NO-Maxi 策略模拟")
    print("="*70)
    print(f"发现 NO-Maxi 机会: {len(ops)} 个\n")
    
    if not ops:
        print("❌ 无机会")
        return
    
    # 显示机会
    print("机会列表:")
    for i, opp in enumerate(ops[:8], 1):
        print(f"  {i}. {opp['question']}")
        print(f"     操作: {opp['action']} @ ${opp['price']:.2f} (胜率: {opp['win_prob']:.0%})")
    
    print("\n" + "="*70)
    print("📊 模拟结果 (1000次, 30天)")
    print("="*70)
    
    results = []
    
    for _ in range(1000):
        capital = 100.0
        
        for day in range(30):
            if capital < 10 or not ops:
                break
            
            # 每天随机选2个机会
            daily_ops = random.sample(ops, min(2, len(ops)))
            
            for opp in daily_ops:
                won, profit = simulate_trade(opp, capital)
                capital += profit
        
        results.append(capital)
    
    # 统计
    wins = sum(1 for r in results if r > 100)
    avg = sum(results) / len(results)
    median = sorted(results)[len(results)//2]
    
    print(f"初始资金: $100")
    print(f"模拟天数: 30天")
    print(f"每日交易: 2笔")
    print(f"\n结果:")
    print(f"  平均最终资金: ${avg:.2f}")
    print(f"  中位数: ${median:.2f}")
    print(f"  盈利概率: {wins/10:.1f}%")
    print(f"  最高: ${max(results):.2f}")
    print(f"  最低: ${min(results):.2f}")
    
    # 手续费
    fees = 100 * 0.10 * 2 * 30 * 0.02  # 本金*仓位*交易数*手续费
    print(f"\n手续费成本 (估计): ${fees:.2f}")
    
    if avg > 100 + fees:
        print("✅ 预期收益 > 手续费")
    else:
        print("⚠️ 预期收益 < 手续费")
    
    print("="*70)

if __name__ == "__main__":
    run_sim()
