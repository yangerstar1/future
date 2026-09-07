# 雨幕终点站 — 最新续作交接

仓库`yangerstar1/future`，制作分支`codex/glasshouse-terminus`，工作根`workspaces/glasshouse-terminus`。

## 当前结论

**已做到G4 R02：真实全场美术扩展与后续干地/环境修正完成，原图已取回审查；完整G4仍为PAUSED_UNMET，尚未成为阶段BEST。** 用户在知晓G3木作复核未结束后明确指令「直接做g04吧」，授权改变阶段顺序。不得继续以旧G3 gate阻止进入G4，也不得把此授权追溯写成G3 PASS或最终用户验收。

本轮清点、G4 R01、G4 R02的所有运行均已结束。最近查询无in-progress运行，没有安排自动后续作业。不要重做G0/G2/G3，不要重复触发本轮已完成request，不要根据旧“正在构建/排队”中途记录重建模型。

读取顺序：本文件 → `PRODUCTION-STATE.md` → **`G4-EVIDENCE-INDEX.json`** → `G4-R02-REVIEW.md` → `G4-R01-REVIEW.md` → 原合同。原`EVIDENCE-INDEX.json`保留G1—G3全部历史，不是最新G4索引；旧G4禁止状态已被后续明确用户授权覆盖，原质量要求没有降低。

## 最新确切恢复点：G4 R02

完整证据commit：**`12ae1030686d97823548b2967805d85853d12ab2`**。
证据分支：`evidence/g4-r02-34142587601-1`。
根目录：`workspaces/glasshouse-terminus/output/g4-r02`。
master：`g4-full-scene-candidate.blend`，实际26,580,528 bytes。
实际SHA-256：

`173da1291bff8a39da704539c737e21f9b2d739e3d32a106f629601bc2abefdc`

run34142587601 / job101811832877，conclusion=success。
制作源码`ca63f0d47f7ec001daa2ab4eb0ee9da605a0c617`；渲染前源checkpoint`b5f866d592b0c722ca75d595038dbc16a07a1904`。
入口：`refine_g4_environment.py`、`.github/workflows/glasshouse-g4-refine.yml`、`g4-refine-request.json`。

实际下载artifact10027422860，ZIP34,126,083 bytes，SHA-256`ac869b1107d64a75a8cb4e2de1cc68a4b831701bbf7c8031ef180558e4240fe3`。17项清单全部匹配，无缺项；新进程重开外部图片缺失0，渲染前后master未变。五张原图全部逐张实际审查。临时artifact只有一天保留期，长期恢复必须用上述Git提交。

证据分支是data-only，不含最新制作代码。应保持制作分支的源码，仅恢复需要的output目录；不要把整个证据分支检出后依据旧README再做阶段。确认真实仓库根、工作树与路径无冲突后，可按已核实的方法取回：

```bash
git fetch --depth=1 origin 12ae1030686d97823548b2967805d85853d12ab2
git archive FETCH_HEAD workspaces/glasshouse-terminus/output/g4-r02 | tar -x
echo '173da1291bff8a39da704539c737e21f9b2d739e3d32a106f629601bc2abefdc  workspaces/glasshouse-terminus/output/g4-r02/g4-full-scene-candidate.blend' | sha256sum --check
```

不要在未知本地目录直接执行命令。先核验Blender4.5.13 LTS、运行入口与实际工件。旧G3或R01渲染脚本会设置其旧世界/照明，不能拿来随意渲染R02并声称相同版本对照；继续时明确保留R02连续World和现有实体灯。

## 这次实际做了什么

### 只读扩展清点，已结束

run34140448762，source`eece9b6c88aa596b64e5bbbba33b4ee9931a9976`，evidence`00390f1a761b1f263e136395444e8bf7c5b7e74a`，目录`output/g4-inventory`。Artifact10025692571，253337 bytes，ZIP SHA`4bb865c5e7f8e6a68a81035d16546a69f049f00be319f547ea47a783021d0000`实际核验。读取真实对象、材质、层级、边界、相机与原源码快照，源R07不变；不是重做G0/G2。

### G4 R01全场扩展，已结束

run34141383107 / job101803916031，success，source`8f4b50842f3fd868c2312b3c20e0df53338930e7`。
源checkpoint`b5611004d3f224a2a41e2d589264ce6b3923f5ca`；完整evidence`99a716c1832d0af37ef65ac2eacbea7239dbfe30`，目录`output/g4-r01`。
master26,730,084 bytes，SHA`2a7197af8f42ae6a543d1b028b4617a4784ec4fb262874e3b46f945216955819`。
Artifact10026933461，40,663,184 bytes，ZIP SHA`cf60f3a5c426b728cf8af64b08b44271e95b81f82e05b96f9672439e568bfe74`，23项清单及九张原图全部实际核验、逐张审查。
入口：`extend_g4_scene.py`、`.github/workflows/glasshouse-g4-expand.yml`、`g4-expansion-request.json`。

