# 《雨幕终点站》新会话完整 Handoff — 2026-09-07

> **这是新会话的第一读取入口。**
>
> 仓库：`yangerstar1/future`  
> 制作分支：`codex/glasshouse-terminus`  
> 工作根：`workspaces/glasshouse-terminus`  
> 权威合同：`GLASSHOUSE-TERMINUS-CONTRACT-v1.0`，SHA-256 `0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`。
>
> **当前真实状态：G2 已有完整白模 BEST；G3 已做到 R05，但最终质量样板仍未通过；G4 禁止开始。视觉精美度是首要目标。**

---

## 0. 新会话必须先做什么

新会话不要根据聊天记忆猜进度，也不要从 G0/G2 重来。先进行一次只读核验：

1. 读取本文件。
2. 读取 `PRODUCTION-STATE.md`。
3. 读取 `EVIDENCE-INDEX.json`。
4. 读取 `G3-R05-REVIEW.md`。
5. 读取 `g3-node-light-request.json`、`relight_g3_nodes.py`、`.github/workflows/glasshouse-g3-node-light.yml`。
6. 查询 `codex/glasshouse-terminus` 当前分支 tip 和 GitHub Actions 实时状态，确认没有用户之外的新提交/运行覆盖本交接。
7. 如果上述真实状态与本文件不一致，以**更新、更具体、可核验的仓库/Actions/工件证据**为准，并先报告差异，不强行套用本交接。

截至本交接创建前最后一次查询：**没有 in-progress Actions**。R05 已完成并回传。

---

## 1. 原始目标与不可改的美术方向

项目是原创虚构场景 **《雨幕终点站》**。

锁定美术方向：

**精致、写实材质的浪漫建筑环境；玻璃花房结构 × 复古铁路工艺 × 雨夜暖光。**

视觉要求不是“做完模型”而是：

- 远看能明确读出玻璃拱顶、列车、海崖三个主体；
- 中景能读出站房组织、玻璃分格、轨道、室内层次；
- 近景能看见木材方向、金属收口、座椅软硬关系、玻璃固定方式、雨水依附的真实表面；
- 色彩以低到中饱和的深蓝灰、瓶绿、木棕、暖白为主；黄铜只作重点；
- 纯黑不能吞掉结构；灯泡/反射不能烧白；植物不是荧光绿填充物；
- 排除低模玩具、体素、赛博霓虹、废土恐怖、过度脏旧、全屏蓝雾、高饱和橙青滤镜。

**用户在当前会话再次强调：着重做视觉精美度。** 因此后续决策优先看实际原尺寸画面，不以代码复杂度、对象数量、CI green、摘要数量或运行时间代替美术。

---

## 2. 合同阶段路线 — 不能跳级

正确阶段顺序：

`G0 环境侦察 → G1 风险小样 → G2 完整白模 → G3 一跨最终质量样板 → G4 全场扩展 → 导演/4K影片 → 短版/证据片 → 同源网页 → 最终验收`

当前：

- G0：完成。
- G1：技术/材质风险验证完成，但 P1 浏览器仍有管理员阻断。
- **G2：阶段 BEST 已建立，禁止回退或重建。**
- **G3：R05 候选，仍未艺术通过。**
- **G4：禁止开始。**
- 最终影片/短版/证据片/同源网页：均未完成。

G3 的目的就是防止“全场做满，处处只有 60 分”。只有这一个样板跨真正达到最终质量，才允许复制/扩展。

---

## 3. G2 BEST — 永久保护，不要重做

阶段标识：`G2-BEST-20260907-R01`。

长期恢复锚点：

- evidence branch：`evidence/g2-repair-34109215120-1`
- evidence commit：`6520a8b6056cd7582e4bfc09367cd37fdfb193a1`
- master：`workspaces/glasshouse-terminus/output/g2-review/g2-complete-whitebox.blend`
- master SHA-256：`0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be`
- G2 run：`34109215120`
- fixed views：C01–C09
- low-cost animatic：28s，640×360，10FPS，280 帧，仅白模预演，不是最终影片

G2 已实际审查完整 A–E 白模和“主厅→站台→停稳列车→车厢→回望主厅”空间链。

后续任何任务如果让你“重新从白模开始”，先停止并检查为什么与本交接冲突。

---

## 4. G1 素材与可复用工具

G1 持久素材恢复：

- commit：`0615e137cd53b3e3a150979b1a17d2d9c818eafb`

已复用路线：

