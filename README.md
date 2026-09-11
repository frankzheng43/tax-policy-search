# tax-policy-search

Agent Skill — 自然语言搜索国家税务总局政策法规库（chinatax.gov.cn），可查看、保存全文，也可顺带抓关联文档

## 安装

```bash
git clone https://github.com/frankzheng43/tax-policy-search.git
```

把整个目录放进你的 agent 的 skills 目录（或让 agent 直接指向该目录）即可。
SKILL.md 里 `${SKILL_DIR}` 指该目录本身，用之前换成实际绝对路径。

依赖：Python 3，无第三方包（全部用 stdlib）。

**不适用于**：企业公告、上市公司披露（那走巨潮资讯等另一类数据源）；会计处理 / 税务处理咨询（本 skill 只取原文，不做判断）。

## 环境变量（可选）

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TAX_SAVE_DIR` | `~/Documents/税务文件` | 保存全文的输出目录 |
| `TAX_STATE_FILE` | `~/.tax_law_state.json` | monitor 的去重状态文件 |

## 功能

- **自然语言搜索**：说「查增值税公告」「找2026年企业所得税文件」即可
- **只搜文件类**：默认滤掉新闻、视频、各地动态等干扰项，只返回法律/法规/规章/规范性文件/解读；传 `"label": ""` 可搜全站
- **筛选条件**：税种、年份、文件类型、时效、行业等
- **查看全文**：含正文、表格（MD格式）、关联解读
- **给链接直接抓**：`fetch_full.py --save <url>` 一步存成 Markdown
- **顺带抓关联文档**：加 `--depth N`（默认关），把正文和关联阅读里的文档一并存下来
- **保存全文**：带 YAML frontmatter，含立法沿革（注释）
- **翻页导航**：上一页/下一页
- **定时监控**：`scripts/monitor.py` 检测新文件，有新内容输出 Markdown，可接任意通知渠道
- **内置重试**：chinatax 偶尔超时，所有网络请求自动重试 3 次（退避 1.5s / 3s）

## 使用方法

对 agent 直接说：

```
帮我查一下2026年增值税的公告
```

```
搜一下小微企业所得税优惠政策
```

```
找财税〔2024〕1号
```

```
下载这个链接 https://fgk.chinatax.gov.cn/zcfgk/c100011/c5245544/content.html
```

```
保存全文
```

已经拿到链接时，跳过搜索，直接抓：

```bash
# 打印全文
python3 scripts/fetch_full.py "http://fgk.chinatax.gov.cn/zcfgk/c100011/c5245544/content.html"

# 直接存成 Markdown（标题、文号、类别、成文日期、时效自动抓）
python3 scripts/fetch_full.py --save "http://fgk.chinatax.gov.cn/zcfgk/c100011/c5245544/content.html"

# 顺带把正文/关联里的文档也抓下来，跟 1 层（默认 0 = 不跟）
python3 scripts/fetch_full.py --depth 1 "http://fgk.chinatax.gov.cn/zcfgk/c100011/c5245544/content.html"
```

`--depth` 只跟法规库详情页，附件（pdf/doc/图片）不跟；http/https 重复链接自动去重，每篇间隔 0.5s。

实测 9 个种子文档：`--depth 1` 通常 3–29 篇，`--depth 2` 到 29–55 篇，3 层往上只多 +1~6 篇。链接图是轴辐式
（所有文档都指向同几部核心法），很快收敛在 30–60 篇，**不会指数爆炸**，最大实测 55 篇（政策法规栏目共 4970 篇）。
所以用 1 或 2 就够，3 以上基本白跑。

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

## 定时监控

```bash
# 有新内容才输出，无新内容静默
python3 scripts/monitor.py | your-notifier
```

配 cron 定时跑即可。状态文件记录已见过的文号，避免重复推送。

## API 参考

详见 [references/api.md](references/api.md)

## License

MIT
