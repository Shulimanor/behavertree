"""教程 08：NPC AI——巡逻->发现敌人->追击->攻击

这是行为树最经典的应用场景：一个 NPC 的完整战斗 AI。

树结构：
  Selector（战斗策略：按优先级选择）
  ├── Sequence（有条件战斗）
  │   ├── Condition: 敌人可见?
  │   ├── Action: 追击敌人
  │   └── Action: 攻击敌人
  └── Action: 巡逻（兜底行为，敌人不在时执行）

执行逻辑：
  - 每 tick，Selector 先尝试「有条件战斗」分支
  - 如果敌人可见 -> 进入追击->攻击 Sequence
  - 如果敌人不可见 -> Condition 失败 -> 整个 Sequence 失败
  - Selector 转而执行「巡逻」
  - 巡逻完毕（SUCCESS），下一 tick 重新从头判断

这就是游戏 AI 中「每帧检查->条件决定行为」的核心模式。
"""

from behave_tree import (
    Status, Action, Condition,
    Sequence, Selector,
    Blackboard, StepExecutor
)


# ─── 条件节点 ───

def is_enemy_visible(bb: Blackboard) -> bool:
    visible = bb.get("npc/can_see_enemy", False)
    if visible:
        print("    [感知] 发现敌人！")
    else:
        print("    [感知] 视野内没有敌人")
    return visible


def is_in_attack_range(bb: Blackboard) -> bool:
    dist = bb.get("enemy/distance", 100)
    in_range = dist <= 2
    if in_range:
        print(f"    [判断] 距离 {dist}m，进入攻击范围！")
    else:
        print(f"    [判断] 距离 {dist}m，还没到攻击范围")
    return in_range


# ─── 动作节点 ───

def patrol_action(bb: Blackboard) -> Status:
    wp = bb.get("patrol/waypoint", 0) + 1
    bb["patrol/waypoint"] = wp
    print(f"    [巡逻] 走向路点 {wp}...")
    # 巡逻中偶尔"发现"敌人
    if wp >= 3:
        print("    [巡逻] 发现远处有什么在动！")
        bb["npc/can_see_enemy"] = True
        bb["enemy/distance"] = 10
        bb["patrol/waypoint"] = 0
        return Status.SUCCESS
    return Status.SUCCESS


def chase_enemy(bb: Blackboard) -> Status:
    dist = bb.get("enemy/distance", 10)
    dist -= 3
    bb["enemy/distance"] = max(0, dist)
    print(f"    [追击] 冲向敌人！剩余距离: {dist}m")
    if dist <= 2:
        print("    [追击] 追上敌人！准备攻击！")
        return Status.SUCCESS
    return Status.RUNNING


def attack_enemy(bb: Blackboard) -> Status:
    hp = bb.get("enemy/hp", 10)
    hp -= 4
    bb["enemy/hp"] = hp
    print(f"    [攻击] 斩击！敌人 HP: {hp}")
    if hp <= 0:
        print("    [攻击] 敌人被击败！")
        bb["npc/can_see_enemy"] = False
        bb["enemy/distance"] = 999
        return Status.SUCCESS
    return Status.SUCCESS


def run():
    print("""
┌──────────────────────────────────────────────────────────┐
│              教程 08：NPC 战斗 AI                         │
│                                                          │
│  经典行为树 NPC AI 结构：                                 │
│                                                          │
│  Selector                                               │
│  ├── Sequence (战斗)                                     │
│  │   ├── [Condition] 敌人在视野?                          │
│  │   ├── [Action] 追击                                   │
│  │   └── [Action] 攻击                                   │
│  └── [Action] 巡逻 (兜底)                                │
│                                                          │
│  每 tick 从 Selector 开始：                               │
│    有敌人 -> 走战斗分支 -> 追击->攻击                        │
│    没敌人 -> 走巡逻 -> 下一 tick 重新判断                   │
└──────────────────────────────────────────────────────────┘
""")

    bb = Blackboard()
    bb["npc/can_see_enemy"] = False
    bb["enemy/hp"] = 10
    bb["patrol/waypoint"] = 0

    npc_ai = Selector("NPC 行为", [
        Sequence("战斗", [
            Condition("敌人在视野?", is_enemy_visible),
            Action("追击敌人", chase_enemy),
            Action("攻击敌人", attack_enemy),
        ]),
        Action("巡逻", patrol_action),
    ])

    print(">>  完整 NPC AI 执行演示：巡逻 -> 发现敌人 -> 追击 -> 攻击\n")

    executor = StepExecutor(npc_ai, bb)
    executor.run_step_by_step(max_ticks=15, title="NPC AI: 巡逻->发现->追击->攻击->击杀")

    print("""
┌──────────────────────────────────────────────────────────┐
│  关键要点：                                               │
│  1. Selector 提供优先级决策：                           │
│     战斗（高优先）-> 巡逻（兜底）                          │
│  2. Sequence 确保战斗步骤按顺序执行                       │
│  3. RUNNING 状态让追击跨越多个 tick                       │
│  4. 黑板记录"敌人距离"、"能否看到敌人"等状态              │
│                                                          │
│  这就是几乎所有游戏 AI 的基础架构！                       │
└──────────────────────────────────────────────────────────┘
""")
