#!/usr/bin/env python3
"""Fetch full text of a tax policy doc from chinatax.gov.cn.

用法：
    python3 fetch_full.py <URL>              # 打印全文（正文+立法沿革+关联）
    python3 fetch_full.py --save <URL>       # 直接存成 Markdown
    python3 fetch_full.py --json <URL>       # 输出 save.py 可吃的 JSON
    python3 fetch_full.py --depth 1 --save <URL>   # 顺带把正文/关联里的文档一起存（默认关）

--depth N：跟到第 N 层。0（默认）= 不跟；1 = 只跟本文里的链接；以此类推。
附件（pdf/doc/图片等）不跟。每篇之间停 0.5s。
"""
import re, sys, os, json, time, urllib.request, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# 只有法规库的详情页才值得跟；附件/图片/pdf 等一律不跟。
DOC_LINK_RE = re.compile(r'^https?://(?:www\.)?(?:fgk\.)?chinatax\.gov\.cn/zcfgk/.+/content\.html$', re.I)
NON_DOC_RE = re.compile(r'\.(?:pdf|docx?|wps|xlsx?|pptx?|zip|rar|jpe?g|png|gif|bmp)(?:[?#]|$)', re.I)

def _is_doc_link(u):
    return bool(DOC_LINK_RE.match(u)) and not NON_DOC_RE.search(u)

def _canon(u):
    """URL 去重键：http/https 视为同一篇（正文里的链接是 https，关联接口给的是 http）。"""
    m = re.match(r'^https?://(?:www\.)?([^/]+)(/.*)?$', u, re.I)
    return (m.group(1).lower() + (m.group(2) or '')).rstrip('/') if m else u

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

def _meta(html, name):
    m = re.search(r'<meta[^>]*name="%s"[^>]*content="([^"]*)"' % name, html)
    return m.group(1).strip() if m else ""

