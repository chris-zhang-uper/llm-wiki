#!/usr/bin/env python3
"""
LLM Wiki 确定性 Lint 脚本 (Layer 1)

功能：
- 索引一致性检查：wiki/index.md 与实际文件对比
- 内部链接完整性：wiki 页面中的 [[链接]] 和 markdown 链接
- Raw 引用完整性：frontmatter 中 raw 字段指向的文件是否存在
- See Also 建议：同 topic 目录下可能缺失的交叉引用

输出：
- 结果写入 pending/lint-YYYY-MM-DD.md
- 不直接修改任何 wiki 文件

用法：
  python3 scripts/lint-deterministic.py [--wiki-dir /path/to/wiki] [--raw-dir /path/to/raw] [--pending-dir /path/to/pending]
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================
# 配置
# ============================================================
DEFAULT_WIKI_DIR = Path(__file__).parent.parent / "wiki"
DEFAULT_RAW_DIR = Path(__file__).parent.parent / "raw"
DEFAULT_PENDING_DIR = Path(__file__).parent.parent / "pending"

# ============================================================
# 工具函数
# ============================================================

def read_file(path: Path) -> str:
    """读取文件内容，不存在则返回空字符串"""
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return ""


def parse_frontmatter(content: str) -> dict:
    """解析 YAML frontmatter"""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).strip().split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            fm[key.strip()] = value.strip().strip('"\'[]')
    return fm


def extract_wiki_links(content: str) -> list[str]:
    """提取 [[wikilink]] 格式的链接"""
    return re.findall(r'\[\[([^\]]+)\]\]', content)


def extract_markdown_links(content: str) -> list[tuple[str, str]]:
    """提取 [text](path) 格式的链接，返回 [(text, path), ...]"""
    return re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)


def extract_raw_references(frontmatter: dict) -> list[str]:
    """从 frontmatter 中提取 raw 引用路径"""
    raw_val = frontmatter.get('raw', '')
    if not raw_val:
        return []
    # 处理可能的列表格式
    paths = re.findall(r'\(([^)]+)\)', raw_val)
    if not paths:
        paths = [p.strip() for p in raw_val.split(';') if p.strip()]
    return paths


# ============================================================
# 检查项
# ============================================================

def check_index_consistency(wiki_dir: Path, index_content: str) -> dict:
    """
    检查 wiki/index.md 与实际文件的一致性
    返回: {
        'missing_from_index': [相对路径列表],  # 文件存在但索引缺失
        'missing_files': [相对路径列表],        # 索引有条目但文件不存在
    }
    """
    # 收集 wiki/ 下所有实际的 .md 文件（排除 index.md 和 log.md）
    actual_files = set()
    if wiki_dir.exists():
        for md_file in wiki_dir.rglob("*.md"):
            rel = md_file.relative_to(wiki_dir)
            if str(rel) not in ("index.md", "log.md"):
                actual_files.add(str(rel))

    # 从 index.md 中提取已索引的文件路径
    indexed_files = set()
    for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', index_content):
        path = match.group(2)
        # 跳过外部链接
        if path.startswith('http') or path.startswith('#'):
            continue
        indexed_files.add(path)

    missing_from_index = sorted(actual_files - indexed_files)
    missing_files = sorted(indexed_files - actual_files)

    return {
        'missing_from_index': missing_from_index,
        'missing_files': missing_files,
    }


def check_internal_links(wiki_dir: Path) -> list[dict]:
    """
    检查 wiki 页面中的内部链接是否有效
    返回: [{'page': 相对路径, 'link': 链接文本, 'type': 'wikilink'|'markdown', 'status': 'broken'|'fixed', 'fix': 修复路径}]
    """
    issues = []
    if not wiki_dir.exists():
        return issues

    # 构建所有 wiki 文件的索引（按文件名和页面标题）
    all_files = {}  # 文件名 -> 相对路径
    title_to_path = {}  # 标题 -> 相对路径

    for md_file in wiki_dir.rglob("*.md"):
        rel = str(md_file.relative_to(wiki_dir))
        if rel in ("index.md", "log.md"):
            continue
        all_files[md_file.name] = rel
        # 尝试从内容提取标题
        content = read_file(md_file)
        title_match = re.match(r'^#\s+(.+)', content)
        if title_match:
            title_to_path[title_match.group(1).strip()] = rel

    # 检查每个页面中的链接
    for md_file in wiki_dir.rglob("*.md"):
        rel = str(md_file.relative_to(wiki_dir))
        if rel in ("index.md", "log.md"):
            continue

        content = read_file(md_file)
        frontmatter = parse_frontmatter(content)
        body = re.sub(r'^---\s*\n.*?\n---', '', content, count=1, flags=re.DOTALL)

        # 检查 [[wikilink]]
        for link_text in extract_wiki_links(body):
            # 尝试多种匹配方式
            possible_targets = [
                link_text + '.md',
                link_text.lower().replace(' ', '-') + '.md',
            ]
            found = False
            for target in possible_targets:
                # 在同目录或任意目录中查找
                for actual_path in all_files.values():
                    if actual_path.endswith(target) or actual_path.endswith('/' + target):
                        found = True
                        break
                if found:
                    break
                # 按标题匹配
                if link_text in title_to_path:
                    found = True
                    break

            if not found:
                issues.append({
                    'page': rel,
                    'link': link_text,
                    'type': 'wikilink',
                    'status': 'broken',
                })

        # 检查 markdown 链接（仅内部链接）
        for text, path in extract_markdown_links(body):
            if path.startswith('http') or path.startswith('#'):
                continue
            # 解析相对路径
            page_dir = str(Path(rel).parent)
            if page_dir == '.':
                full_path = path
            else:
                full_path = page_dir + '/' + path

            # 规范化路径
            normalized = os.path.normpath(full_path)
            if normalized not in all_files.values() and normalized not in [os.path.normpath(p) for p in all_files.values()]:
                # 尝试搜索同名文件
                target_name = Path(path).name
                matches = [p for p in all_files.values() if Path(p).name == target_name]
                if len(matches) == 1:
                    issues.append({
                        'page': rel,
                        'link': path,
                        'type': 'markdown',
                        'status': 'fixable',
                        'fix': matches[0],
                    })
                elif len(matches) == 0:
                    issues.append({
                        'page': rel,
                        'link': path,
                        'type': 'markdown',
                        'status': 'broken',
                    })
                # 多个匹配时不自动修复

    return issues


def check_raw_references(wiki_dir: Path, raw_dir: Path) -> list[dict]:
    """
    检查 wiki 页面 frontmatter 中 raw 字段引用的文件是否存在
    返回: [{'page': 相对路径, 'raw_ref': 引用路径, 'status': 'broken'|'fixable', 'fix': 修复路径}]
    """
    issues = []
    if not wiki_dir.exists() or not raw_dir.exists():
        return issues

    # 构建 raw 文件索引
    raw_files = set()
    for f in raw_dir.rglob("*"):
        if f.is_file():
            raw_files.add(str(f.relative_to(raw_dir)))

    for md_file in wiki_dir.rglob("*.md"):
        rel = str(md_file.relative_to(wiki_dir))
        if rel in ("index.md", "log.md"):
            continue

        content = read_file(md_file)
        frontmatter = parse_frontmatter(content)
        raw_refs = extract_raw_references(frontmatter)

        for ref in raw_refs:
            # 清理路径
            clean_ref = ref.strip().lstrip('./')
            # 去掉可能的 ../../raw/ 前缀，只保留 raw/ 之后的部分
            if 'raw/' in clean_ref:
                clean_ref = clean_ref.split('raw/', 1)[1]

            if clean_ref not in raw_files:
                # 尝试搜索同名文件
                target_name = Path(clean_ref).name
                matches = [f for f in raw_files if Path(f).name == target_name]
                if len(matches) == 1:
                    issues.append({
                        'page': rel,
                        'raw_ref': ref,
                        'status': 'fixable',
                        'fix': matches[0],
                    })
                else:
                    issues.append({
                        'page': rel,
                        'raw_ref': ref,
                        'status': 'broken',
                    })

    return issues


def suggest_cross_references(wiki_dir: Path) -> list[dict]:
    """
    建议同 topic 目录下可能缺失的交叉引用
    返回: [{'page1': 路径, 'page2': 路径, 'reason': 原因}]
    """
    suggestions = []
    if not wiki_dir.exists():
        return suggestions

    # 按 topic 分组
    topics = defaultdict(list)
    for md_file in wiki_dir.rglob("*.md"):
        rel = str(md_file.relative_to(wiki_dir))
        if rel in ("index.md", "log.md"):
            continue
        parts = Path(rel).parts
        if len(parts) >= 2:
            topic = parts[0]
            topics[topic].append(rel)

    # 对每个 topic 内的页面，检查是否互相引用
    for topic, pages in topics.items():
        if len(pages) < 2:
            continue

        for page in pages:
            content = read_file(wiki_dir / page)
            # 提取页面标题
            title_match = re.match(r'^#\s+(.+)', content)
            if not title_match:
                continue
            page_title = title_match.group(1).strip()

            # 提取已有链接
            existing_links = set(extract_wiki_links(content))
            existing_links.update(text for text, _ in extract_markdown_links(content))

            # 检查同 topic 的其他页面是否被引用
            for other_page in pages:
                if other_page == page:
                    continue
                other_content = read_file(wiki_dir / other_page)
                other_title_match = re.match(r'^#\s+(.+)', other_content)
                if not other_title_match:
                    continue
                other_title = other_title_match.group(1).strip()

                # 检查是否有任何关联迹象
                other_tags = parse_frontmatter(other_content).get('tags', '')
                my_tags = parse_frontmatter(content).get('tags', '')

                # 如果共享标签但未互相链接，建议添加
                shared_tags = set(other_tags.split(',')) & set(my_tags.split(','))
                shared_tags.discard('')
                if shared_tags and other_title not in existing_links and page_title not in extract_wiki_links(other_content):
                    suggestions.append({
                        'page1': page,
                        'page2': other_page,
                        'reason': f"共享标签: {', '.join(shared_tags)}",
                    })

    return suggestions


# ============================================================
# 报告生成
# ============================================================

def generate_report(index_issues: dict, link_issues: list,
                    raw_issues: list, cross_refs: list) -> str:
    """生成 Lint 报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    report = f"""# Lint 报告（确定性检查） - {today}

> 生成时间：{now}
> 此报告由 `scripts/lint-deterministic.py` 自动生成。
> **审阅完成后，在 TRAE 中说「应用 Lint 建议」即可执行修改。**

---

## 1. 索引一致性

### 1.1 文件存在但索引缺失（{len(index_issues['missing_from_index'])} 处）
"""
    if index_issues['missing_from_index']:
        for f in index_issues['missing_from_index']:
            report += f"- `{f}` — 建议添加到 index.md，Summary 可暂填 `(no summary)`\n"
    else:
        report += "_无问题_\n"

    report += f"\n### 1.2 索引有条目但文件不存在（{len(index_issues['missing_files'])} 处）\n"
    if index_issues['missing_files']:
        for f in index_issues['missing_files']:
            report += f"- `{f}` — 建议标记为 `[MISSING]`，由用户决定是否删除\n"
    else:
        report += "_无问题_\n"

    broken_links = [i for i in link_issues if i['status'] == 'broken']
    fixable_links = [i for i in link_issues if i['status'] == 'fixable']

    report += f"\n## 2. 内部链接完整性\n"
    report += f"\n### 2.1 断裂链接（{len(broken_links)} 处）\n"
    if broken_links:
        for item in broken_links:
            report += f"- **{item['page']}** 中 `{item['type']}` 链接 `{item['link']}` 无法解析\n"
    else:
        report += "_无问题_\n"

    report += f"\n### 2.2 可自动修复的链接（{len(fixable_links)} 处）\n"
    if fixable_links:
        for item in fixable_links:
            report += f"- **{item['page']}** 中 `{item['link']}` → 建议修复为 `{item['fix']}`\n"
    else:
        report += "_无问题_\n"

    broken_raw = [i for i in raw_issues if i['status'] == 'broken']
    fixable_raw = [i for i in raw_issues if i['status'] == 'fixable']

    report += f"\n## 3. Raw 引用完整性\n"
    report += f"\n### 3.1 断裂的 Raw 引用（{len(broken_raw)} 处）\n"
    if broken_raw:
        for item in broken_raw:
            report += f"- **{item['page']}** 引用了不存在的素材: `{item['raw_ref']}`\n"
    else:
        report += "_无问题_\n"

    report += f"\n### 3.2 可自动修复的 Raw 引用（{len(fixable_raw)} 处）\n"
    if fixable_raw:
        for item in fixable_raw:
            report += f"- **{item['page']}** 中 `{item['raw_ref']}` → 建议修复为 `{item['fix']}`\n"
    else:
        report += "_无问题_\n"

    report += f"\n## 4. 交叉引用建议（{len(cross_refs)} 处）\n"
    if cross_refs:
        for item in cross_refs:
            report += f"- **{item['page1']}** 和 **{item['page2']}** — {item['reason']}\n"
    else:
        report += "_无建议_\n"

    total = (len(index_issues['missing_from_index']) + len(index_issues['missing_files']) +
             len(link_issues) + len(raw_issues) + len(cross_refs))
    report += f"\n---\n**总计：{total} 个检查项**\n"
    report += "\n> ⚠️ 此报告仅包含确定性检查结果。语义分析（矛盾检测、过时内容、知识缺口）请在 TRAE 中执行「深度 Lint」。\n"

    return report


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="LLM Wiki 确定性 Lint 检查")
    parser.add_argument("--wiki-dir", type=Path, default=DEFAULT_WIKI_DIR, help="wiki 目录路径")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR, help="raw 目录路径")
    parser.add_argument("--pending-dir", type=Path, default=DEFAULT_PENDING_DIR, help="pending 输出目录路径")
    args = parser.parse_args()

    wiki_dir = args.wiki_dir
    raw_dir = args.raw_dir
    pending_dir = args.pending_dir

    # 确保目录存在
    pending_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print("🔍 LLM Wiki 确定性 Lint 检查")
    print("=" * 50)
    print(f"  Wiki 目录:    {wiki_dir}")
    print(f"  Raw 目录:     {raw_dir}")
    print(f"  Pending 目录: {pending_dir}")
    print()

    # 1. 索引一致性
    print("📋 检查索引一致性...")
    index_content = read_file(wiki_dir / "index.md")
    index_issues = check_index_consistency(wiki_dir, index_content)
    print(f"   缺失索引: {len(index_issues['missing_from_index'])} | 缺失文件: {len(index_issues['missing_files'])}")

    # 2. 内部链接
    print("🔗 检查内部链接完整性...")
    link_issues = check_internal_links(wiki_dir)
    broken = sum(1 for i in link_issues if i['status'] == 'broken')
    fixable = sum(1 for i in link_issues if i['status'] == 'fixable')
    print(f"   断裂: {broken} | 可修复: {fixable}")

    # 3. Raw 引用
    print("📁 检查 Raw 引用完整性...")
    raw_issues = check_raw_references(wiki_dir, raw_dir)
    broken_raw = sum(1 for i in raw_issues if i['status'] == 'broken')
    fixable_raw = sum(1 for i in raw_issues if i['status'] == 'fixable')
    print(f"   断裂: {broken_raw} | 可修复: {fixable_raw}")

    # 4. 交叉引用建议
    print("🔗 分析交叉引用...")
    cross_refs = suggest_cross_references(wiki_dir)
    print(f"   建议: {len(cross_refs)}")

    # 生成报告
    print("\n📝 生成报告...")
    report = generate_report(index_issues, link_issues, raw_issues, cross_refs)

    today = datetime.now().strftime("%Y-%m-%d")
    report_path = pending_dir / f"lint-{today}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"✅ 报告已写入: {report_path}")

    # 输出摘要
    total = (len(index_issues['missing_from_index']) + len(index_issues['missing_files']) +
             len(link_issues) + len(raw_issues) + len(cross_refs))
    print(f"\n📊 总计: {total} 个检查项")
    if total == 0:
        print("🎉 知识库状态良好！")


if __name__ == "__main__":
    main()
