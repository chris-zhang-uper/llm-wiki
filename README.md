# LLM Wiki

> 基于 [Andrej Karpathy](https://github.com/karpathy) 的 LLM Wiki 模式，使用 TRAE IDE + Obsidian + OpenClaw 构建的个人知识库系统。

**核心理念**：让 LLM 增量构建和维护一个持久化的结构化 Wiki，而非每次查询都从原始文档重新检索。知识复合增长，越用越聪明。

---

## 特性

- 🧠 **增量编译**：新素材自动融入已有知识，更新相关页面（级联更新）
- ⚠️ **矛盾标注**：自动发现不同来源之间的观点冲突，标注后由人类裁决
- 🔍 **语义查询**：基于 Wiki 索引的综合查询，无需 RAG 基础设施
- 📋 **分层 Lint**：确定性检查（自动）+ 语义分析（对话式），保持知识库健康
- 📦 **归档机制**：查询结果可归档为独立页面，形成知识沉淀
- 🔒 **权限分离**：TRAE（AI 写入）+ Obsidian（人类编辑）+ OpenClaw（只读消费）

---

## 架构

```
┌──────────────┐     ┌──────────────┐
│   Obsidian    │     │   TRAE IDE   │
│  (人类编辑)   │     │  (AI 调度)   │
└──────┬───────┘     └──────┬───────┘
       │ 读写                │ 读写
       └────────┬────────────┘
                ▼
     ┌──────────────────┐
     │   LLM Wiki 仓库   │
     │  raw/  wiki/      │
     └────────┬─────────┘
              │ 只读
              ▼
     ┌──────────────────┐
     │   OpenClaw        │
     │  (定时只读消费)    │
     └──────────────────┘
```

---

## 安装

### 前置要求

| 工具 | 版本 | 用途 |
|------|------|------|
| [TRAE IDE](https://trae.ai/) | v3.0+ | AI 知识库管理（核心） |
| [Obsidian](https://obsidian.md/) | 最新版 | 知识库查看和编辑（推荐） |
| Python | 3.8+ | 运行 Lint 脚本 |
| Git | 任意 | 版本控制 |

> OpenClaw 为可选项，用于定时任务和只读查询。

### 关于 Obsidian

[Obsidian](https://obsidian.md/) 是一款免费的双链笔记软件，用于查看和编辑 LLM Wiki 生成的知识库。它提供图谱视图、双向链接导航和丰富的插件生态，是浏览 Wiki 内容的最佳界面。

📥 **下载地址**：[https://obsidian.md/](https://obsidian.md/)（支持 Windows / macOS / Linux / iOS / Android）

> 💡 Obsidian 是可选的。如果你只用 TRAE IDE，也可以直接在 TRAE 的文件浏览器中查看 `wiki/` 目录下的 Markdown 文件。但推荐同时使用 Obsidian，体验双向链接和图谱视图。

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/chris-zhang-uper/llm-wiki.git
cd llm-wiki

# 2. 在 TRAE IDE 中打开此项目
#    文件 → 打开文件夹 → 选择 llm-wiki/
#    TRAE 会自动加载 .trae/rules/project_rules.md 作为项目规则
```

### 配置 Obsidian 读取 LLM Wiki

如果你选择使用 Obsidian，按以下步骤配置：

**第 1 步：打开知识库文件夹**

1. 打开 Obsidian
2. 点击 **"打开文件夹作为仓库"**
3. 选择你克隆的 `llm-wiki/` 文件夹
4. 打开后，左侧文件浏览器会显示项目目录

**第 2 步：查看 Wiki 内容**

- 点击 `wiki/` 目录，查看 LLM 生成的知识页面
- 点击 `wiki/index.md`，查看全局索引（所有页面的入口）
- 点击任意 Wiki 页面，查看内容

**第 3 步：使用图谱视图（推荐）**

1. 点击左侧边栏的 **"图谱视图"** 图标（或按 `Ctrl+G`）
2. 你会看到所有 Wiki 页面之间的关联关系
3. 节点越大表示被引用越多，孤立节点说明缺少关联

**第 4 步：跟随双向链接**

Wiki 页面中使用 `[[页面名称]]` 格式创建双向链接。在 Obsidian 中：
- 点击 `[[链接]]` 可直接跳转到对应页面
- 鼠标悬停在链接上可预览内容（无需离开当前页面）

**第 5 步：安装推荐插件（可选）**

| 插件 | 用途 | 安装方式 |
|------|------|----------|
| Dataview | 动态查询 Wiki 页面（如列出所有标签、最近更新的页面） | 设置 → 第三方插件 → 关闭安全模式 → 搜索 "Dataview" → 安装 |
| Web Clipper | 浏览器一键保存网页为 Markdown 到 `raw/` | [Chrome 扩展商店](https://chrome.google.com/webstore/detail/obsidian-web-clipper) 安装 |

> 💡 安装 Dataview 后，打开 `obsidian/dashboard.md` 可查看知识库仪表盘。

**常见问题**：

| 问题 | 解决方法 |
|------|----------|
| 打开后看不到 Wiki 页面 | 正常，`wiki/` 初始为空，需要先在 TRAE 中执行 Ingest |
| 图谱视图是空的 | 同上，执行 Ingest 后页面会自动出现在图谱中 |
| 想手动编辑 Wiki 页面 | 直接在 Obsidian 中编辑即可，TRAE 会在下次操作时感知变化 |

### 安装完成后的状态

安装完成后（尚未执行任何操作），你的知识库处于**空白初始状态**：

```
llm-wiki/
├── raw/              ← 空目录，等待放入素材
├── wiki/
│   ├── index.md      ← 空索引（只有注释模板）
│   └── log.md        ← 空日志（只有注释模板）
└── pending/          ← 空目录，用于 Lint 待审建议
```

此时：
- `raw/` 是空的，没有素材
- `wiki/` 中只有空的 index.md 和 log.md
- 知识库尚未开始运作

**下一步**：运行验证 → 初始化示例 → 体验功能（见下方）。

---

## 验证安装

安装完成后，按以下步骤验证一切正常：

### 验证 1：TRAE 规则加载

在 TRAE 对话中输入：

```
你是什么角色？
```

**预期回答**：TRAE 应回答自己是"知识库管理员"，并说明职责。如果回答不符合预期，说明 `.trae/rules/project_rules.md` 未被正确加载。

### 验证 2：配置完整性

在 TRAE 中按 `Ctrl+Shift+P`（Mac: `Cmd+Shift+P`），输入 `Tasks: Run Task`，选择 **Wiki: 验证配置**。

**预期结果**：所有检查项显示 ✓：

```
📁 目录结构
  ✓ raw/ 目录存在
  ✓ wiki/ 目录存在
  ✓ pending/ 目录存在
  ✓ scripts/ 目录存在

⚙️ TRAE 配置
  ✓ .trae/rules/project_rules.md 存在
  ✓ .trae/tasks.json 存在
  ✓ .trae/settings.json 存在

🎯 Skills
  ✓ skills/ingest/SKILL.md 存在
  ✓ skills/query/SKILL.md 存在
  ✓ skills/archive/SKILL.md 存在
  ✓ skills/lint/SKILL.md 存在

🤖 Agents
  ✓ agents/wiki-health-reporter.md 存在

📝 Wiki 核心文件
  ✓ wiki/index.md 存在
  ✓ wiki/log.md 存在

📦 Git 配置
  ✓ .gitignore 存在
  ✓ pending/ 已被忽略

✓ 所有检查通过！知识库配置正确。
```

### 验证 3：命令行验证（可选）

```bash
python3 scripts/verify-config.py
```

应输出与上面相同的结果。

---

## 快速体验

验证通过后，按以下 5 步体验知识库的完整工作流。

### 第 1 步：初始化示例素材

在 TRAE 中按 `Ctrl+Shift+P`，运行 **Wiki: 初始化示例数据** Task。

这会在 `raw/demo/` 下创建 3 篇示例素材：
- `2026-04-04-karpathy-llm-wiki.md` — Karpathy 原文介绍
- `2026-04-10-community-wiki-implementation.md` — 社区实现方案
- `2026-04-12-critique-llm-wiki.md` — 批判性分析（与前两篇有矛盾）

> ⚠️ 此步骤只创建原始素材，不创建 wiki 页面。wiki 页面由你在下一步通过 Ingest 流程自行创建。

### 第 2 步：体验 Ingest（摄入素材）

在 TRAE 对话中输入：

```
处理 raw/demo/2026-04-04-karpathy-llm-wiki.md
```

**预期效果**：
- TRAE 读取素材，与你讨论要点
- 在 `wiki/demo/` 下创建新页面（如 `llm-wiki-pattern.md`）
- 更新 `wiki/index.md`（添加新条目）和 `wiki/log.md`（追加记录）

### 第 3 步：体验级联更新

```
处理 raw/demo/2026-04-10-community-wiki-implementation.md
```

**预期效果**：
- 创建新页面（如 `wiki-implementation.md`）
- **同时更新**第 2 步创建的页面（补充社区实践细节）
- 在两个页面之间建立 `[[双向链接]]`
- `wiki/log.md` 中出现 `- Updated: llm-wiki-pattern` 记录

### 第 4 步：体验矛盾标注

```
处理 raw/demo/2026-04-12-critique-llm-wiki.md
```

**预期效果**：
- 创建新页面（如 `llm-wiki-critique.md`）
- **在已有页面中标注矛盾**（如："Karpathy 称维护成本接近零，但批判文章认为被低估"）
- 矛盾以 `> ⚠️ **矛盾标注**：...` 格式呈现

### 第 5 步：体验 Query 和 Lint

```
查询知识库中关于 LLM Wiki 维护成本的内容
```

**预期效果**：TRAE 综合多个页面回答，展示矛盾双方的观点，并询问是否归档。

```
执行 Lint
```

**预期效果**：TRAE 深度阅读所有 wiki 页面，报告发现的问题和建议。

### 第 6 步：在 Obsidian 中查看

1. 打开 Obsidian → 打开 `wiki/demo/` 目录
2. 点击右上角**图谱视图**图标，查看页面之间的关联
3. 打开 `wiki/index.md`，查看全局索引

---

## 功能使用指南

### 功能一：摄入新素材（Ingest）

**用途**：将文章、论文、笔记等素材编译为结构化的 Wiki 知识。

**操作**：
```
处理 raw/<topic>/<文件名>.md
```

**TRAE 会自动执行**：
1. 读取素材全文，提取关键信息
2. 与你讨论要点（可说"跳过"）
3. 创建或更新 Wiki 页面
4. 检测矛盾并标注
5. 级联更新受影响的已有页面
6. 更新索引和日志

**素材准备方式**：

| 方式 | 操作 |
|------|------|
| Obsidian Web Clipper | 浏览器扩展 → 一键保存为 Markdown → 存入 `raw/<topic>/` |
| 手动创建 | 在 `raw/<topic>/` 下创建 `YYYY-MM-DD-标题.md`，粘贴内容 |
| 直接拖放 | 将文件拖入 `raw/<topic>/` 目录 |
| **格式转换** | 使用转换脚本将 PDF/DOCX 等转为 Markdown（见下方） |

**支持的素材格式**：

| 格式 | 支持方式 | 说明 |
|------|----------|------|
| .md | ✅ 直接使用 | Markdown 文件，直接放入 `raw/<topic>/` |
| .txt | ✅ 直接使用 | 纯文本，TRAE 可直接读取 |
| .pdf | ✅ 转换后使用 | 需运行转换脚本（依赖 `pdfplumber`） |
| .docx | ✅ 转换后使用 | 需运行转换脚本（依赖 `python-docx`） |
| .doc | ⚠️ 转换后使用 | 需安装 LibreOffice 或 antiword |
| .html | ✅ 转换后使用 | 需运行转换脚本，或使用 Obsidian Web Clipper |
| .mp3/.m4a/.wav | ✅ 转换后使用 | 音频文件，自动语音转文字（依赖 `whisper`） |
| .mp4/.mkv/.webm | ✅ 转换后使用 | 视频文件，提取音频后转文字（依赖 `ffmpeg` + `whisper`） |
| **视频链接** | ✅ 转换后使用 | YouTube/Bilibili/抖音/TikTok/西瓜视频（依赖 `yt-dlp`） |
| **音频链接** | ✅ 转换后使用 | 喜马拉雅等平台（依赖 `yt-dlp`） |

**格式转换方法**：

```bash
# 1. 安装基础依赖（文档转换）
pip install pdfplumber python-docx yt-dlp --break-system-packages

# 2. 安装音视频转录依赖（可选，处理视频/音频时需要）
pip install openai-whisper --break-system-packages
# Ubuntu: sudo apt install ffmpeg
# macOS: brew install ffmpeg

# 3. 转换文件
python3 scripts/convert-to-raw.py paper.pdf --topic research

# 4. 转换视频链接
python3 scripts/convert-to-raw.py "https://www.youtube.com/watch?v=xxx" --topic ai

# 5. 转换 B 站视频
python3 scripts/convert-to-raw.py "https://www.bilibili.com/video/BV1xx" --topic tutorial

# 6. 转换音频文件
python3 scripts/convert-to-raw.py podcast.mp3 --topic podcast

# 7. 也可在 TRAE 中按 Ctrl+Shift+P → Wiki: 转换文件为 Markdown
```

> 💡 **视频/音频转换策略**：优先提取平台字幕（最快，秒级完成）→ 字幕不可用时下载音频用 Whisper 转录（较慢，需要 GPU 或较长时间）。建议优先选择有字幕的视频。

转换后的 Markdown 文件会自动保存到 `raw/<topic>/` 目录，之后正常使用 Ingest 流程处理即可。

**素材文件格式**：
```markdown
---
source: https://example.com/article
collected: 2026-04-14
published: 2026-04-10
---

# 文章标题

（文章内容）
```

---

### 功能二：查询知识库（Query）

**用途**：基于已有知识综合回答问题。

**操作**：
```
查询关于 XX 的内容
```

**TRAE 会自动执行**：
1. 读取 `wiki/index.md` 定位相关页面
2. 深入阅读相关页面
3. 综合回答（附带引用）
4. 如果回答有长期价值，询问是否归档

---

### 功能三：归档查询结果（Archive）

**用途**：将有价值的查询结果保存为独立的 Wiki 页面。

**操作**：
```
归档这个回答
```

**特点**：
- 归档页面是 **point-in-time 快照**
- 后续 Ingest 不会自动修改归档页面
- 在索引中以 `[Archived]` 前缀标识

---

### 功能四：健康检查（Lint）

**用途**：检查知识库的健康状态，发现矛盾、孤立页面、知识缺口。

**操作**：
```
执行 Lint
```

**两层检查**：

| 层级 | 方式 | 检查内容 |
|------|------|----------|
| Layer 1 | 自动（脚本） | 索引一致性、链接完整性、引用完整性 |
| Layer 2 | 对话式（TRAE） | 语义矛盾、过时内容、知识缺口、新方向建议 |

**Layer 1 也可通过 TRAE Task 执行**：`Ctrl+Shift+P` → **Wiki: 执行确定性 Lint**

检查结果写入 `pending/` 目录，审阅后在 TRAE 中说"应用 Lint 建议"即可修复。

---

### 功能五：健康报告

**用途**：生成知识库的统计概览和状态报告。

**操作**：
```
生成健康报告
```

**报告内容**：页面总数、素材总数、最近活动、孤立页面、待处理建议。

---

### 常用命令速查

| 你说的话 | TRAE 做的事 |
|----------|-------------|
| `处理 raw/xxx.md` | 执行 Ingest，编译素材到 Wiki |
| `处理 raw/video.mp4` | 自动转换视频 → 转录为文字 → 编译到 Wiki |
| `处理 raw/audio.mp3` | 自动转录音频 → 编译到 Wiki |
| `处理 https://youtube.com/...` | 自动提取字幕/转录 → 编译到 Wiki |
| `批量处理 raw/work/` | 扫描目录，逐个处理所有未处理的文件 |
| `扫描新文件` | 扫描整个 raw/ 目录，列出未处理的文件 |
| `查询关于 XX 的内容` | 搜索 Wiki 并综合回答 |
| `归档这个回答` | 将分析保存为 Wiki 页面 |
| `执行 Lint` | 健康检查知识库 |
| `生成健康报告` | 输出统计和状态报告 |

### 拖拽文件使用方式

你可以直接将文件拖入 `raw/<topic>/` 目录（通过文件管理器或 Obsidian），然后在 TRAE 中说：

```
批量处理 raw/work/
```

或

```
扫描新文件
```

TRAE 会自动扫描 `raw/` 目录，对比 `wiki/log.md` 中已处理的记录，找出未处理的文件并逐个执行 Ingest。

**支持拖拽的格式**：`.md` `.txt` `.pdf` `.docx` `.doc` `.html` `.mp3` `.m4a` `.wav` `.flac` `.mp4` `.mkv` `.webm` `.avi` `.mov`

---

## 目录结构

```
llm-wiki/
├── .trae/                        # TRAE IDE 配置
│   ├── rules/project_rules.md    # 核心规则（持续加载）
│   ├── skills/                   # 操作技能（按需加载）
│   │   ├── ingest/SKILL.md       # 摄入新素材
│   │   ├── query/SKILL.md        # 查询知识库
│   │   ├── archive/SKILL.md      # 归档查询结果
│   │   └── lint/SKILL.md         # 健康检查
│   ├── agents/                   # 独立 Agent
│   │   └── wiki-health-reporter.md
│   ├── settings.json             # TRAE 性能配置
│   └── tasks.json                # TRAE Tasks
├── raw/                          # 原始素材（LLM 只读）
├── wiki/                         # 编译知识（LLM 管理）
│   ├── index.md                  # 全局索引
│   └── log.md                    # 操作日志
├── pending/                      # Lint 待审区
├── scripts/                      # 辅助脚本
│   ├── lint-deterministic.py     # 确定性 Lint
│   ├── verify-config.py          # 配置验证
│   └── init-examples.sh          # 示例初始化
├── obsidian/                     # Obsidian 专用
│   └── dashboard.md              # Dataview 仪表盘
├── openclaw-context.md           # OpenClaw 只读上下文
├── QUICKSTART.md                 # 快速入门（详细版）
├── docs/
│   ├── design-process.md         # 设计过程记录
│   ├── architecture-spec.md      # 架构规格书
│   └── deploy-guide.md           # 完整部署指南
├── README.md                     # 本文档
└── LICENSE                       # MIT 开源协议
```

---

## 核心概念

### 三层架构

| 层级 | 目录 | 说明 | 权限 |
|------|------|------|------|
| Raw | `raw/` | 原始素材，不可变 | LLM 只读，人类可读写 |
| Wiki | `wiki/` | 编译后的结构化知识 | LLM 全权管理 |
| Schema | `.trae/rules/` | 行为规范 | 人类维护 |

### 四种操作

| 操作 | 触发词 | 说明 |
|------|--------|------|
| **Ingest** | "处理"、"摄入" | 读取素材 → 编译 Wiki → 级联更新 |
| **Query** | "查询"、"搜索" | 读索引 → 定位页面 → 综合回答 |
| **Archive** | "归档"、"保存" | 将查询结果保存为 Wiki 页面 |
| **Lint** | "lint"、"检查" | 确定性检查 + 语义深度分析 |

---

## 进阶配置

### Obsidian 插件

| 插件 | 用途 | 安装方式 |
|------|------|----------|
| [Dataview](https://github.com/blacksmithgu/obsidian-dataview) | 动态查询 Wiki 页面 | Obsidian → 第三方插件 → 搜索 "Dataview" |
| [Web Clipper](https://obsidian.md/clipper) | 浏览器剪藏网页为 Markdown | [Chrome 扩展商店](https://chrome.google.com/webstore/detail/obsidian-web-clipper) |

### OpenClaw 定时任务（可选）

参考 [openclaw-context.md](openclaw-context.md) 配置：
- 每日工作简报（每天 8:00）
- 素材监控通知（每 2 小时）

### 自定义规则

根据你的领域调整 `.trae/rules/project_rules.md`，例如：
- 修改 Wiki 页面格式规范
- 添加领域特定的 topic 约定
- 调整 LLM 行为偏好

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目主页（本文档） |
| [QUICKSTART.md](QUICKSTART.md) | 详细快速入门教程 |
| [docs/architecture-spec.md](docs/architecture-spec.md) | 完整架构规格书 |
| [docs/design-process.md](docs/design-process.md) | 设计过程和决策记录 |
| [docs/deploy-guide.md](docs/deploy-guide.md) | 完整部署指南 |
| [openclaw-context.md](openclaw-context.md) | OpenClaw 配置参考 |

---

## 致谢

- [Andrej Karpathy](https://github.com/karpathy) — 提出 LLM Wiki 模式
- [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) — 社区最佳实践
- [TRAE IDE](https://trae.ai/) — AI 原生开发环境
- [Obsidian](https://obsidian.md/) — 知识库查看和编辑
- [OpenClaw](https://open-claw.me/) — AI 助手和定时任务

## License

[MIT](LICENSE)