- Blender 4.5.13 LTS
- Cycles CPU
- `scene_common.py`
- `provision.sh`
- `publish_evidence.sh`
- G1 已处理的木材/石材纹理
- Poly Haven CC0 家具/植物候选已经在 G3 实际使用并记录来源

不要重新下载/替换一整套家具，除非实际画面证明现有资产不合格。

---

## 5. G3 各版本真实进度

### R01

- run：`34113862241`
- master SHA：`e95b37d7f2d8a28efc8bca32815b0624acae7a787e2c7bbe7565eb30e3588027`
- 状态：部分候选，细节渲染超时；不是 PASS。

### R02

- run：`34115854145`
- master SHA：`3162ba27fbeb3055c5fbe94a6fc2422cc9cca11f68dda381b06627ebcaf6d680`
- 改善：干/湿石材、灯位、杯碟接触、缺失观察补齐。
- 状态：技术完整，但视觉门槛未通过。

### R03

- run：`34118000931`
- source checkpoint：`22dceca579c272b51767c70c153c540f7defc547`
- master SHA：`cb1ae3c8ace74bcbeeaaf51684bf013cba5b7702803f432c91632e4395fadcfe`
- 完整 ZIP artifact：`10019042448`
- ZIP SHA：`18d514615bbeadc0a059ad52f83549860e2eac5ee310d20f72bc30e83de386c9`
- 43 项清单一致，27 PNG。
- 改善：完整桌椅组合、植物、前室、真实车门/路线语境。
- 主要问题：玻璃门楣大块白色灯反射；D05 原观察被厅门遮挡。

### R03 灯光诊断

- run：`34121257143`
- artifact：`10019119528`
- ZIP SHA：`e4d28113c0f9204326a2e14aeed927262b8c12bac8e07c61f2ac47b08282d88a`
- 结论：**`G3_interior_softbox` 是门楣上方白块的主要来源。**
- 不是通过关闭玻璃/曝光/光线路径作弊；R04 改成实体照明设计。

### R04 — 当前重要父版本

正确 R04 是：

- run：`34125489162`
- source commit：`5df7808221aea777899562807bacc6bbd1c3f49a`
- source checkpoint：`a2b7d9d3c90e928a00bca7898247d764c83afe8a`
- complete evidence commit：`cd3526f4a0f6f8333d75bbd666b4fcfcfa9a529a`
- master：`workspaces/glasshouse-terminus/output/g3-r04/g3-bay-candidate.blend`
- master bytes：`26,455,878`
- master SHA：`18348be4c401601706e10e4346a32bf5e0c406fec2448e1a53290f7840b8a854`
- complete artifact：`10021262934`
- ZIP SHA：`61c958bbaa1a3836b8291bd1b7347d8de46ce33355e2d9f0bb59d10639b20cf6`
- 35 项清单全部匹配；19 张原生 PNG 均已逐一看过。

R04 实际改善：

- 删除/重构了造成白斑的无动机大面积摄影补光；
- 改成有实体结构依据的小壁灯，并保留吊灯/桌灯/车内灯；
- 玻璃大白斑消失，且玻璃仍正常反射/透射；
- 样板跨形成瓶绿主构件 + 灰绿次构件 + 少量黄铜层次；
- 新中心线车门观察真正看见顶部导轨、两门扇、前室和门槛；
- 三个实际状态帧 301/330/348 显示关门→移动→全开；
- 导轮与门槛近景已取得；
- 桌椅、木作、布面、植物仍保持。

**R04 新的重大问题：D01-roof-node 过暗。** 去掉摄影补光后，主拱腹板与拼接板被黑暗吞掉，近景不够“值得看”。

不要混用另一条失败 R04：

- failed run：`34125276363`
- failure evidence：`41c4df71e4eee7f48a733be47df26f36693317e8`
- 该入口在相机投影保护处失败，没有产生可用美术候选。
- 后续恢复 `34125804881` 在 pending 阶段取消，无新渲染。

---

## 6. 当前最新版本：G3 R05

**这是新会话真正要从这里继续的版本。**

