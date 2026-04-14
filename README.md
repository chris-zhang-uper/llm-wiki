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

## 快速开始

### 前置要求

- [TRAE IDE](https://trae.ai/) v3.0+
- [Obsidian](https://obsidian.md/)（最新版）
- Python 3.8+
- Git

### 5 分钟上手

```bash
# 1. 克隆仓库
git clone https://github.com/xmas-mz/llm-wiki.git
cd llm-wiki

# 2. 在 TRAE IDE 中打开此项目
#    TRAE 会自动加载 .trae/rules/project_rules.md

# 3. 运行验证（TRAE 中按 Ctrl+Shift+P → Tasks: Run Task → Wiki: 验证配置）

# 4. 初始化示例数据（TRAE Task → Wiki: 初始化示例数据）

# 5. 体验 Ingest（在 TRAE 对话中输入）：
#    "处理 raw/demo/2026-04-04-karpathy-llm-wiki.md"
```

详细教程请阅读 [QUICKSTART.md](QUICKSTART.md)。

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
├── openclaw-context.md           # OpenClaw 只读上下文
├── QUICKSTART.md                 # 快速入门
└── docs/deploy-guide.md          # 完整部署指南
```

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

## 致谢

- [Andrej Karpathy](https://github.com/karpathy) — 提出 LLM Wiki 模式
- [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) — 社区最佳实践
- [TRAE IDE](https://trae.ai/) — AI 原生开发环境
- [Obsidian](https://obsidian.md/) — 知识库查看和编辑
- [OpenClaw](https://open-claw.me/) — AI 助手和定时任务

## License

[MIT](LICENSE)
