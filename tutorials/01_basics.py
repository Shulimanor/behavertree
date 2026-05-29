"""教程 01：行为树基础——状态和动作节点

行为树的三个核心状态：
  - SUCCESS (成功)：节点完成目标
  - FAILURE (失败)：节点无法完成目标
  - RUNNING (运行中)：节点需要更多 tick 才能完成

RUNNING 是行为树区别于普通决策树的关键特性。
它让 AI 可以执行跨越多个 tick 的行为（如移动、动画播放），
而不需要阻塞整个系统等待动作完成。

本教程演示多种 Action 节点：
  1. "一击制胜"：单 tick 直接返回 SUCCESS
  2. "三击制胜"：内部计数，前两次返回 RUNNING，第三次 SUCCESS
  3. "总是失败"：始终返回 FAILURE（不可能完成的任务）
"""

from behave_tree import Status, Action, Blackboard, StepExecutor


def always_succeed(bb: Blackboard) -> Status:
    print("    [一击制胜] 啪！一击命中！")
    return Status.SUCCESS


def three_hit(bb: Blackboard) -> Status:
    bb.setdefault("three_hit/count", 0)
    bb["three_hit/count"] += 1
    count = bb["three_hit/count"]
    print(f"    [三击制胜] 第 {count} 次攻击...")
    if count >= 3:
        print("    [三击制胜] 第三击！暴击！")
        return Status.SUCCESS
    print("    [三击制胜] 还没结束，继续...")
    return Status.RUNNING


def always_fail(bb: Blackboard) -> Status:
    print("    [总是失败] 我在尝试完成不可能的任务...")
    return Status.FAILURE


def run():
    print("""
┌──────────────────────────────────────────────────────────┐
│              教程 01：行为树基础                          │
│                                                          │
│  行为树有三种执行状态：                                   │
│    SUCCESS  — 成功（绿色）                                │
│    FAILURE  — 失败（红色）                                │
│    RUNNING  — 运行中（黄色），需要更多 tick 才能完成       │
│                                                          │
│  每个 tick，行为树从根节点向下递归执行。                   │
│  叶子节点（Action）是具体做事情的节点。                    │
└──────────────────────────────────────────────────────────┘
""")

    # 构建一个简单的树：根节点是 "一次攻击"
    root = Action("一次攻击", always_succeed)
    bb = Blackboard()

    print(">>  单 tick 就成功的 Action：\n")
    executor = StepExecutor(root, bb)
    executor.run_step_by_step(max_ticks=5, title="Action：一次攻击 (单 tick 成功)")

    # 需要多个 tick 的节点
    print("\n" + "─" * 60)
    print("\n>>  多 tick 的 Action（RUNNING 状态）：\n")
    root2 = Action("三击制胜", three_hit)
    bb2 = Blackboard()
    executor2 = StepExecutor(root2, bb2)
    executor2.run_step_by_step(max_ticks=5, title="Action：三击制胜 (多 tick)")

    # 总是失败的节点
    print("\n" + "─" * 60)
    print("\n>>  总是返回 FAILURE 的 Action：\n")
    root3 = Action("总是失败", always_fail)
    bb3 = Blackboard()
    executor3 = StepExecutor(root3, bb3)
    executor3.run_step_by_step(max_ticks=5, title="Action：总是失败")

    print("""
┌──────────────────────────────────────────────────────────┐
│  关键要点：                                               │
│  1. SUCCESS = 我完成了，父节点可以继续或成功              │
│  2. FAILURE = 我失败了，父节点需要处理这个失败            │
│  3. RUNNING = 我还在忙，下次 tick 继续调用我              │
│                                                          │
│  只有 RUNNING 能让 AI "跨越时间"——                         │
│  这也是行为树在游戏 AI 中如此流行的核心原因。              │
└──────────────────────────────────────────────────────────┘
""")


def build():
    """构建树并返回 Web 前端所需的数据"""
    bb = Blackboard()
    root = Action("一次攻击", always_succeed)
    return {
        "root": root,
        "blackboard": bb,
        "title": "教程 01：行为树基础",
        "description": "行为树有三种核心状态：SUCCESS(成功)、FAILURE(失败)、RUNNING(运行中)。RUNNING 让 AI 可以跨 tick 执行长时间行为。",
    }
