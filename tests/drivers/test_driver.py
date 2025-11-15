"""
测试驱动（Test Driver）
作用：提供统一的测试执行框架，自动化测试流程
在全项目中的作用：这是测试驱动，用于批量执行测试用例，生成测试报告，确保测试的一致性和可重复性
"""

import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestDriver:  # pytest: disable=no-member
    """测试驱动类"""
    
    def __init__(self, test_dir: str = "tests"):
        """
        初始化测试驱动
        :param test_dir: 测试目录路径
        """
        self.test_dir = test_dir
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0
            }
        }
    
    def run_all_tests(self) -> dict:
        """运行所有测试"""
        print("=" * 60)
        print("开始运行测试套件")
        print("=" * 60)
        
        # 使用pytest运行测试
        try:
            result = subprocess.run(
                ['pytest', self.test_dir, '-v', '--tb=short'],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            
            # 解析输出
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                print(line)
            
            # 记录结果
            self.results['summary']['total'] = self._count_tests(output_lines)
            self.results['summary']['passed'] = self._count_passed(output_lines)
            self.results['summary']['failed'] = self._count_failed(output_lines)
            self.results['exit_code'] = result.returncode
            
            return self.results
            
        except Exception as e:
            print(f"测试执行出错: {e}")
            self.results['error'] = str(e)
            return self.results
    
    def _count_tests(self, lines: list) -> int:
        """统计测试总数"""
        count = 0
        for line in lines:
            if 'PASSED' in line or 'FAILED' in line:
                count += 1
        return count
    
    def _count_passed(self, lines: list) -> int:
        """统计通过的测试数"""
        count = 0
        for line in lines:
            if 'PASSED' in line:
                count += 1
        return count
    
    def _count_failed(self, lines: list) -> int:
        """统计失败的测试数"""
        count = 0
        for line in lines:
            if 'FAILED' in line:
                count += 1
        return count
    
    def generate_report(self, output_file: str = "test_report.json"):
        """生成测试报告"""
        report_path = Path(__file__).parent.parent.parent / output_file
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("测试报告摘要")
        print("=" * 60)
        print(f"总测试数: {self.results['summary']['total']}")
        print(f"通过: {self.results['summary']['passed']}")
        print(f"失败: {self.results['summary']['failed']}")
        print(f"报告已保存到: {report_path}")
        print("=" * 60)


if __name__ == "__main__":
    driver = TestDriver()
    results = driver.run_all_tests()
    driver.generate_report()

