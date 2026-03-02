#!/usr/bin/env python3
"""
 Polymarket 真实历史回测 - 基于真实价格数据
 获取历史价格，模拟过去N笔交易，统计真实胜率
"""

import requests
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

DATA_FILE = "/home/ubuntu/.openclaw/workspace/market_history.json"

def get_markets():
    """获取市场列表"""
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
                    "condition_id": m.get('conditionId'),
                    "yes": float(prices[0]),
                    "no": float(prices[1]),
                    "volume": m.get('volumeNum', 0),
                    "liquidity": m.get('liquidityNum', 0),
                })
        except:
            continue
    return result

def get_historical_prices(condition_id):
    """获取历史价格"""
    try:
        url = f"https://gamma-api.polymarket.com/markets/{condition_id}/history"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def get_candles(condition_id, interval="1h", limit=168):
    """获取K线数据 (7天)"""
    try:
        url = f"https://gamma-api.polymarket.com/markets/{condition_id}/candles"
        params = {"interval": interval, "limit": limit}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

# ============ 策略1: 极端反转 (历史验证) ============
def strategy_extreme_reversal(candles):
    """
    如果价格 < 0.10，买入YES等反弹
    如果价格 > 0.90，卖出YES等下跌
    持有1小时后看结果
    """
    if not candles or len(candles) < 2:
        return None
    
    # 遍历每个时间点
    trades = []
    for i in range(len(candles) - 1):
        current = candles[i]
        next_candle = candles[i + 1]
        
        yes_close = float(current.get('close', 0))
        
        # 极端价格信号
        if yes_close < 0.10:
            # 买入YES，1小时后看结果
            entry = yes_close
            exit_price = float(next_candle.get('close', yes_close))
            
            won = exit_price > entry
            profit = (exit_price - entry) / entry if won else (exit_price - entry) / entry
            
            trades.append({
                "type": "BUY_YES_EXTREME_LOW",
                "entry": entry,
                "exit": exit_price,
                "won": won,
                "profit": profit
            })
        
        elif yes_close > 0.90:
            # 假设做空YES (或买入NO)
            entry = yes_close
            exit_price = float(next_candle.get('close', yes_close))
            
            won = exit_price < entry
            profit = (entry - exit_price) / entry if won else (entry - exit_price) / entry
            
            trades.append({
                "type": "BUY_NO_EXTREME_HIGH",
                "entry": entry,
                "exit": exit_price,
                "won": won,
                "profit": profit
            })
    
    return trades

# ============ 策略2: 突破策略 ============
def strategy_breakout(candles):
    """
    突破策略: 如果价格从低位突破0.30，买入
    1小时后看结果
    """
    if not candles or len(candles) < 3:
        return None
    
    trades = []
    for i in range(1, len(candles) - 1):
        prev = candles[i-1]
        current = candles[i]
        next_candle = candles[i + 1]
        
        prev_close = float(prev.get('close', 0))
        curr_close = float(current.get('close', 0))
        
# 突破信号: 从 < 0.30 突破到 > 0.30
        if prev_close < 0.30 and curr_close > 0.30:
            entry = curr_close
            exit_price = float(next_candle.get('close', curr_close))
            
            # 突破后继续上涨的概率
            won = exit_price > entry
            profit = (exit_price - entry) / entry if won else (exit_price - entry) / entry
            
            trades.append({
                "type": "BREAKOUT_ABOVE_30",
                "entry": entry,
                "exit": exit_price,
                "won": won,
                "profit": profit
            })
        
        # 跌破信号
        elif prev_close > 0.70 and curr_close < 0.70:
            entry = curr_close
            exit_price = float(next_candle.get('close', curr_close))
            
            won = exit_price < entry
            profit = (entry - exit_price) / entry if won else (entry - exit_price) / entry
            
            trades.append({
                "type": "BREAKDOWN_BELOW_70",
                "entry": entry,
                "exit": exit_price,
                "won": won,
                "profit": profit
            })
    
    return trades

