#!/usr/bin/env python3
"""行为树交互教程入口

使用方法：
    python run_tutorial.py          # 显示菜单选择
    python run_tutorial.py 1        # 直接运行第 1 个教程
    python run_tutorial.py all      # 运行全部教程
"""

import sys
import os
import io

# 修复 Windows 下中文输出乱码问题
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip().lower()
        from tutorials.runner import TUTORIALS
        if arg == "all" or arg == "a":
            for num, name, desc, mod in TUTORIALS:
                print(f"\n{'#' * 60}")
                print(f"# 教程 {num}: {name}")
                print(f"{'#' * 60}")
                mod.run()
                input(f"\n  按 Enter 继续...")
        elif arg.isdigit() and 1 <= int(arg) <= 10:
            _, _, _, mod = TUTORIALS[int(arg) - 1]
            mod.run()
        else:
            print(f"无效参数: {arg}")
            print("用法: python run_tutorial.py [1-10|all]")
    else:
        from tutorials.runner import main
        main()
