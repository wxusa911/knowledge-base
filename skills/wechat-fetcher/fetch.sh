#!/bin/bash
# 微信公众号文章抓取脚本

cd /home/ubuntu/.openclaw/workspace/wechat-article-to-markdown
source .venv/bin/activate

if [ -z "$1" ]; then
    echo "用法: $0 <微信公众号文章URL>"
    exit 1
fi

python main.py "$1"