def _guess_doc_num(text):
    """从正文头部猜文号。

    ponytail: 只认「…令/公告/通知/函」下一行是「第N号」或「YYYY年第N号」的写法，
    认不出就留空（文件名退化为 全文_<标题>.md）。要更准就回到搜索接口拿 docNum。
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for i, l in enumerate(lines[:8]):
        if re.fullmatch(r'\d{4}年第\d+号|第\d+号', l):
            prev = lines[i - 1] if i else ""
            return prev + l if re.search(r'(令|公告|通知|函)$', prev) else l
    return ""

def parse(url):
    """抓取 + 解析，返回可直接喂给 save.py 的 dict。"""
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
        # 只有块级标签断段；内联标签（span/strong…）直接去掉，
        # 否则「第一条」会和后面的正文分家。
        text = re.sub(r'</p>|</div>|</tr>|</h[1-6]>', '\n\n', text, flags=re.I)
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
        text = re.sub(r'<[^>]+>', '', text)
        for old, new in [('&ensp;', ' '), ('&nbsp;', ' '), ('&ldquo;', '"'), ('&rdquo;', '"'), ('&mdash;', '—'), ('&thinsp;', ' ')]:
            text = text.replace(old, new)
        for i, t in enumerate(tables):
            text = text.replace(f'__TABLE_{i}__', html_table_to_md(t))
        text = re.sub(r'\r\n?', '\n', text)  # 网页是 CRLF，统一成 LF
        # 行首缩进统一去掉：原文一半靠 CSS text-indent、一半靠字面 &ensp;/　　，
        # 提取时分不出来，留着就是参差不齐（且 ≥4 个半角空格在 Markdown 里会变代码块）。
        # 分段交给空行。
        text = re.sub(r'^[ \t\u3000]+|[ \t\u3000]+$', '', text, flags=re.M)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()

        # 有些文种（如税率表）正文整篇就是一张图，提不出文字。
        # 图片相对地址是「<articleId>/images/<文件名>」，拼在页面目录后面。
        if not text:
            base = url.rsplit('/', 1)[0]
            imgs = [s if s.startswith('http') else f"{base}/{s}"
                    for s in re.findall(r'<img[^>]*src=["\']([^"\']+)["\']', raw, flags=re.I)]
            if imgs:
                text = "本文正文为图片，未提取到文字。原文图片：\n\n" + "\n".join(f"- {u}" for u in imgs)

    # 立法沿革
    annotation = ""
    zs = re.search(r'class="zscont">(.*?)</div>', html, re.DOTALL)
    if zs:
        annotation = re.sub(r'<[^>]+>', '', zs.group(1)).replace('&ensp;', ' ').replace('&nbsp;', ' ').strip()
        annotation = re.sub(r'\s+', ' ', annotation)

    # 时效 / 成文日期（arc_date 里的两个 span）
    ad = re.search(r'class="arc_date"[^>]*>(.*?)</p>', html, re.DOTALL)
    ad = ad.group(1) if ad else ""
    xg = re.search(r'class="xg"[^>]*>(.*?)<', ad, re.DOTALL)
    dt = re.search(r'class="date"[^>]*>\s*成文日期：\s*([\d-]+)', ad)
    status = xg.group(1).strip() if xg else ""
    date = dt.group(1) if dt else ""

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
        except Exception:
            pass

    # 标题 + 文号（h3 是标题，h5.actfwzh 只有公告类才有，其余退回正文头部猜）
    h3 = re.search(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
    fwzh = re.search(r'class="actfwzh"[^>]*>(.*?)</h5>', html, re.DOTALL)
    strip_tags = lambda s: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()
    title = _meta(html, "ArticleTitle") or strip_tags(h3.group(1) if h3 else "")
    doc_num = strip_tags(fwzh.group(1) if fwzh else "") or _guess_doc_num(text)

    return {
        "title": title,
        "doc_num": doc_num,
        "tax_type": "",
        "effect_level": _meta(html, "ColumnName"),
        "date": date,
        "status": status,
        "source": url,
        "annotation": annotation,
        "text": text,
        "related_interp": related_interp,
        "related_docs": related_docs,
    }

def crawl(url, depth, delay=0.5):
    """广度优先抓 url 及其正文/关联里的文档链接，共 depth 层。

    ponytail: 串行 + 固定延时，对 gov 站礼貌且够用；量大了再谈并发。
    """
    seen, queue, out = set(), [(url, 0)], []
    while queue:
        u, d = queue.pop(0)
        key = _canon(u)
        if key in seen:
            continue
        seen.add(key)
        if out:
            time.sleep(delay)
        try:
            data = parse(u)
        except Exception as e:
            print(f"[skip] {u} — {e}", file=sys.stderr)
            continue
        out.append(data)
        if d < depth:
            links = re.findall(r'\]\((https?://[^)\s]+)\)', data["text"])
            links += [f"http://fgk.chinatax.gov.cn{p}" for _, p in data["related_interp"] + data["related_docs"]]
            queue += [(l, d + 1) for l in links if _is_doc_link(l) and _canon(l) not in seen]
    return out

def fetch(url):
    """打印人类可读的全文。"""
    d = parse(url)
    if d["annotation"]:
        print(f"> **注释**：{d['annotation']}\n")
    print(d["text"])
    if d["related_interp"]:
        print("\n---\n\n🔗 关联解读：\n")
        for t, u in d["related_interp"]:
            print(f"  [{t}](http://fgk.chinatax.gov.cn{u})\n")
    if d["related_docs"]:
        print("\n🔗 关联文件：\n")
        for t, u in d["related_docs"]:
            print(f"  [{t}](http://fgk.chinatax.gov.cn{u})\n")

def main():
    args = sys.argv[1:]
    flags, urls, depth, i = set(), [], 0, 0
    while i < len(args):
        a = args[i]
        if a == "--depth":
            i += 1
            depth = int(args[i])
        elif a.startswith("--depth="):
            depth = int(a.split("=", 1)[1])
        elif a.startswith("--"):
            flags.add(a)
        else:
            urls.append(a)
        i += 1
    if not urls:
        print(__doc__.strip())
        return 1
    url = urls[0]
    if "--json" in flags:
        print(json.dumps(parse(url), ensure_ascii=False, indent=2))
    elif "--save" in flags or depth:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from save import save as save_file
        docs = crawl(url, depth) if depth else [parse(url)]
        for d in docs:
            save_file(d)
        if len(docs) > 1:
            print(f"共 {len(docs)} 篇（含关联文档）")
    else:
        fetch(url)
    return 0

if __name__ == "__main__":
    sys.exit(main())
