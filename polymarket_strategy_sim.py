#!/usr/bin/env python3
"""
Polymarket 策略模拟测试 - 真实市场数据
"""

import requests
import json

# 获取市场数据
def get_markets():
    url = "https://gamma-api.polymarket.com/markets"
    params = {"closed": "false", "limit": 100}
    r = requests.get(url, params=params, timeout=10)
    return r.json()

def analyze_no_maxi_opportunity(market):
    """
    NO-Maxi 策略分析
    找被高估的 NO (即 YES 概率被低估)
    """
    try:
        prices = json.loads(market.get('outcomePrices', '[]'))
        if len(prices) < 2:
            return None
        
        yes = float(prices[0])
        no = float(prices[1])
        liq = market.get('liquidityNum', 0)
        
        # NO-Maxi: 找 YES > 0.70 的市场 (市场高估了YES)
        # 买 NO 等事实纠正
        if yes > 0.70 and liq > 5000:
            return {
                "type": "NO-Maxi",
                "question": market.get('question', '')[:50],
                "yes": yes,
                "no": no,
                "liquidity": liq,
                "edge": yes - 0.70,  # 市场高估程度
                "action": "BUY_NO",
                "reason": "YES被高估，等待不发生"
            }
        
        # 反向: 找 NO > 0.70 (市场高估了NO)
        if no > 0.70 and liq > 5000:
            return {
                "type": "NO-Maxi",
                "question": market.get('question', '')[:50],
                "yes": yes,
                "no": no,
                "liquidity": liq,
                "edge": no - 0.70,
                "action": "BUY_YES",
                "reason": "NO被高估，等待发生"
            }
        
        return None
    except:
        return None

def simulate_no_maxi(markets, capital=100, trades=5):
    """模拟 NO-Maxi 策略"""
    print("\n" + "="*70)
    print("🎯 Polymarket NO-Maxi 策略模拟")
    print("="*70)
    print(f"初始资金: ${capital}")
    print(f"最大交易数: {trades}")
    print()
    
    # 找机会
    opportunities = []
    for m in markets:
        opp = analyze_no_maxi_opportunity(m)
        if opp:
            opportunities.append(opp)
    
    print(f"📊 发现 {len(opportunities)} 个 NO-Maxi 机会\n")
    
    # 模拟交易
    balance = capital
    wins = 0
    trades_count = 0
    
    for opp in opportunities[:trades]:
        print(f"🔍 {opp['question']}")
        print(f"   YES: {opp['yes']:.0%} | NO: {opp['no']:.0%} | 流动性: ${opp['liquidity']:,.0f}")
        print(f"   建议: {opp['action']} | 原因: {opp['reason']}")
        
        # 简化模拟: 假设 60% 胜率 (基于结构性高估)
        import random
        won = random.random() < 0.60
        
        if won:
            # 买 NO 赢了 = YES概率下降，NO上涨
            profit = balance * 0.20 * (opp['no'] / (1 - opp['no']))
            balance += profit
            wins += 1
            print(f"   ✅ 盈利 +${profit:.2f}")
        else:
            loss = balance * 0.20
            balance -= loss
            print(f"   ❌ 亏损 -${loss:.2f}")
        
        trades_count += 1
        print()
    
    # 统计
    win_rate = wins / trades_count * 100 if trades_count > 0 else 0
    total_return = (balance - capital) / capital * 100
    
    print("="*70)
    print(f"📈 模拟结果:")
    print(f"   交易次数: {trades_count}")
    print(f"   胜率: {wins}/{trades_count} = {win_rate:.0f}%")
    print(f"   最终余额: ${balance:.2f}")
    print(f"   总收益率: {total_return:+.1f}%")
    print("="*70)
    
    if win_rate >= 60:
        print("\n✅ 策略模拟盈利，可考虑实盘测试")
    else:
        print("\n⚠️ 需要优化策略参数")
    
    return balance

if __name__ == "__main__":
    print("📡 获取 Polymarket 市场数据...")
    markets = get_markets()
    print(f"✅ 获取到 {len(markets)} 个市场")
    
    # 运行模拟
    simulate_no_maxi(markets, capital=100, trades=5)
