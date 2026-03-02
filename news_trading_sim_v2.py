#!/usr/bin/env python3
"""
新闻驱动交易策略模拟 V2
改进版: 匹配新闻主题到相关市场
"""

import requests
import json
import random
from datetime import datetime

OPENNEWS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiOVZKcUF4YXR6b1ZjcUJIUVNFWjQ5UzF6MmY2ZWQ1MXJnU1QyZ0VhWVh5QUEiLCJub25jZSI6ImM1YjNjMzQwLTZhOWEtNDc4ZS1iNzRkLTdhMjYyMTczYjU4ZiIsImlhdCI6MTc3MjQ1OTU0NywianRpIjoiMDZkYWYxNTItNjAxYS00MzUzLWEwMzAtYmY2OTM1NGFiMzkxIn0.44E1NynTWXUOu77fRM5LzbEt5C4Kn7Kbp13j5_lOy_c"

INITIAL_CAPITAL = 100
TRADE_AMOUNT = 10
SIMULATION_DAYS = 7
FEE = 0.02

# 主题关键词映射
TOPIC_KEYWORDS = {
    'crypto': ['BTC', 'Bitcoin', 'ETH', 'Ethereum', 'SOL', 'Solana', 'crypto', 'token'],
    'trump': ['Trump', 'President', 'Biden', 'administration', 'White House'],
    'war': ['Ukraine', 'Russia', 'war', 'military', 'ceasefire', 'Iran', 'Middle East'],
    'entertainment': ['GTA', 'album', 'music', 'Rihanna', 'Carti', 'movie', 'release'],
    'tech': ['AI', 'OpenAI', 'Google', 'Apple', 'Microsoft', 'tech']
}

def get_news_with_topics():
    """获取新闻并分类"""
    url = "https://ai.6551.io/open/news_search"
    headers = {"Authorization": f"Bearer {OPENNEWS_TOKEN}", "Content-Type": "application/json"}
    data = {"limit": 50, "page": 1}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=10)
        result = r.json()
        
        topics = {k: {'long': [], 'short': [], 'neutral': [], 'score': 0} for k in TOPIC_KEYWORDS}
        
        for item in result.get('data', []):
            text = item.get('text', '').lower()
            signal = item.get('aiRating', {}).get('signal')
            score = item.get('aiRating', {}).get('score', 0)
            
            # 匹配主题
            for topic, keywords in TOPIC_KEYWORDS.items():
                if any(k.lower() in text for k in keywords):
                    if signal == 'long':
                        topics[topic]['long'].append({'text': item.get('text', '')[:50], 'score': score})
                        topics[topic]['score'] += score
                    elif signal == 'short':
                        topics[topic]['short'].append({'text': item.get('text', '')[:50], 'score': score})
                        topics[topic]['score'] -= score
        
        return topics
    except Exception as e:
        print(f"获取新闻失败: {e}")
        return {k: {'long': [], 'short': [], 'neutral': [], 'score': 0} for k in TOPIC_KEYWORDS}

def get_polymarket_markets():
    """获取Polymarket市场"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {"closed": "false", "limit": 100}
    
    try:
        r = requests.get(url, params=params, timeout=10)
        markets = []
        
        for m in r.json():
            try:
                prices = json.loads(m.get('outcomePrices', '[]'))
                if len(prices) >= 2:
                    q = m.get('question', '').lower()
                    
                    # 识别市场主题
                    topic = None
                    for t, keywords in TOPIC_KEYWORDS.items():
                        if any(k.lower() in q for k in keywords):
                            topic = t
                            break
                    
                    markets.append({
                        'question': m.get('question', ''),
                        'yes': float(prices[0]),
                        'no': float(prices[1]),
                        'liquidity': m.get('liquidityNum', 0),
                        'topic': topic
                    })
            except:
                pass
        
        return markets
    except:
        return []

def make_decision(topics, markets):
    """基于主题匹配做决策"""
    # 找最相关市场
    relevant = [m for m in markets if m['topic'] and m['liquidity'] > 5000]
    
    if not relevant:
        # 没有相关市场，保持观望
        return 'hold', None, 0
    
    # 选择分数最高的主题
    best_topic = max(topics.items(), key=lambda x: abs(x[1]['score']))
    topic_name, topic_data = best_topic
    
    # 找该主题的市场
    topic_markets = [m for m in relevant if m['topic'] == topic_name]
    
    if not topic_markets:
        return 'hold', None, 0
    
    # 选择高流动性市场
    market = max(topic_markets, key=lambda x: x['liquidity'])
    
    signal = topic_data['score']
    
    if signal > 50:  # 强Long信号
        return 'buy_yes', market, signal
    elif signal < -50:  # 强Short信号
        return 'buy_no', market, signal
    else:
        return 'hold', market, signal

def simulate_trade(action, price, capital):
    """模拟交易"""
    if action == 'hold':
        return capital, 0, 'hold'
    
    position = min(TRADE_AMOUNT, capital)
    if position < 1:
        return capital, 0, 'no_capital'
    
    # 假设有信号时胜率更高 (70%)
    win_prob = 0.70
    
    won = random.random() < win_prob
    
    if won:
        profit = position * (1/price - 1) * (1 - FEE)
        exit = 'win'
    else:
        profit = -position * (1 - FEE)
        exit = 'loss'
    
    return capital + profit, profit, exit

def run_simulation():
    print("="*70)
    print("🎯 新闻驱动交易策略模拟 V2 (主题匹配)")
    print("="*70)
    print(f"初始资金: ${INITIAL_CAPITAL}")
    print(f"模拟天数: {SIMULATION_DAYS}")
    print("="*70)
    
    capital = INITIAL_CAPITAL
    trades = []
    
    for day in range(1, SIMULATION_DAYS + 1):
        print(f"\n📅 Day {day}")
        
        topics = get_news_with_topics()
        markets = get_polymarket_markets()
        
        # 显示各主题信号
        print("\n📊 主题信号:")
        for topic, data in topics.items():
            if data['long'] or data['short']:
                score = data['score']
                direction = "📈" if score > 0 else "📉" if score < 0 else "➡️"
                print(f"  {topic}: {direction} (score: {score})")
        
        action, market, signal = make_decision(topics, markets)
        
        if action == 'hold' or not market:
            print(f"\n🎯 决策: hold (无明确信号)")
            continue
        
        print(f"\n🎯 决策: {action}")
        print(f"   市场: {market['question'][:50]}")
        print(f"   主题: {market['topic']}")
        print(f"   信号强度: {signal}")
        
        price = market['yes'] if action == 'buy_yes' else market['no']
        capital, profit, exit = simulate_trade(action, price, capital)
        
        trades.append({
            'day': day,
            'action': action,
            'topic': market['topic'],
            'profit': profit,
            'exit': exit,
            'capital': capital
        })
        
        print(f"   价格: ${price:.2f}")
        print(f"   结果: {exit} | 盈亏: ${profit:+.2f}")
        print(f"   资金: ${capital:.2f}")
    
    # 结果
    print("\n" + "="*70)
    print("📊 模拟结果汇总")
    print("="*70)
    
    wins = sum(1 for t in trades if t['exit'] == 'win')
    total = len(trades)
    
    print(f"总交易次数: {total}")
    print(f"盈利: {wins}")
    print(f"亏损: {total - wins}")
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
