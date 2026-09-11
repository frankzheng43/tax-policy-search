---
name: tax-policy-search
description: "搜索国家税务总局政策法规库（chinatax.gov.cn）。用户提到查/搜/找+税种/政策/文件类型时触发。覆盖所有税种及税务文件效力等级。"
tags: [税法, 政策法规, 国家税务总局, chinatax, 法规搜索]
---

# 国家税务总局政策法规库 — 搜索 Skill

## 触发条件

用户提到：查/搜/找 + 税种/政策/文件类型 + 可选的时间/文号/行业等限定词。

## 执行方式

**用你的代码执行工具运行下面的 Python 代码。**

脚本在本 skill 目录的 `scripts/` 下。下文 `${SKILL_DIR}` 均指该目录，用时替换为实际绝对路径。

## 状态变量（会话内保持）

- `SEARCH_PARAMS`: dict — 当前搜索参数
- `CURRENT_PAGE`: int — 当前页码（从 0 开始）
- `CURRENT_ITEMS`: list — 当前页的搜索结果
- `CURRENT_VIEW`: dict or None — 当前查看的全文数据

## Step 1: 搜索

```python
import subprocess, json, os
script = "${SKILL_DIR}/scripts/search.py"
params = {
    # 以下按用户意图填写：
    # "xxgkSonTaxPolicy": "增值税",     # 税种
    # "xxgkFormulatedYear": "2026",     # 年份
    # "docType": "国家税务总局公告",     # 文件类型（不带空格！）
    # "xxgkAging": "全文有效",           # 时效
    # "searchWord": "小微企业",           # 关键词
    # "docYear": "2026", "docNo": "9",   # 文号
}
r = subprocess.run(["python3", script], input=json.dumps(params), capture_output=True, text=True)
if r.returncode != 0:
    print(f"[Error] 搜索失败: {r.stderr.strip()}")
elif not r.stdout.strip() or "命中：0" in r.stdout:
    print("未找到匹配结果，请换关键词试试")
else:
    print(r.stdout)
```

**参数映射：**

| 用户说 | API 参数 |
|---|---|
| 税种名 | `xxgkSonTaxPolicy=税种名` |
| 年份 | `xxgkFormulatedYear=年份` |
| 公告/通知 | `docType=国家税务总局公告`（不带空格） |
| 全文有效/失效 | `xxgkAging=全文有效` |
| 文号（如2026年第9号） | `docYear=2026 & docNo=9` |
| 关键词 | `searchWord=关键词 & wordPlace=1` |

**⚠️ docType 不带空格：** `财政部税务总局公告`，不是 `财政部 税务总局公告`

## Step 2: 翻页

修改 `params["pageNum"]`（加 1 或减 1），重新执行 Step 1 的代码。

## Step 3: 查看全文

```python
import subprocess, os
script = "${SKILL_DIR}/scripts/fetch_full.py"
url = "ITEMS_URL"  # 替换为用户选择的条目URL
r = subprocess.run(["python3", script, url], capture_output=True, text=True)
print(r.stdout)
```

返回：正文 + 立法沿革 + 关联解读 + 关联文件。
展示脚本原始输出，不要重新组织、摘要或归并。用户要看的就是原文。

## Step 4: 保存全文

用户说"保存全文"时，将 Step 3 的数据传入：

```python
import subprocess, json, os
script = "${SKILL_DIR}/scripts/save.py"
data = {
    "title": "标题", "doc_num": "文号", "tax_type": "税种",
    "effect_level": "类别", "date": "成文日期", "status": "时效",
    "source": "详情页URL", "annotation": "立法沿革", "text": "正文",
    "related_interp": [], "related_docs": [],
}
r = subprocess.run(["python3", script], input=json.dumps(data), capture_output=True, text=True)
print(r.stdout)
```

默认存入 `~/Documents/税务文件/`，用 `TAX_SAVE_DIR` 环境变量可改到别处。

## 分析（可选）

用户说"分析一下"时，加载 `references/analysis-framework.md` 作为分析框架。

## 用户命令

| 输入 | 动作 |
|---|---|
| 编号（1/2/...）| 查看该条全文 |
| b / 返回 | 回到清单 |
| 下一页 / 上一页 | 翻页 |
| 保存全文 | 保存当前条目 |
| 新搜索 | 重新搜索 |

编号支持中文序数（第一/第二/.../最后）。

## 参考文件

- `references/api.md` — 搜索 API 参数详解（用户问"支持哪些参数""怎么填年份/税种"时加载）
- `references/supplementary-tax-disclosure.md` — 上市公司补税公告信息披露框架（用户问"补税披露""巨潮 PDF 提取"时加载）
- `references/analysis-framework.md` — 税务专家分析框架（用户说"分析一下"时加载）

## 配套脚本

- `scripts/monitor.py` — 轮询法规库，有新内容时把 Markdown 打到 stdout（无新内容则静默，退出码 0）。
  自己接通知渠道，例如 `python3 monitor.py | your-notifier`，或用 cron 定时跑。
  状态文件默认 `~/.tax_law_state.json`，用 `TAX_STATE_FILE` 可改。

## 踩坑记录

1. **URL 必须来自 API** — 绝对不能编造链接
2. **docType 不带空格** — `财政部税务总局公告`
3. **pageSize 固定 10** — 设再大也无效，翻页用 pageNum
4. **关联解读通过 AJAX 加载** — 静态 HTML 里没有
5. **网络超时需重试** — chinatax.gov.cn 偶尔超时
6. **立法沿革藏在 `zscont` 区域** — 需单独提取
7. **脚本只用 stdlib** — 全部基于 `urllib.request`，无第三方依赖，任何 Python 3 环境直接跑。
