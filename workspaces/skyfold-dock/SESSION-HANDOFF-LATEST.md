# 《回天港》当前恢复交接 — R01 未达标候选

## 先读取
以PRODUCTION-STATE.json为唯一当前状态，再读EVIDENCE-INDEX.json、R00-REVIEW.md、R01-REVIEW.md、R01-INTERVENTION.json及对应OBSERVATIONS.json。主合同是用户附件SKYFOLD_DOCK_PRODUCTION_CONTRACT_V1(1).md，SHA256 b29cc86937c4667652de7a954871c940e31e1c6493c34575ab8f84db970f7ea7。完整原件保存在本轮聊天交接包；它尚未在公开工程归档。新上下文需要原件时，先用Files检索该上传文件，不重新发明另一份合同，不迁出私有Leaf历史。

## 已经真实完成
G0只读核对及官方Blender4.5.13校验安装、CPU渲染、保存和新进程重开。一次真实原生生图得到参考A，未验证底层型号，不称其已确定使用Images2.5。R00与R01均有可编辑.blend、构建源码、原始PNG、相机矩阵、hash和成功Actions日志；R01有13张观察图，含五时点真实相机位移和旧机位诊断。

最新实际场景：output/r01/skyfold-r01.blend，773347字节，SHA256 84f4e77811724dc632de8abd3885b0a87783ccc937b45f2f82473a544e3fb42a。
实际场景源提交：6fc8f1a73640d18084231e5c58670c72b031ddb9；构建源码SHA256 1bb627df3637886da7e2d89107d6230e1caec87a50501c1d2e0eeb1a2b11249b。后面的文档/未改变工件迁入提交不是新的渲染来源。

R01包含单个有厚度巨环、1137个共享原型城市实例、船坞、货运舰、检修区及交通连接。数量只用于资源和完整性定位，不证明美术达标。主体没有使用参考图投影或生成式修补。

## 当前明确未通过
G1评价校准及完整参考归档仍缺；G2主视觉仍未达标，DESIGN_BASELINE未冻结，best=null。主要问题是货运舰与船坞轮廓混在一起、倒悬城市的视觉身份不足。近景轮距与悬空错误已改源码但还没完成图像复验；禁止标FIXED。G3至G6未通过，规定三张2560/1920成片尚未制作；当前PNG是低成本观察图。机器终态不是AUTO_QUALIFIED。P2视频未选做。用户未接受任何版本。

## 下一步
先读取R01的第二视角、旧相机、O02/O03/O04/O05及五张O06；补齐G1校准。优先把舰体从船坞框架中分离为可读的大形，改善城市从侧壁翻向头顶的剪影。改动建议必须以实际场景和新增观察为准；不要先加螺丝、雾、粒子或大行星。保留当前R01与R00，继续普通内部选择不设用户逐轮审批。

## 真实命令与注意
以下链路已在新GitHub runner成功执行，Blender进程之间无GUI共享状态：

```bash
export SKYFOLD_OUT="$PWD/workspaces/skyfold-dock/output/r01"
export GITHUB_SHA=6fc8f1a73640d18084231e5c58670c72b031ddb9
python3 workspaces/skyfold-dock/prepare_r01.py
blender -b --factory-startup -t 4 --python-exit-code 1 -P workspaces/skyfold-dock/build_scene_r01.py
blender -b "$SKYFOLD_OUT/skyfold-r01.blend" -t 4 --python-exit-code 1 -P workspaces/skyfold-dock/render_r01.py
```

上述GITHUB_SHA只用于重现未修改R01。编辑源码后必须记录新真实版本/工作区签名，不复用旧来源。prepare_r01.py严格从已知R00重新生成R01，会覆盖同名生成源码；它和skyfold-r01.yml是R01复现链，不应拿来验证未经适配的新候选。已有独立build_scene_r01.py可供新候选派生。不要重跑已通过G0，不要从G3开始，不要覆盖旧项目。

## 算力与工具
3个公开ubuntu-24.04标准CPU作业已结束：G0 34486735492（34秒）、R00 34488579285（186秒）、R01 34490878728（145秒），合计365秒，即约0.101389 runner-hours，按GitHub作业起止时间计算，不是账单结算值。48小时规划上限尚余约47.898611小时；9.6小时收尾预留未动用。峰值并发1。未启动付费runner、外部模型API、Actions artifact/cache存储或Release。

本地Codex桥bootstrap返回404；当前连接器对二进制blob的直接读取返回UTF-8错误，聊天容器不能联网拉取。已用带Git blob校验的小JPEG成功建立低分辨率观察通路，但全尺寸检查仍未完成。不要把这解释为所有图都看过，也不要用文本日志代替视觉判断。实际.blend与PNG已在公开仓库可取回，不仅保存在临时Actions artifact。当前没有运行中的作业或另行部署的后台代理。
