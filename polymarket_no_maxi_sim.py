#!/usr/bin/env python3
"""
Polymarket NO-Maxi 策略 - 真实模拟
目标: 小资金稳定收益 > 手续费
"""

import requests
import json
import random
from datetime import datetime

def get_markets():
    url = "https://gamma-api.polymarket.com/markets"
    r = requests.get(url, params={"closed": "false", "limit": 100}, timeout=10)
    return r.json()

def find_no_maxi_opportunities(markets):
    """找 NO-Maxi 机会"""
    opportunities = []
    for m in markets:
        try:
            prices = json.loads(m.get('outcomePrices', '[]'))
            if len(prices) < 2:
                continue
            
            yes = float(prices[0])
            no = float(prices[1])
            liq = m.get('liquidityNum', 0)
            
            # 只看流动性好的
            if liq < 1000:
                continue
            
            # NO-Maxi: 找 YES > 0.65 (市场高估YES)
            if yes > 0.65:
                opportunities.append({
                    "question": m.get('question', '')[:50],
                    "yes": yes,
                    "no": no,
                    "liquidity": liq,
                    "action": "BUY_NO",
                    "edge": yes - 0.65
                })
            
            # 反向: 找 NO > 0.65 (市场高估NO)
            elif no > 0.65:
                opportunities.append({
                    "question": m.get('question', '')[:50],
                    "yes": yes,
                    "no": no,
                    "liquidity": liq,
                    "action": "BUY_YES",
                    "edge": no - 0.65
                })
        except:
            continue
    
    return opportunities

def simulate_trade(opp, capital, fee=0.02):
    """
    模拟单笔交易
    手续费: 2%
    """
    position = capital * 0.10  # 每次10%
    
    if opp['action'] == 'BUY_NO':
        # 买 NO 赢了 = YES概率下降，NO上涨
        # 简化: 假设60%胜率
        win_prob = 0.60
        won = random.random() < win_prob
        
        if won:
            # NO 赢了，收益 = 投入 * (1/no - 1) - 手续费
            profit = position * (1/opp['no'] - 1) * (1 - fee)
        else:
            profit = -position * (1 - fee)
    
    else:  # BUY_YES
        win_prob = 0.60
        won = random.random() < win_prob
        
        if won:
            profit = position * (1/opp['yes'] - 1) * (1 - fee)
        else:
            profit = -position * (1 - fee)
    
    return won, profit

def run_simulation(initial_capital=100, n_days=30, n_simulations=100):
    """Monte Carlo 模拟"""
    
    markets = get_markets()
    opportunities = find_no_maxi_opportunities(markets)
    
    print("="*70)
    print("🎯 Polymarket NO-Maxi 策略模拟")
    print("="*70)
    print(f"初始资金: ${initial_capital}")
    print(f"模拟天数: {n_days}")
    print(f"模拟次数: {n_simulations}")
    print(f"\n发现机会: {len(opportunities)} 个")
    
    if not opportunities:
        print("❌ 无合适机会")
        return
    
    print(f"\n前5个机会:")
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"  {i}. {opp['question']}")
        print(f"     {opp['action']} | YES:{opp['yes']:.0%} NO:{opp['no']:.0%} | 流动性:${opp['liquidity']:,.0f}")
    
    print("\n" + "="*70)
    print("📊 Monte Carlo 模拟结果")
    print("="*70)
    
    results = []
    
    for sim in range(n_simulations):
        capital = initial_capital
        daily_returns = []
        
        for day in range(n_days):
            if not opportunities or capital < 10:
                break
            
            # 每天随机选2个机会
            day_opps = random.sample(opportunities, min(2, len(opportunities)))
            day_profit = 0
            
            for opp in day_opps:
                won, profit = simulate_trade(opp, capital)
                day_profit += profit
            
            capital += day_profit
            daily_returns.append(day_profit)
        
        results.append({
            'final': capital,
            'return': (capital - initial_capital) / initial_capital * 100,
            'days': len(daily_returns)
        })
    
    # 统计
    finals = [r['final'] for r in results]
    returns = [r['return'] for r in results]
    
    avg = sum(finals) / len(finals)
    median = sorted(finals)[len(finals)//2]
    wins = sum(1 for f in finals if f > initial_capital)
    win_rate = wins / n_simulations * 100
    
    print(f"平均最终资金: ${avg:.2f}")
    print(f"中位数: ${median:.2f}")
    print(f"盈利概率: {win_rate:.1f}%")
    print(f"平均收益率: {sum(returns)/len(returns):+.1f}%")
    print(f"最高: ${max(finals):.2f}")
    print(f"最低: ${min(finals):.2f}")
    
    # 手续费覆盖分析
    total_fees = initial_capital * 0.02 * n_days * 2  # 假设每天2笔，每笔2%
    print(f"\n📝 手续费成本 (估计): ${total_fees:.2f}")
    
    if avg > initial_capital + total_fees:
        print("✅ 预期收益 > 手续费成本")
    else:
        print("⚠️ 预期收益 < 手续费成本")
    
    print("="*70)

if __name__ == "__main__":
    run_simulation(initial_capital=100, n_days=30, n_simulations=1000)
