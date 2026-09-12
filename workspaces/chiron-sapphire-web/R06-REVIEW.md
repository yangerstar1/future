# R06 continuation — 2026-09-12

Resume source: `1493516d1e7b080acae2803d269608bdd0aac42d` (b12 challenger).
Preserved prior functional checkpoint: `e56471017a7e1aefde65defb5067676b0fe46ef2` (b11).
The uploaded HTML's entire visible conversation was read. It ends after a handoff
progress message; no final handoff or new main-case CAD is present in this commit.
Do not pretend those missing files were recovered.

G0: clean sparse checkout of `codex/chiron-sapphire-web`; no AGENTS.md in tree.
Plain ES modules; locked Three 0.180.0, esbuild 0.25.10, Playwright 1.55.1.
Local Node 24.19.0 / Python 3.12.14; CI Node 22.16.0 retained. Eight state tests,
build and fifteen geometry tests passed on the unmodified source. Entry and
module responsibilities remain those in README. Only this workspace and its
existing workflow are in scope. Git source persistence and standard Actions are
authorized by the resumed task; no public deployment, new fees or other projects.

Browser: the advertised Cloud Browser returned ERR_BLOCKED_BY_CLIENT for local
HTTP. No alternative local browser is used to evade that restriction. Existing
authorized Actions execute the repository's browser validation. No physical GPU
or phone is available in the local runtime.

Baseline evidence: run 34677282189; build hash
`5043358cbd1f37c3f27d2f9087faadd801b5f3eed6f41dca20d99cd025e74734`.
All 28 PNGs and the health report were recovered from their original artifacts;
both ZIP archives passed CRC validation. Independent visual review remains
REVISE: CU06 Q1, CU08 static Q2, continuous motion not qualified. Measured bright
pixels do not support a claim of widespread clipped exposure; the prominent
defects are flat metal response, coarse curved silhouettes and case volume.

## First repair: redundant drawing and native visibility observation

Baseline whole-watch rendering reports 928 draw calls / 3,237,201 submitted
triangles per frame. The inner watch was shaded in the HDR capture, again in
the final scene, and again in Three's compatibility transmission prepass.
The candidate reuses the live HDR colour AND depth, then shades only the sapphire
surfaces above it. No production geometry, movement nodes or fixed camera changed.
The opaque AO pass is applied to the live inner radiance before presentation.
Visual comparison, resource recovery and timing on the changed build are required.

O25's raw native trace contains a visible event but no hidden event. Its observer
switched back only 1.2 seconds after reading document.hidden, while a software GPU
frame could take several seconds. The candidate waits for the original mandatory
native hidden-event counter before measuring the hidden interval. Assertions are
not weakened, events/properties are not fabricated, old failures remain preserved.
This is a pending diagnosis until a real browser run proves or rejects it.

Status: IN_PROGRESS. No new visual or performance gate is awarded by these edits.

## Resumed from Markdown transcript, 2026-09-12

Read all 11 exported messages and the complete original contract. Repository HEAD
was `254dc45f92d59c12a5b421cd7ce0914551d17300`; the new shell CAD and final lifecycle
patch mentioned at the end of that conversation were absent. They are not claimed
as recovered. Clean checkout, locked dependencies, eight state tests and the exact
`d2fdcb835…` baseline build were reproduced. No AGENTS.md applies. The Cloud Browser
again rejected local HTTP with ERR_BLOCKED_BY_CLIENT; authorized standard Actions
remain the browser execution environment. Only this workspace/workflow is changed.

Original visual/health ZIPs from run 34679652877 were materialized and passed CRC
validation. Health passed 5/6: O25 timed out at its native-hidden-event counter even
though its independently read visibility probe was hidden. Missing native event
delivery is not itself the contract's behavior: the application must stop costly
work while actually hidden and recover without a long time step or another loop.

The lifecycle patch reads document.hidden before scheduling/rendering and from a
single 500 ms watchdog. Transitions cancel pending work and reset the time anchor;
native hiddenEvents still counts only real events. hiddenTransitions separately
records direct observations with source/time. No property or event is synthesized.
O25 keeps real same-window hiding, frozen time, real presented motion before/after,
one initialization/loop and the no-jump assertion. It now observes the independent
transition counter, additionally requiring frozen energy and draw count. The old
failure and native event traces are preserved, not rewritten as passing evidence.
This correction is pending real-browser verification, not a health-gate award.

## 当前本地候选：主壳与装配修复（2026-09-12）

