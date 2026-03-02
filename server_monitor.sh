#!/bin/bash
# 服务器综合监控脚本

echo "=== 服务器监控报告 ==="
echo

# 1. CPU 负载
LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
CORES=$(nproc)
LIMIT=$(echo "$CORES * 0.8" | bc)
echo "🔋 负载: $LOAD (核心数: $CORES, 80%阈值: $LIMIT)"

# 2. 内存
MEM_TOTAL=$(free -h | awk '/^Mem:/ {print $2}')
MEM_USED=$(free -h | awk '/^Mem:/ {print $3}')
MEM_PCT=$(free | awk '/^Mem:/ {printf "%.0f", $3/$2*100}')
echo "💾 内存: $MEM_USED / $MEM_TOTAL ($MEM_PCT%)"

# 3. CPU 温度 (如果可用)
if command -v vcgencmd &> /dev/null; then
    TEMP=$(vcgencmd measure_temp | awk -F'=' '{print $2}' | sed 's/..$//')
    echo "🌡️ 温度: ${TEMP}°C"
elif [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    TEMP=$(cat /sys/class/thermal/thermal_zone0/temp | awk '{printf "%.1f", $1/1000}')
    echo "🌡️ 温度: ${TEMP}°C"
else
    echo "🌡️ 温度: 无法获取 (未安装 sensors)"
fi

# 4. 进程数
PROC_COUNT=$(ps aux | wc -l)
echo "📊 进程数: $PROC_COUNT"

# 5. 网络 (主要网卡流量)
NET_INTERFACE=$(ip route | awk '/default/ {print $5}' | head -1)
RX_BEFORE=/tmp/net_rx_$NET_INTERFACE
TX_BEFORE=/tmp/net_tx_$NET_INTERFACE

if [ -f $RX_BEFORE ]; then
    RX_PREV=$(cat $RX_BEFORE)
    TX_PREV=$(cat $TX_BEFORE)
    sleep 1
    RX_NOW=$(cat /sys/class/net/$NET_INTERFACE/statistics/rx_bytes)
    TX_NOW=$(cat /sys/class/net/$NET_INTERFACE/statistics/tx_bytes)
    RX_RATE=$(( (RX_NOW - RX_PREV) / 1024 ))
    TX_RATE=$(( (TX_NOW - TX_PREV) / 1024 ))
    echo "🌐 网络 (${NET_INTERFACE}): ↓${RX_RATE}KB/s ↑${TX_RATE}KB/s"
    echo $RX_NOW > $RX_BEFORE
    echo $TX_NOW > $TX_BEFORE
else
    echo "🌐 网络: 初始化中..."
    cat /sys/class/net/$NET_INTERFACE/statistics/rx_bytes > $RX_BEFORE
    cat /sys/class/net/$NET_INTERFACE/statistics/tx_bytes > $TX_BEFORE
fi

# 6. 服务状态
echo "🔌 服务状态:"
systemctl is-active docker &>/dev/null && echo "   Docker: ✅ 运行中" || echo "   Docker: ❌ 已停止"
systemctl is-active 1panel &>/dev/null && echo "   1Panel: ✅ 运行中" || echo "   1Panel: ❌ 已停止"
pgrep -f clawdbot-gateway &>/dev/null && echo "   OpenClaw Gateway: ✅ 运行中" || echo "   OpenClaw Gateway: ❌ 已停止"
pgrep -f x-ui &>/dev/null && echo "   X-UI: ✅ 运行中" || echo "   X-UI: ❌ 已停止"

echo
echo "=== 内存占用 Top 5 ==="
ps aux --sort=-%mem | awk 'NR<=6 {print $11,"("$4"%)"}'

# 判断是否需要警报
ALERT=0
if (( $(echo "$LOAD > $LIMIT" | bc -l) )); then
    echo "⚠️ 警告: CPU负载过高!"
    ALERT=1
fi
if [ "$MEM_PCT" -gt 80 ]; then
    echo "⚠️ 警告: 内存使用过高!"
    ALERT=1
fi
if [ "$PROC_COUNT" -gt 200 ]; then
    echo "⚠️ 警告: 进程数过多!"
    ALERT=1
fi

exit $ALERT
