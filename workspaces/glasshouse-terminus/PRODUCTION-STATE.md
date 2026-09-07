# 雨幕终点站 — 当前制作状态

更新：2026-09-07，G3-R01运行中。本页当前状态优先于EVIDENCE-INDEX.json中尚未更新的G3 NOT_STARTED字段；G2 BEST仍以该索引及G2-REVIEW-03.md为准。

权威合同：《雨幕终点站》v1.0，SHA-256 `0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`。保持原创雨夜花房车站、A–E范围、最终原生4K主片与同源网页要求。用户已再次要求通过GitHub继续制作，不需要重做G0/G2。

## 当前制作事实

- 仓库 `yangerstar1/future` 公开；制作分支 `codex/glasshouse-terminus`。本次GitHub返回push权限，读取与Actions状态获取正常，不能沿用旧会话的“GitHub无执行入口”结论。
- G3制作源码commit：`cf89b07e0e3831d892e742083c7e75a05c285525`。
- 实际Actions运行：`34113862241`；job：`101716020299`。
- 已完成：恢复确切G2 BEST与G1素材、工具安装、两类选定模型下载、在原场景内建造一跨G3候选、渲染前持久保存可编辑候选。
- 当前：正在新进程渲染雨夜/中性照明总览及原C03语境；细节图与实际门状态随后由同一有界工作流执行。
- 本轮尚未取回G3原图，不宣称视觉通过，不放行G4。

## 已有G3恢复点 — 不是G3 BEST

证据分支 `evidence/g3-source-34113862241-1`，commit `0dc1d2e9df7d044081a82756218250a4ddd6bfa2`。

目录：`workspaces/glasshouse-terminus/output/g3/`。

主工件：`g3-bay-candidate.blend`。持久build-report记录摘要 `e95b37d7f2d8a28efc8bca32815b0624acae7a787e2c7bbe7565eb30e3588027`；本次已读取报告，完整工件实际下载后的字节核验仍待完成，不将报告摘要冒称下载核验。

实际复用：G1处理过的walnut/slate材质；Poly Haven的GreenChair_01及potted_plant_01。已读取实际MODEL-SOURCES.json，记录下载11,114,639 bytes、作者、来源、许可、依赖和逐文件摘要；模型已经导入，不只是列在计划里。来源许可再次核对官方页面，预览照片不纳入工程。

build-report显示原保护几何/机位在基准帧的摘要前后一致；这不能代替全时域运动与原图审查。

## 保持G2 BEST

- 标识：`G2-BEST-20260907-R01`，同上下文图像/运动自审阶段通过，不代表用户最终接受。
- 完整证据commit：`6520a8b6056cd7582e4bfc09367cd37fdfb193a1`。
- 主工件：`workspaces/glasshouse-terminus/output/g2-review/g2-complete-whitebox.blend`。
- SHA-256：`0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be`。
- 成功运行 `34109215120`；完整九图及28秒640×360/10FPS白模预演已审查。白模不是最终4K影片。
- G1素材持久证据：`0615e137cd53b3e3a150979b1a17d2d9c818eafb`。

不覆盖上述证据分支；main和Leaf保持不变。

## 本轮预算与门槛

沿用g3-request.json：公开标准ubuntu-24.04 runner，单并发、单次运行≤60分钟、外部支出零、下载≤1.5GB、工作盘≤8GB、证据≤180MB，计划制作上限45分钟，预留15分钟保存/取回/审查。不另开重复G3任务，不从白模速度推算最终4K影片成本。

需要取回并审查：雨夜/中性总览、原C03、D01/D02/D03/D05/D06、反向图、停稳/开门过程图；重新打开、外部图片缺失、原始帧391–660通行射线、地板及列车/车门时序证据。只以实际图像与可恢复工件决定G3门槛，CI成功不自动通过。

## 尚未完成与边界

G3质量候选未验收；G4全场精修、G5完整事件与最终电影、G6同源网页、G7完整回归未完成。桥拱接头V形缝仍留在最终问题清单。

G1/P1浏览器 `BLOCKED_BY_ADMINISTRATOR` 保持不变；不清除认证、不改安全配置、不换工具绕过。P0离线制作继续，不删除P1，也不宣称完整任务完成。

历史状态与详细G2恢复记录保留在commit `b9834ccd9c06e8ea0b6c443524c62329d35fdb8f` 的同名文件。当前G3制作入口为已存在的build_g3.py/render_g3.py及glasshouse-g3.yml；下一动作是取回本轮产物，不是重新读取合同后退出。
