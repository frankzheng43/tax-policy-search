# 国家税务总局政策法规库 — API 参考

## 端点

```
GET https://www.chinatax.gov.cn/search5/search/s
```

## 固定参数（每次必传）

| 参数 | 值 | 说明 |
|---|---|---|
| siteCode | bm29000002 | 国家税务总局网站标识码 |
| searchSiteName | GSFFK | 法规库内部搜索引擎名 |
| indexCode | 1 | 索引编号（固定为1） |

## 搜索参数

| 参数 | 说明 | 示例 |
|---|---|---|
| searchWord | 全文关键词搜索 | 增值税 |
| wordPlace | 0=全文（默认）、1=仅标题 | wordPlace=1 |
| participleRule | 5=精准、0=模糊 | participleRule=5 |

## 过滤参数

### xxgkEffectLevel — 效力等级

可选值：`法律` | `行政法规` | `国务院文件` | `税务部门规章` | `财税文件` | `税务规范性文件` | `其他文件` | `工作通知`

### xxgkAging — 文件时效

可选值：`全文有效` | `已修改` | `全文失效` | `全文废止` | `尚未生效`

### xxgkTaxPolicy — 一级主题

可选值：`税收政策` | `社会保险费政策` | `非税收入政策` | `税费征管` | `其他`

### xxgkSonTaxPolicy — 二级主题（税种）

**一级=税收政策时：**
营业税 | **增值税** | 消费税 | 企业所得税 | 个人所得税 | 资源税 | 城市维护建设税 | 房产税 | 印花税 | 城镇土地使用税 | 土地增值税 | 车船税 | 车辆购置税 | 烟叶税 | 耕地占用税 | 契税 | 环境保护税 | 进出口税收 | 国际税收 | 其他税收政策

**一级=社会保险费政策时：**
基本养老保险费 | 基本医疗保险费 | 失业保险费 | 工伤保险费 | 生育保险费 | 职业伤害保障费 | 其他社会保险费

**一级=非税收入政策时：**
教育附加费 | 地方教育费附加 | 文化事业建设费 | 国家留成油收入 | 核事故应急准备专项收入 | 免税商品特许经营费 | 可再生能源电价附加 | 地方水库移民扶持基金 | 大中型水库移民后期扶持基金 | 油价调控风险准备金 | 无居民海岛使用金 | 中央水库移民扶持基金 | 土地闲置费 | 水土保持补偿费 | 水利建设基金 | 石油特别收益金 | 三峡电站水资源费 | 排污权出让收入 | 农网还贷资金 | 免税商品特许经营收入 | 矿产资源专项收入 | 可再生能源发展基金 | 核电站乏燃料处理处置基金 | 海域使用金 | 国有土地使用权出让收入 | 国家重大水利工程建设基金 | 废弃电器电子产品处理基金 | 防空地下室易地建设费 | 城镇垃圾处理费 | 残疾人就业保障金 | (场外)核事故应急准备专项收入 | 其他非税收入政策

### xxgkFormulatedYear — 发文年份

取值范围 `1984` ~ `2026`

### xxgkIndustryType — 行业分类

可选值：`农林业` | `工业` | `服务业` | `金融业` | `房地产业` | `社会民生` | `科技创新` | `创业就业` | `绿色发展` | `区域发展` | `涉外`

### docType — 文种

可选值：
- `国家税务总局令`
- `国家税务总局公告`
- `财政部税务总局公告`
- `财税`
- `国税发`
- `国税函`
- `财关税`
- `财政部海关总署税务总局公告`
- `财政部税务总局中国证监会公告`
- `发改高技`

**⚠️ docType 不带空格**：页面显示"财政部 税务总局公告"，API 存的是 `财政部税务总局公告`

### docYear / docNo — 发文年份/编号

与 docType 配合使用，如 `docType=财税 & docYear=2024 & docNo=1`

### cwrqStart / cwrqEnd — 成文日期范围

格式 `YYYY-MM-DD HH:mm:ss`，如 `cwrqStart=2026-01-01 00:00:00`

