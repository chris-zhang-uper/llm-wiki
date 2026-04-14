#!/usr/bin/env python3
"""
配置验证脚本

检查知识库配置是否正确：
- 目录结构完整性
- TRAE 配置文件存在性
- Skills 文件格式正确性
"""

import os
import sys
from pathlib import Path

# 颜色输出
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check(name: str, condition: bool) -> bool:
    """检查条件并输出结果"""
    status = f"{GREEN}✓{RESET}" if condition else f"{RED}✗{RESET}"
    print(f"  {status} {name}")
    return condition

def main():
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("=" * 50)
    print("🔍 LLM Wiki 配置验证")
    print("=" * 50)

    all_passed = True

    # 1. 目录结构
    print("\n📁 目录结构")
    all_passed &= check("raw/ 目录存在", Path("raw").exists())
    all_passed &= check("wiki/ 目录存在", Path("wiki").exists())
    all_passed &= check("pending/ 目录存在", Path("pending").exists())
    all_passed &= check("scripts/ 目录存在", Path("scripts").exists())

    # 2. TRAE 配置
    print("\n⚙️ TRAE 配置")
    all_passed &= check(".trae/rules/project_rules.md 存在", Path(".trae/rules/project_rules.md").exists())
    all_passed &= check(".trae/tasks.json 存在", Path(".trae/tasks.json").exists())
    all_passed &= check(".trae/settings.json 存在", Path(".trae/settings.json").exists())

    # 3. Skills
    print("\n🎯 Skills")
    for skill in ["ingest", "query", "archive", "lint"]:
        skill_path = Path(f".trae/skills/{skill}/SKILL.md")
        all_passed &= check(f"skills/{skill}/SKILL.md 存在", skill_path.exists())

    # 4. Agents
    print("\n🤖 Agents")
    all_passed &= check("agents/wiki-health-reporter.md 存在", Path(".trae/agents/wiki-health-reporter.md").exists())

    # 5. Wiki 核心文件
    print("\n📝 Wiki 核心文件")
    all_passed &= check("wiki/index.md 存在", Path("wiki/index.md").exists())
    all_passed &= check("wiki/log.md 存在", Path("wiki/log.md").exists())

    # 6. Git 配置
    print("\n📦 Git 配置")
    all_passed &= check(".gitignore 存在", Path(".gitignore").exists())
    all_passed &= check("pending/ 已被忽略", "pending/" in Path(".gitignore").read_text() if Path(".gitignore").exists() else False)

    # 总结
    print("\n" + "=" * 50)
    if all_passed:
        print(f"{GREEN}✓ 所有检查通过！知识库配置正确。{RESET}")
        return 0
    else:
        print(f"{RED}✗ 部分检查未通过，请检查上述项目。{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
