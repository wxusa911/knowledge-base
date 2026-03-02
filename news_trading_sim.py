#!/usr/bin/env python3
"""
新闻驱动交易策略模拟
基于 6551 新闻API + Polymarket 市场
"""

import requests
import json
import random
from datetime import datetime

OPENNEWS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiOVZKcUF4YXR6b1ZjcUJIUVNFWjQ5UzF6MmY2ZWQ1MXJnU1QyZ0VhWVh5QUEiLCJub25jZSI6ImM1YjNjMzQwLTZhOWEtNDc4ZS1iNzRkLTdhMjYyMTczYjU4ZiIsImlhdCI6MTc3MjQ1OTU0NywianRpIjoiMDZkYWYxNTItNjAxYS00MzUzLWEwMzAtYmY2OTM1NGFiMzkxIn0.44E1NynTWXUOu77fRM5LzbEt5C4Kn7Kbp13j5_lOy_c"

# 模拟配置
INITIAL_CAPITAL = 100
TRADE_AMOUNT = 10
SIMULATION_DAYS = 7
FEE = 0.02

def get_news_signals():
    """获取新闻信号"""
    url = "https://ai.6551.io/open/news_search"
    headers = {
        "Authorization": f"Bearer {OPENNEWS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"coins": ["BTC", "ETH", "SOL"], "limit": 50, "page": 1}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=10)
        result = r.json()
        
        longs = []
        shorts = []
        neutrals = []
        
        for item in result.get('data', []):
            signal = item.get('aiRating', {}).get('signal')
            score = item.get('aiRating', {}).get('score', 0)
            text = item.get('text', '')[:80]
            
            if signal == 'long':
                longs.append({'text': text, 'score': score})
            elif signal == 'short':
                shorts.append({'text': text, 'score': score})
            elif signal == 'neutral':
                neutrals.append({'text': text, 'score': score})
        
        return {'long': longs, 'short': shorts, 'neutral': neutrals}
    except Exception as e:
        print(f"获取新闻失败: {e}")
        return {'long': [], 'short': [], 'neutral': []}

def get_polymarket_markets():
    """获取Polymarket市场"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {"closed": "false", "limit": 50}
    
    try:
        r = requests.get(url, params=params, timeout=10)
        markets = []
        
        for m in r.json():
            try:
                prices = json.loads(m.get('outcomePrices', '[]'))
                if len(prices) >= 2:
                    markets.append({
                        'question': m.get('question', '')[:50],
                        'yes': float(prices[0]),
                        'no': float(prices[1]),
                        'liquidity': m.get('liquidityNum', 0)
                    })
            except:
                pass
        
        return markets
    except Exception as e:
        print(f"获取市场失败: {e}")
        return []

def analyze_market_direction(news_signals, markets):
    """
    基于新闻信号分析市场方向
    返回: buy_yes, buy_no, 或 hold
    """
    long_count = len(news_signals['long'])
    short_count = len(news_signals['short'])
    neutral_count = len(news_signals['neutral'])
    
    # 高分新闻权重
    high_score_long = sum(1 for x in news_signals['long'] if x['score'] >= 80)
    high_score_short = sum(1 for x in news_signals['short'] if x['score'] >= 80)
    
    # 计算信号强度
    long_score = long_count * 2 + high_score_long * 3
    short_score = short_count * 2 + high_score_short * 3
    
    print(f"\n📊 信号分析:")
    print(f"  Long信号: {long_count} (高分:{high_score_long})")
    print(f"  Short信号: {short_count} (高分:{high_score_short})")
    print(f"  Neutral: {neutral_count}")
    
    # 决策
    if long_score > short_score + 3:
        return 'buy_yes', 'long'
    elif short_score > long_score + 3:
        return 'buy_no', 'short'
    else:
        return 'hold', 'neutral'

def simulate_trade(action, price, capital):
    """模拟交易"""
    if action == 'hold':
        return capital, 0, 'hold'
    
    position = min(TRADE_AMOUNT, capital)
    if position < 1:
        return capital, 0, 'no_capital'
    
    # 模拟胜率 (基于信号强度)
    if action == 'buy_yes':
        # Long信号强 → 60%概率YES赢
        win_prob = 0.60
    else:
        # Short信号强 → 60%概率NO赢  
        win_prob = 0.60
    
    won = random.random() < win_prob
    
    if won:
        if action == 'buy_yes':
            profit = position * (1/price - 1) * (1 - FEE)
        else:
            profit = position * (1/(1-price) - 1) * (1 - FEE)
        exit = 'win'
    else:
        profit = -position * (1 - FEE)
        exit = 'loss'
    
    return capital + profit, profit, exit

def run_simulation():
    """运行模拟"""
    print("="*70)
    print("🎯 新闻驱动交易策略模拟")
    print("="*70)
    print(f"初始资金: ${INITIAL_CAPITAL}")
    print(f"模拟天数: {SIMULATION_DAYS}")
    print("="*70)
    
    capital = INITIAL_CAPITAL
    trades = []
    
    for day in range(1, SIMULATION_DAYS + 1):
        print(f"\n📅 Day {day}")
        print("-"*50)
        
        # 获取新闻信号
        print("📰 获取新闻中...")
        news = get_news_signals()
        
        # 获取市场
        print("📊 获取市场数据...")
        markets = get_polymarket_markets()
        
        if not markets:
            print("❌ 无法获取市场数据")
            continue
        
        # 分析决策
        action, signal_type = analyze_market_direction(news, markets)
        
        # 选择高流动性市场
        high_liq_markets = [m for m in markets if m['liquidity'] > 10000]
        if high_liq_markets:
            market = random.choice(high_liq_markets[:5])
        else:
            market = random.choice(markets[:3])
        
        print(f"\n🎯 决策: {action} | 信号: {signal_type}")
        print(f"   市场: {market['question']}")
        
        if action == 'hold':
            print(f"   原因: 信号不明显，保持观望")
            continue
        
        # 执行模拟交易
        price = market['yes'] if action == 'buy_yes' else market['no']
        capital, profit, exit = simulate_trade(action, price, capital)
        
        trades.append({
            'day': day,
            'action': action,
            'market': market['question'],
            'price': price,
            'profit': profit,
            'exit': exit,
            'capital': capital
        })
        
        print(f"   价格: ${price:.2f}")
        print(f"   结果: {exit} | 盈亏: ${profit:+.2f}")
        print(f"   资金: ${capital:.2f}")
    
    # 结果汇总
    print("\n" + "="*70)
    print("📊 模拟结果汇总")
    print("="*70)
    
    wins = sum(1 for t in trades if t['exit'] == 'win')
    losses = sum(1 for t in trades if t['exit'] == 'loss')
    total = len(trades)
    
    print(f"总交易次数: {total}")
    print(f"盈利: {wins}")
    print(f"亏损: {losses}")
    print(f"胜率: {wins/total*100:.1f}%" if total > 0 else "N/A")
    print(f"最终资金: ${capital:.2f}")
    print(f"总盈亏: ${capital - INITIAL_CAPITAL:+.2f}")
    print(f"ROI: {(capital - INITIAL_CAPITAL)/INITIAL_CAPITAL*100:+.1f}%")
    
    if capital > INITIAL_CAPITAL:
        print("\n✅ 模拟盈利!")
    else:
        print("\n❌ 模拟亏损")
    
    print("="*70)

if __name__ == "__main__":
    run_simulation()
