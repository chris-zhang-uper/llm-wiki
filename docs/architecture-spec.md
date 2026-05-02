# LLM Wiki 最终架构规格书

> 版本：v3.0 | 日期：2026-04-14 | 状态：已发布

---

## 1. 概述

### 1.1 项目定义

LLM Wiki 是一个基于 Andrej Karpathy 的 LLM Wiki 模式构建的个人知识库系统。它使用 TRAE IDE 作为 AI 调度中心，Obsidian 作为人类查看界面，OpenClaw 作为只读消费端，通过 Git 进行版本控制。

### 1.2 核心理念

> 让 LLM 增量构建和维护一个持久化的结构化 Wiki，而非每次查询都从原始文档重新检索。知识复合增长，越用越聪明。

### 1.3 与传统 RAG 的区别

| 维度 | 传统 RAG | LLM Wiki |
|------|----------|----------|
| 知识存储 | 向量数据库 | Markdown 文件 |
| 查询方式 | 每次重新检索 | 增量编译，一次编译多次使用 |
| 知识积累 | 无 | 复合增长 |
| 维护成本 | 低（自动） | 低（LLM 自动维护） |
| 可解释性 | 低（黑盒） | 高（人类可读 Markdown） |
| 矛盾处理 | 无 | 自动标注 |
| 知识关联 | 隐式（向量相似度） | 显式（双向链接） |

---

## 2. 系统架构

### 2.1 组件关系

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                             │
│                                                          │
│   ┌──────────────┐         ┌──────────────────────┐     │
│   │   Obsidian    │         │     TRAE IDE         │     │
│   │              │         │                      │     │
│   │ · 查看知识库  │         │ · AI 调度中心         │     │
│   │ · 手动编辑   │         │ · Ingest/Query/Lint  │     │
│   │ · 图谱视图   │         │ · Schema 管理         │     │
│   │ · Web Clipper│         │ · 级联更新            │     │
│   └──────┬───────┘         └──────────┬───────────┘     │
│          │ 读写                        │ 读写            │
│          └──────────┬──────────────────┘                 │
│                     ▼                                   │
│   ┌─────────────────────────────────────────────────┐   │
│   │              知识库（Git 仓库）                    │   │
│   │                                                  │   │
│   │   raw/          wiki/         index.md  log.md  │   │
│   │   (原始素材)    (编译知识)     (索引)    (日志)   │   │
│   │                                                  │   │
│   └────────────────────┬────────────────────────────┘   │
│                        │ 只读                           │
│   ┌────────────────────▼────────────────────────────┐   │
│   │              OpenClaw（本地 + 服务器）              │   │
│   │                                                  │   │
│   │   · 定时工作简报                                   │   │
│   │   · 素材监控通知                                   │   │
│   │   · 辅助查询                                      │   │
│   │                                                  │   │
│   └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 权限矩阵

| 操作 | TRAE IDE | Obsidian | OpenClaw | Lint 脚本 |
|------|----------|----------|----------|-----------|
| 读取 raw/ | ✅ | ✅ | ✅ | ✅ |
| 写入 raw/ | ❌ | ✅ | ❌ | ❌ |
| 读取 wiki/ | ✅ | ✅ | ✅ | ✅ |
| 写入 wiki/ | ✅ | ✅ | ❌ | ❌ |
| 读取 pending/ | ✅ | ✅ | ✅ | ✅ |
| 写入 pending/ | ✅ | ✅ | ❌ | ✅ |
| 修改 .trae/ | ❌ | ✅ | ❌ | ❌ |

### 2.3 数据流

#### Ingest 流程

```
浏览器 → Obsidian Web Clipper → raw/<topic>/YYYY-MM-DD-slug.md
                                        │
                                        ▼
                              TRAE 读取 raw/ 素材
                                        │
                              ┌─────────┼─────────┐
                              ▼         ▼         ▼
                         创建新页面   合并已有   矛盾标注
                              │         │         │
                              └─────────┼─────────┘
                                        ▼
                              级联更新（扫描受影响页面）
                                        │
                                        ▼
                              更新 wiki/index.md
                                        │
                                        ▼
                              追加 wiki/log.md
                                        │
                                        ▼
                              Obsidian 实时查看结果
```

