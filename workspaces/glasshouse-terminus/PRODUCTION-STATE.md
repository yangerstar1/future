# 雨幕终点站 — 当前续作入口

2026-09-07。原合同SHA-256：0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f。视觉精美度是本阶段的核心验收，不以CI、摘要或物体数量替代。

**G2完整白模BEST不回退；当前为G3样板精修，R04已取得完整工件，R05定向节点修正已提交。G3尚未宣布通过，G4没有放行。** 本页的运行状态是取回时的记录，继续时读取最新Actions元数据，不把静态“运行中”当永远成立。

## R04 — 已有实际成果，不重做

实际入口polish_g3.py / render_g3_polish.py / glasshouse-g3-polish.yml；源码5df7808221aea777899562807bacc6bbd1c3f49a，运行34125489162。与失败的另一路34125276363区分，不能混用两个R04。

源checkpoint a2b7d9d3c90e928a00bca7898247d764c83afe8a；目录workspaces/glasshouse-terminus/output/g3-r04；master g3-bay-candidate.blend，SHA-256 18348be4c401601706e10e4346a32bf5e0c406fec2448e1a53290f7840b8a854。

已取回最终artifact10021262934，ZIP SHA-256 61c958bbaa1a3836b8291bd1b7347d8de46ce33355e2d9f0bb59d10639b20cf6。完整清单逐项核验与主文件字节校验已执行；原图包括总览、木作/椅面/玻璃/节点、无遮挡车门、门槛/导轮、反向、植物、门状态和路线观察。保持实际文件的来源，不将R03图片冒充R04。

实际美术判断见G3-R04-REVIEW.md：大块玻璃白斑和车门观察遮挡有明确改善；但D01拱柱/拼接件在雨夜近景中压黑，不能因此建立G3最终质量BEST。有限路线与文件完整性检查不抵消这个问题。

## R05 — 有界定向修正，原图验收尚未完成

入口relight_g3_nodes.py，工作流glasshouse-g3-node-light.yml，请求g3-node-light-request.json；请求源码8a5eb925c4e88c4155b2148059898b3736386895，运行34128911415。先核查该确切运行及其工件，不重复提交、不开第二套G3构建。

候选只校准两根主拱及其柱/柱头/拼接板的缎面漆，并加两组有支承、远离既有通行路线的紧凑柱脚洗光灯。原几何、原相机、运动、曝光0、AgX、玻璃反射/透射和光线可见性保持。样板范围不扩成G4，不重新下载家具与纹理。

预算已写入请求：一次运行，公开标准ubuntu-24.04、单并发、job30分钟，生产23分钟、保存取回7分钟，外部付费零，下载1.5GB、工作盘8GB、证据80MB。目标输出workspaces/glasshouse-terminus/output/g3-r05。不要把该目标路径或脚本存在直接当作已通过。

待核验的是R05真实保存工件与六张原尺寸观察：原D01节点、完整bay夜景、玻璃近景、原近机位夜景、中性bay、无遮挡车门。只有实际图像证明节点更清楚，且没有重新出现大片白斑、爆白或破坏雨夜主次，才采用为后续候选。当前不替用户或美术评审签署通过。

## 保护对象与范围

G2 BEST：6520a8b6056cd7582e4bfc09367cd37fdfb193a1 / workspaces/glasshouse-terminus/output/g2-review/g2-complete-whitebox.blend，SHA-256 0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be。G1素材0615e137cd53b3e3a150979b1a17d2d9c818eafb。R01–R04历史源码、工件、失败原图和main/Leaf均不覆盖。

G1/P1浏览器BLOCKED_BY_ADMINISTRATOR仍保留，不清认证、不改安全设置、不换工具绕过。全场精修、桥拱V形收口、原生4K30主片、短版、证据片、同源网页及最终用户验收仍未完成，不删减原合同范围。

下一动作：读取R05实时结果，取回并核验实际字节，逐张看原尺寸画面，以R04同机位对照决定后续。不得再次从G0/G2或旧G3 NOT_STARTED记录重启。
