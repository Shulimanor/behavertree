"""装饰节点：包装单个子节点，修改其行为"""

from .core import Node, Status, Blackboard


class Inverter(Node):
    """取反节点——翻转子节点的 SUCCESS 和 FAILURE，RUNNING 保持不变。

    常见用途：将「敌人不在视野内」转为「安全」，用于 Selector 中的守卫逻辑。
    """

    def __init__(self, name: str, child: Node):
        super().__init__(name)
        self.child = child

    def tick(self, blackboard: Blackboard) -> Status:
        status = self.child.tick(blackboard)
        if status == Status.SUCCESS:
            self.last_status = Status.FAILURE
        elif status == Status.FAILURE:
            self.last_status = Status.SUCCESS
        else:
            self.last_status = Status.RUNNING
        return self.last_status


class Repeater(Node):
    """重复节点——重复执行子节点指定次数。

    - repeat_times: 重复次数，None 表示无限重复
    - 每次子节点结束（SUCCESS 或 FAILURE），计数器 +1
    - 子节点 RUNNING -> 返回 RUNNING
    - 达到次数后，返回最后一次子节点的状态
    """

    def __init__(self, name: str, child: Node, repeat_times: int | None = None):
        super().__init__(name)
        self.child = child
        self.repeat_times = repeat_times
        self._count = 0

    def tick(self, blackboard: Blackboard) -> Status:
        if self.repeat_times is not None and self._count >= self.repeat_times:
            self._count = 0
            self.last_status = Status.SUCCESS
            return self.last_status

        status = self.child.tick(blackboard)
        if status != Status.RUNNING:
            self._count += 1

        if self.repeat_times is not None and self._count >= self.repeat_times:
            self._count = 0
            self.last_status = status
            return self.last_status

        self.last_status = Status.RUNNING
        return self.last_status

    def reset(self):
        self._count = 0


class UntilFail(Node):
    """直到失败节点——重复执行子节点，直到子节点返回 FAILURE。

    子节点 FAILURE -> 返回 SUCCESS（「直到失败」本身成功了）
    子节点 SUCCESS -> 继续重复（返回 RUNNING）
    子节点 RUNNING -> 返回 RUNNING
    """

    def __init__(self, name: str, child: Node):
        super().__init__(name)
        self.child = child

    def tick(self, blackboard: Blackboard) -> Status:
        status = self.child.tick(blackboard)
        if status == Status.FAILURE:
            self.last_status = Status.SUCCESS
        else:
            self.last_status = Status.RUNNING
        return self.last_status


class UntilSuccess(Node):
    """直到成功节点——重复执行子节点，直到子节点返回 SUCCESS。

    子节点 SUCCESS -> 返回 SUCCESS
    子节点 FAILURE -> 继续重复（返回 RUNNING）
    子节点 RUNNING -> 返回 RUNNING
    """

    def __init__(self, name: str, child: Node):
        super().__init__(name)
        self.child = child

    def tick(self, blackboard: Blackboard) -> Status:
        status = self.child.tick(blackboard)
        if status == Status.SUCCESS:
            self.last_status = Status.SUCCESS
        else:
            self.last_status = Status.RUNNING
        return self.last_status
