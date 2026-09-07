# 雨幕终点站 — 当前制作状态

更新：2026-09-07，R02总览已取回，细节与补充接口观察正在执行。本页优先于尚未更新的 EVIDENCE-INDEX.json 中 G3 NOT_STARTED 字段；严禁据旧索引重建G0/G2或删除现有候选。完整合同SHA-256：0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f。

## 当前结论

G2已有阶段BEST。G3已实际完成一版建模、两版总览和一次有诊断的材质/灯光修正；**尚无G3 BEST，G4不放行**。同上下文实际图像自审，不是独立代理或用户验收。完整原生4K影片与同源网页要求不变，不能用局部样板代替最终交付。

## G3 R01 — 可恢复但未通过

- 制作源码：cf89b07e0e3831d892e742083c7e75a05c285525；运行34113862241。
- 持久源：evidence/g3-source-34113862241-1；commit 0dc1d2e9df7d044081a82756218250a4ddd6bfa2；目录 workspaces/glasshouse-terminus/output/g3。
- 真实master：g3-bay-candidate.blend，26,357,297 bytes，SHA-256 e95b37d7f2d8a28efc8bca32815b0624acae7a787e2c7bbe7565eb30e3588027，实际下载字节已核验。
- Artifact 10016442524，44,664,662 bytes，ZIP SHA-256 c53bcc5460025e24920d2b9ff3225d9f63857ce6d9a12ce3f8581f5f555d626d；38个清单条目全部匹配。
- 细节步骤18分钟超时，仅取得7张PNG；缺D06、反向图及三张门状态图，不能称完整12视图。保留PARTIAL状态，不盲重跑。
- 复用G1处理过的木材/石材，以及已经实际下载并适配的Poly Haven软包椅、盆栽；原始来源和依赖在同目录models中。
- 审查：G3-REVIEW-01.md及G3-R01-DETAIL-AUDIT.md。

## G3 R02 — 总览有明确改善，整体门槛仍待判断

- 源码：d146517b4abbe82d236a11b86880dc5384eab3f9；运行34115854145，job101724359412。
- 新持久源：evidence/g3-r02-source-34115854145-1；commit87d75e3b90d6b330fb378d1fc2200f5d1a52e418；目录workspaces/glasshouse-terminus/output/g3-r02。
- 构建报告记录master SHA-256 3162ba27fbeb3055c5fbe94a6fc2422cc9cca11f68dda381b06627ebcaf6d680；当前已读取报告并由运行重开，完整master的本地下载核验仍等待最终工件，不能冒称已经完成。
- 已下载overview artifact10016822625，5,313,272 bytes，ZIP SHA-256 2b7c59879938e000b9318977ed5b276a90b0d10fa08305d98f0f41f105e8a4a4；逐一看过1440×900雨夜/中性图、1280×800 C03以及720×450单灯诊断。
- 实际图像：禁用单个rim灯的诊断消除了左上白盘；最终修正使用实际抬高灯位而非关闭玻璃响应。修正总览中白盘消失，室内石地面不再镜面化，檐下站台样板有连续表面。其余细节、反向与门状态尚待完整取回。
- 既有相机、几何、曝光、玻璃响应和运动保护不变；3毫米杯碟间隙按实际测量消除。限定路线诊断仍为0次射线碰撞、18次地面命中，不代替视觉验收。

## 额外接口证据 — 不是第三轮建模或G4

G3-V01来自已经查看的D05原图：顶部机构和底部门槛被裁掉。保留原D05，并从同一R02 master追加完整门口、桌椅语境、导轮与门槛近景及实际301/330/348帧状态。

入口observe_g3.py及glasshouse-g3-observe.yml；请求g3-observe-request.json；源码a0a2f186d02b009f37734ad24970c8ca83ecb6bc；运行34117403238已排队，依赖相同单并发锁。只添加诊断机位，不改源master字节、几何、材料或动画。25分钟作业上限、15分钟生产截止、10分钟保存取回预留、证据上限50MB；不重下模型。

R02仍使用原45分钟生产截止、15分钟保存取回预留、单作业60分钟和180MB证据上限。全部为公开标准runner、单并发、无外部付费，不启动重复R02或G4。

## 保持的恢复锚点与未关闭问题

G2-BEST-20260907-R01：证据commit6520a8b6056cd7582e4bfc09367cd37fdfb193a1；master workspaces/glasshouse-terminus/output/g2-review/g2-complete-whitebox.blend；SHA-256 0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be。G1素材commit0615e137cd53b3e3a150979b1a17d2d9c818eafb。

G3原图仍有局部取景、门口观察覆盖与未完成车辆语境，后续以实际新图判断，不把“文件存在”当艺术通过。R01/R02的neutral世界色互相一致，但不同于G2原世界色；不得冒称完全同照明的G2对照。桥拱接头V形缝仍在最终问题清单。

G1/P1浏览器BLOCKED_BY_ADMINISTRATOR不变：不清除认证、不改安全设置、不换工具绕过；P0离线制作继续但不删除P1交付。main与Leaf以及旧证据分支保持不变。

下一动作：取回34115854145完整修正工件与34117403238补充观察，核验实际字节并逐一审图，再决定G3门槛。不是再次从NOT_STARTED启动整套构建。本页上一版保存在a0a2f186d02b009f37734ad24970c8ca83ecb6bc的同名文件。
