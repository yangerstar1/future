# 雨幕终点站 — 当前制作状态

2026-09-07，本页记录到R03提交ce12e2059f3dae4a0e20098164b353f094572cc7。完整合同SHA-256：0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f。G3字段以本页与最新审查为准；EVIDENCE-INDEX.json的G3 NOT_STARTED为旧记录，不能据此重做G0/G2。

## 阶段

G2已有完整白模BEST；G3已实际建造与取图，R02总览较R01有明确改善，但尚无最终质量样板BEST。G4不放行。完整原生4K影片、短版、证据片、同源网页仍在原合同范围内，未完成不能删除。评审是同上下文原图自审，不是独立代理或用户接受。

## 已验证的恢复锚点

G2 BEST：6520a8b6056cd7582e4bfc09367cd37fdfb193a1 / workspaces/glasshouse-terminus/output/g2-review/g2-complete-whitebox.blend。SHA-256 0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be。九张空间视图与28秒低成本白模预演已审查。G1材质持久证据0615e137cd53b3e3a150979b1a17d2d9c818eafb。

G3 R01：源码cf89b07e0e3831d892e742083c7e75a05c285525，运行34113862241。源checkpoint0dc1d2e9df7d044081a82756218250a4ddd6bfa2；结束时证据6570525810ce4118e77651790ffce6464850d9fb，目录output/g3（前缀workspaces/glasshouse-terminus/）。master 26,357,297 bytes，SHA-256 e95b37d7f2d8a28efc8bca32815b0624acae7a787e2c7bbe7565eb30e3588027。artifact10016442524实际下载ZIP摘要c53bcc5460025e24920d2b9ff3225d9f63857ce6d9a12ce3f8581f5f555d626d，38项清单全部匹配。注意：18分钟细节步骤超时，只7张图，不能称完整12视图；植物/反向/门状态缺失。保留PARTIAL状态。

G3 R02：源码d146517b4abbe82d236a11b86880dc5384eab3f9，运行34115854145 / job101724359412。源checkpoint87d75e3b90d6b330fb378d1fc2200f5d1a52e418，目录output/g3-r02。报告摘要3162ba27fbeb3055c5fbe94a6fc2422cc9cca11f68dda381b06627ebcaf6d680，完整master实际下载审计待结束工件。已核验总览artifact10016822625：5,313,272 bytes，ZIP摘要2b7c59879938e000b9318977ed5b276a90b0d10fa08305d98f0f41f105e8a4a4。已逐一打开雨夜/中性/C03和单灯隔离原图：白盘消失、室内石面反射弱化、站台样板干湿表面连续；详细门槛仍未通过。

## 当前唯一续作候选

R03源码ce12e2059f3dae4a0e20098164b353f094572cc7，Actions34118000931，最近读取为pending，等待相同单并发锁。入口finish_g3.py、render_g3.py的r03分组、glasshouse-g3-finish.yml、g3-finish-request.json。新工件拟写output/g3-r03，绝不覆盖上述旧证据。

范围：先量后椅/柜体间隙，只在必要时移动整组柜体和台灯；完善同一门口对应的前室表面、木作收口与真实灯具外壳；把运动表面纹理/遮罩绑定列车坐标；保留全部原相机，追加完整桌椅、椅面、全车门/门槛和屋面节点观察。

资源：一次候选，公开标准ubuntu-24.04，单并发，外部付费零，job60分钟；45分钟生产硬截止、预留15分钟保存/取回/判断；下载1.5GB、工作盘8GB、证据180MB上限。使用原生Cycles自适应采样，阈值0.04/最低16，逐图记录，不降低原生图像尺寸；不声称无噪声保证。缺失观察仍记缺失。

## 重叠作业已核对

仓库还包含observe_g3.py / glasshouse-g3-observe.yml / g3-observe-request.json及G3-R01-DETAIL-AUDIT.md，源a0a2f186d02b009f37734ad24970c8ca83ecb6bc。已读取其代码：它只从R02补观察、不改master；不是新建模或G4。运行34117403238的实时元数据为completed/cancelled，取消时间11:42:29Z，jobs为空，没有实际渲染产物。不能把状态文档中的“已排队”继续当事实。

上述源码保留，不覆盖或删除。R03覆盖完整样板/门口/状态观察并另有真实前室修改；不再次同时提交observe/R03相同队列。原独立导轮近景脚本仍可在需要时复用，但未执行的导轮近景不能标PASS。参考G3-REVIEW-02.md的实际原图缺陷，不因内部文档互相冲突重建整个项目。

## 当前未解决项与下一动作

1. G3样板的完整桌椅、车门门槛、植物/反向、前室语境及新材质仍需取回实际新图判断。
2. R01/R02 neutral世界色相同但不同于G2原始世界色；R03单列恢复G2世界色的C03，不冒称其他图完全同G2照明。
3. G1/P1浏览器BLOCKED_BY_ADMINISTRATOR不变；不清认证、不改安全设置、不换工具绕过。桥拱接头V形缝继续保留在最终问题表。

下一动作：取回R02结束包并核验；跟踪R03确切运行，取回新master及观察集，实际审图后决定G3状态。CI成功、脚本存在和文档数量不算美术通过。main、Leaf、G2 BEST、R01/R02证据保持不变。此更新没有声称任何未返回的结果。
