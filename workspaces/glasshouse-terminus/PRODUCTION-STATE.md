# 雨幕终点站 — 当前制作状态

更新：2026-09-07。本页与 EVIDENCE-INDEX.json、G2-REVIEW-03.md 是当前交接入口。旧会话里「Future未执行」和「G2仍在运行」均不能代表当前状态。

权威合同：《雨幕终点站》v1.0，SHA-256 `0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`。完整合同已取回核验并阅读；不改变主题、A–E范围或最终4K要求。

## 当前门槛

| 项目 | 状态 |
|---|---|
| G0 | 制作入口已验证；不重新开始 |
| G1 | P0风险样板允许继续白模；完整G1未全部通过，P1浏览器仍BLOCKED_BY_ADMINISTRATOR |
| G2 | `G2_STAGE_GATE_PASSED_SELF_REVIEW`，已建立完整白模阶段BEST |
| G3 | 尚未开始，下一制作段为一个最终质量样板 |
| 完整任务 | `PAUSED_UNMET`，不是最终成品，不是用户ACCEPTED |

G2结论来自实际九个固定原图、同条件修正对照、覆盖全部280帧的联系表和关键原生帧、真实工件/重开与事件检查；不是CI绿灯或自评分。评审为同上下文自审，独立代理不可用，用户尚未验收。

## BEST与恢复入口

- 阶段标识：`G2-BEST-20260907-R01`。
- 制作源码：`91d414fb8ac9aadf74e5a86d4fc74f9ac7ab234a`。
- 成功运行：`34109215120`；job `101702897010`，已完成，不再等待。
- 持久完整工件分支：`evidence/g2-repair-34109215120-1`。
- 持久完整工件commit：`6520a8b6056cd7582e4bfc09367cd37fdfb193a1`。
- 工件根目录：`workspaces/glasshouse-terminus/output/g2-review/`。
- master：`g2-complete-whitebox.blend`，实际字节SHA-256 `0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be`。
- 完整ZIP artifact：`10014580129`，25,784,156 bytes，SHA-256 `5bef8306c0ed602b8f176366377a98590a740fee26ce4554c9b7f464dac8702d`。临时artifact只保留1天，长期恢复使用上面的Git证据commit。
- `whitebox-28s.mp4`：原生640×360、10FPS、280帧、28秒，Blender Workbench低成本预演，不是最终4K影片。
- `C01.png`至`C09.png`：原生1280×800、24samples、Cycles固定观察。机位/焦距/曝光/基准时刻/色彩管理以BEST主工件及render-metrics.json冻结。

父白模与失败观察没有覆盖：`453a74c1d0eb668ed483219eb684bf57798d4a8c`。修正仅处理主构图裁切及共享桥墩重复/错向连接，保护既有A–D、轨道、列车/门/步行事件和材质。细节见三份G2审查记录。

## 本轮失败与恢复事实

原G2运行 `33930258391` 的建模/渲染已成功，但证据分支继承工作流文件，推送被权限检查拒绝；临时工件后来过期。本轮复用已有publish_evidence.sh，写数据专用唯一证据分支，没有提高workflows权限。

恢复运行 `34106817235` 保存了九图与master；其17分钟预演步骤超时，只有278帧，因此不算完整视频。之后依据原图缺陷只进行一次定向修正，运行 `34109215120` 的固定图、新进程重开、完整预演、持久保存和回传全部完成。完整下载工件的65项清单摘要均匹配；原partial日志摘要异常没有混入新BEST。

## 已核验和仍未通过

G2已核验：A–E低成本骨架、完整正反面/车厢、九视图、28秒预演和实际「主厅→站台→停稳列车→车厢→回望主厅」空间链。源帧301停稳，314仍关门，315开始移动，348开门完成。抽样通行射线无碰撞记录，18个地板检查命中真实地面；这是抽样诊断，不是所有路线的穷尽人体碰撞证明。

前三项待解决：
1. G3真正最终质量样板尚未制作：白模玻璃、木作、座椅、植物与湿区不是最终材质/资产。
2. 桥拱接头近景仍有V形缝；最终细节镜头及开门动作可读性仍需后续完善，不能在最终验收清单中消失。
3. G1/P1浏览器仍被管理员安全检查阻断。未清认证、改安全配置或换工具绕过；网页不能从完整任务删除。

最终4K30主片、12秒短版、15–20秒证据片、同源网页、完整质量回归与用户验收均未完成。

## 下一动作和有限资源

下一段先读G3-NEXT-STEP.md与本次审查，从核验摘要后的G2 BEST继续。先做现有主厅临站台、门洞所在x=-4至0的一个结构跨，完成中性/目标雨夜照明下的C03局部及D01–D03/D05近景；样板未通过不批量扩展。

本轮公开标准runner、单并发、外部支出零。恢复及定向修正分别有界，定向修正请求限定一次、job60分钟内；此请求已执行结束，没有未声明的后台G3作业。后续G3制作/渲染/下载预算未启用，必须按实际场景吞吐另行记录，不把白模速度外推为4K成片速度。

最近成功的云端核心命令（工作目录为真实runner仓库根）：
```bash
blender -b workspaces/glasshouse-terminus/output/g2/g2-complete-whitebox.blend -t 4 --python-exit-code 1 -P workspaces/glasshouse-terminus/refine_g2.py
G2_OUTPUT_ROOT=workspaces/glasshouse-terminus/output/g2-review xvfb-run -a -s '-screen 0 1280x720x24' blender -b workspaces/glasshouse-terminus/output/g2-review/g2-complete-whitebox.blend -t 4 --python-exit-code 1 -P workspaces/glasshouse-terminus/render_animatic.py
```
这些命令来自成功工作流；单独执行仍需按该工作流准备确切父工件、工具和输出目录，不能在未知环境盲跑。

## 历史G0和参考矩阵

2026-09-05的完整只读侦察、工具探针与已看参考矩阵保留在[历史状态原文](https://github.com/yangerstar1/future/blob/91d414fb8ac9aadf74e5a86d4fc74f9ac7ab234a/workspaces/glasshouse-terminus/PRODUCTION-STATE.md)，其中阶段标签属于当时，不再代表当前。

已验证历史环境：真实runner工作根`/home/runner/work/future/future`，4逻辑CPU、16,766,414,848 bytes RAM；Blender4.5.13LTS、Cycles CPU；固定工具探针保存/新进程重开逐像素相同。后续runner资源可能变化，不保证磁盘每次相同。浏览器探针为软件渲染，不冒充独显性能。

G1持久副本仍为`evidence/g1-recovered-33930445031-1` / `0615e137cd53b3e3a150979b1a17d2d9c818eafb`。Leaf与main保持不变，所有制作和状态写入仅在本任务分支及新证据分支。
