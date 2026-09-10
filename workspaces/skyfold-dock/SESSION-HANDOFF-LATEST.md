# 回天港当前恢复交接 — R03B 已复验，G2 仍未通过

先读 PRODUCTION-STATE.json、R03B-REVIEW.md、EVIDENCE-INDEX.json、RUN-LEDGER.json。不要沿用旧 R01 或 R02 正在运行的状态，不重跑 G0，不直接进入 G3/G4。

## 可恢复工件

当前 output/r03b/skyfold-r03b.blend，1203557 字节，SHA256 dca722c1cbfada7ce9a5a9b16926b136a29fd1ee256d5073c9b41852e5c64c68。
真实渲染源提交 3bf60dbd37a451ea097e67666b9d922ddd4f877b；Actions 34500065780 已成功结束；后续归档提交不是新的渲染来源。
完整 18 张原始 PNG 与日志在已取回的聊天包 skyfold-r03b-observations.zip 和整合恢复包 Skyfold_Dock_R03B_Checkpoint.zip；仓库 output/r03b 仅保留选定五张 PNG、场景及完整清单/日志，不宣称所有历史图都进 Git。临时 artifact 10161747801 于 2026-09-11T16:14:20Z 到期，不是唯一保存介质。
主合同原件/hash 与生成参考 A 随聊天整合恢复包交付，没有复制私有 Leaf 历史。原图模型底层型号未核实，不能写 Images 2.5 已验证。

## 已完成的局部闭环

R03 降低近侧平台 240 米，同步支撑、轨道、货物、入口升降台，并保留远侧高平台与舰体接口；R03B 修正上层回程轨道端点和新增相机的清单矩阵。原 R02 16 个观察的相机、焦距、尺寸、采样与合成状态逐项保持；18 个实际相机矩阵通过新进程验证，下载后 29 文件哈希与 18 PNG 解码通过。
实际主图、中性版及五时点观察确认舰体不再被平台整体挡住。新增回程升降图仍裁掉上下落点；轨道端点已通过技术坐标检查，但整条运输链未完成视觉终验。不要把代码修正冒充完整接口关闭。

## 明确未通过

best=null，G2 未冻结。主构图空白过大、城市在边缘、人类尺度前景过弱；城市重复感与近景工艺仍未到要求。B/C 和旧 R01 机位已观察，但未偷偷替换主机位。G1 正式校准与优良锚点仍有缺口；当前只是真实顺序自审。三张规定成片、全局缺陷关闭、G4 终版成本门和 G6 冷恢复未完成。P2 未选做，用户未接受任何版本。

## 实际成功命令

以下在上述源提交的新标准 Ubuntu runner 中成功，Blender 为锁定的 4.5.13 LTS，Cycles CPU。重新执行时先另建工作副本保护已有输出。

```bash
# 已安装相同 Blender 后，从已核验的当前场景重渲染
export GITHUB_SHA=3bf60dbd37a451ea097e67666b9d922ddd4f877b
export SKYFOLD_OUT="$PWD/workspaces/skyfold-dock/output/r03b"
blender -b "$SKYFOLD_OUT/skyfold-r03b.blend" -t 4 --python-exit-code 1 -P workspaces/skyfold-dock/render_r03b.py
```

重做 R03B 修正需要精确 R03 输入：evidence/skyfold-r03-34498166928-1 中 output/r03/skyfold-r03.blend 与 BUILD-MANIFEST.json，场景 hash e1f8815c36bb30b8c245715fb56fd9c3a38c77955535ea99b4011170a95d4787。实际 skyfold-r03-qa-fix.yml 使用 git fetch/restore 取得它；聊天整合恢复包已包含这些输入。finalize_r03b.py 的源场景 hash 断言不能盲目移除。修改源码后记录真实新源版本，不能继续冒用上述 GITHUB_SHA。整链从参数重建后逐字节完全相同未被证明，不把快照重开当作 G6 终验。

## 下一步与预算

优先在现有主题内修近景栈桥—船坞—连续内翻城市弧线的构图关系；复用已有几何/机位，不加新的泛化框架或微装饰。保留当前舰体显露和原失败观察用于回归。升降链补包含上下落点的观察，不能用新裁切图宣告完整运行。

八个已结束 job 共 1648 秒，约 0.457778 runner-hours；本轮 R03+R03B 共 835 秒。48 小时为已记录规划上限而非消耗目标；9.6 小时收尾预留未消耗，峰值并发 2。没有本任务活动作业、自动后台代理、付费 runner/API、Release 或 Pages。账户总存储账单未暴露，不声称零存储费用。不要重做已通过链路或改其他项目分支。
