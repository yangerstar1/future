# 雨幕终点站 — 最新续作入口

## 当前真实状态（本轮接管检查点，图像审查未结束）

仓库 `yangerstar1/future`；制作分支 `codex/glasshouse-terminus`；工作根 `workspaces/glasshouse-terminus`。

**不要恢复到旧G4-R02，也不要把“雨尚未做、只有脚本”的旧回复当作工程事实。当前最新保存的综合候选已经是COAST-R04。** 它保留COAST-R03光学水体、原生谱海浪/泡沫、扫描岩体、R03表面材质以及圆雨滴修正，再加入已下载的HDR环境和扫描羊毛。保存成功和艺术通过是两件事，G4仍未通过。

本轮已实际下载source artifact `10030246035`：195,923,818 bytes，ZIP SHA-256 `def4eb8f6de5b23a51a3c2b956dd3f2ba342392cfb4442dbb3a61a5848ea8e88`。

真实主文件 `output/g4-coast-r04/g4-full-scene-candidate.blend`，151,742,376 bytes，已核验实际SHA-256：

`51a3501edd81f879ba1b5c3e6dd6986e3306968d1319199a624f363667d65a9c`

制作源码 `a530d5ae0a4fcd6f29b9d07939af3584e0ec6994`；入口 `finish_g4_coast_surface_readability.py` / `.github/workflows/glasshouse-g4-coast-surfaces.yml`。源保存于既有run `34153713427`，source job `101841053257` 已success；native review job `101841283640` 当前pending。**先查询现有运行，不重复触发该workflow。** 本段未声称COAST-R04已产图或通过。

## 同一生产队列

本轮查得雨光学run `34149669782` attempt2 / job `101839241954` 正在原生玻璃/厅景渲染，后续还有运动帧。该旧材料源不含最新海岸，不能整场覆盖COAST。

COAST-R03 run `34152626028` 的原生水体观察排队中；COAST-R04 run `34153713427` 在其后。沿用 `glasshouse-production`、`queue: max`、`cancel-in-progress: false`，一次只有一个生产renderer。没有为本次接管额外触发生产重跑，没有取消正在制作的工件。

## 当前阅读优先级

本文件中已核验的COAST-R04源/实时运行信息优先于旧 `PRODUCTION-STATE.md` 的COAST-R02中途状态，以及更旧 `G4-EVIDENCE-INDEX.json` 的G4-R02阶段索引。这些旧文件保留历史，不足以代表最新队列。待实际结束包取回后统一更新。

直接父版COAST-R03：source evidence `563ecf127826cf0b93faf72443c19e6a271401d9`，master SHA `1ed77cc2acaabe09a921aaae5443256b6ffb9674d6912bcdbe754d3290d0990b`。其前COAST-R02 source evidence `071ba6959335f094209fbc4537d2ce2b1246d2dc`，master SHA `b8cea93e7511088f418afbc843b66ddd4dcd0e82f34860b192150341f258ef64`。Git中的大主文件使用可校验无损分块，恢复入口是项目已存在的 `coast_master_transport.py` 或工件中的 `restore_master.py`，不删贴图降质解决存储。

## 必须用真实画面继续

本轮已重新打开历史原图：COAST-R02远海出现拉伸三角条纹且崖壁偏黑；R03木作近景有过匀高光和桌沿条带。它们是旧版已知问题，不代表新候选尚未渲出的结论。

下一动作是收取现有原生结果、核验ZIP与实际master/清单，打开原尺寸外景、岩水、羊毛、雨玻璃和厅景。要同时保住海/山/雨/材料，不各有一版互相缺失。任何新修正须针对已见图且在新有限请求内执行，不无限调亮、叠灯或造噪声。

原合同SHA `0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`，本轮已重新完整读取。G4顺序例外来自用户「直接做g04吧」，不是降低品质或追溯G3 PASS。生成图不是本项目证据；main/Leaf/G2 BEST与历史源不改。浏览器管理员阻断不绕过。完整影片/网页/最终验收尚未完成，human_acceptance=false。

更早完整G4-R02交接保留于commit `819b499bd9c532de7271f22ce1d58364c6f11f2e` 的同名文件，不据旧版本回退。
