#!/usr/bin/env python3
"""
Polymarket Trader - 新闻驱动自动交易策略
优化版: 缓存 + 批量处理 + 减少token
"""

import os
import sys
import json
import time
import requests
import hashlib
from datetime import datetime, timedelta

# ============== 配置 ==============
OPENNEWS_TOKEN = os.getenv("OPENNEWS_TOKEN", "")
POLYMARKET_PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY", "")
POLYGON_RPC_URL = os.getenv("POLYGON_RPC_URL", "")

# 模拟配置
INITIAL_CAPITAL = 100
TRADE_AMOUNT = 10  # 每次10%
FEE = 0.02

# 主题关键词映射 (优化: 精简关键词)
TOPIC_KEYWORDS = {
    'crypto': ['BTC', 'Bitcoin', 'ETH', 'Ethereum', 'SOL', 'crypto'],
    'trump': ['Trump', 'President', 'Biden', 'White House'],
    'war': ['Ukraine', 'Russia', 'war', 'ceasefire', 'Iran'],
    'gta': ['GTA', 'album', 'music', 'Rihanna', 'release']
}

# ============== 缓存系统 (优化: 减少API调用) ==============
class Cache:
    def __init__(self, ttl=300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
        return None
    
    def set(self, key, data):
        self.cache[key] = (data, time.time())

cache = Cache(ttl=300)  # 5分钟缓存

# ============== 优化1: 批量获取新闻 ==============
def get_news_batch(coins=None, limit=50):
    """批量获取新闻，减少API调用"""
    cache_key = f"news_{coins}_{limit}"
    cached = cache.get(cache_key)
    if cached:
        print("📰 [缓存] 新闻数据")
        return cached
    
    url = "https://ai.6551.io/open/news_search"
    headers = {
        "Authorization": f"Bearer {OPENNEWS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"limit": limit, "page": 1}
    if coins:
        data["coins"] = coins
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=10)
        result = r.json()
        cache.set(cache_key, result)
        return result
    except Exception as e:
        print(f"❌ 获取新闻失败: {e}")
        return {"data": []}

# ============== 优化2: 精简信号分析 ==============
def analyze_signals_fast(news_data):
    """快速分析信号 - 简化逻辑减少token"""
    topics = {k: {'long': 0, 'short': 0, 'score': 0} for k in TOPIC_KEYWORDS}
    
    for item in news_data.get('data', []):
        text = item.get('text', '').lower()
        signal = item.get('aiRating', {}).get('signal', 'neutral')
        score = item.get('aiRating', {}).get('score', 0)
        
        # 优化: 只处理高分新闻
        if score < 60:
            continue
        
        # 匹配主题
        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(k.lower() in text for k in keywords):
                if signal == 'long':
                    topics[topic]['score'] += score
                elif signal == 'short':
                    topics[topic]['score'] -= score
    
    return topics

# ============== 优化3: 缓存市场数据 ==============
def get_markets_cached():
    """缓存市场数据"""
    cache_key = "polymarket_markets"
    cached = cache.get(cache_key)
    if cached:
        print("📊 [缓存] 市场数据")
        return cached
    
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
        
        cache.set(cache_key, markets)
        return markets
    except Exception as e:
        print(f"❌ 获取市场失败: {e}")
        return []

# ============== 优化4: 简化决策逻辑 ==============
def make_decision(topics, markets):
    """简化决策 - 减少复杂计算"""
    # 找有信号且有相关市场的主题
    for topic, data in topics.items():
        score = data['score']
        if abs(score) < 50:  # 优化: 阈值判断
            continue
        
        # 找相关市场
        relevant = [m for m in markets 
                   if m['topic'] == topic and m['liquidity'] > 5000]
        if relevant:
            market = max(relevant, key=lambda x: x['liquidity'])
            if score > 0:
                return 'buy_yes', market, score
            else:
                return 'buy_no', market, score
    
    return 'hold', None, 0

# ============== 模拟交易 ==============
def simulate_trade(action, price, capital):
    """简化交易模拟"""
    if action == 'hold':
        return capital, 0, 'hold'
    
    position = min(TRADE_AMOUNT, capital)
    if position < 1:
        return capital, 0, 'no_capital'
    
    # 优化: 有信号时假设70%胜率
    won = (action == 'buy_yes' and 
           random.random() < 0.70) or \
          (action == 'buy_no' and 
           random.random() < 0.70)
    
    if won:
        profit = position * (1/price - 1) * (1 - FEE)
        exit = 'win'
    else:
        profit = -position * (1 - FEE)
        exit = 'loss'
    
    return capital + profit, profit, exit

import random

# ============== 主程序 ==============
def run_trader(mode='simulate', days=7):
    print("="*60)
    print("📈 Polymarket Trader - 优化版")
    print("="*60)
    print(f"模式: {mode}")
    print(f"Token: {'已设置' if OPENNEWS_TOKEN else '未设置'}")
    print("="*60)
    
    capital = INITIAL_CAPITAL
    trades = []
    
    for day in range(1, days + 1):
        print(f"\n📅 Day {day}")
        
        # 优化: 批量获取
        news = get_news_batch(limit=50)
        markets = get_markets_cached()
        
        # 优化: 快速分析
        topics = analyze_signals_fast(news)
        
        # 显示信号
        print("\n📊 信号:")
        for topic, data in topics.items():
            if data['score']:
                print(f"  {topic}: {data['score']:+d}")
        
        # 决策
        action, market, score = make_decision(topics, markets)
        
        if action == 'hold' or not market:
            print(f"\n🎯 决策: hold (信号不明显)")
            continue
        
        print(f"\n🎯 决策: {action}")
        print(f"   市场: {market['question'][:50]}")
        
        price = market['yes'] if action == 'buy_yes' else market['no']
        capital, profit, exit_type = simulate_trade(action, price, capital)
        
        trades.append({
            'day': day,
            'action': action,
            'profit': profit,
            'exit': exit_type,
            'capital': capital
        })
        
        print(f"   结果: {exit_type} | 盈亏: ${profit:+.2f}")
        print(f"   资金: ${capital:.2f}")
    
    # 结果
    print("\n" + "="*60)
    print("📊 结果汇总")
    print("="*60)
    wins = sum(1 for t in trades if t['exit'] == 'win')
    total = len(trades)
    print(f"交易: {total} | 胜率: {wins/total*100:.0f}%" if total else "N/A")
    print(f"资金: ${capital:.2f}")
    print(f"盈亏: ${capital - INITIAL_CAPITAL:+.2f}")
    print(f"ROI: {(capital - INITIAL_CAPITAL)/INITIAL_CAPITAL*100:+.0f}%")
    print("="*60)
    
    return {
        'capital': capital,
        'trades': total,
        'win_rate': wins/total*100 if total else 0,
        'profit': capital - INITIAL_CAPITAL
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='simulate')
    parser.add_argument('--days', type=int, default=7)
    args = parser.parse_args()
    
    run_trader(mode=args.mode, days=args.days)