- run：`34128911415`
- job：`101764327257`
- run conclusion：`success`
- source commit：`8a5eb925c4e88c4155b2148059898b3736386895`
- source checkpoint：`ee77c110f190f7b944dbe8fb2455f87296a76b96`
- persistent complete evidence commit：`4436b5cb5f870e834ff65639d1a1fbd365b9d4e3`
- evidence branch：`evidence/g3-r05-34128911415-1`
- directory：`workspaces/glasshouse-terminus/output/g3-r05`
- master：`g3-bay-candidate.blend`
- master bytes：`26,457,653`
- master SHA：`8ca4ca940a98e80d980fbd895f5ae7c27568b28ee361422bfe4ed267b7b8f02e`
- artifact：`10021873685`
- artifact bytes：`34,863,936`
- ZIP SHA：`3aea7bc1c9a85bea8f833522b40106b274f21c6c41191df5b05a9948fc2698d3`
- 19 个 DELIVERY 清单条目全部匹配，无缺失；6 张 PNG 全部实际打开；fresh-process reopen 成功，无缺失外部图片，渲染后 master 未改。

R05 实际修改：

1. 只校准样板跨主拱、立柱、柱帽、拼接板的缎面绿色漆反应；
2. 在柱脚加入两组**有实体落地支承**的紧凑 SpotLight 上照灯；
3. 新灯与已保存步行路线保守 XY 间距约 1.66 m；
4. 原相机、列车/车门/步行动画、玻璃反射/透射、曝光0、AgX 均保持；
5. 没有重新建场、没有重下家具、没有扩 G4。

R05 已确认的视觉改善：

- 原 `D01-glass-metal` 中，柱面绿色漆、壁灯、夹具和柱截面更可读；
- 完整 bay 中木材、软包、陶盆、低饱和绿仍有不同材质响应；
- R04 去掉的大白斑没有回来；
- D05 无遮挡门口仍成立。

### R05 当前唯一首要阻塞

**`D01-roof-node` 上部主拱腹板 / 拼接板仍近乎黑色。**

R05 的柱脚上照确实改善了下部柱面，但没有充分恢复上部节点可读性。螺栓只剩局部边光。按合同“纯黑不能吞掉结构”和 D01 近景要求，**G3 仍然不通过。**

当前阶段状态必须写成：

`G3 = PAUSED_UNMET / R05 可恢复候选 / G4_NOT_ALLOWED`

不能因为 Actions success、master 可恢复、其他画面变好就把 G3 判 PASS。

---

## 7. 新会话下一步 — 只做这一件事

**先只读诊断 R05 上部节点为什么没有吃到足够的光。**

不要直接再加功率。先用 R05 确切 master：

`workspaces/glasshouse-terminus/output/g3-r05/g3-bay-candidate.blend`

做以下只读/内存诊断：

1. 确认 `D01-roof-node` 相机的实际世界坐标和目标面；
2. 获取主拱腹板、拼接板、柱帽、横梁的真实对象名、world bounds、法线/朝向；
3. 对现有 R05 两盏 SpotLight，检查灯源到上部拼接板/腹板采样点的首命中对象；
4. 区分：
   - 灯被柱帽/横梁遮挡；
   - 入射方向与观察面法线不匹配；
   - 光锥没有覆盖节点；
   - 漆面 BRDF/粗糙度导致高光位置不在镜头；
   - 或其他真实原因；
5. 输出诊断 JSON / 少量标注性原生裁切，不保存成新 BEST。

**只有诊断证明根因后，才允许下一次小范围艺术修正。**

候选修正优先级：

- 优先利用真实已有结构安装点调整局部灯位置/角度/遮光，而不是增大整个空间的补光；
- 如需要新灯，必须有实体灯具外壳/安装关系，不能出现无来源摄影灯；
- 不改曝光；
- 不关闭玻璃响应；
- 不改旧相机；
- 不裁掉失败 D01；
- 不移动模型给镜头让路；
- 不重新进入 G4。

修正后必须原生重渲至少：

- `D01-roof-node`
- `D01-glass-metal`
- 原 `G3-bay-night`
- `R05-complete-bay-night`/对应新版本完整 bay
- 中性完整 bay
- `D05-unoccluded-interface`

验收重点不是“更亮”，而是：

- 能读出主拱截面、拼接板、螺栓与材料层次；
- 仍保持低饱和雨夜；
- 不出现新大片白斑；
- 灯具自身不烧白；
- 暖光不能把整个画面染橙；
- 结构与家具仍有主次。

---

## 8. G3 通过前仍要盯的次级问题

这些不是当前第一阻塞，但不能从最终清单消失：

- 木作侧面与桌面曲边的纹理方向/延展；
- 样板外仍大量白模，属于 G4 后续，不得现在宣传成全场成品；
- G2 桥拱接头近景的 V 形收口仍在最终问题表；
- 最终电影中的开门/节点可读性还没验；
- 最终全场环境、海崖和列车其余细节尚未扩到最终质量。

