# tax-policy-search

Hermes Agent Skill — 自然语言搜索国家税务总局政策法规库

## 安装

```bash
npx skills add frankzheng43/tax-policy-search --yes --global
```

或者手动安装：

```bash
mkdir -p ~/.hermes/skills/research/tax-policy-search
curl -sL https://raw.githubusercontent.com/frankzheng43/tax-policy-search/main/SKILL.md \
  -o ~/.hermes/skills/research/tax-policy-search/SKILL.md
# 下载脚本和参考文件
for f in search.py fetch_full.py save.py monitor.py; do
  curl -sL "https://raw.githubusercontent.com/frankzheng43/tax-policy-search/main/scripts/$f" \
    -o ~/.hermes/skills/research/tax-policy-search/scripts/$f
done
for f in api.md supplementary-tax-disclosure.md analysis-framework.md; do
  curl -sL "https://raw.githubusercontent.com/frankzheng43/tax-policy-search/main/references/$f" \
    -o ~/.hermes/skills/research/tax-policy-search/references/$f
done
```

依赖：Python 3（stdlib，无需额外包）

## 功能

- **自然语言搜索**：说「查增值税公告」「找2026年企业所得税文件」即可
- **筛选条件**：税种、年份、文件类型、时效、行业等
- **查看全文**：含正文、表格（MD格式）、关联解读
- **保存全文**：带 YAML frontmatter，含立法沿革（注释）
- **下载附件**：PDF/WPS 保存到本地
- **翻页导航**：上一页/下一页
- **导出清单**：搜索结果导出为 Markdown

## 使用方法

在 Hermes Agent 中直接说：

```
帮我查一下2026年增值税的公告
```

```
搜一下小微企业所得税优惠政策
```

```
找财税〔2024〕1号
```

## 保存的文件格式

```markdown
---
title: 中华人民共和国环境保护税法（2025年修订）
doc_num: ""
tax_type: 环境保护税
effect_level: 法律
date: 2025-10-28
status: 全文有效
source: http://fgk.chinatax.gov.cn/zcfgk/...
annotation: "2016年12月25日..."
---

# 中华人民共和国环境保护税法（2025年修订）

> **注释**：2016年12月25日...第二次修正

正文...

---

🔗 关联解读：

  [标题](url)
```

## API 参考

详见 [references/api.md](references/api.md)

## License

MIT
