"""叶子节点：Action 和 Condition"""

from .core import Node, Status, Blackboard
from typing import Callable


class Action(Node):
    """行为节点——执行一个动作。

    fn 返回 Status 表示成功/失败/运行中。
    也可以直接返回 SUCCESS，通过回调内部逻辑执行动作。
    """

    def __init__(self, name: str, fn: Callable[[Blackboard], Status]):
        super().__init__(name)
        self._fn = fn

    def tick(self, blackboard: Blackboard) -> Status:
        self.last_status = self._fn(blackboard)
        return self.last_status


class Condition(Node):
    """条件节点——检查某个条件是否成立。

    fn 返回 True（视为 SUCCESS）或 False（视为 FAILURE）。
    条件节点不返回 RUNNING——条件是瞬间判断的。
    """

    def __init__(self, name: str, fn: Callable[[Blackboard], bool]):
        super().__init__(name)
        self._fn = fn

    def tick(self, blackboard: Blackboard) -> Status:
        result = self._fn(blackboard)
        self.last_status = Status.SUCCESS if result is True else Status.FAILURE
        return self.last_status