# ============ 策略3: 均值回归 ============
def strategy_mean_reversion(candles):
    """
    均值回归: 价格远离0.50时买入回归
    """
    if not candles or len(candles) < 2:
        return None
    
    trades = []
    for i in range(len(candles) - 1):
        current = candles[i]
        next_candle = candles[i + 1]
        
        close = float(current.get('close', 0))
        
        # 远离均值
        dist_from_50 = abs(close - 0.50)
        
        if dist_from_50 > 0.30:  # 价格在 < 0.20 或 > 0.80
            entry = close
            exit_price = float(next_candle.get('close', close))
            
            # 向0.50回归
            if close < 0.50:
                won = exit_price > entry
            else:
                won = exit_price < entry
            
            profit = abs(exit_price - entry) / entry if won else -abs(exit_price - entry) / entry
            
            direction = "REVERT_UP" if close < 0.50 else "REVERT_DOWN"
            trades.append({
                "type": f"MEAN_REVERSION_{direction}",
                "entry": entry,
                "exit": exit_price,
                "won": won,
                "profit": profit
            })
    
    return trades

# ============ 主回测 ============
def run_backtest():
    print(f"\n{'='*75}")
    print(f"🎯 Polymarket 真实历史数据回测")
    print(f"   数据源: Polymarket API (K线)")
    print(f"   周期: 1小时K线, 7天历史")
    print(f"{'='*75}\n")
    
    markets = get_markets()
    print(f"📊 获取 {len(markets)} 个市场\n")
    
    # 收集所有策略结果
    all_results = {
        "EXTREME_REVERSAL": [],
        "BREAKOUT": [],
        "MEAN_REVERSION": []
    }
    
    # 遍历市场获取历史数据
    count = 0
    for m in markets[:30]:  # 前30个市场
        if m['liquidity'] < 5000:  # 跳过低流动性
            continue
            
        print(f"🔍 {m['question'][:40]}...", end=" ")
        
        candles = get_candles(m['condition_id'], interval="1h", limit=168)
        
        if candles and len(candles) > 10:
            # 策略1: 极端反转
            r1 = strategy_extreme_reversal(candles)
            if r1:
                all_results["EXTREME_REVERSAL"].extend(r1)
            
            # 策略2: 突破
            r2 = strategy_breakout(candles)
            if r2:
                all_results["BREAKOUT"].extend(r2)
            
            # 策略3: 均值回归
            r3 = strategy_mean_reversion(candles)
            if r3:
                all_results["MEAN_REVERSION"].extend(r3)
            
            count += 1
            print(f"✓ {len(candles)} 根K线")
        else:
            print(f"✗ 无足够数据")
    
    print(f"\n{'='*75}")
    print(f"📈 回测结果统计")
    print(f"{'='*75}")
    
    total_trades = 0
    total_wins = 0
    total_profit = 0
    
    for strategy, trades in all_results.items():
        if not trades:
            continue
        
        wins = sum(1 for t in trades if t['won'])
        count = len(trades)
        win_rate = wins / count * 100 if count > 0 else 0
        profit = sum(t['profit'] for t in trades)
        
        print(f"\n📌 {strategy}:")
        print(f"   交易次数: {count}")
        print(f"   胜率: {wins}/{count} = {win_rate:.1f}%")
        print(f"   总盈亏: {profit*100:+.1f}%")
        
        total_trades += count
        total_wins += wins
        total_profit += profit
    
    # 总体统计
    overall_win_rate = total_wins / total_trades * 100 if total_trades > 0 else 0
    
    print(f"\n{'='*75}")
    print(f"🏆 总体统计:")
    print(f"   总交易次数: {total_trades}")
    print(f"   总胜率: {total_wins}/{total_trades} = {overall_win_rate:.1f}%")
    print(f"   总盈亏: {total_profit*100:+.1f}%")
    
    if overall_win_rate >= 75:
        print(f"\n✅ 胜率 >= 75%，策略可用于实盘!")
    else:
        print(f"\n⚠️ 胜率 < 75%，需要优化策略")
    
    print(f"{'='*75}\n")

if __name__ == "__main__":
    run_backtest()
