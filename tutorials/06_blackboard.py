"""教程 06：黑板（Blackboard）——节点间共享数据

Blackboard 是行为树中各节点共享数据的存储空间。

为什么需要黑板？
  - 节点之间不能直接通信——它们通过树结构连接
  - 但往往需要共享数据（敌人位置、血量、弹药数等）
  - 黑板提供了一个统一的键值存储

命名规范：
  - 使用命名空间前缀避免键冲突：'enemy/hp', 'npc/position'
  - 用 / 分隔层级，类似文件路径
"""

from behave_tree import (
    Status, Action, Condition,
    Sequence, Selector,
    Blackboard, StepExecutor
)


def consume_food(bb: Blackboard) -> Status:
    hunger = bb.get("player/hunger", 50)
    food = bb.get("player/food", 3)
    print(f"    [吃东西] 饥饿值: {hunger}, 食物: {food}")
    if food <= 0:
        print("    [吃东西] 没有食物了！")
        return Status.FAILURE
    bb["player/food"] = food - 1
    bb["player/hunger"] = max(0, hunger - 30)
    print(f"    [吃东西] 吃了食物，饥饿值 -> {bb['player/hunger']}")
    return Status.SUCCESS


def is_hungry(bb: Blackboard) -> bool:
    hunger = bb.get("player/hunger", 0)
    print(f"    [检查饥饿] 饥饿值: {hunger}")
    return hunger > 30


def hunt(bb: Blackboard) -> Status:
    """狩猎分两步：追踪->捕获"""
    stage = bb.get("hunt/stage", 0)
    if stage == 0:
        print("    [狩猎] 寻找猎物...")
        bb["hunt/stage"] = 1
        return Status.RUNNING
    if stage == 1:
        food = bb.get("player/food", 0)
        bb["player/food"] = food + 1
        print(f"    [狩猎] 捕获猎物！食物 +1，总食物: {bb['player/food']}")
        bb["hunt/stage"] = 0
        return Status.SUCCESS
    return Status.RUNNING


def have_food(bb: Blackboard) -> bool:
    food = bb.get("player/food", 0)
    print(f"    [检查食物] 当前食物储备: {food}")
    return food > 0


def run():
    print("""
┌──────────────────────────────────────────────────────────┐
│              教程 06：黑板 (Blackboard)                   │
│                                                          │
│  黑板是节点间共享数据的字典：                              │
│    • 任何节点都可以读写黑板                                 │
│    • 推荐用命名空间前缀避免键冲突                          │
│      V 'player/hp', 'enemy/position'                     │
│      X 'hp', 'pos'                                      │
└──────────────────────────────────────────────────────────┘
""")

    # ─── 生存逻辑 ───
    print(">>  生存 AI：饿了就吃，没食物就狩猎\n")

    bb = Blackboard()
    bb["player/hunger"] = 60   # 饿了
    bb["player/food"] = 1      # 有一点食物

    survival_tree = Sequence("生存策略", [
        Selector("解决饥饿", [
            # 优先方案：直接吃
            Sequence("吃东西", [
                Condition("饿了?", is_hungry),
                Condition("有食物?", have_food),
                Action("吃食物", consume_food),
            ]),
            # 备选方案：去打猎
            Sequence("去狩猎", [
                Condition("饿了?", is_hungry),
                Action("狩猎", hunt),
                Action("吃食物", consume_food),
            ]),
        ]),
    ])

    executor = StepExecutor(survival_tree, bb)
    executor.run_step_by_step(max_ticks=10,
                              title="生存 AI: 饿了->检查食物->狩猎->再吃")

    print("""
┌──────────────────────────────────────────────────────────┐
│  关键要点：                                               │
│  1. 黑板 = 行为树的"共享记忆"                             │
│  2. 节点通过读写黑板协调行为                               │
│  3. 命名空间前缀 (player/, enemy/) 避免冲突               │
│  4. 黑板不参与树的结构决策，只是数据载体                   │
└──────────────────────────────────────────────────────────┘
""")

def build():
    bb = Blackboard()
    bb["player/hunger"] = 60
    bb["player/food"] = 1
    root = Sequence("生存策略", [
        Selector("解决饥饿", [
            Sequence("吃东西", [
                Condition("饿了?", is_hungry),
                Condition("有食物?", have_food),
                Action("吃食物", consume_food),
            ]),
            Sequence("去狩猎", [
                Condition("饿了?", is_hungry),
                Action("狩猎", hunt),
                Action("吃食物", consume_food),
            ]),
        ]),
    ])
    return {
        "root": root,
        "blackboard": bb,
        "title": "教程 06：黑板 (Blackboard)",
        "description": "Blackboard 是所有节点共享数据的字典。节点通过读写黑板协调行为。推荐用命名空间前缀(如 player/hp)避免键冲突。",
    }
