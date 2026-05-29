"""行为树核心：Status 枚举、Node 抽象基类、Blackboard 黑板"""

from enum import Enum
from abc import ABC, abstractmethod


class Status(Enum):
    """行为树节点执行结果"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"

    def __bool__(self):
        """SUCCESS=True, FAILURE/RUNNING=False，方便直接用于 if 判断"""
        return self == Status.SUCCESS


class Blackboard(dict):
    """行为树共享数据黑板。

    继承自 dict，所有节点共享此对象来读写状态。
    推荐使用命名空间前缀避免键冲突，如 'npc/hp', 'npc/position'。
    """
    pass


class Node(ABC):
    """行为树节点抽象基类。

    所有节点（Action、Condition、Composite、Decorator）都继承此类。
    子类只需实现 tick() 方法。
    """

    def __init__(self, name: str):
        self.name = name
        self.last_status: Status | None = None  # 最近一次 tick 的执行结果

    @abstractmethod
    def tick(self, blackboard: Blackboard) -> Status:
        """执行节点逻辑，返回 SUCCESS / FAILURE / RUNNING。

        实现时应该在返回前设置 self.last_status。
        """
        ...

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"
