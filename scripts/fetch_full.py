#!/usr/bin/env python3
"""Fetch full text of a tax policy doc from chinatax.gov.cn.
Usage: python3 fetch_full.py <URL>"""
import re, sys, urllib.request, urllib.parse, json

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def html_table_to_md(html):
    """HTML table -> MD table. Handles colspan only (rowspan is rare in tax docs)."""
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    if not rows:
        return re.sub(r'<[^>]+>', '', html)
    out = []
    for row in rows:
        cells = re.findall(r'<(t[hd])([^>]*)>(.*?)</\1>', row, re.DOTALL)
        row_cells = []
        for _tag, attrs, cell in cells:
            c = re.sub(r'<[^>]+>', '', cell)
            for old, new in [('&ensp;', ' '), ('&nbsp;', ' '), ('&ldquo;', '"'),
                             ('&rdquo;', '"'), ('&mdash;', '—'), ('&thinsp;', ' ')]:
                c = c.replace(old, new)
            c = re.sub(r'\r?\n', ' ', c).strip()
            colspan = int(m.group(1)) if (m := re.search(r'colspan=["\']?(\d+)', attrs)) else 1
            row_cells.extend([c] + [''] * (colspan - 1))
        out.append('| ' + ' | '.join(row_cells) + ' |')
    cols = max(len(r.split('|')) - 2 for r in out) if out else 1
    sep = '| ' + ' | '.join(['---'] * cols) + ' |'
    out.insert(1, sep)
    return '\n'.join(out)

def fetch(url):
    resp = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30)
    html = resp.read().decode("utf-8", errors="replace")

    # 正文
    m = re.search(r'class="arc_cont"[^>]*>(.*?)</div>', html, re.DOTALL)
    text = ""
    if m:
        raw = m.group(1)
        tables = re.findall(r'(<table[^>]*>.*?</table>)', raw, flags=re.DOTALL)
        for i, t in enumerate(tables):
            raw = raw.replace(t, f'\n__TABLE_{i}__\n')
        text = re.sub(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r'[\2](\1)', raw, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '\n', text)
        for old, new in [('&ensp;', ' '), ('&nbsp;', ' '), ('&ldquo;', '"'), ('&rdquo;', '"'), ('&mdash;', '—'), ('&thinsp;', ' ')]:
            text = text.replace(old, new)
        for i, t in enumerate(tables):
            text = text.replace(f'__TABLE_{i}__', html_table_to_md(t))
        text = re.sub(r'\n{3,}', '\n\n', text).strip()

    # 立法沿革
    annotation = ""
    zs = re.search(r'class="zscont">(.*?)</div>', html, re.DOTALL)
    if zs:
        annotation = re.sub(r'<[^>]+>', '', zs.group(1)).replace('&ensp;', ' ').replace('&nbsp;', ' ').strip()

    # 关联解读 + 关联文件
    related_interp, related_docs = [], []
    aid_m = re.search(r'<meta[^>]*name="articleId"[^>]*content="(\d+)"', html)
    if aid_m:
        try:
            req = urllib.request.Request("https://www.chinatax.gov.cn/queryManuscriptAssociation",
                data=urllib.parse.urlencode({"id": aid_m.group(1)}).encode(),
                headers={"User-Agent": UA})
            assoc = json.loads(urllib.request.urlopen(req, timeout=15).read())
            results = assoc.get("results", {}).get("data", {}).get("results", [])
            if results and len(results) > 1:
                r = results[1]
                related_interp = [(d.get("title",""), d.get("url","").replace("zcfgknw","zcfgk")) for d in r.get("policyInterpretation", [])]
                related_docs = [(d.get("title",""), d.get("url","").replace("zcfgknw","zcfgk")) for d in r.get("policyDocument", [])]
        except:
            pass

    # 输出
    if annotation:
        print(f"> **注释**：{annotation}\n")
    print(text)
    if related_interp:
        print("\n---\n\n🔗 关联解读：\n")
        for t, u in related_interp:
            print(f"  [{t}](http://fgk.chinatax.gov.cn{u})\n")
    if related_docs:
        print("\n🔗 关联文件：\n")
        for t, u in related_docs:
            print(f"  [{t}](http://fgk.chinatax.gov.cn{u})\n")

if __name__ == "__main__":
    fetch(sys.argv[1])