---

## 9. 绝对不要做的事情

新会话禁止：

- 不要重新 G0；
- 不要重新 G2；
- 不要从 `G3 NOT_STARTED` 开工；
- 不要推翻已有家具/植物/列车/门/路线；
- 不要因为想“更精美”就随机换美术风格；
- 不要把 R04/R05 的真实失败原图删掉；
- 不要让生成式图片替代 Blender 原生证据；
- 不要以对象数、测试数、文件数、CI green、运行时长代替美术；
- 不要在 G3 未通过时批量复制到 G4；
- 不要写 main/Leaf；
- 不要覆盖旧 evidence 分支；
- 不要启用付费 GPU / 大规格 runner，除非用户另行明确授权；
- 不要清除浏览器认证、修改安全设置或换工具绕过 `BLOCKED_BY_ADMINISTRATOR`；
- 不要删除最终网页交付，只能继续优先 P0。

---

## 10. 资源与执行边界

最近 R05 单次预算：

- public standard `ubuntu-24.04` runner
- 单并发
- 外部支出：0
- job：30 分钟
- 生产硬截止：23 分钟
- 保存/取回：7 分钟
- 下载上限：1.5 GB
- 工作盘：8 GB
- 证据：80 MB

这只是已结束 R05 的有限请求，不是无限重跑授权。下一轮如需执行，先记录新的有限请求，但沿用用户已给出的项目执行授权和零外部付费边界，不用重新询问主题。

---

## 11. P1 浏览器阻塞

G1/P1 浏览器仍是：

`BLOCKED_BY_ADMINISTRATOR`

处理原则不变：

- 不清认证；
- 不改安全配置；
- 不换工具绕过；
- 离线 P0 制作可以继续；
- 同源网页仍属于最终合同，不得从范围删除。

---

## 12. 完整项目尚未完成的最终交付

即使未来 G3 通过，仍剩：

1. G4 全场最终美术扩展；
2. 全场质量回归与四周成立；
3. 桥体最终收口；
4. 原生 4K30 约 28 秒主片；
5. 12 秒信息流短版；
6. 15–20 秒真实空间/编辑证据片；
7. 同源 GLB/Three.js 网页，可探索、重放来车、开关车门并复位；
8. 最终质量核验与用户验收。

当前 `human_acceptance = false`。

---

## 13. 新会话建议直接发送的启动指令

复制下面这段到新会话即可：

> 继续执行《雨幕终点站》。仓库 `yangerstar1/future`，分支 `codex/glasshouse-terminus`。先只读读取并核对 `workspaces/glasshouse-terminus/SESSION-HANDOFF-LATEST.md`、`PRODUCTION-STATE.md`、`EVIDENCE-INDEX.json`、`G3-R05-REVIEW.md`，以及 R05 对应脚本/工作流。不要重做 G0/G2，不要从 G3 NOT_STARTED 开工。当前最新可恢复候选是 R05，master SHA-256 `8ca4ca940a98e80d980fbd895f5ae7c27568b28ee361422bfe4ed267b7b8f02e`，G3 仍未通过，主要阻塞是 D01-roof-node 上部拱/拼接板过黑。严格参照原合同，视觉精美度优先。下一步先只读诊断 R05 灯光到上部节点的真实光路/遮挡/法线，再基于证据做最小局部艺术修正；实际原尺寸图像审查通过前禁止 G4。继续直接执行，不要只写计划或文档。

---

## 14. 当前权威读取顺序

新会话按以下优先级解释状态：

1. `SESSION-HANDOFF-LATEST.md` — 新会话入口与执行边界
2. `PRODUCTION-STATE.md` — 当前实时续作状态
3. `EVIDENCE-INDEX.json` — 版本/工件/摘要/恢复锚点
4. `G3-R05-REVIEW.md` — 最新原图艺术判断
5. `G3-R04-REVIEW.md` — R05 的父版全覆盖证据
6. 原合同 — 范围、质量和阶段门槛的最终权威

如果某个上传时 `DELIVERY.json` 写着 `REVIEW_PENDING_NOT_A_PASS`，这是历史上传状态；必须结合后续实际原图审查。但任何后续自审也**不等于用户最终 ACCEPTED**。

**最后状态：PAUSED_UNMET，安全可恢复；下一步不是重建，而是诊断并解决 R05 上部节点可读性。**
