---
name: ingest
description: 处理 raw/ 目录中的新素材，编译为 wiki 页面。支持 PDF/DOCX/DOC/TXT/HTML/Markdown 格式。触发词：处理、摄入、ingest、添加到知识库
---

# Ingest 操作流程

## 触发条件

用户说："处理 raw/xxx"、"摄入新素材"、"把这个加到知识库"

支持的文件格式：
- `.md` / `.markdown` — Markdown（直接处理）
- `.txt` — 纯文本（直接处理）
- `.pdf` — PDF 文档（自动转换）
- `.docx` — Word 文档（自动转换）
- `.doc` — Word 文档（自动转换，需 LibreOffice）
- `.html` / `.htm` — 网页（自动转换）

## 操作步骤

### 0. 格式检测与自动转换 ⭐

当用户指定的文件不是 Markdown 格式时，**自动执行转换**，用户无需手动操作：

1. 检查文件扩展名
2. 如果是 `.pdf`、`.docx`、`.doc`、`.txt`、`.html`：
   - 运行转换命令：`python3 scripts/convert-to-raw.py <文件路径> --topic <topic>`
   - 等待转换完成，获取生成的 Markdown 文件路径
   - 告知用户："已自动将 PDF 转换为 Markdown：raw/<topic>/YYYY-MM-DD-xxx.md"
3. 如果是 `.md`：直接读取，跳过此步骤
4. 如果格式不支持：告知用户并建议先手动转换

**转换依赖**：
- PDF：`pdfplumber`（`pip install pdfplumber --break-system-packages`）
- DOCX：`python-docx`（`pip install python-docx --break-system-packages`）
- DOC：LibreOffice 或 antiword
- TXT/HTML：无额外依赖

如果依赖未安装，告知用户安装命令。

### 1. 读取素材
- 读取 raw/ 中指定的素材全文（Markdown 格式）
- 识别主题领域、核心论点、关键实体和数据

### 2. 与用户讨论（可选）
- 简要总结素材要点
- 询问用户希望强调或忽略的内容
- 用户可说"跳过"直接进入下一步

### 3. 确定归属
判断新内容如何融入已有知识：
- **合并**：与已有页面核心论点一致 → 更新该页面
- **新建**：引入全新概念或实体 → 创建新页面
- **跨主题**：涉及多个 topic → 放入最相关的，用 See Also 链接其他

### 4. 矛盾检测与标注 ⭐
比对新信息与已有 wiki 页面：
- 发现矛盾时，在**两个相关页面**中都标注：
  ```
  > ⚠️ **矛盾标注**：[来源A](../../raw/...) 主张 X，而 [来源B](../../raw/...) 主张 Y
  ```
- 不要自行裁决，标注后让人类判断

### 5. 级联更新（Cascade Updates）⭐
一篇新素材可能影响 10-15 个已有页面：
- 扫描**同 topic** 目录下的所有页面
- 扫描 **wiki/index.md** 中其他 topic 的条目
- 对每个受影响的页面进行**实质性修改**：
  - 补充新数据或修正过时描述
  - 刷新 `updated` 日期
  - 追加 `sources` 和 `raw` 引用
- 级联更新不涉及 Archive 页面

### 6. 更新索引
更新 `wiki/index.md`：添加或修改所有受影响页面的条目

### 7. 记录日志
追加 `wiki/log.md`：
```
## [YYYY-MM-DD] ingest | <主页面标题>
- Updated: <级联更新的页面标题>
```

## 完成确认

操作完成后，告知用户：
- 原始格式是什么（如果是非 Markdown，说明已自动转换）
- 创建/更新了哪些页面
- 发现了哪些矛盾（如果有）
- 建议用户在 Obsidian 中查看图谱视图
