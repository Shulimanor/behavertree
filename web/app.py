"""行为树 Web 教程 —— Flask 后端"""

import sys
import os
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, render_template
from behave_tree.core import Status
from behave_tree.serialize import node_to_dict, blackboard_to_dict

app = Flask(__name__)

TUTORIAL_NAMES = [
    "01_basics", "02_conditions", "03_sequence", "04_selector",
    "05_decorators", "06_blackboard", "07_parallel",
    "08_npc_ai", "09_door_logic", "10_guard_ai",
]

TUTORIAL_META = [
    {"id": i, "name": name, "title": ""}
    for i, name in enumerate(TUTORIAL_NAMES, 1)
]

# 服务端 session 存储：每个教程的当前状态
_sessions: dict[str, dict] = {}


def _load_tutorial(tutorial_id: int):
    """加载教程模块并返回 build() 结果"""
    if tutorial_id < 1 or tutorial_id > 10:
        return None
    name = TUTORIAL_NAMES[tutorial_id - 1]
    mod = importlib.import_module(f"tutorials.{name}")
    return mod.build()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tutorials")
def list_tutorials():
    result = []
    for meta in TUTORIAL_META:
        data = _load_tutorial(meta["id"])
        result.append({
            "id": meta["id"],
            "title": data["title"] if data else meta["name"],
            "description": data["description"] if data else "",
        })
    return jsonify(result)


@app.route("/api/tutorial/<int:tid>/start", methods=["POST"])
def start_tutorial(tid):
    data = _load_tutorial(tid)
    if not data:
        return jsonify({"error": "Tutorial not found"}), 404

    # 重置树中所有节点的 last_status
    _reset_status(data["root"])

    # 保存到服务端 session
    sid = str(tid)
    _sessions[sid] = {
        "root": data["root"],
        "blackboard": data["blackboard"],
    }

    # 收集初始日志
    logs = [{"tick": 0, "msg": f"加载教程: {data['title']}"}]

    return jsonify({
        "tick": 0,
        "tree": node_to_dict(data["root"]),
        "blackboard": blackboard_to_dict(data["blackboard"]),
        "logs": logs,
        "title": data["title"],
        "description": data["description"],
        "running": True,
    })


@app.route("/api/tutorial/<int:tid>/tick", methods=["POST"])
def tick_tutorial(tid):
    sid = str(tid)
    session = _sessions.get(sid)
    if not session:
        return jsonify({"error": "Tutorial not started"}), 400

    root = session["root"]
    bb = session["blackboard"]

    status = root.tick(bb)

    # 收集执行日志
    logs = _collect_logs(root)

    return jsonify({
        "tree": node_to_dict(root),
        "blackboard": blackboard_to_dict(bb),
        "status": status.value,
        "running": status == Status.RUNNING,
        "logs": logs,
    })


@app.route("/api/tutorial/<int:tid>/run", methods=["POST"])
def run_tutorial(tid):
    """连续运行直到结束，返回所有 tick 的结果"""
    sid = str(tid)
    session = _sessions.get(sid)
    if not session:
        return jsonify({"error": "Tutorial not started"}), 400

    root = session["root"]
    bb = session["blackboard"]

    ticks = []
    max_ticks = 20
    for _ in range(max_ticks):
        status = root.tick(bb)
        ticks.append({
            "tree": node_to_dict(root),
            "blackboard": blackboard_to_dict(bb),
            "status": status.value,
        })
        if status != Status.RUNNING:
            break

    logs = _collect_logs(root)

    return jsonify({
        "ticks": ticks,
        "last_status": ticks[-1]["status"],
        "running": ticks[-1]["status"] == "RUNNING",
        "logs": logs,
    })


@app.route("/api/tutorial/<int:tid>/reset", methods=["POST"])
def reset_tutorial(tid):
    data = _load_tutorial(tid)
    if not data:
        return jsonify({"error": "Tutorial not found"}), 404

    _reset_status(data["root"])
    sid = str(tid)
    _sessions[sid] = {
        "root": data["root"],
        "blackboard": data["blackboard"],
    }

    logs = [{"tick": 0, "msg": "已重置"}]

    return jsonify({
        "tick": 0,
        "tree": node_to_dict(data["root"]),
        "blackboard": blackboard_to_dict(data["blackboard"]),
        "logs": logs,
        "title": data["title"],
        "description": data["description"],
        "running": True,
    })


def _reset_status(node):
    """递归重置节点状态"""
    node.last_status = None
    if hasattr(node, "children"):
        for child in node.children:
            _reset_status(child)
    if hasattr(node, "child"):
        _reset_status(node.child)
    # 重置 composite 内部状态
    if hasattr(node, "_running_index"):
        node._running_index = 0
    if hasattr(node, "_count"):
        node._count = 0


def _collect_logs(node, depth=0):
    """递归收集所有节点的执行日志"""
    logs = []
    status_text = _status_label(node.last_status)
    extra = ""
    if node.last_status:
        logs.append(f"{'  ' * depth}[{node.name}] → {status_text}{extra}")
    children = []
    if hasattr(node, "children"):
        children = node.children
    elif hasattr(node, "child"):
        children = [node.child]
    for child in children:
        logs.extend(_collect_logs(child, depth + 1))
    return logs


def _status_label(status):
    if status is None:
        return "未执行"
    if status == Status.SUCCESS:
        return "成功"
    if status == Status.FAILURE:
        return "失败"
    return "运行中"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
