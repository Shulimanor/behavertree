"""教程运行器——CLI 菜单，供用户选择要学习的教程"""

import sys
import os
import importlib

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_modules():
    """动态加载以数字开头的教程模块（Python 不允许直接 import 数字开头的模块）"""
    modules = []
    names = [
        "01_basics", "02_conditions", "03_sequence", "04_selector",
        "05_decorators", "06_blackboard", "07_parallel",
        "08_npc_ai", "09_door_logic", "10_guard_ai",
    ]
    for name in names:
        mod = importlib.import_module(f"tutorials.{name}")
        modules.append(mod)
    return modules


MODULES = _load_modules()

TUTORIALS = [
    ("01", "基础知识", "状态 (SUCCESS/FAILURE/RUNNING) 和 Action 节点", MODULES[0]),
    ("02", "条件节点", "Condition 节点——判断真假", MODULES[1]),
    ("03", "Sequence", "顺序节点——全部成功才算成功 (AND)", MODULES[2]),
    ("04", "Selector", "选择节点——有一个成功就行 (OR/优先级)", MODULES[3]),
    ("05", "装饰节点", "Inverter、Repeater、UntilFail、UntilSuccess", MODULES[4]),
    ("06", "黑板", "节点间共享数据的 Blackboard", MODULES[5]),
    ("07", "Parallel", "并行节点——同时执行所有子节点", MODULES[6]),
    ("08", "NPC AI", "综合场景：巡逻->发现->追击->攻击", MODULES[7]),
    ("09", "开门逻辑", "综合场景：检查条件->多方案尝试", MODULES[8]),
    ("10", "守卫 AI", "综合场景：完整的守卫决策链", MODULES[9]),
]


def show_menu():
    print("""
╔══════════════════════════════════════════════════════════╗
║              行为树 (Behavior Tree) 交互教程             ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  行为树是游戏 AI 中最常用的决策框架。                     ║
║  从简单的巡逻守卫到复杂的战略 AI，都基于行为树。          ║
║                                                          ║
║  本教程通过 10 个渐进式示例，带你亲手体验行为树的：        ║
║    - 节点类型：Action、Condition、Composite、Decorator    ║
║    - 执行逻辑：每 tick 递归遍历树                         ║
║    - 状态流转：SUCCESS / FAILURE / RUNNING               ║
║    - 组合模式：Sequence、Selector、Parallel               ║
╚══════════════════════════════════════════════════════════╝
""")

    print("  可用教程：\n")
    for num, name, desc, _ in TUTORIALS:
        print(f"  [{num}] {name:<12} {desc}")
    print(f"\n  [q] 退出教程")
    print(f"  [a] 运行全部教程\n")


def main():
    show_menu()
    while True:
        choice = input("  请选择教程编号 (1-10, a=全部, q=退出): ").strip().lower()

        if choice == 'q':
            print("\n  感谢学习！祝你写出更聪明的 AI！\n")
            break

        if choice == 'a':
            for num, name, desc, mod in TUTORIALS:
                print(f"\n\n{'#' * 60}")
                print(f"# 教程 {num}: {name}")
                print(f"{'#' * 60}")
                mod.run()
                input(f"\n  教程 {num} 结束，按 Enter 继续下一个...")
            continue

        if choice.isdigit() and 1 <= int(choice) <= 10:
            num, name, desc, mod = TUTORIALS[int(choice) - 1]
            mod.run()
            input(f"\n  教程 {choice} 结束，按 Enter 返回菜单...")
            show_menu()
        else:
            print("  无效选择，请重新输入。")


if __name__ == "__main__":
    main()