R01扩展了原R07的两侧/端部拱架和玻璃密封、全厅地面/站台、家具植物、实体照明、车厢内外、海崖桥体表面。复用真实成熟家具和植物、木材/石材贴图与原native helper；没有整场重建。只按明确清单替换已观察到的白模家具/部分植物和不贴合外壳的平板车内顶，新增连续内拱顶与横肋。原相机、幸存原对象坐标、声明范围的关键帧变换校验不变。

R01已经对桌沿采用周向UV、柜侧/构件采用分面木纹UV，但实际D02仍有部分条带感，不是“改UV即木作通过”。R01原图还暴露干地强反射、屋顶有限环境光卡形状、崖桥过暗及车体端部上表面折痕。详见G4-R01-REVIEW.md，commit`7aa8dcc7e49e13a49c8818c7a04c62f9031f468b`。

### G4 R02局部修正，已结束

直接打开已保存R01，不重建全场。大厅从样板扩展时漏带了原refine_g3.py已验证的干区粗糙度修正，本版恢复rough贴图至0.52–0.78、coat0，仅改大厅材质副本，原图/UV保持。

三盏有限环境AREA卡被设为能量0并保留对象，改用连续原生World蓝灰云层环境；相机、照明与玻璃反射共用同一份环境，不用LIGHT_PATH分支、不关闭玻璃/阴影，不改曝光或实体灯具。没有做逐盏隔离实验，不声称某一盏是唯一原因。

原相机/几何/父子/射线标记/非环境灯保护摘要前后相同：`5e45a6fd7b19b2cfc67205df6f4557bc1fee104c27e734057a22cebe92076256`；仅代表脚本声明的检查范围。

## 实际看过的R02画面及当前门槛

五张当前版本夜景：C01-full-night、C03-hall-night、G3-bay-context-night为1440×900；D01-roof-node-regression与C09-car-aisle-night为1280×800。帧451、曝光0、AgX和原相机变换/焦距已核对，采样数与对应R01相同。渲染记录合计1053.50秒，只是预览，不推算最终4K影片保证。

大厅干地拖长刺眼反射与屋顶大块白色灯卡形状已消除，木作、座椅、盆栽、入口恢复主次；D01截面/拼接板/螺栓保持可读，车厢连续内顶、木作、软包/扶手与驾驶区保持。C01桥墩、拱口和崖壁可见度改善，但岩体仍是大块平面/折面，海面直线边界明显，环境衔接未到最终精度。不能把“比原来亮”当作地质造型和桥体工艺通过。

完整评审`G4-R02-REVIEW.md`，commit`d161c075ed0f94e64f27f1e94628cd2bf3b567b4`。同上下文自审，不虚构独立代理。保留R02为最新候选，`g4_stage_pass=false`、`stage_best=null`、`human_acceptance=false`。

R01 C02反侧、C05站台、D02木作、中性图属于R01历史覆盖，不能记成R02新图；当前版本完整阶段观察与动态验收尚未做完。原图没有AI增强或超分；对比图只并排原像素及独立标签带。

## 下一批应做什么，不再卡在灯光上

先只读定位R01 C05暴露的车体端部/车头上部曲面，回传真实对象、拓扑、法线/平滑设置以及需改源码范围；据证据局部修正，不猜对象后缀、不认定一个法线开关就能解决。

再针对海崖地质大面、岩体/基础接触、海面远景边界、桥拱V形弦段接头做构造收口。原桥体的材质与边缘线不是接头修复证据。木作边缘条带感及少量生活痕迹也保留；改后应取得当前版本相关近景、反侧/中性及全景回归，不随意改镜头遮缺陷。

G5电影制作未开始；不要以当前全场候选的存在宣布G4最终通过或进入最终验收。用户授权只让阶段顺序前进，未降低视觉精美度要求。

## 预算与历史保护

本轮只读1次；R01一次45分钟job/34分钟生产/11分钟保存余量，R02一次26分钟job/22分钟生产/4分钟保存余量，均已结束。公开标准ubuntu-24.04 runner、串行CPU渲染、外部费用0。每次下载1.5GB、工作盘8GB、证据100MB；没有自动下一轮或无限重跑授权。新的续作应记录新的有限请求，不修改旧触发文件重复启动。

R07父证据`192eba1352585df211f1aa2447a193eec949f6be` / `output/g3-r07-recovered`，master SHA`1680bcbcc8f8c0911c3c3486f7fc5da5d849b4a7016e87fad67f4233beb14d5e`保留。G2 BEST证据`6520a8b6056cd7582e4bfc09367cd37fdfb193a1` / `output/g2-review`，master SHA`0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be`保留。所有相对output路径均在工作根内。完整G1—G3历史见旧EVIDENCE-INDEX和不可变`29bdb3ad91af4f4a161fc0b4815b3b1e0fc0270e`同名交接，不覆盖旧失败证据。

原合同SHA`0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`。main/Leaf不改，不清认证、不改安全配置、不绕过G1/P1 BLOCKED_BY_ADMINISTRATOR。最终雨动画、原生4K30主片、短版、空间证据片、同源网页与最终验收仍未完成。复用Blender4.5.13 LTS、Cycles、scene_common.py、provision.sh和data-only publish_evidence.sh，避免另起框架。
