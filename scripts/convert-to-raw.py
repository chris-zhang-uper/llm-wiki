#!/usr/bin/env python3
"""
文件格式转换脚本

将 PDF、DOCX、DOC、TXT、HTML 等非 Markdown 文件转换为 Markdown 格式，
放入 raw/ 目录供 LLM Wiki 的 Ingest 流程使用。

用法：
  python3 scripts/convert-to-raw.py <输入文件或目录> [--topic <topic>] [--output-dir <目录>]

示例：
  # 转换单个文件
  python3 scripts/convert-to-raw.py paper.pdf --topic research

  # 转换整个目录
  python3 scripts/convert-to-raw.py ./downloads/ --topic work

  # 指定输出目录
  python3 scripts/convert-to-raw.py report.docx --topic work --output-dir /path/to/my-wiki/raw
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

# ============================================================
# 配置
# ============================================================
DEFAULT_RAW_DIR = Path(__file__).parent.parent / "raw"
DEFAULT_TOPIC = "general"

SUPPORTED_EXTENSIONS = {
    '.pdf': 'PDF',
    '.docx': 'Word (DOCX)',
    '.doc': 'Word (DOC)',
    '.txt': '纯文本 (TXT)',
    '.html': 'HTML',
    '.htm': 'HTML',
    '.md': 'Markdown',
    '.markdown': 'Markdown',
}

# ============================================================
# 转换器
# ============================================================

def convert_txt(file_path: Path) -> str:
    """TXT 文件直接读取，清理格式"""
    content = file_path.read_text(encoding='utf-8', errors='replace')
    # 清理多余空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def convert_pdf(file_path: Path) -> str:
    """PDF 转 Markdown"""
    try:
        import pdfplumber
    except ImportError:
        print("  ⚠️  需要安装 pdfplumber：pip install pdfplumber --break-system-packages")
        sys.exit(1)

    text_parts = []
    with pdfplumber.open(str(file_path)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                text_parts.append(f"<!-- 第 {i+1} 页 -->\n\n{text}")
    
    if not text_parts:
        return ""
    
    return "\n\n---\n\n".join(text_parts)


def convert_docx(file_path: Path) -> str:
    """DOCX 转 Markdown"""
    try:
        from docx import Document
    except ImportError:
        print("  ⚠️  需要安装 python-docx：pip install python-docx --break-system-packages")
        sys.exit(1)

    doc = Document(str(file_path))
    md_lines = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            md_lines.append("")
            continue
        
        # 检测标题样式
        style_name = para.style.name if para.style else ""
        if "Heading 1" in style_name or "标题 1" in style_name:
            md_lines.append(f"# {text}")
        elif "Heading 2" in style_name or "标题 2" in style_name:
            md_lines.append(f"## {text}")
        elif "Heading 3" in style_name or "标题 3" in style_name:
            md_lines.append(f"### {text}")
        elif "Heading 4" in style_name or "标题 4" in style_name:
            md_lines.append(f"#### {text}")
        else:
            md_lines.append(text)
    
    # 处理表格
    for table in doc.tables:
        md_lines.append("")
        # 表头
        header = [cell.text.strip() for cell in table.rows[0].cells]
        md_lines.append("| " + " | ".join(header) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        # 表体
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            md_lines.append("| " + " | ".join(cells) + " |")
        md_lines.append("")
    
    return "\n".join(md_lines)


def convert_doc(file_path: Path) -> str:
    """DOC 转 Markdown（通过 LibreOffice 或 antiword）"""
    import subprocess
    import tempfile
    
    # 尝试使用 LibreOffice 转换为 DOCX，再用 docx 转换器
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                ['libreoffice', '--headless', '--convert-to', 'docx',
                 '--outdir', tmpdir, str(file_path)],
                capture_output=True, timeout=60
            )
            docx_file = Path(tmpdir) / (file_path.stem + ".docx")
            if docx_file.exists():
                return convert_docx(docx_file)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # 尝试使用 antiword
    try:
        result = subprocess.run(
            ['antiword', str(file_path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("  ⚠️  无法转换 .doc 文件。请安装以下工具之一：")
    print("     - LibreOffice: https://www.libreoffice.org/")
    print("     - antiword: sudo apt install antiword")
    print("     - 或者手动将 .doc 另存为 .docx 后重试")
    return ""


def convert_html(file_path: Path) -> str:
    """HTML 转 Markdown"""
    try:
        from html.parser import HTMLParser
    except ImportError:
        pass
    
    # 简单的 HTML → 文本转换
    content = file_path.read_text(encoding='utf-8', errors='replace')
    
    # 移除 script 和 style
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # 转换常见标签
    content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
    content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>', r'![\2](\1)', content, flags=re.IGNORECASE)
    
    # 移除所有剩余标签
    content = re.sub(r'<[^>]+>', '', content)
    
    # 解码 HTML 实体
    content = content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    
    # 清理
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def convert_markdown(file_path: Path) -> str:
    """Markdown 文件直接读取"""
    return file_path.read_text(encoding='utf-8', errors='replace')


# ============================================================
# 转换调度
# ============================================================

CONVERTERS = {
    '.txt': convert_txt,
    '.pdf': convert_pdf,
    '.docx': convert_docx,
    '.doc': convert_doc,
    '.html': convert_html,
    '.htm': convert_html,
    '.md': convert_markdown,
    '.markdown': convert_markdown,
}


def convert_file(file_path: Path, topic: str, output_dir: Path) -> Path:
    """转换单个文件为 Markdown 并保存到 raw/<topic>/"""
    ext = file_path.suffix.lower()
    
    if ext not in CONVERTERS:
        print(f"  ⚠️  跳过不支持的格式: {file_path.name} ({ext})")
        return None
    
    print(f"  📄 转换 {file_path.name} ({SUPPORTED_EXTENSIONS[ext]})...")
    
    # 执行转换
    content = CONVERTERS[ext](file_path)
    
    if not content:
        print(f"  ⚠️  转换结果为空，跳过: {file_path.name}")
        return None
    
    # 生成输出文件
    slug = re.sub(r'[^\w\u4e00-\u9fff-]+', '-', file_path.stem)[:60]
    today = datetime.now().strftime("%Y-%m-%d")
    output_name = f"{today}-{slug}.md"
    output_path = output_dir / topic / output_name
    
    # 避免文件名冲突
    counter = 2
    while output_path.exists():
        output_name = f"{today}-{slug}-{counter}.md"
        output_path = output_dir / topic / output_name
        counter += 1
    
    # 写入文件（带元数据）
    source_url = ""
    if ext == '.html' or ext == '.htm':
        source_url = file_path.as_uri()
    
    frontmatter = f"""---
