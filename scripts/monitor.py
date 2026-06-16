#!/usr/bin/env python3
"""Monitor 国家税务总局政策法规库. Silent if nothing new; posts to IMA on changes."""
import json, os, subprocess
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

STATE_FILE = os.path.expanduser("~/.hermes/tax_law_state.json")
API_URL = "https://www.chinatax.gov.cn/search5/search/s"
IMA_API = os.path.expanduser("~/.hermes/skills/ima-skill/ima_api.cjs")
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

def post_ima(title, content):
    """Post markdown as IMA note. Returns note_id or None."""
    body = json.dumps({"content_format": 1, "title": title, "content": content}, ensure_ascii=False)
    try:
        r = subprocess.run(["node", IMA_API, "openapi/note/v1/import_doc", body],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            print(f"[IMA Error] {r.stderr.strip()}")
            return None
        resp = json.loads(r.stdout)
        if resp.get("code") == 0:
            return resp["data"]["note_id"]
        print(f"[IMA API Error] {resp.get('msg', 'unknown')}")
    except Exception as e:
        print(f"[IMA Error] {e}")
    return None

def main():
    try:
        req = Request(API_URL + "?" + urlencode(PARAMS),
                      headers={"User-Agent": UA, "Accept": "application/json"})
        data = json.loads(urlopen(req, timeout=20).read().decode("utf-8", errors="replace"))
    except Exception as e:
        return print(f"[Tax Law] API请求失败: {e}")

    articles = data.get("searchResultAll", {}).get("searchTotal", [])
    if not articles:
        return  # ponytail: no results, nothing to do

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    seen = load_state()
    new = [a for a in articles if a.get("id") not in seen]
    current_keys = {a.get("id") for a in articles}

    if not new:
        save_state(current_keys)
        return  # ponytail: silent, no news is no news

    # Build markdown, grouped by category
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
    note_content = "\n".join(parts)
    note_title = f"📋 税务总局政策法规库 {now}"

    note_id = post_ima(note_title, note_content)
    if note_id:
        print(f"[Tax Law] ✓ 已保存到IMA笔记 (note_id={note_id})")
    else:
        print(f"[Tax Law] IMA保存失败，输出到stdout:\n{note_content}")

    save_state(current_keys)

if __name__ == "__main__":
    main()
