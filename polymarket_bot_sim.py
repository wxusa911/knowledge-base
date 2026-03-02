#!/usr/bin/env python3
"""
BTC 15分钟自动交易模拟器 (模拟资金)
基于 polymarket-bot 逻辑，无实盘操作
"""

import random
import time
import json
from datetime import datetime

# ============== 模拟配置 ==============
INITIAL_CAPITAL = 100  # 模拟资金 $100
TRADE_AMOUNT = 5        # 每次下单金额
SIMULATION_DAYS = 7     # 模拟天数

# 触发条件 (与原脚本一致)
CONDITIONS = [
    {"time": 120, "diff": 30, "min_prob": 0.80, "max_prob": 0.92},  # C1
    {"time": 120, "diff": 30, "min_prob": 0.80, "max_prob": 0.92},  # C2
    {"time": 60, "diff": 50, "min_prob": 0.80, "max_prob": 0.92},   # C3
    {"time": 60, "diff": 50, "min_prob": 0.80, "max_prob": 0.92},   # C4
]

# 风控参数
STOP_LOSS_PCT = 0.15   # 止损线
TAKE_PROFIT_RR = 1.0   # 止盈:风险回报比
FEE = 0.02             # 手续费 2%

# ============== 模拟数据 ==============
def generate_market_data():
    """生成模拟市场数据"""
    # 模拟BTC价格在95000-97000之间波动
    btc_price = random.uniform(95000, 97000)
    
    # 模拟目标价格 (15分钟后的价格)
    target_price = btc_price + random.uniform(-200, 200)
    
    # 模拟UP/DOWN概率 (80%-92%之间)
    if random.random() > 0.5:
        up_prob = random.uniform(0.80, 0.92)
        down_prob = 1 - up_prob
    else:
        down_prob = random.uniform(0.80, 0.92)
        up_prob = 1 - down_prob
    
    # 模拟剩余时间 (0-900秒, 15分钟)
    remaining = random.randint(0, 900)
    
    # 模拟价差 (0-100)
    spread = random.uniform(10, 60)
    
    return {
        "btc_price": btc_price,
        "target_price": target_price,
        "up_prob": up_prob,
        "down_prob": down_prob,
        "remaining": remaining,
        "spread": spread,
        "timestamp": datetime.now().isoformat()
    }

def check_conditions(market_data):
    """检查是否满足任一触发条件"""
    triggered = []
    
    for i, cond in enumerate(CONDITIONS):
        if (market_data["remaining"] <= cond["time"] and 
            market_data["spread"] >= cond["diff"]):
            
            # 检查概率范围
            if cond["min_prob"] <= market_data["up_prob"] <= cond["max_prob"]:
                triggered.append({
                    "condition": i+1,
                    "side": "UP",
                    "prob": market_data["up_prob"],
                    "remaining": market_data["remaining"]
                })
            elif cond["min_prob"] <= market_data["down_prob"] <= cond["max_prob"]:
                triggered.append({
                    "condition": i+1,
                    "side": "DOWN", 
                    "prob": market_data["down_prob"],
                    "remaining": market_data["remaining"]
                })
    
    return triggered

def simulate_trade(market_data, side, capital):
    """
    模拟单笔交易
    返回: (是否触发止损, 盈亏)
    """
    position = TRADE_AMOUNT
    
    if side == "UP":
        buy_prob = market_data["up_prob"]
        price = market_data["up_prob"]  # 价格=概率
    else:
        buy_prob = market_data["down_prob"]
        price = market_data["down_prob"]
    
    # 决定是否成交 (基于概率)
    won = random.random() < buy_prob
    
    if won:
        # 赢了: 收益 = 投入 * (1/price - 1) - 手续费
        profit = position * (1/price - 1) * (1 - FEE)
        
        # 检查是否触发止盈
        risk = position * FEE
        if profit >= risk * TAKE_PROFIT_RR:
            # 止盈平仓
            profit = risk * TAKE_PROFIT_RR
            stop_triggered = False
            exit_reason = "TAKE_PROFIT"
        else:
            exit_reason = "HELD_TO_END"
    else:
        # 输了: 亏损 = 投入 - 手续费
        profit = -position * (1 - FEE)
        
        # 检查是否触发止损
        loss_pct = abs(profit) / position
        if loss_pct >= STOP_LOSS_PCT:
            exit_reason = "STOP_LOSS"
        else:
            exit_reason = "HELD_TO_END"
    
    return exit_reason, profit