#### Query 流程

```
用户在 TRAE 中提问
        │
        ▼
  读取 wiki/index.md → 定位相关页面
        │
        ▼
  深入阅读 wiki 页面
        │
        ▼
  综合回答（附带引用）
        │
        ├──→ 无长期价值 → 结束
        │
        └──→ 有长期价值 → 询问用户是否归档
                              │
                              ▼
                    执行 Archive 操作
                              │
                              ▼
                    创建 wiki 页面（point-in-time 快照）
```

#### Lint 流程

```
Layer 1（自动）：
  cron/TRAE Task → lint-deterministic.py
                          │
                          ▼
                  确定性检查（链接、索引、引用）
                          │
                          ▼
                  结果写入 pending/lint-YYYY-MM-DD.md

Layer 2（对话式）：
  用户说"执行 Lint" → TRAE 加载 lint Skill
                          │
                          ▼
                  深度阅读整个 wiki
                          │
                          ▼
                  语义分析（矛盾、过时、缺口、建议）
                          │
                          ▼
                  报告发现 → 用户确认 → TRAE 执行修改
```

---

## 3. 目录结构规格

```
llm-wiki/
├── .trae/                              # TRAE IDE 配置（核心）
│   ├── rules/
│   │   └── project_rules.md            # 核心规则（~80 行，持续加载）
│   ├── skills/                         # 操作技能（按需加载）
│   │   ├── ingest/
│   │   │   └── SKILL.md                # Ingest 操作流程
│   │   ├── query/
│   │   │   └── SKILL.md                # Query 操作流程
│   │   ├── archive/
│   │   │   └── SKILL.md                # Archive 操作流程
│   │   └── lint/
│   │       └── SKILL.md                # Lint 操作流程
│   ├── agents/
│   │   └── wiki-health-reporter.md     # 健康报告 Agent（隔离上下文）
│   ├── settings.json                   # TRAE 性能配置
│   └── tasks.json                      # TRAE Tasks 定义
│
├── raw/                                # 原始素材层（LLM 只读，人类可读写）
│   └── <topic>/                        # 按主题分子目录（动态创建）
│       └── YYYY-MM-DD-slug.md          # 命名格式
│
├── wiki/                               # 编译知识层（LLM 全权管理）
│   ├── index.md                        # 全局索引（查询入口）
│   ├── log.md                          # 操作日志（append-only）
│   └── <topic>/                        # 只允许一级深度
│       └── concept-name.md             # 知识页面
│
├── pending/                            # Lint 待审建议（不入 Git）
│
├── scripts/                            # 辅助脚本
│   ├── lint-deterministic.py           # 确定性 Lint（Layer 1）
│   ├── verify-config.py                # 配置验证
│   └── init-examples.sh                # 示例数据初始化
│
├── obsidian/                           # Obsidian 专用
│   └── dashboard.md                    # Dataview 仪表盘
│
├── docs/                               # 文档
│   ├── design-process.md               # 设计过程记录
│   ├── architecture-spec.md            # 本文档
│   └── deploy-guide.md                 # 部署指南
│
├── openclaw-context.md                 # OpenClaw 只读上下文入口
├── QUICKSTART.md                       # 5 分钟快速入门
├── README.md                           # 项目主页
├── LICENSE                             # MIT 开源协议
├── .gitignore                          # Git 忽略规则
└── .github/                            # GitHub 配置
    ├── ISSUE_TEMPLATE/                 # Issue 模板
    │   ├── bug_report.md
    │   └── feature_request.md
    └── PULL_REQUEST_TEMPLATE.md        # PR 模板
```

---

## 4. Wiki 页面格式规格

### 4.1 标准 Wiki 页面

