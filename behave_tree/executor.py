"""逐步交互执行引擎——让用户按 Enter 逐步观察行为树的 tick 过程"""

from .core import Node, Status, Blackboard
from .renderer import print_tree

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_CYAN = "\033[96m"
_GREEN = "\033[92m"
_RED = "\033[91m"


class StepExecutor:
    """逐步执行器。

    每个 tick：
    1. 对根节点执行一次 tick
    2. 遍历整棵树收集每个节点的 last_status
    3. 用颜色渲染树，展示每个节点的最新状态
    4. 等待用户按 Enter 进入下一 tick
    """

    def __init__(self, root: Node, blackboard: Blackboard):
        self.root = root
        self.blackboard = blackboard
        self.tick_count = 0

    def _collect_statuses(self, node: Node) -> dict[str, Status | None]:
        """递归遍历树，收集所有节点的 last_status"""
        result = {node.name: node.last_status}
        children = []
        if hasattr(node, 'children'):
            children = node.children
        elif hasattr(node, 'child'):
            children = [node.child]
        for child in children:
            result.update(self._collect_statuses(child))
        return result

    def run_step_by_step(self, max_ticks: int = 20, title: str = ""):
        """逐步执行行为树。

        Args:
            max_ticks: 最大 tick 次数（防止无限循环）
            title: 教程标题
        """
        if title:
            print(f"\n{_BOLD}{_CYAN}{'=' * 60}{_RESET}")
            print(f"{_BOLD}{_CYAN}  {title}{_RESET}")
            print(f"{_BOLD}{_CYAN}{'=' * 60}{_RESET}\n")

        print(f"{_DIM}按 Enter 执行下一 tick  |  输入 q 退出  |  输入 r 连续运行到结束{_RESET}\n")

        # 先展示初始树状态（所有节点无状态）
        print(f"{_BOLD}--- 行为树结构 ---{_RESET}")
        print_tree(self.root, {})
        print(f"\n{_DIM}黑板初始状态: {dict(self.blackboard)}{_RESET}\n")

        while self.tick_count < max_ticks:
            print(f"\n{_BOLD}--- Tick {self.tick_count + 1} ---{_RESET}")

            # 执行一次 tick
            root_status = self.root.tick(self.blackboard)

            # 收集所有节点的最终状态
            status_map = self._collect_statuses(self.root)

            # 打印黑板
            print(f"{_DIM}黑板: {dict(self.blackboard)}{_RESET}\n")

            # 渲染带颜色状态的树
            print_tree(self.root, status_map)
            print()

            self.tick_count += 1

            if root_status != Status.RUNNING:
                color = _GREEN if root_status == Status.SUCCESS else _RED
                print(f"{color}{_BOLD}树执行结束: {root_status.value}{_RESET}\n")
                break

            user_input = input(">>> ").strip().lower()
            if user_input == 'q':
                print("退出教程。")
                return
            if user_input == 'r':
                print(f"{_DIM}连续运行模式...{_RESET}\n")
                self._run_continuous(max_ticks - self.tick_count)
                return

        if self.tick_count >= max_ticks:
            print(f"{_RED}达到最大 tick 次数 ({max_ticks})，停止。{_RESET}")

    def _run_continuous(self, remaining: int):
        """连续运行模式——不再等待用户输入，直到树执行结束"""
        for _ in range(remaining):
            status = self.root.tick(self.blackboard)
            self.tick_count += 1
            if status != Status.RUNNING:
                status_map = self._collect_statuses(self.root)
                print(f"{_DIM}黑板: {dict(self.blackboard)}{_RESET}\n")
                print_tree(self.root, status_map)
                print()
                color = _GREEN if status == Status.SUCCESS else _RED
                print(f"{color}{_BOLD}树执行结束: {status.value} (共 {self.tick_count} ticks){_RESET}\n")
                return
        print(f"{_RED}达到最大 tick 次数。{_RESET}")
