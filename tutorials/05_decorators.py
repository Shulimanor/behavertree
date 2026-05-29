"""教程 05：装饰节点——修改单个子节点的行为

装饰节点（Decorator）包装一个子节点，改变其返回状态。

四种核心装饰器：
  - Inverter (NOT)：取反。SUCCESS->FAILURE, FAILURE->SUCCESS
  - Repeater (R)：重复执行 n 次
  - UntilFail (~F)：重复直到子节点失败
  - UntilSuccess (~S)：重复直到子节点成功

装饰器是"语法糖"——你可以用其他节点组合实现同样效果，
但装饰器让树更简洁易读。
"""

from behave_tree import (
    Status, Action, Condition,
    Sequence, Selector,
    Inverter, Repeater, UntilFail, UntilSuccess,
    Blackboard, StepExecutor
)


def is_enemy_visible(bb: Blackboard) -> bool:
    visible = bb.get("enemy/visible", False)
    print(f"    [检测] 敌人{'在视野内' if visible else '不在视野内'}")
    return visible


def patrol(bb: Blackboard) -> Status:
    print("    [巡逻] 走来走去...")
    return Status.SUCCESS


def charge(bb: Blackboard) -> Status:
    distance = bb.get("enemy/distance", 100)
    distance -= 30
    bb["enemy/distance"] = max(0, distance)
    print(f"    [冲锋] 冲向敌人！剩余距离: {distance}")
    if distance <= 0:
        print("    [冲锋] 进入近战范围！")
        return Status.SUCCESS
    return Status.RUNNING


def attack(bb: Blackboard) -> Status:
    count = bb.get("attack/count", 0)
    bb["attack/count"] = count + 1
    print(f"    [攻击] 第 {count + 1} 次挥砍！")
    if count + 1 >= 3:
        print("    [攻击] 敌人被击败！")
        bb["enemy/hp"] = 0
        return Status.SUCCESS
    print("    [攻击] 敌人还在战斗...")
    return Status.RUNNING


def run():
    print("""
┌──────────────────────────────────────────────────────────┐
│              教程 05：装饰节点                            │
│                                                          │
│  装饰器 = 包装单个子节点，改变其行为                      │
│                                                          │
│  Inverter:    翻转 SUCCESS ↔ FAILURE                     │
│  Repeater:    重复执行 n 次                               │
│  UntilFail:   重复直到失败                                │
│  UntilSuccess: 重复直到成功                               │
└──────────────────────────────────────────────────────────┘
""")

    # ─── Inverter ───
    print(">>  示例一：Inverter 取反——「敌人不在 = 安全」\n")
    print("   Selector( 巡逻(敌在?->失败) | 取反：敌不在?->成功->巡逻 )\n")

    bb1 = Blackboard()
    bb1["enemy/visible"] = False  # 敌人不在视野

    guard_tree = Selector("守卫行为", [
        Sequence("战斗", [
            Condition("敌在视野?", is_enemy_visible),
            Action("冲锋", charge),
        ]),
        Inverter("没看到敌人", Condition("敌在视野?", is_enemy_visible)),
    ])
    # 简化：用更直观的例子

    print("   敌人不在视野时：Condition「敌在?」返回 FAILURE")
    print("   Inverter 将其翻转为 SUCCESS -> 守卫成功完成巡逻\n")

    simple_inv = Inverter("没敌人=安全", Condition("敌人存在?", is_enemy_visible))
    executor_inv = StepExecutor(simple_inv, bb1)
    executor_inv.run_step_by_step(max_ticks=5, title="Inverter: 敌人不存在 -> 翻转 -> SUCCESS")

    # ─── Repeater ───
    print("\n" + "─" * 60)
    print("\n>>  示例二：Repeater——重复攻击 3 次\n")

    bb2 = Blackboard()
    attack_action = Action("攻击", attack)
    repeat_attack = Repeater("三连击", attack_action, repeat_times=3)
    executor_rep = StepExecutor(repeat_attack, bb2)
    executor_rep.run_step_by_step(max_ticks=10, title="Repeater: 攻击 ×3 次")

    # ─── UntilSuccess ───
    print("\n" + "─" * 60)
    print("\n>>  示例三：UntilSuccess——持续冲锋直到进入近战范围\n")

    bb3 = Blackboard()
    bb3["enemy/distance"] = 100

    until_charge = UntilSuccess("冲向敌人", Action("冲锋", charge))
    executor_us = StepExecutor(until_charge, bb3)
    executor_us.run_step_by_step(max_ticks=10, title="UntilSuccess: 冲锋直到距离=0")

    print("""
┌──────────────────────────────────────────────────────────┐
│  关键要点：                                               │
│  1. 装饰器修改单个子节点的行为，让树更简洁                 │
│  2. Inverter: 翻转成功/失败（"不存在"->"安全"）            │
│  3. Repeater: 执行固定次数                                │
│  4. UntilFail/UntilSuccess: 循环直到条件满足               │
└──────────────────────────────────────────────────────────┘
""")
