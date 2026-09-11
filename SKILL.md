---
name: tax-policy-search
description: "搜索国家税务总局政策法规库（chinatax.gov.cn）的政策文件原文，可查看、保存全文，也可顺带抓关联文档。用户说「查/搜/找 + 税种/政策/文件类型」「下载这个链接」「保存全文」「监控税务总局新文件」时触发。不适用于企业公告、上市公司披露，也不适用于会计处理咨询。"
tags: [税法, 政策法规, 国家税务总局, chinatax, 法规搜索, 下载全文]
---

# 国家税务总局政策法规库 — 搜索 / 下载 Skill

## 触发条件

- 「查 / 搜 / 找」+ 税种 / 政策 / 文件类型，可带时间、文号、行业限定词
- 「下载这个链接 https://fgk.chinatax.gov.cn/...」「保存全文」
- 「监控税务总局有没有新文件」

**不适用**：企业公告、上市公司披露（走巨潮资讯等另一类数据源）；会计处理 / 税务处理咨询（本 skill 只取原文，不做判断）。

## 前置依赖

Python 3。脚本只用 stdlib，无第三方包。环境里没有 Python 3 时本 skill 不可用。

## 执行方式

脚本在 skill 目录的 `scripts/` 下，下文 `${SKILL_DIR}` 指该目录，用时替换为实际绝对路径。

脚本都是命令行工具，用 shell 或代码执行工具直接跑即可。退出码非 0 就是失败，原因在 stderr。

| 脚本 | 用法 |
|---|---|
| `search.py` | stdin 收 JSON 参数，输出结果清单 |
| `fetch_full.py URL` | 打印全文（正文 + 立法沿革 + 关联解读 + 关联文件） |
| `fetch_full.py --save URL` | 存成带 frontmatter 的 Markdown |
| `fetch_full.py --json URL` | 输出结构化数据（喂给 `save.py`） |
| `fetch_full.py --depth N URL` | 顺带跟正文/关联里的文档链接，N 层（默认 0 = 不跟） |
| `save.py` | stdin 收结构化数据，写成 Markdown |
| `monitor.py` | 有新文件时把 Markdown 打到 stdout，无新内容静默；`TAX_STATE_FILE` 可改状态文件路径，`python3 monitor.py \| your-notifier` 接通知 |

## Step 1: 搜索

```bash
echo '{"searchWord":"欠税公告办法"}' | python3 "${SKILL_DIR}/scripts/search.py"
```

输出 `命中：0 条` 就是没搜到，换关键词或减少限定条件。

**参数映射：**

| 用户说 | JSON 键 |
|---|---|
| 税种名 | `"xxgkSonTaxPolicy": "增值税"` |
| 年份 | `"xxgkFormulatedYear": "2026"` |
| 公告 / 通知 | `"docType": "国家税务总局公告"`（**不带空格**） |
| 全文有效 / 失效 | `"xxgkAging": "全文有效"` |
| 文号（如 2026 年第 9 号） | `"docYear": "2026", "docNo": "9"` |
| 关键词 | `"searchWord": "小微企业", "wordPlace": "1"` |
| 翻页 | `"pageNum": "1"`（从 0 开始，每页固定 10 条） |

⚠️ `docType` 不带空格：`财政部税务总局公告`，不是 `财政部 税务总局公告`。

## Step 2: 翻页

上表加 `"pageNum"`，重跑 Step 1。

## Step 3: 查看全文

```bash
python3 "${SKILL_DIR}/scripts/fetch_full.py" "条目URL"
```

**原样展示脚本输出，不要重新组织、摘要或归并** —— 用户要看的就是原文。

用户直接给链接时（「下载这个 http://fgk.chinatax.gov.cn/...」），跳过 Step 1–2。

## Step 4: 保存全文

```bash
python3 "${SKILL_DIR}/scripts/fetch_full.py" --save "URL"
```

标题、文号、类别、成文日期、时效自动从页面抓。存到 `~/Documents/税务文件/`，`TAX_SAVE_DIR` 可改。

想把正文和关联阅读里的文档一并抓下来，加 `--depth N`（默认 0 = 不跟）：

```bash
python3 "${SKILL_DIR}/scripts/fetch_full.py" --depth 1 "URL"
```

实测规模（9 个种子文档）：`--depth 1` 通常 3–29 篇，`--depth 2` 到 29–55 篇，从 3 层往上只多 +1~6 篇。
链接图是轴辐式（大家都指向同几部核心法），很快收敛在 30–60 篇，不会指数爆炸，最大实测 55 篇。
所以用 1 或 2 就够，3 以上基本白跑。附件（pdf/doc/图片）不跟，http/https 重复链接自动去重，每篇间隔 0.5s。

**已知数据、只需写文件时**，直接把结构化数据喂给 `save.py`：

```bash
echo '{"title":"标题","doc_num":"文号","tax_type":"税种","effect_level":"类别","date":"成文日期","status":"时效","source":"URL","annotation":"立法沿革","text":"正文","related_interp":[],"related_docs":[]}' | python3 "${SKILL_DIR}/scripts/save.py"
```

## 用户命令

| 输入 | 动作 |
|---|---|
| 编号（1/2/…，支持第一/第二/…/最后） | 查看该条全文 |
| b / 返回 | 回到清单 |
| 下一页 / 上一页 | 翻页 |
| 保存全文 | 保存当前条目 |
| 新搜索 | 重新搜索 |

## 参考文件

- `references/api.md` — 搜索 API 参数详解（用户问「支持哪些参数」「怎么填年份/税种」时加载）
- `references/supplementary-tax-disclosure.md` — 上市公司补税公告信息披露框架（用户问「补税披露」「巨潮 PDF 提取」时加载）
- `references/analysis-framework.md` — 税务专家分析框架（用户说「分析一下」时加载）

## 踩坑记录

1. **URL 必须来自搜索结果或用户给的链接** — 绝对不要编造详情页 URL
2. **`docType` 不带空格** — `财政部税务总局公告`
3. **`pageSize` 固定 10** — 设 20、50 都只返回 10 条，翻页只能用 `pageNum`
4. **关联解读通过 AJAX 加载** — 静态 HTML 里没有，要调 `queryManuscriptAssociation`
5. **超时已内置 3 次重试** — chinatax 偶尔超时，脚本自动退避重试，仍失败才报错
6. **立法沿革藏在 `zscont` 区域** — 需单独提取，正文区里没有
7. **脚本只用 stdlib** — 全部基于 `urllib.request`，任何 Python 3 环境可直接跑
8. **图片型文章不是失败** — 有些文种（如「2026 最新增值税税率表」）正文整篇是一张图，提不出文字；脚本会明确说明并给出图片地址，不要当成抓取失败
9. **文号抓不全属正常** — 老文件页面上没有文号元素，`doc_num` 会留空，文件名退化为 `全文_<标题>.md`；要精确文号得回搜索接口取 `docNum` 字段
