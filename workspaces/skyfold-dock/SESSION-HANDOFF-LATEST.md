# 回天港恢复交接 — R04C 视频已完成，R05B 城市实验已复验

先读 PRODUCTION-STATE.json、R05B-REVIEW.md、R04C-MOTION-REVIEW.md、R04C-TARGET-SIZE-REVIEW.md、EVIDENCE-INDEX.json、RUN-LEDGER.json。不要再沿用动画运行中、拼接排队或 R05 仅有源码的旧状态。本轮相关作业全部成功结束，没有活动渲染或待执行后台代理。

## 当前双版本工件

**可编辑工作场景 R05B**：output/r05b-city/skyfold-r05b.blend，2382725 字节，SHA256 890c7d7d166371fb59627d1ab43bacae36a031c81f3a3eebc5de418e7cb363f2。源提交 d00012b9bf8574d950a71803ab1cbd908237e26a；run 34515248217。带控制图及 11 张低成本候选观察，保留为技术工作候选，未晋级。

**完整呈现检查点 R04C**：output/r04c-assembled/source/skyfold-r04c.blend，SHA256 831c51340a7c81012e517d4ea0ce0da4a6412a1d86940ad74c7a7f0b1f760261。stills 子目录有 2560×1440 主图、两张 1920×1080 及八张结构图。视频 Skyfold_Dock_R04C_Motion_720p.mp4 为 1280×720、192 帧、24 fps、8 秒、无音轨，SHA256 15848f4d744c53cc6f1175fd1ab79a3c6ed212b82ad2d8b522704c64e8fa87a0。原渲染 run 34507267207，拼接 run 34510781990，均已完成；不重开这一批。

视频属于 R04C，不包含 R05/R05B 后续城市修改。不要把两版混称成同源最终交付。已保留所有帧 hash/矩阵/日志和部分原始 PNG，不声称保存了全部 192 张原始 PNG。

## 结果与下一动作

G1 校准证据仍不足，G2 未冻结；G3–G6 未通过，best=null、AUTO_QUALIFIED=false、USER_ACCEPTED=false。城市的规则内壁感、舰体与近景工艺、运输接口、旧失败机位遮挡仍是具体未通过项。视频虽技术完整，前景尺度很快消失，完整 24 fps 时域闪烁未取得充分视觉证明；720p 不是合同 1080p P2 通过。

两轮城市局部修改没有充分解决宏观观感。下一步先做一轮有明确假设的跨环取景诊断，保护原场景及失败机位，对照舰体侧面长度、城市连续上翻弧线和前景持续可读性；不要继续沿环轴拍出大黑洞后堆楼。新机位未执行，也未冻结。只有这一关系成立，才处理工艺和新的高成本序列。

## 真实复现入口

使用锁定 Blender 4.5.13 LTS / Cycles CPU；provision.sh 保留官方校验链。在仓库根目录运行，输出必须放到新的空目录，不能覆盖归档。

```bash
export SKYFOLD_OUT="$PWD/workspaces/skyfold-dock/output/local-r05b-recheck"
export R05_PHASE=candidate
export GITHUB_SHA=d00012b9bf8574d950a71803ab1cbd908237e26a
blender -b workspaces/skyfold-dock/output/r05b-city/skyfold-r05b.blend -t 4 --python-exit-code 1 -P workspaces/skyfold-dock/render_r05_city.py
```

以上是已有成功的新进程渲染调用改为独立输出目录；GITHUB_SHA 只适用于未改动的冻结脚本。改代码后记录新签名，不冒用旧来源。R05B 从快照重开不是 G6 完整冷启动终验。

重建 R05B 时，revise_r05b_city.py 要求精确 R05 输入及相邻 BUILD-MANIFEST：scene hash cf54a7be3f679643ff6abd54ca438389bdf4654c206b53bdebca9205d80249c1；它们在 evidence commit 99e13a9a9a86627fa640196c700016c4048daac5 的 output/r05-city，也在聊天恢复包内。脚本还依赖经 hash 核验的 revise_r05_city.py 与 build_scene_r01.py，不要删除断言强行套用。

R04C 重渲染使用其 source/.blend 与相邻 manifest、render_r04.py 的 stills 或 motion 模式。现有成片已取回，无必要不重跑。拼接验证入口为 assemble_r04c.py，不渲染新帧。

## 保存与资源

原始合同及生成参考 A 随聊天恢复包交付，底层生图型号未核实，不复制私有 Leaf 历史。当前 R04C 和 R05B 工件已经并入生产分支，并有聊天下载包，不只依赖一天有效期的 Actions artifact。

全任务已结束 19 个 job、16 个 run，共 11749 作业秒（3.263611 runner-hours），实测峰值并发 2；48 小时规划上限尚余约 44.736389 小时，9.6 小时为收尾预留。不是账单、不是聊天耗时，也不以凑满预算为目标。未启动付费 runner/模型 API、Release 或 Pages；账户总存储费用未暴露，不声称免费存储无限。
