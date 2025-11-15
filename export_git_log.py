#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导出Git日志脚本
用于生成项目文档所需的完整Git日志
"""

import subprocess
import sys
from pathlib import Path

def export_git_log():
    """导出Git日志到文件"""
    
    # 方法1：简洁格式（用于文档）
    print("正在导出Git日志...")
    
    result = subprocess.run(
        ['git', 'log', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=iso'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return
    
    # 保存详细格式
    detailed_file = Path('docs/git_log_complete.txt')
    with open(detailed_file, 'w', encoding='utf-8') as f:
        f.write("# 完整Git提交历史\n\n")
        f.write("格式: 完整哈希|作者|邮箱|日期|提交信息\n\n")
        f.write(result.stdout)
    print(f"[OK] 详细日志已保存到: {detailed_file}")
    
    # 方法2：Markdown格式（用于文档）
    result2 = subprocess.run(
        ['git', 'log', '--pretty=format:- **%h** - %s (by %an, %ar)'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    markdown_file = Path('docs/git_log_markdown.md')
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write("# Git提交历史\n\n")
        f.write("## 所有提交记录\n\n")
        f.write(result2.stdout)
    print(f"[OK] Markdown格式日志已保存到: {markdown_file}")
    
    # 方法3：表格格式（用于文档）
    result3 = subprocess.run(
        ['git', 'log', '--pretty=format:%h|%an|%ad|%s', '--date=short'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    table_file = Path('docs/git_log_table.md')
    with open(table_file, 'w', encoding='utf-8') as f:
        f.write("# Git提交历史（表格格式）\n\n")
        f.write("| 提交哈希 | 作者 | 日期 | 提交信息 |\n")
        f.write("|---------|------|------|----------|\n")
        for line in result3.stdout.strip().split('\n'):
            if line:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    f.write(f"| {parts[0]} | {parts[1]} | {parts[2]} | {parts[3]} |\n")
    print(f"[OK] 表格格式日志已保存到: {table_file}")
    
    # 方法4：简洁格式（用于文档）
    result4 = subprocess.run(
        ['git', 'log', '--pretty=format:%h - %an, %ar : %s'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    simple_file = Path('docs/git_log_simple.txt')
    with open(simple_file, 'w', encoding='utf-8') as f:
        f.write("# Git提交历史（简洁格式）\n\n")
        f.write(result4.stdout)
    print(f"[OK] 简洁格式日志已保存到: {simple_file}")
    
    print("\n所有Git日志已成功导出！")

if __name__ == "__main__":
    export_git_log()

