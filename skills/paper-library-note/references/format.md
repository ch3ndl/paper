# Saline Papers 笔记格式 v1

UTF-8 JSON，所有正文是纯文本；不写 HTML 或 Markdown 格式标记。段落间用 `\n\n`。网站会转义内容，按结构生成页面。

```json
{
  "schemaVersion": 1,
  "slug": "paper-short-name",
  "title": "中文标题",
  "subtitle": "Original paper title",
  "year": 2026,
  "category": "研究主题",
  "tags": ["方法", "研究对象", "任务"],
  "updated": "2026-11-11",
  "status": "draft",
  "source": {
    "url": "https://doi.org/10.xxxx/example",
    "citation": "作者. 题名. 期刊, 年份, 卷: 页码. DOI."
  },
  "summary": "一句话概括研究问题、方法与最重要的发现。",
  "coverage": "说明实际读过的正文、图表与补充材料，以及仍未读取的内容。",
  "sections": [
    {
      "id": "introduction",
      "title": "引言",
      "originalHeading": "1 Introduction",
      "sourceLocation": "正文第 1 节，PDF 第 2 页；以实际读取版本为准",
      "blocks": [
        {
          "heading": "1.1 原文小节名：研究问题如何提出",
          "explanation": "详细中文讲解，多个段落以空行分隔。",
          "analysis": "作者解释：……\n\nAI 分析：……",
          "englishParaphrase": "Optional English paraphrase, never a verbatim quote.",
          "quote": "可选，必要的短原文引句",
          "figures": [
            {
              "path": "assets/images/paper-short-name/figure-1.jpg",
              "alt": "图 1 的内容描述，供读屏使用",
              "caption": "图号、图意、关键面板与阅读方式。图片作者署名与改动情况。",
              "source": "https://example.org/article/figure/1",
              "license": "实际核实的许可与署名，勿猜测"
            }
          ]
        }
      ]
    }
  ],
  "assessment": "综合贡献、证据边界和后续值得核查的问题。"
}
```

示例文字仅说明字段，生成时必须替换为论文实际内容；未知字段用正文说明未知，不能沿用示例 DOI 或虚构页码。

- `slug` 与 JSON 文件名相同；`id` 在全篇唯一，使用英文小写数字和连字符。
- `year` 为四位整数；`updated` 为用户本地日期 ISO `YYYY-MM-DD`。
- `status` 为 `draft`（默认待核对）、`reviewed`（用户已人工核对）或 `imported`（旧笔记迁移）。状态不控制是否公开；被提交的文章都会发布。
- `title/summary/category/coverage/source.url/source.citation/sections` 必填；tags 是文本数组。建议填写 assessment。
- 每节需要 `id/title/originalHeading/sourceLocation/blocks`。至少一个 block，每个 block 需要 `heading/explanation`，建议有 analysis。
- 可选字段没有内容时省略或使用空文本；没有图片时省略 figures 或用空数组，不能保留不存在的文件路径。
- 图片路径严格为 `assets/images/<slug>/<英文文件名>.png|jpg|jpeg|webp`，每张图需要 path/alt/caption/source/license。图片来源链接用稳定的 http(s) 地址。
- 文章更新保持 slug 不变。图片文件名也尽量稳定，新版本替换应说明内容改动。
- 网站管理页支持标准 ZIP（store 或 deflate），打包脚本使用无压缩 ZIP 提高兼容性。单文件不超过 12 MiB，整体不超过 30 MiB，最多 100 个文件。

输出目录：
```text
paper-export/
  notes/paper-short-name.json
  assets/images/paper-short-name/figure-1.jpg
```

网站：`https://ch3ndl.github.io/paper/`；仓库：`https://github.com/ch3ndl/paper`。
