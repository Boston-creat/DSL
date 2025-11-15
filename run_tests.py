#!/usr/bin/env python
"""
自动测试脚本
作用：一键运行所有测试，生成测试报告
在全项目中的作用：这是自动测试脚本，用于CI/CD流程，确保代码质量
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.drivers.test_driver import TestDriver


def main():
    """主函数"""
    print("DSL Agent 测试套件")
    print("=" * 60)
    
    driver = TestDriver()
    results = driver.run_all_tests()
    driver.generate_report("test_report.json")
    
    # 返回退出码
    exit_code = results.get('exit_code', 0)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