def run_simulation():
    """运行模拟"""
    print("="*70)
    print("🎯 BTC 15分钟自动交易模拟器")
    print("="*70)
    print(f"初始资金: ${INITIAL_CAPITAL}")
    print(f"每次下单: ${TRADE_AMOUNT}")
    print(f"模拟天数: {SIMULATION_DAYS}")
    print(f"止损线: {STOP_LOSS_PCT*100}%")
    print(f"止盈比: {TAKE_PROFIT_RR}")
    print("="*70)
    
    capital = INITIAL_CAPITAL
    trades = []
    daily_stats = []
    
    # 每天约20个15分钟周期
    periods_per_day = 20
    
    for day in range(1, SIMULATION_DAYS + 1):
        day_trades = 0
        day_profit = 0
        day_wins = 0
        
        for period in range(periods_per_day):
            # 生成市场数据
            market = generate_market_data()
            
            # 检查触发条件
            triggers = check_conditions(market)
            
            if triggers and capital >= TRADE_AMOUNT:
                # 触发交易
                trigger = random.choice(triggers)
                
                exit_reason, profit = simulate_trade(
                    market, trigger["side"], capital
                )
                
                capital += profit
                day_trades += 1
                day_profit += profit
                
                if profit > 0:
                    day_wins += 1
                
                trades.append({
                    "day": day,
                    "period": period,
                    "side": trigger["side"],
                    "prob": trigger["prob"],
                    "remaining": trigger["remaining"],
                    "exit": exit_reason,
                    "profit": profit,
                    "capital": capital
                })
        
        daily_stats.append({
            "day": day,
            "trades": day_trades,
            "wins": day_wins,
            "profit": day_profit,
            "capital": capital
        })
        
        print(f"Day {day}: {day_trades}笔交易, 盈亏 ${day_profit:+.2f}, 资金 ${capital:.2f}")
    
    # 统计结果
    print("\n" + "="*70)
    print("📊 模拟结果汇总")
    print("="*70)
    
    total_trades = len(trades)
    wins = sum(1 for t in trades if t["profit"] > 0)
    win_rate = wins / total_trades * 100 if total_trades > 0 else 0
    
    total_profit = capital - INITIAL_CAPITAL
    roi = total_profit / INITIAL_CAPITAL * 100
    
    print(f"总交易次数: {total_trades}")
    print(f"盈利次数: {wins}")
    print(f"胜率: {win_rate:.1f}%")
    print(f"最终资金: ${capital:.2f}")
    print(f"总盈亏: ${total_profit:+.2f}")
    print(f"ROI: {roi:+.1f}%")
    
    # 退出原因统计
    exit_reasons = {}
    for t in trades:
        r = t["exit"]
        exit_reasons[r] = exit_reasons.get(r, 0) + 1
    
    print(f"\n退出原因:")
    for reason, count in sorted(exit_reasons.items(), key=lambda x: -x[1]):
        print(f"  {reason}: {count}")
    
    # 手续费统计
    total_fees = total_trades * TRADE_AMOUNT * FEE
    print(f"\n手续费成本: ${total_fees:.2f}")
    
    if capital > INITIAL_CAPITAL:
        print("✅ 模拟盈利!")
    else:
        print("❌ 模拟亏损")
    
    print("="*70)
    
    return {
        "capital": capital,
        "trades": total_trades,
        "win_rate": win_rate,
        "profit": total_profit,
        "roi": roi,
        "fees": total_fees
    }

if __name__ == "__main__":
    run_simulation()
