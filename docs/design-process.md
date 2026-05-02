# LLM Wiki 项目设计过程

> 记录从概念到实现的设计决策和演进过程。

---

## 项目背景

### 初始需求

用户希望基于 Andrej Karpathy 的 LLM Wiki 模式，构建一个个人知识库系统。

### 环境约束

- **TRAE IDE**：作为 AI 调度中心，唯一写入入口
- **Obsidian**：作为人类查看和编辑界面
- **OpenClaw**：只读访问，用于定时任务和查询
- **Git**：版本控制和协作

---

## 第一轮方案（v1.0）

### 设计思路

将 Karpathy 的 LLM Wiki 模式直接适配到 TRAE + Obsidian + OpenClaw 工作流。

### 核心架构

```
┌─────────────────────────────────────────────────┐
│   Obsidian    │     │   TRAE IDE    │
│  (人类编辑)   │     │  (AI 调度中心) │
└──────┬───────┘     └──────┬───────┘
       │ 读写                │ 读写
       └────────┬─────────────┘
                ▼
     ┌──────────────────┐
     │ LLM Wiki 仓库 │
     │ raw/  wiki/     │
     └──────────────────┘
                ▼
     ┌──────────────────┐
     │ OpenClaw        │
     │ (只读消费)     │
     └──────────────────┘
```

### 文件结构

```
my-wiki/
├── CLAUDE.md                  ← Schema（328 行，单体文件）
├── raw/                       ← 原始素材
├── wiki/                      ← 编译知识
│   ├── index.md               ← 全局索引
│   └── log.md                 ← 操作日志
├── pending/                   ← Lint 待审区
├── scripts/                   ← 辅助脚本
│   └── lint-deterministic.py  ← 确定性 Lint
└── docs/
    ├── deploy-guide.md         ← 部署指南
    └── openclaw-readonly-config.md ← OpenClaw 配置
```

### 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| Schema 文件 | CLAUDE.md | 借鉴 Karpathy 原文命名 |
| 索引位置 | wiki/ 目录内 | 参考社区实践（Astro-Han） |
| Lint 分层 | 自动 + 对话式 | Karpathy 强调的语义分析需要人在场 |
| OpenClaw 权限 | 只读 | 用户明确要求 |

---

## 第二轮审查：TRAE 兼容性分析

### 发现的问题

| 问题 | 严重程度 | 说明 |
|------|----------|------|
| CLAUDE.md 单体文件 | 🔴 高 | 328 行持续加载，浪费 token；未利用 TRAE 的 .trae/ 体系 |
| MCP 配置位置错误 | 🟡 中 | 文档中未明确写入 .trae/mcp.json |
| 缺少性能配置 | 🟡 中 | 未配置文件监控排除规则 |
| docs/ 目录干扰 | 🟢 低 | 可能被 TRAE 索引，产生噪音 |
| 内部逻辑矛盾 | 🔴 高 | CLAUDE.md 中权限规则与演进规则冲突 |

### TRAE 原生配置体系研究

通过研究掘金文章和 TRAE 官方文档，发现：

```
.trae/
├── rules/
│   ├── user_rules.md         ← 个人规则（全局）
│   └── project_rules.md      ← 项目规则（持续加载）
├── skills/
│   └── <skill-name>/
│       └── SKILL.md           ← 按需加载
├── agents/
│   └── <agent-name>.md       ← 独立 Agent（隔离上下文）
├── settings.json              ← 性能配置
├── tasks.json                ← TRAE Tasks
└── mcp.json                  ← MCP Server 配置
```

### 关键洞察

- **Rules vs Skills**：Rules 持续加载（~100 行），Skills 按需加载（关键词匹配）
- **Agents**：独立上下文，可用更便宜的模型，适合重型任务
- **Tasks**：TRAE 原生任务自动化，可替代系统 cron

---

## 第三轮审查：用户和产品视角

### 用户画像

- 已有 TRAE + OpenClaw + Obsidian 环境
- 想构建个人/工作知识库
- 对 AI 工具有基本认知，但不是专家

### 发现的体验问题

| 问题 | 影响 | 优化 |
|------|------|------|
| 入门门槛过高 | 用户在第一步可能放弃 | QUICKSTART.md + verify-config.py |
| 无示例数据 | 不知道"正确结果"长什么样 | init-examples.sh |
| CLAUDE.md 引用失效文件 | 404 错误 | 删除 CLAUDE.md，改用 .trae/rules/ |
| 示例数据太简单 | 无法体验级联更新和矛盾标注 | 提供 3 篇有关联素材 |
| OpenClaw 路径硬编码 | 知识库位置变化需逐个修改 | openclaw-context.md 统一入口 |

### 产品完整性缺失

| 缺失项 | 重要性 | 优化 |
|--------|--------|------|
| README.md | 🔴 必须 | 项目主页，5 分钟了解项目 |
| LICENSE | 🔴 必须 | MIT 开源协议 |
| .github/ 模板 | 🟡 推荐 | Issue/PR 模板 |
| dashboard.md 位置 | 🟢 低 | 移入 obsidian/ 子目录 |

---

## 第四轮方案：v3.0（最终版）

### 核心改进

| 改进项 | v1.0 → v3.0 |
|--------|-------------|
| Schema 文件 | CLAUDE.md (328 行) → .trae/rules/project_rules.md (~80 行) |
| 操作流程 | 单体文件 → 4 个 Skills（按需加载） |
| Lint | 单体 Skill → Skills + Agent（wiki-health-reporter） |
| 配置验证 | 无 → verify-config.py + TRAE Tasks |
| 示例数据 | 1 篇素材 + 1 篇 wiki → 3 篇素材（含级联和矛盾） |
| OpenClaw 配置 | 分散在多个文件 → openclaw-context.md 统一入口 |
| README | 无 → 完整项目主页 |
| 开源准备 | 无 → LICENSE + .github/ 模板 |

