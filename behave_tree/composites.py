"""组合节点：Sequence、Selector、Parallel"""

from .core import Node, Status, Blackboard
from enum import Enum


class Sequence(Node):
    """顺序节点——按顺序执行子节点，「所有都成功」才算成功。

    执行逻辑（类 AND）：
    1. 依次 tick 子节点
    2. 遇到第一个 FAILURE -> 立即返回 FAILURE
    3. 遇到 RUNNING -> 记录位置，返回 RUNNING，下次从这个子节点继续
    4. 全部 SUCCESS -> 返回 SUCCESS

    常见用途：一连串必须全部完成的任务，如打开门=走到门前->解锁->推门。
    """

    def __init__(self, name: str, children: list[Node]):
        super().__init__(name)
        self.children = children
        self._running_index = 0

    def tick(self, blackboard: Blackboard) -> Status:
        for i in range(self._running_index, len(self.children)):
            child = self.children[i]
            status = child.tick(blackboard)
            if status == Status.FAILURE:
                self._running_index = 0
                self.last_status = Status.FAILURE
                return self.last_status
            if status == Status.RUNNING:
                self._running_index = i
                self.last_status = Status.RUNNING
                return self.last_status
        self._running_index = 0
        self.last_status = Status.SUCCESS
        return self.last_status

    def reset(self):
        self._running_index = 0


class Selector(Node):
    """选择节点——按顺序尝试子节点，「有一个成功」就算成功。

    执行逻辑（类 OR，也叫 Fallback）：
    1. 依次 tick 子节点
    2. 遇到第一个 SUCCESS -> 立即返回 SUCCESS
    3. 遇到 RUNNING -> 记录位置，返回 RUNNING，下次从这个子节点继续
    4. 全部 FAILURE -> 返回 FAILURE

    常见用途：按优先级尝试多种方案，如攻击=远程攻击->近战攻击->逃跑。
    """

    def __init__(self, name: str, children: list[Node]):
        super().__init__(name)
        self.children = children
        self._running_index = 0

    def tick(self, blackboard: Blackboard) -> Status:
        for i in range(self._running_index, len(self.children)):
            child = self.children[i]
            status = child.tick(blackboard)
            if status == Status.SUCCESS:
                self._running_index = 0
                self.last_status = Status.SUCCESS
                return self.last_status
            if status == Status.RUNNING:
                self._running_index = i
                self.last_status = Status.RUNNING
                return self.last_status
        self._running_index = 0
        self.last_status = Status.FAILURE
        return self.last_status

    def reset(self):
        self._running_index = 0


class ParallelPolicy(Enum):
    """并行节点的成功条件策略"""
    ALL = "ALL"              # 所有子节点都成功
    ANY = "ANY"              # 任意一个子节点成功
    NONE_FAIL = "NONE_FAIL"  # 没有失败（全部成功或运行中）


class Parallel(Node):
    """并行节点——同时 tick 所有子节点。

    每 tick 都会依次执行所有子节点（不短路），根据 policy 决定最终状态。
    """

    def __init__(self, name: str, children: list[Node], policy: ParallelPolicy = ParallelPolicy.ALL):
        super().__init__(name)
        self.children = children
        self.policy = policy

    def tick(self, blackboard: Blackboard) -> Status:
        statuses = [child.tick(blackboard) for child in self.children]

        if self.policy == ParallelPolicy.ALL:
            if all(s == Status.SUCCESS for s in statuses):
                self.last_status = Status.SUCCESS
            elif any(s == Status.FAILURE for s in statuses):
                self.last_status = Status.FAILURE
            else:
                self.last_status = Status.RUNNING
        elif self.policy == ParallelPolicy.ANY:
            if any(s == Status.SUCCESS for s in statuses):
                self.last_status = Status.SUCCESS
            elif all(s == Status.FAILURE for s in statuses):
                self.last_status = Status.FAILURE
            else:
                self.last_status = Status.RUNNING
        elif self.policy == ParallelPolicy.NONE_FAIL:
            if any(s == Status.FAILURE for s in statuses):
                self.last_status = Status.FAILURE
            elif all(s == Status.SUCCESS for s in statuses):
                self.last_status = Status.SUCCESS
            else:
                self.last_status = Status.RUNNING
        else:
            self.last_status = Status.FAILURE

        return self.last_status