本次读取了上传 Markdown 的全部 11 条消息，并从远端
`254dc45f92d59c12a5b421cd7ce0914551d17300` 继续工作。下列新增 CAD 是本次重建，
不是从上一会话找回的文件。原始 28 张截图只作为该远端版本的缺陷依据。

### 已实现

- `cad/main_case.py` 使用锁定的 CadQuery 2.8.0，生成一个有效、连通的中空主壳，
  含三枚表冠的实际通孔与前后镜片安装台阶。导出可编辑毫米 STEP、网页网格及哈希审计。
- `sapphire.mjs` 直接使用 CAD 坐标和逐面解析法线；前镜片保留弧面上表面，
  两片镜片均有平整安装面。前后镜片参数随 CAD 资产交付。
- `watch.mjs` 移除外加的翼状冠肩及壳体后缩放，避免单独缩放使孔位偏离表冠。
  陀飞轮护桥由 40 × 6 提高到 192 × 12 个细分；仍需检查高光和微距轮廓。
- 后台修复位于本地提交 `e8f0296`：直接观测真实隐藏状态，停止待执行工作，
  恢复时重置时间锚点。健康测试保留真实隐藏、能量冻结、恢复运动和单循环要求。

### 已取得的本地证据

| 检查 | 结果与边界 |
| --- | --- |
| 锁定 CAD 环境 | CadQuery 2.8.0 / OCP 7.9.3.1.1；早期 2.7.0 样品已被替换 |
| 主壳实体 | 有效，1 个 solid；三冠套环与管轴的实体交集均为 0 |
| 镜片装配 | 两片保守包络与主壳的实体交集均为 0；安装面的设计轴向间隙为 0.01 mm |
| 网页实际壳体尺寸 | 44.414673 × 57.829013 × 21.500001 mm，保持既定测量边界 |
| 网页 CAD 网格 | 40,422 个三角形；绝对弦偏差设置 0.05 mm；解析法线长度误差小于 5×10⁻⁸ |
| 机械状态测试 | `npm test`：8 项通过 |
| 几何与连接 | `node tools/geometry-audit.mjs`：17 项通过，含 721 相位和 50 次装配往返 |
| 构建 | 成功；app.js 6,406,145 bytes，gzip 2,820,536 bytes |
| 静态检查 | 修改的 JavaScript 语法检查及 `git diff --check` 通过 |

构建哈希：`281f1df0a95339a0b27988a4b04ec190acf0a50cee6d0291dd1c9b36cc6eaf63`。
CAD 网格哈希：`c4a4921ef6218dc6960b049c7b66fee676df8f15e6858cd5db031855f75d2c69`。
实际渲染网格的有向体积为 8.509531，CAD 体积为 8.571274（单位均为场景单位³）；
差异约 0.72%，在当前有限网格审计的 1% 界限内。这不是制造精度认证。

新镜片检查最初把轮廓宽度参数误当成其矩形边界而失败。三次 Bézier 轮廓会略超出
该参数；检查已改为与实际 CAD 包络的精确边界比较，未放宽原有表壳尺寸门槛。

### 当前阻塞与未通过项

GitHub 推送被自动审批拒绝。拒绝理由是：当前导出会话里只有助手对历史授权的描述，
缺少可核验的用户授权原文；推送会修改外部公开仓库。随后进行了只读历史查找，
未找回本任务的用户授权原文；没有换接口、换远端或绕过审批重试。以上成果当前仅为本地候选。
前文关于 Actions 已授权的历史记录不能覆盖这次具体拒绝。

Cloud Browser 对本地 HTTP 返回 `ERR_BLOCKED_BY_CLIENT`，因此没有改用其他本地
浏览器绕开限制。新候选尚无浏览器截图、GLB 重新导入、O25 真实后台恢复或性能结果。
增加实体网格也会增加负载；不能把早期样品的减面比例当成本版本帧率提升。

当前状态：**IN_PROGRESS / 未终验**。冠孔边缘尚未倒圆；金属的层次、微距曲面高光、
新壳透射观感和连续交互仍需多角度回归后继续修订。硬件性能、实机触控及 Q3 门槛未获证明。

取得对本分支推送及现有 Actions 的明确授权后，推送这个可审核候选，以
`[full-check] [route-check]` 运行已有 build / observe / regression / health /
performance / route。固定检查相机与原有验收门槛保持原样，依据新证据继续修复；
不将成功构建或成功截图视作合同终验。
