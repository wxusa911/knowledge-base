# TOOLS.md - Local Notes

## 服务器配置 (Oracle)

| 项目 | 配置 |
|------|------|
| 内存 | 8GB |
| 磁盘 | 45GB |
| 系统 | Ubuntu |

---

## 已安装工具

- Python 3.12
- py-clob-client (Polymarket SDK)
- xreach-cli (Twitter访问)
- websocket-client
- requests

---

## 常用命令

### Twitter搜索
```bash
export PATH=$HOME/.local/bin:$PATH && xreach --auth-token "xxx" --ct0 "xxx" search "关键词"
```

### Polymarket Python
```python
from py_clob_client.client import ClobClient
```

---

## 知识库

- 位置: `/home/ubuntu/.openclaw/workspace/knowledge/`
- GitHub: wxusa911/knowledge-base
- 同步: 自动推送到GitHub

---

## Polymarket策略笔记

- 成功率最高: Carry Trade (买高+低概率)
- 最简单: YES + NO < $1 时买入
- 代码示例: knowledge/研究/Polymarket/
