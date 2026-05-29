"""教程 10：守卫 AI——综合利用所有节点类型

这是一个完整的守卫 AI，综合运用了所有学过的知识：

  - Condition：检测状态（敌人、血量、体力）
  - Action：执行动作（巡逻、追击、战斗、逃跑、治疗）
  - Sequence：确保动作按顺序执行
  - Selector：按优先级选择行为
  - Inverter：翻转条件（「不危险」-> 安全）
  - 黑板：共享数据

守卫行为优先级（从高到低）：
  1. 逃跑保命 -> 血量太低先跑
  2. 治疗 -> 血量不足时治疗
  3. 战斗 -> 发现敌人就战斗
  4. 巡逻 -> 以上都不成立时巡逻
"""

from behave_tree import (
    Status, Action, Condition,
    Sequence, Selector, Inverter,
    Blackboard, StepExecutor
)


# ─── 条件节点 ───

def is_enemy_visible(bb: Blackboard) -> bool:
    visible = bb.get("enemy/visible", False)
    if visible:
        print(f"    [感知] !! 发现入侵者！")
    return visible


def is_low_health(bb: Blackboard) -> bool:
    hp = bb.get("guard/hp", 100)
    low = hp < 20
    if low:
        print(f"    [检查] HP {hp} < 20 —— 血量危险！")
    return low


def is_wounded(bb: Blackboard) -> bool:
    hp = bb.get("guard/hp", 100)
    wounded = hp < 50
    if wounded:
        print(f"    [检查] HP {hp} < 50 —— 需要治疗")
    return wounded


def has_potion(bb: Blackboard) -> bool:
    potions = bb.get("guard/potions", 2)
    print(f"    [检查] 药水数量: {potions}")
    return potions > 0


# ─── 动作节点 ───

def flee(bb: Blackboard) -> Status:
    dist = bb.get("guard/flee_dist", 10)
    dist -= 5
    bb["guard/flee_dist"] = dist
    print(f"    [逃跑] 撤退！剩余逃离距离: {dist}")
    if dist <= 0:
        print("    [逃跑] 已脱战！")
        bb["enemy/visible"] = False
        bb["guard/flee_dist"] = 10
        return Status.SUCCESS
    return Status.RUNNING


def use_potion(bb: Blackboard) -> Status:
    potions = bb["guard/potions"]
    bb["guard/potions"] = potions - 1
    bb["guard/hp"] = min(100, bb["guard/hp"] + 40)
    print(f"    [治疗] 喝下药水！HP -> {bb['guard/hp']}")
    return Status.SUCCESS


def chase(bb: Blackboard) -> Status:
    dist = bb.get("enemy/distance", 8)
    dist -= 2
    bb["enemy/distance"] = max(0, dist)
    print(f"    [追击] 冲向入侵者！剩余距离: {dist}")
    if dist <= 1:
        print("    [追击] 进入交战范围！")
        return Status.SUCCESS
    return Status.RUNNING


def fight(bb: Blackboard) -> Status:
    eh = bb.get("enemy/hp", 20)
    gh = bb.get("guard/hp", 100)
    damage = 8
    eh -= damage
    bb["enemy/hp"] = eh
    # 敌人也反击
    gh -= 3
    bb["guard/hp"] = gh
    print(f"    [战斗] 守卫造成 {damage} 伤害，敌人 HP: {eh}")
    print(f"    [战斗] 守卫受到 3 伤害，HP: {gh}")
    if eh <= 0:
        print("    [战斗] 入侵者被击败！")
        bb["enemy/visible"] = False
        bb["enemy/distance"] = 8
        return Status.SUCCESS
    if gh <= 0:
        print("    [战斗] 守卫倒下了...")
        return Status.FAILURE
    return Status.SUCCESS


def patrol_action(bb: Blackboard) -> Status:
    step = bb.get("patrol/step", 0) + 1
    bb["patrol/step"] = step
    print(f"    [巡逻] 在城墙上来回踱步... ({step})")
    return Status.SUCCESS


def run():
    print("""
┌──────────────────────────────────────────────────────────┐
│              教程 10：守卫 AI —— 综合实战                │
│                                                          │
│  完整守卫 AI，综合运用了所有节点类型：                     │
│                                                          │
│  Selector（从高到低优先级）                               │
│  ├── 濒死逃跑 (血量<20)                                  │
│  ├── 治疗 (血量<50, 有药)                                │
│  ├── 战斗 (发现敌人)                                     │
│  └── 巡逻 (平安无事)                                     │
└──────────────────────────────────────────────────────────┘
""")

    bb = Blackboard()
    bb["guard/hp"] = 100
    bb["guard/potions"] = 2
    bb["enemy/visible"] = False
    bb["guard/flee_dist"] = 10
    bb["patrol/step"] = 0

    guard_ai = Selector("守卫 AI", [
        # 优先级 1：血量太低，逃跑
        Sequence("濒死逃跑", [
            Condition("血量危险?", is_low_health),
            Action("逃跑", flee),
        ]),
        # 优先级 2：血量不足，治疗
        Sequence("治疗", [
            Condition("需要治疗?", is_wounded),
            Condition("有药水?", has_potion),
            Action("喝药水", use_potion),
        ]),
        # 优先级 3：发现敌人，战斗
        Sequence("战斗", [
            Condition("有敌人?", is_enemy_visible),
            Action("追击", chase),
            Action("交战", fight),
        ]),
        # 优先级 4：平安无事，巡逻
        Action("巡逻", patrol_action),
    ])

    print(">>  守卫 AI 完整执行演示\n")
    print("   守卫从巡逻开始，中途遭遇敌人，血量下降后治疗，")
    print("   最终击败敌人，回到巡逻...\n")

    # 预设：巡逻几次后出现敌人
    # 我们用黑板来模拟敌人定时出现
    bb["enemy/visible"] = True   # 一开始就有敌人
    bb["enemy/distance"] = 6
    bb["enemy/hp"] = 20

    executor = StepExecutor(guard_ai, bb)
    executor.run_step_by_step(max_ticks=20, title="守卫 AI: 完整决策链")

    print("""
┌──────────────────────────────────────────────────────────┐
│  总结：你已学完所有行为树核心概念！                       │
│                                                          │
│  节点类型：                                               │
│    Action      — 执行动作，可能持续多 tick                │
│    Condition   — 检查条件，瞬间完成                       │
│    Sequence    — 全部成功才算成功 (AND)                   │
│    Selector    — 有一个成功就行 (OR/优先级)               │
│    Parallel    — 同时执行所有子节点                       │
│    Decorator   — 修改单个子节点行为                       │
│                                                          │
│  核心思想：                                               │
│    • 每 tick 从根节点遍历，RUNNING 实现跨 tick 行为       │
│    • 复合节点控制执行流程（短路、优先级、并行）            │
│    • 黑板提供共享数据                                    │
│    • 树结构 = 可读的决策逻辑                              │
└──────────────────────────────────────────────────────────┘
""")
