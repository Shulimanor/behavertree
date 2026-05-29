"""树形可视化渲染器——用 ANSI 颜色和 box-drawing 字符绘制行为树执行状态"""

from .core import Node, Status
from .composites import Sequence, Selector, Parallel
from .decorators import Inverter, Repeater, UntilFail, UntilSuccess
from .leaves import Action, Condition

# ANSI 颜色代码
_RESET = "\033[0m"
_GREEN = "\033[92m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_CYAN = "\033[96m"
_DIM = "\033[2m"


def _status_color(status: Status | None) -> str:
    if status is None:
        return _DIM
    if status == Status.SUCCESS:
        return _GREEN
    if status == Status.FAILURE:
        return _RED
    return _YELLOW  # RUNNING


def _status_text(status: Status | None) -> str:
    if status is None:
        return "-"
    return status.value


def _node_type_label(node: Node) -> str:
    """返回节点类型简写标签"""
    mapping = {
        Sequence: "->",       # 顺序（箭头表示单向流程）
        Selector: "?",       # 选择（问号表示尝试）
        Parallel: "||",       # 并行
        Inverter: "NOT",       # 取反
        Repeater: "R",       # 重复
        UntilFail: "~F",
        UntilSuccess: "~S",
        Action: "",        # 动作
        Condition: "?",      # 条件
    }
    for cls, label in mapping.items():
        if isinstance(node, cls):
            return label
    return "?"


def render_tree(node: Node, status_map: dict[str, Status | None] = None,
                prefix: str = "", is_last: bool = True, depth: int = 0) -> list[str]:
    """递归生成行为树的文本渲染行。

    Args:
        node: 当前节点
        status_map: 节点名 -> 执行状态的映射
        prefix: 当前行的缩进前缀
        is_last: 当前节点是否为同级最后一个
        depth: 当前深度（根节点深度为 0）

    Returns:
        字符串列表，每个元素是一行
    """
    if status_map is None:
        status_map = {}

    lines = []
    node_status = status_map.get(node.name)

    # 选择连接符
    if depth == 0:
        connector = ""
    elif is_last:
        connector = "└── "
    else:
        connector = "├── "

    # 类型标签和状态
    type_label = _node_type_label(node)
    color = _status_color(node_status)
    status_str = _status_text(node_status)

    # 额外信息（如 Repeater 的次数）
    extra = ""
    if isinstance(node, Repeater):
        extra = f" [×{node.repeat_times}]" if node.repeat_times else ""
    elif isinstance(node, Parallel):
        extra = f" [{node.policy.value}]"

    line = f"{prefix}{connector}{color}[{type_label}] {node.name} [{status_str}]{extra}{_RESET}"
    lines.append(line)

    # 递归渲染子节点
    children = []
    if hasattr(node, 'children'):
        children = node.children
    elif hasattr(node, 'child'):
        children = [node.child]

    if children:
        # 计算子节点的前缀
        if depth == 0:
            child_prefix = ""
        elif is_last:
            child_prefix = prefix + "    "
        else:
            child_prefix = prefix + "│   "

        for i, child in enumerate(children):
            child_is_last = (i == len(children) - 1)
            lines.extend(render_tree(child, status_map, child_prefix, child_is_last, depth + 1))

    return lines


def print_tree(node: Node, status_map: dict[str, Status | None] = None):
    """打印行为树"""
    lines = render_tree(node, status_map)
    for line in lines:
        print(line)
