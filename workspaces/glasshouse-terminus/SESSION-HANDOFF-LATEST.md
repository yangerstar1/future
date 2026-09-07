# 雨幕终点站 — 最新会话交接

更新时间：2026-09-07。仓库 `yangerstar1/future`，制作分支 `codex/glasshouse-terminus`，工作根 `workspaces/glasshouse-terminus`。

## 当前实时状态

**R05 只读光路诊断已实际完成；R06 局部修正已保存并在新进程渲染。G3 未放行，G4 禁止。** 最新可恢复但尚未审图的候选为 R06；最近已完整审查的候选仍为 R05 / PAUSED_UNMET。不要重做 G0/G2，不要从 G3 NOT_STARTED 开始，不要重复启动 R05/R06 请求。

此段是运行中 checkpoint，不是完成或用户验收。当前唯一 R06 运行：`34134897722`，job `101783432648`，源码 `2ab0070ad8a6ed7ba89cd16d2096724828abd06a`。已核实安装、构建、源工件保存步骤成功；六张原尺寸图像的渲染步骤仍在运行。先核对该运行最新结果，不另建重试。

## 已保存的 R06

源 checkpoint：`310f07c71dcf63db9a6e8e333bebd289717aae0f`，分支 `evidence/g3-r06-source-34134897722-1`。

根目录 `workspaces/glasshouse-terminus/output/g3-r06`；主文件 `g3-bay-candidate.blend`。构建报告记录 SHA-256 `65ef58c38685aa6ef26aa0f2d5116e1535e879f4a2b01975100d71be7cb7de26`。**该新 master 的本会话下载字节核验及实际原图审查尚待结束包，不能冒称已做。**

入口：`relight_g3_upper_nodes.py`、`.github/workflows/glasshouse-g3-upper-node.yml`、`g3-upper-node-request.json`。这是本会话实际新增的局部流程，不是原先已有入口。

具体干预：在既有 `Longitudinal_roof_purlin.001` 上夹持两只紧凑射灯，36W/盏，以斜向下光路照亮一跨两端节点；保留 R05 柱脚灯、原材质、原结构、玻璃响应与全部旧相机。先核对真实安装面、目标受光和灯壳自遮挡，再保存。原对象几何/绑定材质名/射线可见性、旧灯参数、相机参数及七个关键帧对象变换的前后摘要一致。此检查不等于像素审美通过。

保存后新进程固定帧451、曝光0、AgX实渲六个观察：D01-roof-node、完整bay夜景、D01-glass-metal、原42mm bay、中性bay、无遮挡D05。完成时将发布 `evidence/g3-r06-34134897722-1` 和 artifact `g3-r06-34134897722`；此时尚未核实其存在，恢复者应先查询实际结果。

## 已完成的 R05 根因诊断

运行 `34134203847`，job `101781208601`，源码 `05119473ea654ffbe49b1d3887b33e6bf6484a4b`，全部成功。持久证据 `4cb68d0db15031059ea05054847ae75491569e64`，目录 `output/g3-r05-node-diagnosis`。artifact `10023321291`，880217 bytes，ZIP SHA-256 `b35adc49c11f0192015b0733e7d2ff46bebdb84a3df21aba86495135824d9e1e`，本会话实际下载并验证五项清单。

报告 `node-path-diagnosis.json` / `node-path-summary.json`；审查 `G3-R05-NODE-DIAGNOSIS.md`。R05 源 master 前后未变。目标拼接板六个采样都在近灯锥内，但五个被 `Column_capital.007` 遮挡；主拱二十个采样中九个被柱帽、三个被 `Load_column.007` 遮挡。灯源半径偏移射线重现遮挡。其他可达面仍是掠射入射；不是靠继续加大原灯功率解决。目标未发现负行列式或链接的法线扰动，不能据此夸大为全部着色问题已穷尽。

## 不覆盖的历史恢复点

R05：完整证据 `4436b5cb5f870e834ff65639d1a1fbd365b9d4e3`，源 checkpoint `ee77c110f190f7b944dbe8fb2455f87296a76b96`；目录 `output/g3-r05`。master 26,457,653 bytes，SHA-256 `8ca4ca940a98e80d980fbd895f5ae7c27568b28ee361422bfe4ed267b7b8f02e`。运行 `34128911415`，源码 `8a5eb925c4e88c4155b2148059898b3736386895`；artifact `10021873685`，ZIP SHA `3aea7bc1c9a85bea8f833522b40106b274f21c6c41191df5b05a9948fc2698d3`。本会话重新核验实际字节、19项清单和全部六张原图。上部主拱/拼接板仍黑，不能把 R05 写成 G3 PASS。

R04：正确完整证据 `cd3526f4a0f6f8333d75bbd666b4fcfcfa9a529a`，源 checkpoint `a2b7d9d3c90e928a00bca7898247d764c83afe8a`；目录 `output/g3-r04`；master SHA `18348be4c401601706e10e4346a32bf5e0c406fec2448e1a53290f7840b8a854`。运行 `34125489162`，不能混用失败入口 `34125276363`。十九张原图与门运动/反侧证据是 R04 的历史已审覆盖，不冒称 R06 新渲染。

G2 BEST：`6520a8b6056cd7582e4bfc09367cd37fdfb193a1`；`output/g2-review/g2-complete-whitebox.blend`；SHA `0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be`。G1 素材 `0615e137cd53b3e3a150979b1a17d2d9c818eafb`。上述相对 output 路径均位于工作根内。旧完整版交接在不可变提交 `8ae76b3e1b1126ab091b18ae9bd00dab52f63da5` 的同名文件中保留。

## 恢复顺序与门槛

本文件当前运行状态优先于尚待本轮结束后更新的 `PRODUCTION-STATE.md` / `EVIDENCE-INDEX.json`。先查询上述已有 R06 运行和工件；下载 ZIP，核对实际主文件/清单，逐张打开原尺寸图，对比相同相机的 R05。若源文件中继承的 build-report 根字段指向 G2/R01，应视为历史构建血缘；本轮直接父版以 `upper-node-report.json` 和 request 的 R05 SHA 为准。

审查必须确认：上部腹板/拼接板/螺栓可读；没有玻璃大白斑、灯具烧白或暖色泛滥；夜景主次、原42mm机位、门路与中性结构无退步。木作曲边/柜体侧面纹理方向仍需工艺复核。没有真实原图结论不得晋级 G4，不以文件数或 Actions success 替代。

R06 一次请求为30分钟job、23分钟生产截止、7分钟保存取回余量；公开标准runner、单并发、外部费用0，下载1.5GB、工作盘8GB、证据80MB。不是无限重试授权；到界保住候选和失败记录。

原合同 v1.0 SHA-256 `0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`，本会话已从 Library 取回并完整读取、核验字节。视觉精美度优先，保持原雨夜花房车站方向。main、Leaf、历史 BEST 不改；不删除失败相机或关阴影遮丑。

G1/P1 浏览器 `BLOCKED_BY_ADMINISTRATOR` 未解除，不绕过；P1 仍属合同。G4全场、桥拱收口、原生4K30主片、短版、证据片、同源网页与最终验收仍未完成。全部自审为同上下文，不虚构独立代理；`human_acceptance=false`。
