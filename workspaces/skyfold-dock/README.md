# 回天港 / SKYFOLD DOCK

**已生成真实可编辑Blender工程；当前R01仍未达到任务合同质量要求。不是最终成片，不是AUTO_QUALIFIED。**

[打开当前场景文件](output/r01/skyfold-r01.blend) · [实际主视角PNG](output/r01/O01_HERO.png) · [第二空间视角](output/r01/O01_SECOND.png) · [近景](output/r01/O04_CRAFT.png)

[继续执行入口](SESSION-HANDOFF-LATEST.md) · [唯一生产状态](PRODUCTION-STATE.json) · [R01严格审查](R01-REVIEW.md) · [证据索引](EVIDENCE-INDEX.json)

## 已落地
使用本公开仓库的标准Ubuntu Actions与Blender4.5.13 Cycles CPU；完成能力预检、R00整体场景、一次有真实图像依据的R01结构修订。单个巨环、内侧城市、船坞、货运舰、检修栈桥及货运路径均为三维对象/可追踪实例，不是参考图贴在平面上。

R01交接文件包括.blend、独立构建源码、13张真实结构观察、逐图相机/参数/hash、构建和渲染日志、资源统计。原始PNG最高960×540（近景800×450）；不是合同要求的2560/1920终版图。场景里预设的最终画幅不能当作已完成渲染。

## 尚未完成
G1校准与参考完整归档；G2全观察审查与设计冻结；船舰与船坞的清楚读形；中近景专业工艺；三张规定成片；全部缺陷关闭和G6冷恢复。当前没有阶段best，只有可恢复候选。完整主合同与本轮原始参考在聊天交接包，公开工程没有复制私有Leaf历史。

## 文件入口
- build_scene.py：已实测R00独立生成源码。
- build_scene_r01.py：已实测R01独立生成源码；render_r01.py：真实观察渲染。
- prepare_r01.py、R01-INTERVENTION.json、R01-SOURCE.diff：有校验的R00→R01差异。
- output/r00与output/r01：实际.blend、PNG和不可变候选证据；当前以PRODUCTION-STATE.json与评审裁决为准。
- DEPENDENCIES-AND-ASSETS.json：锁定Blender与原生资产来源。

## 已结束的实际Actions
[G0能力预检](https://github.com/yangerstar1/future/actions/runs/34486735492) · [R00场景与观察](https://github.com/yangerstar1/future/actions/runs/34488579285) · [R01修订与回归](https://github.com/yangerstar1/future/actions/runs/34490878728)

3个job合计365秒，按作业起止时间统计。未启用付费算力、第三方模型API、Release、Pages或自动循环渲染。其他项目分支和main不在本任务写入范围。