```markdown
---
tags: [标签1, 标签2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: 作者/机构 + 日期; 作者/机构 + 日期
raw: [../../raw/<topic>/<file>.md](../../raw/<topic>/<file>.md)
status: active | draft | superseded
---

# 页面标题

> 一句话摘要（2-3 句话概括核心内容）

## 正文

（结构化 markdown，使用 H2/H3 分节）

## 关键实体与关联

- [[相关页面1]] — 关联说明
- [[相关页面2]] — 关联说明

## 参考来源

1. [来源标题](../../raw/<topic>/<file>.md)
```

### 4.2 Archive 页面（归档）

```markdown
---
tags: [archived, 标签1]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: wiki:页面A, wiki:页面B
status: archived
---

# 页面标题

> [Archived] 一句话摘要

## 正文

（综合分析内容）

## 来源页面

- [[页面A]]
- [[页面B]]
```

### 4.3 字段说明

| 字段 | 标准页面 | Archive 页面 | 说明 |
|------|----------|-------------|------|
| tags | 必须 | 必须 | 用于 Dataview 查询 |
| created | 必须 | 必须 | 页面创建日期 |
| updated | 必须 | 必须 | 知识内容最后变更日期 |
| sources | 必须 | 必须 | 来源归属 |
| raw | 有 | 无 | 指向 raw 文件的相对路径 |
| status | 必须 | archived | active/draft/superseded/archived |

---

## 5. 操作规格

### 5.1 Ingest

**触发词**：处理、摄入、ingest、添加到知识库

**流程**：
1. 读取 raw/ 中指定素材
2. 与用户讨论要点（可跳过）
3. 确定归属（合并/新建/跨主题）
4. 矛盾检测与标注
5. 级联更新（扫描同 topic + 跨 topic）
6. 更新 wiki/index.md
7. 追加 wiki/log.md

**级联更新规则**：
- 单篇素材可能影响 10-15 个已有页面
- 不涉及 Archive 页面（point-in-time 快照）
- 每个修改页面刷新 updated 日期

**矛盾标注格式**：
```
> ⚠️ **矛盾标注**：[来源A](../../raw/...) 主张 X，而 [来源B](../../raw/...) 主张 Y
```

### 5.2 Query

**触发词**：查询、搜索、query、知识库里有

**流程**：
1. 读取 wiki/index.md 定位相关页面
2. 深入阅读 wiki 页面
3. 综合回答（优先 wiki 内容，附带引用）
4. 不自动写入文件
5. 主动询问是否归档

### 5.3 Archive

**触发词**：归档、保存回答、archive

**流程**：
1. 创建新 wiki 页面
2. 使用 Archive 格式（sources 引用 wiki 页面）
3. 更新 wiki/index.md（Summary 前加 [Archived]）
4. 追加 wiki/log.md

**关键规则**：Archive 页面是 point-in-time 快照，后续 Ingest 不会修改。

### 5.4 Lint

**触发词**：lint、健康检查、维护

**Layer 1（确定性检查）**：
- 索引一致性
- 内部链接完整性
- Raw 引用完整性
- 交叉引用建议
- 输出到 pending/

**Layer 2（语义深度分析）**：
- 矛盾检测（全局扫描）
- 过时内容识别
- 知识缺口发现
- 结构建议
- 新方向建议
- 输出到 pending/ 或直接在对话中报告

---

## 6. 索引与日志规格

### 6.1 wiki/index.md

```markdown
# Knowledge Base Index

## <topic-1>
- [页面标题](<topic-1>/page1.md) — 一句话摘要 | Updated: YYYY-MM-DD
- [页面标题](<topic-1>/page2.md) — [Archived] 一句话摘要 | Updated: YYYY-MM-DD

## <topic-2>
- [页面标题](<topic-2>/page3.md) — 一句话摘要 | Updated: YYYY-MM-DD
```

- Updated 日期反映知识内容最后变更时间
- Archived 页面 Summary 以 `[Archived]` 开头
- 每新增 topic 附带一行描述

