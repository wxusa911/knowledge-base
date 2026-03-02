#!/usr/bin/env python3
"""
Twitter 自动发帖生产线
流程: 搜索信息 → 过滤 → 生成推文 → 发送
"""

import subprocess
import json
import sys
from datetime import datetime

# 配置
AUTH_TOKEN = "f4649e6f60a743433e39fbb3a1781ce56a7a4883"
CT0 = "dd8fa721f1a37a051af69d3f866b79027b3a78501b236d259cbc56c0ba363c05cf9a01318e501cf3fec27f96fb531ffbaebf8808bb94d7910eb9d62751348ea15a5d3b59547b4c65df5bfcd40add1bf1"

def run_xreach(args):
    """运行 xreach 命令"""
    cmd = f"xreach --auth-token {AUTH_TOKEN} --ct0 {CT0} {args}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def search_tweets(keyword, limit=5):
    """Step 1: 搜索信息"""
    print(f"\n🔍 搜索: {keyword}")
    output = run_xreach(f'search "{keyword}" -n {limit}')
    return output

def filter_info(tweets_text):
    """Step 2: 过滤有价值的信息"""
    # 简单过滤：保留有观点/数据的推文
    lines = tweets_text.strip().split('\n')
    filtered = [l for l in lines if any(k in l.lower() for k in ['$', '%', 'win', 'trade', 'bot', 'strategy', 'profit'])]
    return '\n'.join(filtered[:3]) if filtered else "无热点信息"

def generate_tweet(info):
    """Step 3: 生成推文 (使用 Gemini)"""
    prompt = f"""基于以下信息，生成一条简洁有价值的Twitter推文（英文，50字以内，带1-2个emoji）:

{info}

只返回推文内容，不要解释。"""
    
    cmd = f'gemini -p "{prompt}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def post_tweet(content):
    """Step 4: 发送推文"""
    # 由于 xreach 不支持发推，这里先返回内容让用户确认
    # 实际发送需要安装 bird
    print(f"\n📤 待发送推文:")
    print(f"   {content}")
    return content

def run_pipeline(keyword):
    """运行完整生产线"""
    print(f"\n{'='*60}")
    print(f"🐦 Twitter 自动发帖生产线")
    print(f"   关键词: {keyword}")
    print(f"{'='*60}")
    
    # Step 1: 搜索
    tweets = search_tweets(keyword)
    
    # Step 2: 过滤
    filtered = filter_info(tweets)
    print(f"\n📋 过滤后的信息:")
    print(f"   {filtered[:100]}...")
    
    # Step 3: 生成
    tweet = generate_tweet(filtered)
    print(f"\n✍️ 生成的推文:")
    print(f"   {tweet}")
    
    # Step 4: 发送
    result = post_tweet(tweet)
    
    print(f"\n{'='*60}")
    return result

if __name__ == "__main__":
    keyword = sys.argv[1] if len(sys.argv) > 1 else "Polymarket"
    run_pipeline(keyword)
