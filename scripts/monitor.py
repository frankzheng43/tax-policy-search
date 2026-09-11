#!/usr/bin/env python3
"""Monitor 国家税务总局政策法规库. 有新内容时把 Markdown 打到 stdout，无新内容则静默退出。

用法：
    python3 monitor.py                     # 直接打印
    python3 monitor.py > new.md            # 存文件
    python3 monitor.py | your-notifier     # 接自己的通知渠道

状态文件默认 ~/.tax_law_state.json，用 TAX_STATE_FILE 可改。
只用 stdlib，无需第三方包。
"""
import json, os, sys, time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

STATE_FILE = os.path.expanduser(os.environ.get("TAX_STATE_FILE", "~/.tax_law_state.json"))
API_URL = "https://www.chinatax.gov.cn/search5/search/s"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
PARAMS = {
    "siteCode": "bm29000002", "searchWord": "", "type": "",
    "pageSize": "20", "pageNum": "0", "orderBy": "5",
    "column": "政策法规,政策解读,政策指引",
    "label": "文字政策解读,法律,行政法规,国务院文件,税务部门规章,税务规范性文件,财税文件,其他文件,工作通知,政策指引",
    "likeDoc": "0", "wordPlace": "0", "indexCode": "1"
}

def load_state():
    if os.path.exists(STATE_FILE):
        try: return set(json.load(open(STATE_FILE)))
        except: pass
    return set()

def save_state(keys):
    with open(STATE_FILE, "w") as f: json.dump(sorted(keys), f)

def _read(url, timeout=20, tries=3):
    """GET 带重试。chinatax 偶尔超时。"""
    last = None
    for i in range(tries):
        try:
            req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            return urlopen(req, timeout=timeout).read()
        except Exception as e:
            last = e
            if i < tries - 1:
                time.sleep(1.5 * (i + 1))
    raise last

def main():
    try:
        data = json.loads(_read(API_URL + "?" + urlencode(PARAMS)).decode("utf-8", errors="replace"))
    except Exception as e:
        print(f"[monitor] API 请求失败: {e}", file=sys.stderr)
        return 1

    articles = data.get("searchResultAll", {}).get("searchTotal", [])
    if not articles:
        return 0

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    seen = load_state()
    new = [a for a in articles if a.get("id") not in seen]
    current_keys = {a.get("id") for a in articles}

    if not new:
        save_state(current_keys)
        return 0  # 没新闻就是没新闻

    # 按类别分组
    cats = {}
    for a in new:
        cats.setdefault(a.get("label", "其他"), []).append(a)

    parts = [f"# 📋 国家税务总局政策法规库 更新\n\n⏰ {now} | 共 {len(new)} 条新内容\n"]
    for cat, items in cats.items():
        parts.append(f"\n## #{cat}\n")
        for a in items:
            title = a.get("title", "无标题")
            date = a.get("pubDate", "")[:10]
            url = a.get("url", "")
            doc_num = a.get("govDoc", {}).get("docNum", "")
            content = a.get("content", "")
            summary = (content[:500] + "…") if content and len(content) > 500 else (content or "")
            parts.append(f"### 📌 {title}")
            if doc_num: parts.append(f"📎 {doc_num}")
            parts.append(f"📅 {date} | 🔗 {url}")
            if summary: parts.append(f"\n> {summary}\n")

    parts.append(f"\n---\n共 {len(new)} 条新内容")
    print("\n".join(parts))
    print(f"[monitor] {len(new)} 条新内容", file=sys.stderr)

    save_state(current_keys)
    return 0

if __name__ == "__main__":
    sys.exit(main())
