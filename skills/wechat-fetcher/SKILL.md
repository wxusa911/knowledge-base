# 微信公众号文章抓取工具

> 抓取微信公众号文章并转换为 Markdown 格式

## 功能

- 🦸 反检测抓取 - 使用 Camoufox 浏览器
- 📄 文章抓取 - URL → Markdown
- 🖼️ 图片本地化 - 自动下载到本地
- 📅 元数据保留 - 标题、公众号名、发布时间

## 使用方法

```bash
# 抓取文章
cd /home/ubuntu/.openclaw/workspace/wechat-article-to-markdown
source .venv/bin/activate
python main.py "https://mp.weixin.qq.com/s/xxx"

# 或使用脚本
/home/ubuntu/.openclaw/workspace/skills/wechat-fetcher/fetch.sh "https://mp.weixin.qq.com/s/xxx"
```

## 输出

```
output/
└── 文章标题/
    ├── 文章标题.md
    └── images/
        ├── img_001.png
        └── ...
```

## 示例输出

```markdown
# 文章标题

> 公众号: xxx
> 发布时间: 2026-02-28 11:42
> 原文链接: https://mp.weixin.qq.com/s/...

---

正文内容...

![](images/img_001.png)
```

## 依赖

- Camoufox (反检测浏览器)
- BeautifulSoup
- markdownify
- httpx

## 注意事项

- 需要能访问微信的服务器网络
- 图片会自动下载到本地
- 支持代码块识别
