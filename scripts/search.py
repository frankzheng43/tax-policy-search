#!/usr/bin/env python3
"""Search 国家税务总局. Usage: echo '{"searchWord":"增值税"}' | python3 search.py

默认只搜「文件类」（见 FILE_LABELS），滤掉新闻/视频/各地动态/互动交流。
传 {"label": ""} 可搜全站。"""
import json, re, sys, time, urllib.request, urllib.parse

API_URL = "https://www.chinatax.gov.cn/search5/search/s"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
BASE_PARAMS = {"siteCode": "bm29000002", "searchSiteName": "GSFFK", "indexCode": "1",
               "pageSize": "10", "pageNum": "0", "orderBy": "2"}

# 文件类白名单。不加这个，宽泛关键词（如「小微企业」）会被新闻/视频/Murge成 5000+ 条。
# 测：「小微企业」默认 5095 条 → 加白名单 189 条。
# monitor.py 里有一份同样的，故意不复用 —— 那个要能单独拷走跑。
FILE_LABELS = ("法律,行政法规,国务院文件,税务部门规章,税务规范性文件,"
               "财税文件,其他文件,工作通知,政策指引,文字政策解读")

def _read(url, timeout=20, tries=3):
    """GET 带重试。chinatax 偶尔超时。"""
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=timeout).read()
        except Exception as e:
            last = e
            if i < tries - 1:
                time.sleep(1.5 * (i + 1))
    raise last

def strip_html(t):
    return re.sub(r'<[^>]+>', '', t) if t else ""

def search(params):
    p = {**BASE_PARAMS, "label": FILE_LABELS, **params}
    data = json.loads(_read(API_URL + "?" + urllib.parse.urlencode(p)))
    result = data.get("searchResultAll", {})
    total = result.get("total", 0)
    items = result.get("searchTotal", [])
    print(f"命中：{total} 条\n")
    for i, item in enumerate(items):
        title = strip_html(item.get("title", ""))
        doc_num = item.get("docNum", "")
        cwrq = (item.get("cwrq", "") or "")[:10]
        label = item.get("label", "")
        aging = item.get("xxgk_aging", "")
        url = item.get("url", "")
        content = strip_html(item.get("content", ""))[:200]
        print(f"{i+1}. {title}\n   文号：{doc_num}\n   成文日期：{cwrq} | 类别：{label} | 时效：{aging}\n   摘要：{content}\n   链接：{url}\n")
    pages = (total + 9) // 10
    print(f"共 {total} 条 | 第 {p['pageNum']}/{pages-1} 页")

if __name__ == "__main__":
    search(json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {})