### 6.2 wiki/log.md

```markdown
# Wiki Log

## [YYYY-MM-DD] ingest | 页面标题
- Updated: 级联更新页面1
- Updated: 级联更新页面2

## [YYYY-MM-DD] query | Archived: 归档页面标题

## [YYYY-MM-DD] lint | N issues found, M applied

## [YYYY-MM-DD] schema | 变更描述
```

- 只能追加，不能修改历史记录
- 可用 `grep "^## \[" wiki/log.md | tail -5` 查看最近 5 条

---

## 7. TRAE 配置规格

### 7.1 Rules（持续加载）

`.trae/rules/project_rules.md`：
- 身份定义
- 权限规则
- 目录结构
- Wiki 页面格式
- 操作触发词映射
- 索引与日志规范

**约束**：控制在 ~80 行以内，详细流程放 Skills。

### 7.2 Skills（按需加载）

| Skill | 触发词 | 说明 |
|-------|--------|------|
| ingest | 处理、摄入、ingest | 摄入新素材 |
| query | 查询、搜索、query | 查询知识库 |
| archive | 归档、保存、archive | 归档查询结果 |
| lint | lint、检查、维护 | 健康检查 |

### 7.3 Agents（隔离上下文）

| Agent | 用途 | 模型建议 |
|-------|------|----------|
| wiki-health-reporter | 生成健康报告 | sonnet（更便宜） |

### 7.4 Tasks

| Task | 命令 | 说明 |
|------|------|------|
| Wiki: 验证配置 | verify-config.py | 检查所有配置文件 |
| Wiki: 初始化示例数据 | init-examples.sh | 创建 3 篇示例素材 |
| Wiki: 执行确定性 Lint | lint-deterministic.py | Layer 1 检查 |

### 7.5 Settings

- `files.watcherExclude`：排除 pending/、__pycache__/
- `search.exclude`：同上
- `trae.ai.codeIndex.enabled`：启用代码索引
- `trae.rules.autoLoad`：自动加载规则

---

## 8. OpenClaw 配置规格

### 8.1 权限

- ✅ 读取所有文件
- ❌ 写入任何文件

### 8.2 上下文入口

`openclaw-context.md`：
- 知识库路径表
- 使用规则
- 查询流程
- 定时任务示例

### 8.3 定时任务

| 任务 | 频率 | 说明 |
|------|------|------|
| 每日简报 | 每天 8:00 | 读取 index.md，生成工作简报 |
| 素材监控 | 每 2 小时 | 检测 raw/ 新文件，通知用户 |

---

## 9. 部署规格

### 9.1 环境要求

| 组件 | 版本 | 用途 |
|------|------|------|
| TRAE IDE | v3.0+ | AI 知识库管理 |
| Obsidian | 最新版 | 知识库查看和编辑 |
| OpenClaw | 已安装 | 定时任务和只读查询 |
| Python | 3.8+ | Lint 脚本 |
| Git | 任意 | 版本控制 |

### 9.2 部署步骤

1. 克隆仓库
2. 在 TRAE 中打开项目
3. 运行验证 Task
4. 初始化示例数据
5. 配置 Obsidian（Dataview + Web Clipper）
6. 配置 OpenClaw（可选）

### 9.3 验证清单

- [ ] verify-config.py 所有检查通过
- [ ] TRAE 对话中"你是什么角色？"回答知识库管理员
- [ ] Ingest 示例素材成功创建 wiki 页面
- [ ] Obsidian 图谱视图显示知识关联
- [ ] Lint 脚本正常运行

---

## 10. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-04-13 | 初始方案（单体 CLAUDE.md） |
| v2.0 | 2026-04-13 | 修正 Karpathy 原则偏差（级联更新、矛盾标注、Archive） |
| v3.0 | 2026-04-14 | TRAE 原生适配（.trae/ 体系）+ 产品化优化 + 开源发布 |