### 最终架构

```
┌─────────────────────────────────────────────────┐
│   Obsidian    │     │   TRAE IDE    │
│  (人类编辑)   │     │  (AI 调度中心) │
└──────┬───────┘     └──────┬───────┘
       │ 读写                │ 读写
       └────────┬─────────────┘
                ▼
     ┌──────────────────┐
     │ LLM Wiki 仓库 │
     │ raw/  wiki/     │
     └──────────────────┘
                ▼
     ┌──────────────────┐
     │ OpenClaw        │
     │ (只读消费)     │
     └──────────────────┘
```

### 最终文件结构

```
llm-wiki/
├── .trae/                        ← TRAE 原生配置
│   ├── rules/project_rules.md      ← 核心规则（~80 行，持续加载）
│   ├── skills/                   ← 操作技能（按需加载）
│   │   ├── ingest/SKILL.md       ← Ingest 操作
│   │   ├── query/SKILL.md        ← Query 操作
│   │   ├── archive/SKILL.md      ← Archive 操作
│   │   └── lint/SKILL.md         ← Lint 操作
│   ├── agents/
│   │   └── wiki-health-reporter.md ← 健康报告 Agent
│   ├── settings.json             ← 性能配置
│   └── tasks.json                ← TRAE Tasks
├── raw/                          ← 原始素材（LLM 只读）
├── wiki/                         ← 编译知识（LLM 管理）
│   ├── index.md                  ← 全局索引
│   └── log.md                    ← 操作日志
├── pending/                      ← Lint 待审区
├── scripts/                      ← 辅助脚本
│   ├── lint-deterministic.py     ← 确定性 Lint
│   ├── verify-config.py          ← 配置验证
│   └── init-examples.sh          ← 示例初始化
├── obsidian/dashboard.md          ← Obsidian 仪表盘
├── openclaw-context.md           ← OpenClaw 只读上下文
├── QUICKSTART.md                 ← 快速入门
├── README.md                     ← 项目主页
├── LICENSE                        ← MIT 协议
├── .github/                      ← GitHub 配置
│   ├── ISSUE_TEMPLATE/           ← Issue 模板
│   └── PULL_REQUEST_TEMPLATE.md   ← PR 模板
└── docs/deploy-guide.md          ← 完整部署指南
```

---

## 设计原则总结

### Karpathy 原始原则

1. **Wiki 是持久化的、复合增长的产物**
2. **LLM 全权拥有 wiki 层**
3. **Schema 是你和 LLM 共同演进的**
4. **好的查询答案应该回写**
5. **人类负责策源和提问，LLM 负责其余一切**

### TRAE 适配原则

1. **利用 .trae/ 原生体系**：Rules + Skills + Agents
2. **按需加载**：减少 context window 占用
3. **Tasks 自动化**：替代系统 cron
4. **性能优化**：配置文件监控和搜索排除

### 产品化原则

1. **开箱即用**：5 分钟快速上手
2. **配置验证**：一键检查所有配置
3. **示例数据**：立即体验完整工作流
4. **预期效果**：每步都有预期说明

---

## 关键技术决策

| 决策点 | 方案 | 理由 |
|--------|------|------|
| Schema 文件名 | .trae/rules/project_rules.md | TRAE 原生，符合约定 |
| index.md 位置 | wiki/index.md | 社区最佳实践 |
| Lint 分层 | 自动脚本 + 对话式 | Karpathy 强调语义分析需要人在场 |
| OpenClaw 权限 | 只读 | 用户明确要求 |
| 示例数据策略 | 只创建 raw，不创建 wiki | 让用户自己体验 Ingest |
| Git 分支 | main | GitHub 新标准 |

---

## 演进历程

### v1.0 → v2.0

- 修复：index.md/log.md 移入 wiki/
- 修复：Lint 分层设计
- 修复：增加级联更新和矛盾标注
- 修复：增加 Archive 操作

### v2.0 → v3.0

- 修复：CLAUDE.md 拆分为 .trae/ 体系
- 修复：增加 verify-config.py
- 修复：示例数据从 1 篇扩展到 3 篇（含级联和矛盾）
- 修复：OpenClaw 配置统一到 openclaw-context.md
- 修复：README.md + LICENSE + .github/ 模板
- 修复：dashboard.md 移入 obsidian/ 子目录

---

## 未来优化方向

| 方向 | 优先级 | 说明 |
|------|--------|------|
| GitHub Actions CI | 🟡 中 | 自动运行验证脚本和 Lint |
| 英文版 README | 🟡 中 | 扩大国际受众 |
| CONTRIBUTING.md | 🟢 低 | 社区贡献指南 |
| Release + Changelog | 🟢 低 | 版本管理 |
| Wiki 页面模板 | 🟢 低 | 在 raw/ 中提供更多领域模板 |
| TRAE MCP Server | 🟢 低 | 开发专用 MCP Server 替代文件系统操作 |

---

## 致谢

- Andrej Karpathy — 提出 LLM Wiki 模式
- Astro-Han — 社区最佳实践参考
- TRAE IDE 团队 — 提供 AI 原生开发环境
- Obsidian 团队 — 提供知识库查看工具
- OpenClaw 团队 — 提供 AI 助手和定时任务
