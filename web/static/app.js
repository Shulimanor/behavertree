// 行为树 Web 教程 —— 前端交互逻辑

let currentTid = null;
let tickCount = 0;
let autoTimer = null;
let autoSpeed = 800;

// ── 初始化 ──
document.addEventListener("DOMContentLoaded", () => {
  loadTutorialList();
  document.getElementById("btn-step").addEventListener("click", doStep);
  document.getElementById("btn-auto").addEventListener("click", doAuto);
  document.getElementById("btn-stop").addEventListener("click", doStop);
  document.getElementById("btn-reset").addEventListener("click", doReset);
  document.getElementById("speed").addEventListener("input", (e) => {
    autoSpeed = parseInt(e.target.value);
    if (autoTimer) {
      clearInterval(autoTimer);
      autoTimer = setInterval(doStep, autoSpeed);
    }
  });
});

// ── 加载教程列表 ──
async function loadTutorialList() {
  const res = await fetch("/api/tutorials");
  const tutorials = await res.json();
  const nav = document.getElementById("tutorial-nav");
  nav.innerHTML = tutorials.map(t => `
    <div class="tut-item" data-id="${t.id}" onclick="selectTutorial(${t.id})">
      <strong>${String(t.id).padStart(2,'0')}.</strong> ${t.title}
    </div>
  `).join("");
}

// ── 选择教程 ──
async function selectTutorial(tid) {
  currentTid = tid;
  document.querySelectorAll(".tut-item").forEach(el => el.classList.remove("active"));
  document.querySelector(`.tut-item[data-id="${tid}"]`).classList.add("active");

  const res = await fetch(`/api/tutorial/${tid}/start`, { method: "POST" });
  const data = await res.json();

  tickCount = 0;
  renderTree(data.tree);
  renderBlackboard(data.blackboard);
  renderLogs(data.logs);
  renderDesc(data);
  updateControls(true, data.running);
  document.getElementById("tick-counter").textContent = `Tick: 0`;
}

// ── 渲染树 ──
function renderTree(treeData) {
  const container = document.getElementById("tree-container");
  container.innerHTML = `
    <div class="tree-root">
      ${renderNode(treeData)}
    </div>
  `;
}

function renderNode(node) {
  const statusClass = `status-${node.status}`;
  const statusLabel = statusLabels[node.status] || "未执行";
  const extra = node.extra ? `<div class="node-extra">${node.extra}</div>` : "";

  const card = `
    <div class="node-card ${statusClass}">
      <div class="node-icon">[${node.icon}] ${node.type}</div>
      <div class="node-name">${node.name}</div>
      <div class="node-status">${statusLabel}</div>
      ${extra}
    </div>
  `;

  if (!node.children || node.children.length === 0) {
    return `<div class="tree-child-group">${card}</div>`;
  }

  const childrenHtml = node.children.map(child => renderNode(child)).join("");

  return `
    <div class="tree-child-group">
      ${card}
      <div class="tree-children">
        ${childrenHtml}
      </div>
    </div>
  `;
}

const statusLabels = {
  "idle": "未执行",
  "SUCCESS": "成功",
  "FAILURE": "失败",
  "RUNNING": "运行中",
};

// ── 渲染黑板 ──
function renderBlackboard(bb) {
  const container = document.getElementById("blackboard");
  const entries = Object.entries(bb);
  if (entries.length === 0) {
    container.innerHTML = `<p class="placeholder">无数据</p>`;
    return;
  }
  container.innerHTML = `
    <table class="bb-table">
      ${entries.map(([k, v]) => `
        <tr>
          <td class="bb-key">${k}</td>
          <td class="bb-val">${JSON.stringify(v)}</td>
        </tr>
      `).join("")}
    </table>
  `;
}

// ── 渲染日志 ──
function renderLogs(logs) {
  const container = document.getElementById("log-container");
  if (!logs || logs.length === 0) {
    container.innerHTML = `<p class="placeholder">无日志</p>`;
    return;
  }
  container.innerHTML = logs.map(log => {
    let cls = "";
    if (log.includes("→ 成功")) cls = "log-success";
    else if (log.includes("→ 失败")) cls = "log-failure";
    else if (log.includes("→ 运行中")) cls = "log-running";
    return `<div class="log-entry ${cls}">${log}</div>`;
  }).join("");
  container.scrollTop = container.scrollHeight;
}

// ── 渲染说明 ──
function renderDesc(data) {
  document.getElementById("tutorial-desc").innerHTML = `
    <strong style="color:#e94560">${data.title}</strong>
    <p style="margin-top:8px">${data.description}</p>
  `;
}

// ── 控制按钮状态 ──
function updateControls(enabled, running) {
  document.getElementById("btn-step").disabled = !enabled;
  document.getElementById("btn-auto").disabled = !enabled || !running;
  document.getElementById("btn-stop").disabled = !enabled;
  document.getElementById("btn-reset").disabled = !enabled;
}

// ── 单步执行 ──
async function doStep() {
  if (!currentTid) return;
  const res = await fetch(`/api/tutorial/${currentTid}/tick`, { method: "POST" });
  const data = await res.json();

  tickCount++;
  renderTree(data.tree);
  renderBlackboard(data.blackboard);
  renderLogs(data.logs);
  updateControls(true, data.running);
  document.getElementById("tick-counter").textContent = `Tick: ${tickCount}`;

  if (!data.running) {
    doStop();
  }
}

// ── 自动播放 ──
function doAuto() {
  if (!currentTid) return;
  document.getElementById("btn-auto").disabled = true;
  document.getElementById("btn-step").disabled = true;
  autoTimer = setInterval(doStep, autoSpeed);
}

// ── 暂停 ──
function doStop() {
  if (autoTimer) {
    clearInterval(autoTimer);
    autoTimer = null;
  }
  if (currentTid) {
    document.getElementById("btn-auto").disabled = false;
    document.getElementById("btn-step").disabled = false;
  }
}

// ── 重置 ──
async function doReset() {
  doStop();
  if (!currentTid) return;
  const res = await fetch(`/api/tutorial/${currentTid}/reset`, { method: "POST" });
  const data = await res.json();
  tickCount = 0;
  renderTree(data.tree);
  renderBlackboard(data.blackboard);
  renderLogs(data.logs);
  updateControls(true, data.running);
  document.getElementById("tick-counter").textContent = `Tick: 0`;
}
