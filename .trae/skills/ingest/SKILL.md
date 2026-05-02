---
name: ingest
description: 处理 raw/ 目录中的新素材，编译为 wiki 页面。支持 PDF/DOCX/DOC/TXT/HTML/视频链接/音频链接/Markdown 格式。触发词：处理、摄入、ingest、添加到知识库、批量处理、扫描新文件
---

# Ingest 操作流程

## 触发条件

用户说："处理 raw/xxx"、"摄入新素材"、"把这个加到知识库"、"批量处理"、"扫描新文件"

支持的输入类型：
- **文件**：`.md` `.txt` `.pdf` `.docx` `.doc` `.html` `.mp3` `.m4a` `.wav` `.flac` `.mp4` `.mkv` `.webm` `.avi` `.mov`
- **链接**：YouTube / Bilibili / 抖音 / TikTok / 西瓜视频 / 喜马拉雅 等平台链接
- **批量**：`raw/` 目录或子目录（自动扫描未处理的文件）
- **拖拽**：用户将文件拖入 `raw/` 后说"处理新文件"

## 操作步骤

### 0. 格式检测与自动转换 ⭐

当用户指定的输入不是 Markdown 格式时，**自动执行转换**，用户无需手动操作：

**如果是文件路径**：
1. 检查文件扩展名
2. 如果是 `.pdf`、`.docx`、`.doc`、`.txt`、`.html`、`.mp3`、`.mp4`、`.avi`、`.mov` 等非 Markdown 格式：
   - 运行转换命令：`python3 scripts/convert-to-raw.py <文件路径> --topic <topic>`
   - 等待转换完成，获取生成的 Markdown 文件路径
   - 告知用户："已自动将 PDF 转换为 Markdown：raw/<topic>/YYYY-MM-DD-xxx.md"
3. 如果是 `.md`：直接读取，跳过此步骤

**如果是视频/音频链接**：
1. 检测输入是否为 URL（以 http:// 或 https:// 开头）
2. 如果是视频/音频平台链接：
   - 运行转换命令：`python3 scripts/convert-to-raw.py "<URL>" --topic <topic>`
   - 转换策略：优先提取平台字幕 → 字幕不可用时下载音频用 Whisper 转录
   - 等待转换完成，获取生成的 Markdown 文件路径
   - 告知用户："已自动将视频转换为 Markdown：raw/<topic>/YYYY-MM-DD-xxx.md"
3. 如果是普通网页链接：建议用户使用 Obsidian Web Clipper 保存

**如果是批量处理请求**：
1. 用户说"批量处理"、"处理所有新文件"、"扫描 raw/"等
2. 扫描 `raw/` 目录，对比 `wiki/log.md` 中已处理的记录
3. 列出未处理的文件清单，确认后逐个执行 Ingest

**转换依赖**：
- 文档：`pdfplumber`、`python-docx`（`pip install pdfplumber python-docx --break-system-packages`）
- 视频/音频链接：`yt-dlp`（`pip install yt-dlp --break-system-packages`）
- 语音转录：`openai-whisper`（`pip install openai-whisper --break-system-packages`）
- 视频提取：`ffmpeg`（`sudo apt install ffmpeg`）

如果依赖未安装，告知用户安装命令。

### 1. 读取素材
- 读取 raw/ 中指定的素材全文（Markdown 格式）
- 识别主题领域、核心论点、关键实体和数据

### 2. 与用户讨论（可选）
- 简要总结素材要点
- 询问用户希望强调或忽略的内容
- 用户可说"跳过"直接进入下一步
- **批量处理时默认跳过讨论**，直接执行

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
- **批量处理时**：输出处理摘要（成功 N 个，失败 N 个，跳过 N 个）
