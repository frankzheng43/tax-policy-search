#!/usr/bin/env python3
"""Search 国家税务总局. Usage: echo '{"searchWord":"增值税"}' | python3 search.py"""
import json, re, sys, urllib.request, urllib.parse

API_URL = "https://www.chinatax.gov.cn/search5/search/s"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
BASE_PARAMS = {"siteCode": "bm29000002", "searchSiteName": "GSFFK", "indexCode": "1",
               "pageSize": "10", "pageNum": "0", "orderBy": "2"}

def strip_html(t):
    return re.sub(r'<[^>]+>', '', t) if t else ""

def search(params):
    p = {**BASE_PARAMS, **params}
    req = urllib.request.Request(API_URL + "?" + urllib.parse.urlencode(p),
                                 headers={"User-Agent": UA})
    data = json.loads(urllib.request.urlopen(req, timeout=20).read())
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
