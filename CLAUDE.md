# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个行为树（Behavior Tree）交互教程项目，帮助学习者通过可交互的逐步执行来理解行为树的运行逻辑。

## 常用命令

```bash
# Web 版（推荐）：启动 Flask 服务器，浏览器访问 http://localhost:5000
python web/app.py

# CLI 版：启动交互式教程菜单
python run_tutorial.py

# CLI 版：直接运行指定教程
python run_tutorial.py 1      # 运行第 1 个教程
python run_tutorial.py all    # 运行全部教程
```

依赖安装：`pip install flask`

CLI 版 Windows 下如遇中文乱码，使用：
```bash
PYTHONIOENCODING=utf-8 python run_tutorial.py
```

## 核心架构

```
behave_tree/         # 核心库
├── core.py          # Status 枚举、Node ABC、Blackboard
├── leaves.py        # Action（执行动作）和 Condition（检查条件）叶子节点
├── composites.py    # Sequence（AND）、Selector（OR/优先级）、Parallel（并行）
├── decorators.py    # Inverter、Repeater、UntilFail、UntilSuccess
├── serialize.py     # 树结构→JSON 序列化（供 Web API 使用）
├── renderer.py      # CLI 用 ANSI 颜色和 box-drawing 字符可视化
└── executor.py      # CLI 用逐步交互执行引擎

web/                 # Web 版前端
├── app.py           # Flask 后端 API
├── templates/
│   └── index.html   # 主页面
└── static/
    ├── style.css    # 深色主题样式
    └── app.js       # 前端交互逻辑

tutorials/           # 10 个渐进式教程
├── 01_basics.py     # 三种状态和 Action 节点
├── 02_conditions.py # Condition 节点
├── 03_sequence.py   # Sequence 顺序节点
├── 04_selector.py   # Selector 选择/回退节点
├── 05_decorators.py # 四种装饰器
├── 06_blackboard.py # 黑板共享数据
├── 07_parallel.py   # Parallel 并行节点
├── 08_npc_ai.py     # 综合：NPC 巡逻→追击→攻击
├── 09_door_logic.py # 综合：开门多方案逻辑
├── 10_guard_ai.py   # 综合：完整守卫 AI
└── runner.py        # CLI 菜单启动器
```
每个教程模块包含：
- 辅助函数（Action/Condition 的 fn 回调）
- `build()` — 构建树+黑板，返回 dict（供 Web API 使用）
- `run()` — CLI 版逐步执行（供命令行教程使用）
```

## 关键设计

- **Node ABC**: 所有节点继承 `Node`，需实现 `tick(blackboard)`，返回 `Status`
- **last_status**: 每个节点在 tick 返回前设置 `self.last_status`，渲染器据此着色
- **RUNNING 恢复**: Sequence 和 Selector 用 `_running_index` 记录当前子节点，支持跨 tick 恢复
- **黑板**: `Blackboard` 继承 `dict`，推荐用 `namespace/key` 避免键冲突
- **渲染**: `render_tree()` 递归生成彩色树文本，`print_tree()` 直接打印
- **执行器**: `StepExecutor` 封装 tick→收集状态→渲染→等待输入的循环
