"""教程 07：Parallel 并行节点——同时执行多个子节点

Parallel（并行节点）在同一 tick 内执行所有子节点。

与 Sequence/Selector 的关键区别：
  - Sequence/Selector: 按顺序执行，可以"短路"
  - Parallel: 所有子节点都执行，然后在"最后"判断结果

三种成功策略：
  - ALL: 所有子节点都 SUCCESS 才算成功
  - ANY: 任意一个子节点 SUCCESS 就算成功
  - NONE_FAIL: 没有失败（全部成功或运行中）

常见用途：
  - 同时移动和播放动画
  - 同时检查多个条件
  - 战斗中的攻防同步
"""

from behave_tree import (
    Status, Action, Condition,
    Parallel, ParallelPolicy,
    Blackboard, StepExecutor
)


def update_animation(bb: Blackboard) -> Status:
    frame = bb.get("anim/frame", 0) + 1
    bb["anim/frame"] = frame
    print(f"    [动画] 播放第 {frame} 帧")
    if frame >= 3:
        print("    [动画] 动画播放完毕")
        return Status.SUCCESS
    return Status.RUNNING


def move_forward(bb: Blackboard) -> Status:
    pos = bb.get("player/pos", 0) + 1
    bb["player/pos"] = pos
    print(f"    [移动] 前进到位置 {pos}")
    if pos >= 3:
        print("    [移动] 抵达目标位置")
        return Status.SUCCESS
    return Status.RUNNING


def check_health(bb: Blackboard) -> bool:
    hp = bb.get("player/hp", 100)
    print(f"    [血量检测] HP: {hp}")
    return hp > 0


def check_mana(bb: Blackboard) -> bool:
    mana = bb.get("player/mana", 50)
    print(f"    [法力检测] Mana: {mana}")
    return mana >= 10


def can_cast_spell(bb: Blackboard) -> Status:
    print(f"    [施法] 火球术！")
    bb["player/mana"] = bb.get("player/mana", 50) - 10
    return Status.SUCCESS


def run():
    print("""
┌──────────────────────────────────────────────────────────┐
│              教程 07：Parallel 并行节点                   │
│                                                          │
│  Parallel 在同一 tick 内执行所有子节点                    │
│                                                          │
│  策略：                                                   │
│    ALL      — 所有子节点都成功                            │
│    ANY      — 任意一个成功                                │
│    NONE_FAIL — 没有一个失败（全成功或全运行中）           │
└──────────────────────────────────────────────────────────┘
""")

    # ─── 示例一：移动 + 动画同时进行 ───
    print(">>  示例一：ALL 策略——边移动边播放动画，两者都完成才算成功\n")

    bb1 = Blackboard()
    parallel_move = Parallel("边走边动", [
        Action("播放动画", update_animation),
        Action("向前移动", move_forward),
    ], policy=ParallelPolicy.ALL)

    executor1 = StepExecutor(parallel_move, bb1)
    executor1.run_step_by_step(max_ticks=10, title="Parallel ALL: 动画+移动 同步完成")

    # ─── 示例二：ALL 策略——检查多个前置条件 ───
    print("\n" + "─" * 60)
    print("\n>>  示例二：ALL 策略——检查施法条件（有血、有蓝）\n")

    bb2 = Blackboard()
    bb2["player/hp"] = 100
    bb2["player/mana"] = 50

    spell_tree = Parallel("施法前置检查", [
        Condition("有血量", check_health),
        Condition("有法力", check_mana),
    ], policy=ParallelPolicy.ALL)

    executor2 = StepExecutor(spell_tree, bb2)
    executor2.run_step_by_step(max_ticks=5,
                               title="Parallel ALL: 条件和条件同时检查")

    # ─── 示例三：有前置检查 + 动作 ───
    print("\n" + "─" * 60)
    print("\n>>  示例三：组合——先用 Parallel 检查条件，再执行动作\n")

    bb3 = Blackboard()
    bb3["player/hp"] = 100
    bb3["player/mana"] = 20

    combined = Sequence("施法", [
        Parallel("条件检查", [
            Condition("有血量", check_health),
            Condition("有法力", check_mana),
        ], policy=ParallelPolicy.ALL),
        Action("释放火球", can_cast_spell),
    ])

    executor3 = StepExecutor(combined, bb3)
    executor3.run_step_by_step(max_ticks=5,
                               title="Sequence( Parallel(条件1, 条件2), 动作 )")

    print("""
┌──────────────────────────────────────────────────────────┐
│  关键要点：                                               │
│  1. Parallel = 同时执行，不短路                           │
│  2. 适合：动画+移动、多条件同时检查                        │
│  3. 常见配方：Sequence( Parallel(条件们), Action(操作) )  │
│  4. 选择策略决定最终的成败判定方式                         │
└──────────────────────────────────────────────────────────┘
""")
