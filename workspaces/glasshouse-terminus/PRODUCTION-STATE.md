# 雨幕终点站 — 当前制作状态

**G4第一轮全场扩展已启动。** 用户在获知G3木作复核未结束后，明确要求「直接做g04吧」。本次按`G4-AUTHORIZATION.md`进入G4；这是用户授权的阶段顺序例外，不把历史G3改写为PASS，不等于最终验收。

## 当前唯一生产运行

- run：`34141383107`，源码`8f4b50842f3fd868c2312b3c20e0df53338930e7`。
- 入口：`extend_g4_scene.py`、`.github/workflows/glasshouse-g4-expand.yml`、`g4-expansion-request.json`。
- 状态：已启动，等待实际构建/图像结果；不得据此宣称已经生成或审查新工件。
- 有限预算：45分钟job、34分钟生产截止、11分钟保存/取回余量；公开标准runner，渲染单并发，外部费用0，单次请求。

不要重跑G0/G2，不重复G3节点调光，不另启并行G4请求。先查上述现有运行；若已结束，以实际工件和原图更新本页。

## 已完成的G4续作清点

只读run`34140448762`，源码`eece9b6c88aa596b64e5bbbba33b4ee9931a9976`。持久证据`00390f1a761b1f263e136395444e8bf7c5b7e74a`，目录`output/g4-inventory`。实际下载并校验artifact10025692571，ZIP SHA-256 `4bb865c5e7f8e6a68a81035d16546a69f049f00be319f547ea47a783021d0000`；读取2389个真实对象、69个材质及现有源码快照。源master未保存或修改。数量只用于定位工程，不代表美术质量。

复用R07完整场景、原家具植物、已处理木材/石材贴图及既有Blender4.5.13 LTS/Cycles和证据管线。源码确认了桌面曲边XY、柜体全表面YZ映射的侧面维度塌缩，本轮仅在对应对象采用面向构件的UV修正，并等待D02实际图像复核。

## 当前可恢复父候选：R07

commit `192eba1352585df211f1aa2447a193eec949f6be` / `workspaces/glasshouse-terminus/output/g3-r07-recovered/g3-bay-candidate.blend`。

实际SHA-256：`1680bcbcc8f8c0911c3c3486f7fc5da5d849b4a7016e87fad67f4233beb14d5e`。24项清单本次再次实际核验。原D01近黑问题已解决；原G3-R07-REVIEW与EVIDENCE-INDEX保留历史事实，不受本次阶段授权追溯改写。

G4第一批覆盖建筑两侧及端部、完整地面/站台、家具植物、真实车厢内外和海崖材料。桥拱V形接头、全场灯光/反射平衡、继承木作问题仍需原图复核；全场候选不自动成为G4 PASS。

原合同SHA-256 `0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`。G2 BEST、所有父工件与失败图保留；main和Leaf不改。G1/P1浏览器管理员阻断不绕过；最终雨动画、原生4K30主片、短版、证据片与同源网页未完成。`human_acceptance=false`。
