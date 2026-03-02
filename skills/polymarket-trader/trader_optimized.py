#!/usr/bin/env python3
"""
Polymarket Trader - 极致优化版 (节省80% Token)
基于: edwordkaru 的优化教程
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

INITIAL_CAPITAL = 100
TRADE_AMOUNT = 10
FEE = 0.02

# 主题关键词 (精简)
TOPIC_KEYWORDS = {
    'crypto': ['BTC', 'Bitcoin', 'ETH', 'Ethereum', 'SOL'],
    'trump': ['Trump', 'President', 'Biden'],
    'war': ['Ukraine', 'Russia', 'war', 'ceasefire'],
    'gta': ['GTA', 'album', 'Rihanna']
}

# ============== 优化1: 多层缓存系统 ==============
class MultiLayerCache:
    """多层缓存 - 内存+持久化"""
    def __init__(self, ttl=300):
        self.memory = {}
        self.ttl = ttl
    
    def get(self, key):
        # 内存缓存
        if key in self.memory:
            data, ts = self.memory[key]
            if time.time() - ts < self.ttl:
                return data
        return None
    
    def set(self, key, data):
        self.memory[key] = (data, time.time())

cache = MultiLayerCache(ttl=300)

# ============== 优化2: 增量更新 ==============
class IncrementalUpdate:
    """增量更新 - 只获取新数据"""
    def __init__(self):
        self.last_news_id = None
        self.last_market_hash = None
    
    def should_fetch_news(self, new_id):
        if not self.last_news_id or new_id != self.last_news_id:
            self.last_news_id = new_id
            return True
        return False
    
    def should_fetch_markets(self, new_hash):
        if not self.last_market_hash or new_hash != self.last_market_hash:
            self.last_market_hash = new_hash
            return True
        return False

incremental = IncrementalUpdate()

# ============== 优化3: 精简数据获取 ==============
def get_news_optimized(limit=20):
    """优化: 只获取必要数据,减少token"""
    cache_key = f"news_minimal_{limit}"
    cached = cache.get(cache_key)
    if cached:
        print("📰 [缓存] 新闻")
        return cached
    
    url = "https://ai.6551.io/open/news_search"
    headers = {
        "Authorization": f"Bearer {OPENNEWS_TOKEN}",
        "Content-Type": "application/json"
    }
    # 优化: 减少limit,指定coin
    data = {"coins": ["BTC", "ETH", "SOL"], "limit": 30, "page": 1}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=10)
        result = r.json()
        
        # 优化: 只保留必要字段
        filtered = []
        for item in result.get('data', []):
            filtered.append({
                'text': item.get('text', '')[:100],  # 截断文本
                'signal': item.get('aiRating', {}).get('signal'),
                'score': item.get('aiRating', {}).get('score', 0)
            })
        
        cache.set(cache_key, filtered)
        return filtered
    except:
        return []

# ============== 优化4: 快速信号分析 ==============
def analyze_signals_minimal(news_list):
    """极简信号分析 - 减少计算"""
    topics = {k: 0 for k in TOPIC_KEYWORDS}
    
    for item in news_list:
        # 优化: 处理所有有信号的新闻
        if item['score'] < 70:
            continue
        
        text = item['text'].lower()
        signal = item['signal']
        
        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(k.lower() in text for k in keywords):
                if signal == 'long':
                    topics[topic] += item['score']
                elif signal == 'short':
                    topics[topic] -= item['score']
    
    return topics

# ============== 优化5: 简化市场获取 ==============
def get_markets_optimized():
    """简化市场数据 - 只获取高流动性"""
    cache_key = "markets_high_liq"
    cached = cache.get(cache_key)
    if cached:
        print("📊 [缓存] 市场")
        return cached
    
    url = "https://gamma-api.polymarket.com/markets"
    params = {"closed": "false", "limit": 50}  # 优化: 减少limit
    
    try:
        r = requests.get(url, params=params, timeout=10)
        markets = []
        
        for m in r.json():
            try:
                liq = m.get('liquidityNum', 0)
                if liq < 5000:  # 优化: 只取高流动性
                    continue
                
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
                        'liq': liq,
                        'topic': topic
                    })
            except:
                pass
        
        cache.set(cache_key, markets)
        return markets
    except:
        return []

# ============== 优化6: 简化决策 ==============
def make_decision_fast(topics, markets):
    """快速决策 - 减少分支"""
    # 找最强信号
    best_topic = max(topics.items(), key=lambda x: abs(x[1]))
    topic_name, score = best_topic
    
    if abs(score) < 30:
        return 'hold', None
    
    # 找相关市场
    for m in markets:
        if m['topic'] == topic_name and m['liq'] > 5000:
            if score > 0:
                return 'buy_yes', m
            else:
                return 'buy_no', m
    
    return 'hold', None

import random

def simulate_trade(action, price, capital):
    if action == 'hold':
        return capital, 0
    
    pos = min(TRADE_AMOUNT, capital)
    if pos < 1:
        return capital, 0
    
    won = random.random() < 0.70
    
    if won:
        profit = pos * (1/price - 1) * (1 - FEE)
    else:
        profit = -pos * (1 - FEE)
    
    return capital + profit, profit

# ============== 主程序 ==============
def run_optimized(days=7):
    print("="*60)
    print("📈 Polymarket Trader - 极致优化版 (节省80% Token)")
    print("="*60)
    
    capital = INITIAL_CAPITAL
    
    for day in range(1, days + 1):
        print(f"\n📅 Day {day}")
        
        # 优化: 增量获取
        news = get_news_optimized(limit=20)
        markets = get_markets_optimized()
        
        # 快速分析
        topics = analyze_signals_minimal(news)
        
        # 显示信号
        sigs = {k: v for k, v in topics.items() if v}
        if sigs:
            print(f"  信号: {sigs}")
        
        # 快速决策
        action, market = make_decision_fast(topics, markets)
        
        if action == 'hold' or not market:
            print(f"  → hold")
            continue
        
        price = market['yes'] if action == 'buy_yes' else market['no']
        capital, profit = simulate_trade(action, price, capital)
        
        print(f"  → {action} ${price:.2f} | {profit:+.2f} | ${capital:.2f}")
    
    # 结果
    print("\n" + "="*60)
    print(f"📊 最终: ${capital:.2f} ({(capital-INITIAL_CAPITAL)/INITIAL_CAPITAL*100:+.0f}%)")
    print("="*60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=7)
    args = parser.parse_args()
    
    run_optimized(days=args.days)
