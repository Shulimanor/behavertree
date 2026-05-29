"""教程 09：开门逻辑——条件判断 + 多方案尝试

这是一个经典的日常生活场景，展示了 Selector 的优先级决策能力。

树结构：
  Sequence (开门)
  ├── Action: 走到门前
  └── Selector (尝试开门的方式，按优先级)
      ├── Sequence (直接推开)
      │   └── [Condition] 门没锁？
      ├── Sequence (用钥匙)
      │   ├── [Condition] 有钥匙？
      │   └── [Action] 解锁
      ├── Sequence (撞门)
      │   ├── [Condition] 足够强壮？
      │   └── [Action] 撞开
      └── [Action] 放弃 (兜底)

体现了行为树的灵活性：
  - Sequence 用于「必须完成的步骤」（先走到门前）
  - Selector 用于「多种尝试方式」（推->解锁->撞->放弃）
  - Condition 用于「判断是否有能力」（有钥匙吗？强壮吗？）
"""

from behave_tree import (
    Status, Action, Condition,
    Sequence, Selector,
    Blackboard, StepExecutor
)


def walk_to_door(bb: Blackboard) -> Status:
    dist = bb.get("dist_to_door", 3)
    dist -= 1
    bb["dist_to_door"] = dist
    print(f"    [走到门前] 距离: {dist}")
    if dist <= 0:
        print("    [走到门前] 已站在门前")
        return Status.SUCCESS
    return Status.RUNNING


def is_unlocked(bb: Blackboard) -> bool:
    locked = bb.get("door/locked", True)
    print(f"    [检查] {'门没锁，可以直接推' if not locked else '门是锁住的'}")
    return not locked


def push_open(bb: Blackboard) -> Status:
    print("    [推门] 吱——门轻松打开！")
    bb["door/opened"] = True
    return Status.SUCCESS


def has_key(bb: Blackboard) -> bool:
    key = bb.get("player/has_key", False)
    print(f"    [检查] {'有钥匙' if key else '没有钥匙'}")
    return key


def unlock_door(bb: Blackboard) -> Status:
    print("    [解锁] 插入钥匙，咔嗒——锁开了！")
    bb["door/locked"] = False
    return Status.SUCCESS


def is_strong(bb: Blackboard) -> bool:
    strength = bb.get("player/strength", 5)
    print(f"    [检查力气] 力气值: {strength}")
    return strength >= 8


def bash_door(bb: Blackboard) -> Status:
    print("    [撞门] 砰！！门被撞开了！")
    bb["door/locked"] = False
    bb["door/opened"] = True
    bb["player/hp"] = bb.get("player/hp", 100) - 10
    print(f"    [撞门] 肩膀很痛，HP -10")
    return Status.SUCCESS


def give_up(bb: Blackboard) -> Status:
    print("    [放弃] 打不开...被永远困在这里了...")
    return Status.FAILURE


def run():
    print("""
┌──────────────────────────────────────────────────────────┐
│              教程 09：开门逻辑                            │
│                                                          │
│  展示 Selector 的多方案优先级策略                         │
│                                                          │
│  Sequence (开门)                                         │
│  ├── 走到门前                                            │
│  └── Selector (尝试开门)                                 │
│      ├── 直接推 (门没锁?)                                │
│      ├── 解锁 (有钥匙?)                                  │
│      ├── 撞开 (有蛮力?)                                  │
│      └── 放弃                                            │
└──────────────────────────────────────────────────────────┘
""")

    # ─── 场景一：有钥匙 ───
    print(">>  场景一：走到门前，门锁着，但有钥匙 -> 解锁推门\n")

    bb1 = Blackboard()
    bb1["dist_to_door"] = 2
    bb1["door/locked"] = True
    bb1["player/has_key"] = True
    bb1["player/strength"] = 5

    door_tree_1 = Sequence("开门", [
        Action("走到门前", walk_to_door),
        Selector("尝试开门", [
            Sequence("直接推", [
                Condition("没锁?", is_unlocked),
                Action("推开", push_open),
            ]),
            Sequence("用钥匙", [
                Condition("有钥匙?", has_key),
                Action("解锁", unlock_door),
                Action("推开", push_open),
            ]),
            Sequence("撞开", [
                Condition("够强壮?", is_strong),
                Action("撞门", bash_door),
            ]),
            Action("放弃", give_up),
        ]),
    ])

    executor1 = StepExecutor(door_tree_1, bb1)
    executor1.run_step_by_step(max_ticks=10, title="开门: 有钥匙 -> 解锁 -> 推门")

    # ─── 场景二：没钥匙但强壮 ───
    print("\n" + "─" * 60)
    print("\n>>  场景二：门锁了，没钥匙，但很强壮 -> 撞开！\n")

    bb2 = Blackboard()
    bb2["dist_to_door"] = 1
    bb2["door/locked"] = True
    bb2["player/has_key"] = False
    bb2["player/strength"] = 10  # 大力士
    bb2["player/hp"] = 100

    door_tree_2 = Sequence("开门", [
        Action("走到门前", walk_to_door),
        Selector("尝试开门", [
            Sequence("直接推", [
                Condition("没锁?", is_unlocked),
                Action("推开", push_open),
            ]),
            Sequence("用钥匙", [
                Condition("有钥匙?", has_key),
                Action("解锁", unlock_door),
                Action("推开", push_open),
            ]),
            Sequence("撞开", [
                Condition("够强壮?", is_strong),
                Action("撞门", bash_door),
            ]),
            Action("放弃", give_up),
        ]),
    ])

    executor2 = StepExecutor(door_tree_2, bb2)
    executor2.run_step_by_step(max_ticks=10, title="开门: 没钥匙 -> 蛮力撞开")

    print("""
┌──────────────────────────────────────────────────────────┐
│  关键要点：                                               │
│  1. Selector 提供多层级的回退方案                          │
│  2. 子 Selector 可以再嵌套 Sequence                       │
│  3. 每个方案排列优先级：好方案靠前                         │
│  4. 树的结构清晰表达了「决策逻辑」——                     │
│     不需要读代码就能理解 NPC 会怎么尝试开门               │
└──────────────────────────────────────────────────────────┘
""")

def build():
    bb = Blackboard()
    bb["dist_to_door"] = 2
    bb["door/locked"] = True
    bb["player/has_key"] = True
    bb["player/strength"] = 5
    root = Sequence("开门", [
        Action("走到门前", walk_to_door),
        Selector("尝试开门", [
            Sequence("直接推", [
                Condition("没锁?", is_unlocked),
                Action("推开", push_open),
            ]),
            Sequence("用钥匙", [
                Condition("有钥匙?", has_key),
                Action("解锁", unlock_door),
                Action("推开", push_open),
            ]),
            Sequence("撞开", [
                Condition("够强壮?", is_strong),
                Action("撞门", bash_door),
            ]),
            Action("放弃", give_up),
        ]),
    ])
    return {
        "root": root,
        "blackboard": bb,
        "title": "教程 09：开门逻辑",
        "description": "展示 Selector 多方案回退：走到门前→尝试直接推→用钥匙→撞开→放弃。Sequence 确保步骤顺序，Selector 提供优先级选择。",
    }