### column / label — 栏目/标签

| 参数 | 常用值 |
|---|---|
| column | 政策法规 / 政策解读 / 政策指引 |
| label | 文字政策解读,法律,行政法规,国务院文件,税务部门规章,税务规范性文件,财税文件,其他文件,工作通知,政策指引 |

## 分页与排序

| 参数 | 说明 | 值 |
|---|---|---|
| pageSize | 固定返回10条，设大无效 | 10 |
| pageNum | 页码从0开始 | 0,1,2... |
| orderBy | 5=相关度、2=日期倒序、1=类别、3=热度 | 2 |
| likeDoc | 相似文档折叠 | 0 |

## 返回数据结构

```json
{
  "totalSearch": 10,
  "searchResultAll": {
    "total": 35,
    "searchTotal": [
      {
        "title": "<span>增值税</span>相关公告",
        "content": "根据《中华人民共和国<span>增值税</span>法》…",
        "url": "http://fgk.chinatax.gov.cn/zcfgk/c102416/c5247431/content.html",
        "govDoc": {
          "docNum": "财政部 税务总局公告2026年第9号",
          "docType": "财政部税务总局公告",
          "docYear": "2026",
          "docNo": "9"
        },
        "label": "财税文件",
        "xxgk_aging": "",
        "xxgk_taxPolicy": ["税收政策"],
        "xxgk_son_taxPolicy": ["增值税"],
        "xxgk_formulatedYear": "2026",
        "cwrq": "2026-01-30 00:00:00",
        "pubDate": "2026-01-30 00:00:10",
        "pubName": "财政部,国家税务总局",
        "appendix": [
          {"appendixName": "适用9%税率注释.pdf", "appendixUrl": "http://fgk.chinatax.gov.cn/.../文件名.pdf"}
        ]
      }
    ],
    "agingList": [{"doc_count": 4, "key": "全文有效"}],
    "effectLevelList": [{"doc_count": 29, "key": "财税文件"}],
    "taxPolicyList": [{"key": "税收政策", "doc_count": 2, "sonDatas": {"增值税": 2}}],
    "formulatedYearList": [{"doc_count": 10, "key": "2026"}]
  }
}
```

## 关联内容 API

```
POST https://www.chinatax.gov.cn/queryManuscriptAssociation
Body: id=<articleId>（表单编码）
```

返回 `results.data.results[1]` 包含：
- `policyDocument[]` — 关联文件（title, url, aging, writtentext, effectlevel）
- `policyInterpretation[]` — 关联解读（title, url）

article_id 从搜索结果 `id` 字段取第一段数字，或从页面 `<meta name="articleId">` 获取。

## 踩坑记录

1. `docType` 不带空格
2. `pageSize` 永远返回10条，必须用 pageNum 翻页
3. 精确筛选用 `xxgkSonTaxPolicy`，不要依赖 `searchWord`
4. `cwrq`=成文日期（文件落款），`pubDate`=入库日期
5. `searchWord` 为空时，只要有其他过滤参数也能搜索
6. 标题/正文含 `<span>` HTML 标签，展示时需 strip；但 `<a>` 标签要先转 Markdown 链接再 strip
7. 附件 URL 模式：`http://fgk.chinatax.gov.cn/zcfgk/{栏目ID}/{文章ID}/{文章ID}/files/{文件名}`
8. 关联解读/关联文件通过 POST `https://www.chinatax.gov.cn/queryManuscriptAssociation` `data={id: articleId}` 获取，静态 HTML 中没有
9. 网络偶尔超时，重试一次通常能成功
10. **导出文件中的所有 URL 必须来自 API 返回数据，绝不能编造**
8. **关联解读/关联文件是 AJAX 动态加载的**，静态 HTML 中 `gljdlist`/`glwjlist` 为空，必须调 `queryManuscriptAssociation` 接口获取
9. 页面 `<meta name="articleId">` 可能为空（法律类文章无此标签），需从 URL 路径 `/zcfgk/c{xxx}/c{articleId}/content.html` 提取
