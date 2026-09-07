# 雨幕终点站 — 当前续作入口

2026-09-07。权威合同 v1.0 SHA-256：`0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`。

**当前是 G3-R05 已完成局部制作与六张原图审查，状态 PAUSED_UNMET。G2 完整白模 BEST 不回退；G3 尚未达到最终质量样板门槛，G4 不放行。** 以本页、EVIDENCE-INDEX.json 和 G3-R05-REVIEW.md 续接，不据历史“运行中/NOT_STARTED”标签重建工程。视觉精美度优先；文件、日志、CI 与摘要不代替美术。

## 当前可恢复的最新候选

- 制作源码：`8a5eb925c4e88c4155b2148059898b3736386895`。
- Actions：`34128911415`，job `101764327257`，已完成且 success；这仅证明本轮执行完成。
- 入口：`relight_g3_nodes.py`、`.github/workflows/glasshouse-g3-node-light.yml`、`g3-node-light-request.json`。
- 源 checkpoint：`ee77c110f190f7b944dbe8fb2455f87296a76b96`。
- 完整结束证据：`4436b5cb5f870e834ff65639d1a1fbd365b9d4e3`，分支 `evidence/g3-r05-34128911415-1`。
- 主文件：`workspaces/glasshouse-terminus/output/g3-r05/g3-bay-candidate.blend`，26,457,653 bytes，实际 SHA-256 `8ca4ca940a98e80d980fbd895f5ae7c27568b28ee361422bfe4ed267b7b8f02e`。
- Artifact `10021873685`，34,863,936 bytes，实际 ZIP SHA-256 `3aea7bc1c9a85bea8f833522b40106b274f21c6c41191df5b05a9948fc2698d3`；19个清单条目全部匹配，六张PNG均已逐一查看。新进程重开无缺失外部图片，渲染后master未改。临时artifact只有一天保留期，长期恢复使用上述Git提交。

实际改动：在原R04上校准选定主拱/立柱/柱帽/拼接板的缎面漆，并加入两组有实体落地支承的局部上照灯。复用原家具、植物与材质，不重建整个场景。原相机、运动、曝光0与玻璃响应保留。

## 当前视觉判断

原42mm近机位与完整样板夜景的巨大摄影灯白斑没有回来。柱面的绿色漆质和部分截面更清楚，木材、软包、陶盆与金属有不同响应。无遮挡车门观察仍能看清导轨、门扇、门槛和真实前室。以上是可见的局部进步，不是完整G3通过。

**首要未解决问题：D01-roof-node 上部主拱腹板与拼接板仍近乎黑色。** R05柱脚上照改善了柱面，但没有充分恢复上部节点；不能以其他画面改善、增加灯具或工作流成功抵消。具体遮挡物/入射方向还没有经过实际光路诊断，不把猜测当结论。

木作侧面与曲边纹理方向仍在工艺复核清单。样板外白模是尚未扩展的区域，不得宣传为全场成品。完整评审见 `G3-R05-REVIEW.md`；R04的19张独立证据不能冒称R05新渲染的19张。

## 下一动作

从校验实际字节后的R05 master继续，先只读检查灯源至上部拼接板、腹板和观察面的首命中物体、遮挡与受光方向。取得证据后才决定局部灯具安装点、方向或构造调整；不盲目继续增大同一盏灯功率，不改曝光、不裁掉失败机位、不移动模型给镜头让路。

后续仍只针对该可见缺陷进行有界修正，保留原D01、原42mm机位、完整样板夜景/中性对照。若节点更清楚但引入烧白、大片玻璃反光或破坏雨夜主次，仍判未通过。真正达到样板门槛后才按合同顺序进入G4。

最近成功的渲染命令来自上述实际R05工作流（仓库根工作目录，先恢复确切父工件并安装锁定工具）：
```bash
G3_NODE_MODE=render G3_NODE_DEADLINE=<工作流记录的Unix截止时刻> blender -b workspaces/glasshouse-terminus/output/g3-r05/g3-bay-candidate.blend -t 4 --python-exit-code 1 -P workspaces/glasshouse-terminus/relight_g3_nodes.py
```
`G3_NODE_DEADLINE`不是新假定常量，实际由工作流在开始时设置；不得在未知环境忽略准备步骤直接运行。

R05本次请求上限为30分钟job、23分钟生产、7分钟保存取回，公开标准runner、单并发、外部支出零。该单次请求已执行结束；本页没有自动追加新的渲染。下一次执行须记录有限预算，沿用既有授权，不把已结束请求理解为无限重跑许可。

## 保留的历史恢复点

R04完整证据：`cd3526f4a0f6f8333d75bbd666b4fcfcfa9a529a`，源checkpoint `a2b7d9d3c90e928a00bca7898247d764c83afe8a`；root `workspaces/glasshouse-terminus/output/g3-r04`；master SHA-256 `18348be4c401601706e10e4346a32bf5e0c406fec2448e1a53290f7840b8a854`。其19张原图及35项清单已审，详见G3-R04-REVIEW.md。不得混用另一路失败的art-r04运行34125276363；其失败记录和已取消的重复恢复请求均保留在索引。

G2 BEST：`6520a8b6056cd7582e4bfc09367cd37fdfb193a1` / `workspaces/glasshouse-terminus/output/g2-review/g2-complete-whitebox.blend`，SHA-256 `0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be`。G1素材：`0615e137cd53b3e3a150979b1a17d2d9c818eafb`。所有父工件、失败图、原相机、main与Leaf均保留。

G1/P1浏览器 `BLOCKED_BY_ADMINISTRATOR` 仍未解除，不清认证、不改安全配置、不换工具绕过。全场精修、桥拱收口、原生4K30主片、短版、证据片和同源网页仍未完成；不缩减原合同。所有评审为同上下文实际原图自审，用户最终接受仍为false。
