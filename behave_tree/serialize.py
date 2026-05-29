"""将行为树序列化为前端可渲染的 JSON 结构"""

from .core import Node, Status
from .composites import Sequence, Selector, Parallel, ParallelPolicy
from .decorators import Inverter, Repeater, UntilFail, UntilSuccess
from .leaves import Action, Condition


def node_type_info(node: Node) -> dict:
    """获取节点类型信息：类型名、图标、额外描述"""
    info = {"type": "Unknown", "icon": "?", "extra": ""}
    if isinstance(node, Sequence):
        info = {"type": "Sequence", "icon": "Seq", "extra": ""}
    elif isinstance(node, Selector):
        info = {"type": "Selector", "icon": "Sel", "extra": ""}
    elif isinstance(node, Parallel):
        info = {"type": "Parallel", "icon": "Par", "extra": node.policy.value}
    elif isinstance(node, Inverter):
        info = {"type": "Inverter", "icon": "Not", "extra": ""}
    elif isinstance(node, Repeater):
        info = {"type": "Repeater", "icon": "Rep", "extra": str(node.repeat_times) if node.repeat_times else "∞"}
    elif isinstance(node, UntilFail):
        info = {"type": "UntilFail", "icon": "UFail", "extra": ""}
    elif isinstance(node, UntilSuccess):
        info = {"type": "UntilSuccess", "icon": "USucc", "extra": ""}
    elif isinstance(node, Action):
        info = {"type": "Action", "icon": "Act", "extra": ""}
    elif isinstance(node, Condition):
        info = {"type": "Condition", "icon": "Cond", "extra": ""}
    return info


def status_info(status: Status | None) -> str:
    """状态转前端用的字符串"""
    if status is None:
        return "idle"
    return status.value  # "SUCCESS", "FAILURE", "RUNNING"


def node_to_dict(node: Node) -> dict:
    """递归将节点树转为字典结构"""
    info = node_type_info(node)

    result = {
        "name": node.name,
        "type": info["type"],
        "icon": info["icon"],
        "extra": info["extra"],
        "status": status_info(node.last_status),
    }

    if isinstance(node, (Sequence, Selector, Parallel)):
        result["children"] = [node_to_dict(c) for c in node.children]
    elif isinstance(node, (Inverter, Repeater, UntilFail, UntilSuccess)):
        result["children"] = [node_to_dict(node.child)]
    else:
        result["children"] = []

    return result


def blackboard_to_dict(bb) -> dict:
    """黑板数据转纯 dict（Blackboard 本身是 dict 子类）"""
    return dict(bb)
