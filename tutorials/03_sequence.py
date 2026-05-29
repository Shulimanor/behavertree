"""教程 03：Sequence 顺序节点——「全部成功」才算成功

Sequence（顺序节点，也叫序列节点）是行为树最核心的组合节点之一。

执行逻辑（AND 语义）：
  1. 从第一个子节点开始，依次执行
  2. 遇到 SUCCESS -> 继续下一个子节点
  3. 遇到 FAILURE -> 立即停止，返回 FAILURE（短路）
  4. 遇到 RUNNING -> 暂停，返回 RUNNING，下次从该子节点继续
  5. 全部子节点 SUCCESS -> 返回 SUCCESS

类比："一连串必须全部完成的步骤"
  例如：开门 = 走到门前 -> 解锁 -> 推开门
  如果"解锁"失败了，就不会再"推开门"。

短路行为：一旦某步失败，后续步骤都不会执行！
"""

from behave_tree import (
    Status, Action, Condition,
    Sequence, Blackboard, StepExecutor
)


# ─── 辅助函数 ───

def walk_to_door(bb: Blackboard) -> Status:
    dist = bb.get("dist_to_door", 5)
    print(f"    [走到门前] 距离门 {dist} 步...")
    if bb.get("is_at_door", False):
        print("    [走到门前] 已经在门前了！")
        return Status.SUCCESS
    # 模拟：每次走一步
    dist -= 1
    bb["dist_to_door"] = dist
    if dist <= 0:
        bb["is_at_door"] = True
        print("    [走到门前] 抵达门前！")
        return Status.SUCCESS
    return Status.RUNNING


def unlock(bb: Blackboard) -> Status:
    if not bb.get("door/locked", True):
        print("    [解锁] 门本来就没锁")
        return Status.SUCCESS
    if bb.get("door/has_key", False):
        print("    [解锁] 用钥匙解锁！")
        bb["door/locked"] = False
        return Status.SUCCESS
    print("    [解锁] 门锁着，没有钥匙！")
    return Status.FAILURE


def push_door(bb: Blackboard) -> Status:
    if bb.get("door/locked", True):
        print("    [推门] 推不动！门锁着！")
        return Status.FAILURE
    print("    [推门] 吱呀——门开了！")
    bb["door/opened"] = True
    return Status.SUCCESS


def is_enemy_visible(bb: Blackboard) -> bool:
    visible = bb.get("enemy/visible", False)
    print(f"    [检测敌人] {'发现敌人！' if visible else '没有敌人'}")
    return visible


def run():
    print("""
┌──────────────────────────────────────────────────────────┐
│              教程 03：Sequence 顺序节点                   │
│                                                          │
│   Sequence = "全部成功才算成功"，类 AND 逻辑              │
│                                                          │
│   执行方式：                                              │
│    子节点1 -> 子节点2 -> 子节点3 -> ...                      │
│    任何一个失败 -> 立即返回 FAILURE（短路！）               │
│    全部成功 -> 返回 SUCCESS                                │
│    遇到 RUNNING -> 暂停，下次从这里继续                    │
└──────────────────────────────────────────────────────────┘
""")

    # ─── 场景一：开门成功 ───
    print(">>  场景一：完整的开门流程（有钥匙，顺利开门）\n")

    open_tree = Sequence("开门流程", [
        Action("走到门前", walk_to_door),
        Action("解锁", unlock),
        Action("推门", push_door),
    ])
    bb1 = Blackboard()
    bb1["dist_to_door"] = 2
    bb1["door/locked"] = True
    bb1["door/has_key"] = True

    executor1 = StepExecutor(open_tree, bb1)
    executor1.run_step_by_step(max_ticks=10, title="Sequence: 开门流程（有钥匙）")

    # ─── 场景二：开门失败（没钥匙）───
    print("\n" + "─" * 60)
    print("\n>>  场景二：走到门前，但没带钥匙——Sequence 短路！\n")
    print("   注意：解锁失败后，推门动作完全不会执行！\n")

    open_tree2 = Sequence("开门流程", [
        Action("走到门前", walk_to_door),
        Action("解锁", unlock),
        Action("推门", push_door),
    ])
    bb2 = Blackboard()
    bb2["dist_to_door"] = 2
    bb2["door/locked"] = True
    bb2["door/has_key"] = False  # 没钥匙！

    executor2 = StepExecutor(open_tree2, bb2)
    executor2.run_step_by_step(max_ticks=10, title="Sequence: 开门流程（没钥匙 -> 短路！）")

    print("""
┌──────────────────────────────────────────────────────────┐
│  关键要点：                                               │
│  1. Sequence = 必须按顺序全部完成（AND 逻辑）             │
│  2. 遇到失败立即返回（短路），后面的不执行                 │
│  3. 遇到 RUNNING 保留位置，下次 tick 继续                 │
│  4. 常见用途：分步骤任务、检查后执行、前置条件验证         │
└──────────────────────────────────────────────────────────┘
""")


def build():
    """构建树并返回 Web 前端所需的数据"""
    bb = Blackboard()
    bb["dist_to_door"] = 2
    bb["door/locked"] = True
    bb["door/has_key"] = True
    root = Sequence("开门流程", [
        Action("走到门前", walk_to_door),
        Action("解锁", unlock),
        Action("推门", push_door),
    ])
    return {
        "root": root,
        "blackboard": bb,
        "title": "教程 03：Sequence 顺序节点",
        "description": "Sequence = 全部成功才算成功(AND)。按顺序执行子节点，遇到 FAILURE 立即停止(短路)，遇到 RUNNING 保留位置下次继续。",
    }
