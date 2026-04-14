#!/bin/bash
# 初始化示例数据脚本
# 注意：此脚本只创建 raw/ 素材，不创建 wiki 页面
# wiki 页面由用户通过 TRAE 的 Ingest 流程自行创建

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 初始化 LLM Wiki 示例素材..."
echo ""

# 检查是否已有数据
if [ -d "$PROJECT_ROOT/raw/demo" ]; then
    echo "⚠️  raw/demo/ 目录已存在，跳过初始化。"
    echo "   如果想重新初始化，请先删除 raw/demo/ 和 wiki/demo/ 目录。"
    exit 0
fi

# 创建示例 raw 文件
echo "📄 创建示例素材（共 3 篇）..."
echo ""

mkdir -p "$PROJECT_ROOT/raw/demo"

# 素材 1：Karpathy 原文介绍
cat > "$PROJECT_ROOT/raw/demo/2026-04-04-karpathy-llm-wiki.md" << 'EOF'
---
source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
collected: 2026-04-13
published: 2026-04-04
---

# LLM Wiki - Andrej Karpathy

A pattern for building personal knowledge bases using LLMs.

## The core idea

Instead of just retrieving from raw documents at query time, the LLM **incrementally builds and maintains a persistent wiki** — a structured, interlinked collection of markdown files that sits between you and the raw sources.

The key difference: **the wiki is a persistent, compounding artifact.** The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read.

## Architecture

Three layers:
- **Raw sources** — immutable source documents
- **The wiki** — LLM-generated markdown files, the LLM owns this layer
- **The schema** — tells the LLM how the wiki is structured

## Operations

- **Ingest**: drop a new source, LLM compiles it into wiki, updates cross-references
- **Query**: ask questions, LLM reads wiki and synthesizes answers
- **Lint**: health-check for contradictions, orphans, gaps

A single source might touch 10-15 wiki pages through cascade updates.
EOF

echo "  ✓ 2026-04-04-karpathy-llm-wiki.md"

# 素材 2：社区实践（与素材 1 互补，展示具体实现）
cat > "$PROJECT_ROOT/raw/demo/2026-04-10-community-wiki-implementation.md" << 'EOF'
---
source: https://github.com/Astro-Han/karpathy-llm-wiki
collected: 2026-04-13
published: 2026-04-10
---

# Karpathy LLM Wiki 社区实现

社区基于 Karpathy 的 LLM Wiki 模式开发的完整实现方案。

## 关键设计决策

### 目录结构
- raw/ — 按主题分子目录存放原始素材
- wiki/ — 编译后的知识文章，只允许一级深度
- wiki/index.md — 全局索引
- wiki/log.md — 操作日志

### Cascade Updates（级联更新）
当摄入新素材时，不仅创建主页面，还要：
1. 扫描同 topic 目录下的所有页面
2. 扫描 index.md 中其他 topic 的条目
3. 对每个受影响的页面进行实质性修改
4. 每个修改的页面刷新 updated 日期

### 矛盾标注
如果新素材与已有内容冲突：
- 在两个相关页面中都标注矛盾
- 附带来源归属
- 不自行裁决，让人类判断

### Lint 分层
- 确定性检查：索引一致性、链接完整性、引用完整性
- 语义分析：矛盾检测、过时内容、知识缺口

## 实践经验

- 前 5-10 篇素材是调校期，之后流程会越来越顺畅
- Schema 需要你和 LLM 共同演进
- index.md 在中等规模（~100 篇素材）下效果很好，无需 RAG 基础设施
EOF

echo "  ✓ 2026-04-10-community-wiki-implementation.md"

# 素材 3：不同观点（与素材 1、2 有部分矛盾，用于展示矛盾标注）
cat > "$PROJECT_ROOT/raw/demo/2026-04-12-critique-llm-wiki.md" << 'EOF'
---
source: https://example.com/blog/critique-llm-wiki
collected: 2026-04-13
published: 2026-04-12
---

# LLM Wiki 的局限性与改进方向

对 Karpathy LLM Wiki 模式的批判性分析。

## 主要局限

### 1. 上下文窗口限制
Karpathy 声称 index.md 在中等规模下效果很好，但实际上当 wiki 超过 200 篇页面时，index.md 本身会变得过长，LLM 难以在一次读取中有效定位相关内容。此时需要引入向量搜索等 RAG 技术。

### 2. LLM 幻觉风险
让 LLM 全权维护 wiki 意味着它可能在编译过程中引入幻觉——比如将不同来源的信息错误地合并，或者创建实际上不存在于原始素材中的"综合结论"。

### 3. 维护成本被低估
虽然 Karpathy 说"维护成本接近零"，但实际使用中 Schema 的调校、矛盾的人工裁决、以及 Lint 后的审阅仍然需要大量人类参与。

## 改进建议

- 在 index.md 之外引入轻量级向量搜索（如 qmd）
- 对 wiki 页面增加"置信度"标记
- 建立版本快照机制，方便回滚 LLM 的错误修改
EOF

echo "  ✓ 2026-04-12-critique-llm-wiki.md"

echo ""
echo "✅ 示例素材创建完成！"
echo ""
echo "📁 位置：raw/demo/"
echo "   ├── 2026-04-04-karpathy-llm-wiki.md          （Karpathy 原文）"
echo "   ├── 2026-04-10-community-wiki-implementation.md （社区实现）"
echo "   └── 2026-04-12-critique-llm-wiki.md           （批判性分析）"
echo ""
echo "📝 注意：wiki 页面尚未创建。请按以下顺序在 TRAE 中体验："
echo ""
echo "   第 1 步：处理 raw/demo/2026-04-04-karpathy-llm-wiki.md"
echo "   第 2 步：处理 raw/demo/2026-04-10-community-wiki-implementation.md"
echo "            → 观察级联更新（第 1 步创建的页面会被更新）"
echo "   第 3 步：处理 raw/demo/2026-04-12-critique-llm-wiki.md"
echo "            → 观察矛盾标注（批判性观点与已有内容冲突）"
echo ""
echo "   第 4 步：在 Obsidian 中打开图谱视图，查看知识关联"
echo "   第 5 步：在 TRAE 中说「执行 Lint」，体验健康检查"