source: {source_url or file_path.name}
collected: {today}
published: Unknown
original_format: {ext}
---

"""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(frontmatter + content, encoding='utf-8')
    
    print(f"  ✅ 已保存: raw/{topic}/{output_name}")
    return output_path


def convert_directory(dir_path: Path, topic: str, output_dir: Path):
    """转换目录中的所有支持的文件"""
    converted = []
    skipped = []
    
    for file_path in sorted(dir_path.rglob("*")):
        if not file_path.is_file():
            continue
        ext = file_path.suffix.lower()
        if ext in CONVERTERS:
            result = convert_file(file_path, topic, output_dir)
            if result:
                converted.append(result)
        else:
            skipped.append(file_path.name)
    
    return converted, skipped


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="将 PDF/DOCX/DOC/TXT/HTML 文件转换为 Markdown 格式，放入 raw/ 目录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支持的格式：
  .pdf    PDF 文档
  .docx   Word 文档
  .doc    Word 文档（需要 LibreOffice 或 antiword）
  .txt    纯文本
  .html   网页
  .md     Markdown（直接复制）

依赖安装：
  pip install pdfplumber python-docx --break-system-packages

示例：
  python3 scripts/convert-to-raw.py paper.pdf --topic research
  python3 scripts/convert-to-raw.py ./downloads/ --topic work
  python3 scripts/convert-to-raw.py report.docx --topic work --output-dir /path/to/wiki/raw
"""
    )
    parser.add_argument("input", help="输入文件或目录路径")
    parser.add_argument("--topic", "-t", default=DEFAULT_TOPIC, help=f"主题目录名（默认: {DEFAULT_TOPIC}）")
    parser.add_argument("--output-dir", "-o", default=str(DEFAULT_RAW_DIR), help="输出目录（默认: raw/）")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    
    if not input_path.exists():
        print(f"❌ 路径不存在: {input_path}")
        sys.exit(1)
    
    print("=" * 50)
    print("🔄 文件格式转换工具")
    print("=" * 50)
    print(f"  输入: {input_path}")
    print(f"  主题: {args.topic}")
    print(f"  输出: {output_dir}/{args.topic}/")
    print()
    
    if input_path.is_file():
        convert_file(input_path, args.topic, output_dir)
    elif input_path.is_dir():
        converted, skipped = convert_directory(input_path, args.topic, output_dir)
        print()
        print(f"✅ 转换完成: {len(converted)} 个文件")
        if skipped:
            print(f"⚠️  跳过: {len(skipped)} 个不支持的文件")
            for name in skipped[:10]:
                print(f"   - {name}")
            if len(skipped) > 10:
                print(f"   ... 还有 {len(skipped) - 10} 个")
    else:
        print(f"❌ 不支持的输入类型: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
