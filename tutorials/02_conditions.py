"""教程 02：条件节点——判断真假

条件节点（Condition）是行为树的"眼睛"。
它检查某个条件是否成立，返回 SUCCESS（条件满足）或 FAILURE（条件不满足）。

条件节点从不返回 RUNNING——判断是瞬间完成的。

关键区别：
  - Action：做事情，可能耗时（返回 RUNNING）
  - Condition：判断状态，瞬间完成（只返回 SUCCESS/FAILURE）

本教程演示：
  - 简单条件检查
  - 条件与动作的组合
"""

from behave_tree import (
    Status, Action, Condition,
    Sequence, Selector,
    Blackboard, StepExecutor
)


def try_open_door(bb: Blackboard) -> Status:
    print("    [开门] 尝试推门...")
    if bb.get("door/locked", False):
        print("    [开门] 门锁住了！打不开！")
        return Status.FAILURE
    print("    [开门] 门没锁，轻松推开~")
    return Status.SUCCESS


def is_door_locked(bb: Blackboard) -> bool:
    locked = bb.get("door/locked", False)
    status_text = "锁住了" if locked else "没锁"
    print(f"    [检查锁] 门{status_text}")
    return locked


def unlock_door(bb: Blackboard) -> Status:
    if bb.get("door/has_key", False):
        print("    [解锁] 用钥匙打开了锁！")
        bb["door/locked"] = False
        return Status.SUCCESS
    print("    [解锁] 没有钥匙...")
    return Status.FAILURE


def run():
    print("""
┌──────────────────────────────────────────────────────────┐
│              教程 02：条件节点                            │
│                                                          │
│  Condition 节点检查某个条件：                              │
│    • 条件满足 -> SUCCESS                                  │
│    • 条件不满足 -> FAILURE                                │
│                                                          │
│  Condition 永远不返回 RUNNING——判断是瞬间的。             │
│                                                          │
│  条件节点通常和组合节点（Sequence/Selector）搭配使用。     │
└──────────────────────────────────────────────────────────┘
""")

    # 场景：门没锁，直接开门
    print(">>  场景一：门没锁，直接开门\n")
    print("   行为树: 开门(尝试推门)")
    bb1 = Blackboard()
    bb1["door/locked"] = False
    root1 = Action("开门", try_open_door)
    executor1 = StepExecutor(root1, bb1)
    executor1.run_step_by_step(max_ticks=5, title="门没锁 -> 直接成功")

    # 场景：门锁住了，没有钥匙
    print("\n" + "─" * 60)
    print("\n>>  场景二：门锁住了，没有钥匙\n")
    print("   行为树: 开门(尝试推门)")
    bb2 = Blackboard()
    bb2["door/locked"] = True
    bb2["door/has_key"] = False
    root2 = Action("开门", try_open_door)
    executor2 = StepExecutor(root2, bb2)
    executor2.run_step_by_step(max_ticks=5, title="门锁住且没钥匙 -> 失败")

    # 场景：先用条件判断门是否锁住（为后面 Sequence 教程做铺垫）
    print("\n" + "─" * 60)
    print("\n>>  场景三：用 Condition 节点检查门锁状态\n")
    print("   行为树: 检查锁(是锁住的吗?)")
    bb3 = Blackboard()
    bb3["door/locked"] = True
    root3 = Condition("检查锁", is_door_locked)
    executor3 = StepExecutor(root3, bb3)
    executor3.run_step_by_step(max_ticks=5, title="Condition: 门锁住 -> SUCCESS (条件成立)")

    print("""
┌──────────────────────────────────────────────────────────┐
│  关键要点：                                               │
│  1. Condition 返回 SUCCESS = 条件成立（门锁了）           │
│  2. Condition 返回 FAILURE = 条件不成立（门没锁）         │
│  3. Condition 是行为树的"决策依据"                        │
│                                                          │
│  下一个教程会展示如何把 Condition 和 Action 组合起来！     │
└──────────────────────────────────────────────────────────┘
""")


def build():
    """构建树并返回 Web 前端所需的数据"""
    bb = Blackboard()
    bb["door/locked"] = True
    bb["door/has_key"] = True
    root = Condition("检查锁", is_door_locked)
    return {
        "root": root,
        "blackboard": bb,
        "title": "教程 02：条件节点",
        "description": "Condition 检查布尔条件，返回 SUCCESS(条件成立) 或 FAILURE(条件不成立)，永不返回 RUNNING。",
    }
