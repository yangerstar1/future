# 回天港恢复交接 — R08B 已渲染与审查，无活动作业

先读 PRODUCTION-STATE.json、R08B-REVIEW.md、TRACKING-DELIVERY-REVIEW.md、EVIDENCE-INDEX.json、RUN-LEDGER.json。不要沿用旧“tracking 或 R08B 正在运行”的标记，不重跑 G0，不重复已完成影片。

## 当前工作工件

output/r08b-native/source/skyfold-r08b.blend，与相邻 BUILD-MANIFEST.json。场景 SHA256 e714356e215b7e857adaf29c224cb8d9261ab094f74cfb5e11ada45e0e05d877，场景生成源 4987ec9eeed2d632acb35863f7f7834f380e7aa2。相同场景也在 output/r08b-context 中，含首尾及中性观察。

主图 output/r08b-native/R08B_HERO_2560.png，2560x1440，SHA256 ba1f752872d38829ddb71727cf9e02d83feb2ca6fe4dda8e03aad8ce0a597ad7。无合成对照 R08B_RAW_1280.png。原生渲染源 529dad6da328fdc8296e05cc300b9e32f206779c；run 34583100587 成功。渲染参数与实际矩阵在 OBSERVATIONS.json，不把归档提交冒充渲染来源。

当前是工作候选，不是阶段 best 或成品。G1 部分完成、G2 未冻结、G3–G6 未通过，best=null，auto_qualified=false。楼群重复与远城纹理化、舰体原始体感、人类尺度前景和完整功能接口仍有重大缺口。不要只加灯带/更多小楼或无限换镜头。

## 已完成的旧影片

output/tracking-delivery/Skyfold_Forward_Flight_1080p.mp4：旧 R07B 外部跟拍，1920x1080、24fps、192 帧、8 秒、无音轨；SHA256 f2c30462e9c9850599f43bd82a3dbcbed710cd9e87c4219695f254d265f34ce8。run 34559500985 的全部七个 job 成功，126 清单文件已核验，全部视频帧重新解码并与原分片核对一致，PTS 连续。

该电影不是 R08B。R08B 保留 192 帧可编辑动画，但本轮只渲染静帧/端点，不冒称新整段已完成。

## 可复现命令

下列命令对应实际成功的 native workflow。需相同官方 Blender 4.5.13、Linux 依赖；provision.sh 需要联网并可能使用 sudo。先保护源和旧输出，在仓库根目录建立新输出目录：

```bash
export GITHUB_SHA=529dad6da328fdc8296e05cc300b9e32f206779c
export GITHUB_RUN_ID=local-r08b-replay
export SKYFOLD_OUT="$PWD/skyfold-r08b-local-replay"
mkdir -p "$SKYFOLD_OUT"
blender -b workspaces/skyfold-dock/output/r08b-native/source/skyfold-r08b.blend -t 4 --python-exit-code 1 -P workspaces/skyfold-dock/render_r08_snapshot.py
```

这个来源标签只用于未改源码重放；修改源码后必须写真实新来源，不冒用旧 SHA。脚本会设置输出路径，不依赖 .blend 中遗留的 runner 绝对输出路径。当前已在新 runner/新 Blender 进程重开并渲染，但原合同要求的全项目 O08 冷恢复仍未完成。

重建 R08B 使用 r08_refine_frame.py，必须输入精确 R08：2636f1582b1bdbd0d60ab08428f29f8ccc85b27aa2c52086832876aa30eaa6e4；在证据 commit 6cf46e7391357341916c073f9359db5fc583a8b7 的 output/r08-context。聊天恢复包也包含该输入。R08 的父输入是已交旧影片源场景 e9ffbb9051f27fe6c19d6ff7069cd5f419b9517e3b4ee2b0d0f889845e8086c6。不要移除输入 hash 断言。

## 保存范围与资源

生产分支包含旧完整跟拍交付、R08B probe 和 native 输出；失败 R08 在对应证据分支及聊天包，历史 R00–R07 通过索引/旧提交恢复。不是每一轮的全部历史 PNG 都复制到主分支。旧影片保存所有编码帧、所有源帧 hash/变换和选定原始 PNG，不保留全部未压缩序列。

本轮三次 R08 作业合计 617 秒；全任务 37 个已结束 job、28 个 run、20575 秒，约 5.715278 runner-hours。上限48h、收尾预留9.6h、峰值并发2；这是作业时间而非账单或对话耗时。没有活动/排队作业，没有后台代理、付费 runner/API、Release/Pages。账户总存储费用未知。

下一步保留选定低位机位，修城市与舰体可见轮廓/工艺，先同机位验证再决定是否做新完整影片。旧核心规格、缺陷和恢复验证不因用户要求飞行镜头而自动通过。
