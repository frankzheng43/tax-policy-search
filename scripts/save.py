#!/usr/bin/env python3
"""Save full text as Markdown file. Usage: echo 'JSON' | python3 save.py"""
import json, os, sys

SAVE_DIR = "/sdcard/Documents/税务文件"

def save(data):
    os.makedirs(SAVE_DIR, exist_ok=True)
    title = data.get("title", "无标题")
    doc_num = data.get("doc_num", "")
    tax_type = data.get("tax_type", "")
    effect_level = data.get("effect_level", "")
    date = data.get("date", "")
    status = data.get("status", "")
    source = data.get("source", "")
    annotation = data.get("annotation", "")
    text = data.get("text", "")
    related_interp = data.get("related_interp", [])
    related_docs = data.get("related_docs", [])

    fm = ["---",
          f"title: {title}",
          f'doc_num: "{doc_num}"',
          f"tax_type: {tax_type}",
          f"effect_level: {effect_level}",
          f"date: {date}",
          f"status: {status}",
          f"source: {source}"]
    if annotation:
        fm.append(f'annotation: "{annotation}"')
    fm.append("---")
    frontmatter = "\n".join(fm)

    body = f"\n\n# {title}\n\n"
    if annotation:
        body += f"> **注释**：{annotation}\n\n"
    body += text
    if related_interp:
        body += "\n\n---\n\n🔗 关联解读：\n\n"
        body += "\n".join(f"  [{t}](http://fgk.chinatax.gov.cn{u})\n" for t, u in related_interp)
    if related_docs:
        body += "\n🔗 关联文件：\n\n"
        body += "\n".join(f"  [{t}](http://fgk.chinatax.gov.cn{u})\n" for t, u in related_docs)

    filename = f"全文_{title}（{doc_num}）.md" if doc_num else f"全文_{title}.md"
    filename = filename.replace("/", "_").replace("\\", "_")
    path = os.path.join(SAVE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(frontmatter + body)
    print(f"已保存：{path}")

if __name__ == "__main__":
    save(json.loads(sys.stdin.read()))
