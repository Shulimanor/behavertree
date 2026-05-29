"""教程 04：Selector 选择节点——「有一个成功」就算成功

Selector（选择节点，也叫 Fallback）是 Sequence 的对偶。

执行逻辑（OR 语义）：
  1. 从第一个子节点开始，依次尝试
  2. 遇到 SUCCESS -> 立即停止，返回 SUCCESS（短路！）
  3. 遇到 FAILURE -> 继续尝试下一个子节点
  4. 遇到 RUNNING -> 暂停，返回 RUNNING，下次从该子节点继续
  5. 全部子节点都 FAILURE -> 返回 FAILURE

类比："按优先级尝试多种方案"
  例如：攻击目标 = 远程狙击 -> 近战攻击 -> 逃跑撤退
  优先尝试远程，远程做不到就换近战，近战也不行就跑路。
"""

from behave_tree import (
    Status, Action, Condition,
    Sequence, Selector,
    Blackboard, StepExecutor
)


def ranged_attack(bb: Blackboard) -> Status:
    distance = bb.get("enemy/distance", 10)
    ammo = bb.get("ammo", 3)
    print(f"    [远程攻击] 敌距 {distance}m，弹药 {ammo}")
    if distance > 50:
        print("    [远程攻击] 太远了，打不到！")
        return Status.FAILURE
    if ammo <= 0:
        print("    [远程攻击] 没弹药了！")
        return Status.FAILURE
    bb["ammo"] -= 1
    print("    [远程攻击] 砰！命中敌人！")
    return Status.SUCCESS


def melee_attack(bb: Blackboard) -> Status:
    distance = bb.get("enemy/distance", 10)
    print(f"    [近战攻击] 敌距 {distance}m")
    if distance > 3:
        print("    [近战攻击] 距离太远，够不着！")
        return Status.FAILURE
    print("    [近战攻击] 咔嚓！重击敌人！")
    return Status.SUCCESS


def retreat(bb: Blackboard) -> Status:
    print("    [撤退] 打不过，溜了溜了...")
    bb["is_retreating"] = True
    return Status.SUCCESS


def is_enemy_alive(bb: Blackboard) -> bool:
    alive = bb.get("enemy/hp", 100) > 0
    print(f"    [检查] 敌人{'存活' if alive else '已死'}")
    return alive


def run():
    print("""
┌──────────────────────────────────────────────────────────┐
│              教程 04：Selector 选择节点                   │
│                                                          │
│   Selector = "有一个成功就行"，类 OR 逻辑                 │
│                                                          │
│   执行方式（按优先级尝试）：                               │
│    方案1 -> 失败？-> 方案2 -> 失败？-> 方案3                  │
│    任何一个成功 -> 立即返回 SUCCESS（短路！）               │
│    全部失败 -> 返回 FAILURE                                │
└──────────────────────────────────────────────────────────┘
""")

    # ─── 场景一：远程就能打 ───
    print(">>  场景一：敌人在射程内，第一选择（远程）直接成功\n")

    bb1 = Blackboard()
    bb1["enemy/distance"] = 20  # 在射程内
    bb1["ammo"] = 5
    combat_tree1 = Selector("战斗策略", [
        Action("远程攻击", ranged_attack),
        Action("近战攻击", melee_attack),
        Action("撤退", retreat),
    ])
    executor1 = StepExecutor(combat_tree1, bb1)
    executor1.run_step_by_step(max_ticks=5, title="Selector: 远程攻击 (第一选择成功)")

    # ─── 场景二：远程打不到，近战解决 ───
    print("\n" + "─" * 60)
    print("\n>>  场景二：敌人太远但弹药耗尽，远程失败 -> 近战也远 -> 撤退\n")

    bb2 = Blackboard()
    bb2["enemy/distance"] = 80  # 太远
    bb2["ammo"] = 0             # 没弹药
    combat_tree2 = Selector("战斗策略", [
        Action("远程攻击", ranged_attack),
        Action("近战攻击", melee_attack),
        Action("撤退", retreat),
    ])
    executor2 = StepExecutor(combat_tree2, bb2)
    executor2.run_step_by_step(max_ticks=5,
                               title="Selector: 远程失败 -> 近战失败 -> 撤退成功")

    # ─── 场景三：近战范围内 ───
    print("\n" + "─" * 60)
    print("\n>>  场景三：敌人在近战范围，但远程先试（没弹药），近战解决\n")

    bb3 = Blackboard()
    bb3["enemy/distance"] = 2   # 近在咫尺
    bb3["ammo"] = 0             # 没弹药 -> 远程失败
    combat_tree3 = Selector("战斗策略", [
        Action("远程攻击", ranged_attack),
        Action("近战攻击", melee_attack),
        Action("撤退", retreat),
    ])
    executor3 = StepExecutor(combat_tree3, bb3)
    executor3.run_step_by_step(max_ticks=5,
                               title="Selector: 远程失败 -> 近战成功")

    print("""
┌──────────────────────────────────────────────────────────┐
│  关键要点：                                               │
│  1. Selector = 优先级策略（Fallback）                     │
│  2. 子节点按优先级排列：最好的方案排最前面                 │
│  3. 短路：一旦某个方案成功，后续方案不再考虑               │
│  4. 组合配方：Selector(尝试1, 尝试2, ..., 兜底方案)       │
└──────────────────────────────────────────────────────────┘
""")
