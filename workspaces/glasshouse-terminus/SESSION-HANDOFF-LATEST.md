# 雨幕终点站 — 最新会话交接

更新时间：2026-09-07。仓库`yangerstar1/future`，制作分支`codex/glasshouse-terminus`，工作根`workspaces/glasshouse-terminus`。

## 立即读取的当前结论

**本会话已从确切R05完成只读光路诊断、R06实体灯具修正、R07仅功率校准及一张缺失观察的只读补渲。最新候选是R07，四张同源夜景原图已实际逐张审查。原D01上部主拱/拼接板近黑剪影问题已解决；完整G3仍为PAUSED_UNMET_G3_CRAFT_REVIEW，G4禁止。**

不要重做G0/G2，不从历史G3 NOT_STARTED开工，不重复已经结束的R05诊断、R06/R07制作或恢复请求。所有本会话运行已结束，没有仍在运行/排队的工作。R06“正在渲染”的中途交接现已过期；历史版本保留在Git中。

权威续作入口是本文件、`PRODUCTION-STATE.md`、`EVIDENCE-INDEX.json`、`G3-R07-REVIEW.md`。原G3-R05-REVIEW只解释旧版，不是当前判定。原README中的旧阶段标签不覆盖这些实际证据。

## 当前唯一优先恢复点

最新完整观察证据commit：`192eba1352585df211f1aa2447a193eec949f6be`。

证据分支：`evidence/g3-r07-recovered-34138330518-1`。

工件根：`workspaces/glasshouse-terminus/output/g3-r07-recovered`。

主文件：`g3-bay-candidate.blend`，实际26,463,151 bytes，SHA-256：

`1680bcbcc8f8c0911c3c3486f7fc5da5d849b4a7016e87fad67f4233beb14d5e`

Artifact `10025000004`，32,065,879 bytes，实际ZIP SHA-256 `7c077fac0acc27e471d2db4f131633426b3781a57422e253c89e60fb10c67608`。24个清单条目全部匹配，无缺项；四张PNG已实际审查。新进程重开外部图片缺失0，主文件与已完成图像字节未被恢复操作改变。

临时artifact只保留一天，长期恢复用上述Git提交。证据分支是data-only、以main为基底，不是最新制作代码分支。保持制作分支检出后，仅恢复所需output目录；不要把整个证据分支覆盖到制作分支，也不要据证据分支里的旧README重新启动阶段。

在已确认位于本仓库根、无路径冲突的环境，可按确切提交恢复：

```bash
git fetch --depth=1 origin 192eba1352585df211f1aa2447a193eec949f6be
git archive FETCH_HEAD workspaces/glasshouse-terminus/output/g3-r07-recovered | tar -x
echo '1680bcbcc8f8c0911c3c3486f7fc5da5d849b4a7016e87fad67f4233beb14d5e  workspaces/glasshouse-terminus/output/g3-r07-recovered/g3-bay-candidate.blend' | sha256sum --check
```

不要在未知本地工程目录直接执行这些命令；先只读确认工作树、工具版本及真实路径。新任务基于已校验master继续，不重跑本次已完成触发文件。

## 实际执行链与故障保留

### R05只读诊断：已完成

源码`05119473ea654ffbe49b1d3887b33e6bf6484a4b`；run`34134203847` / job`101781208601`，success。证据`4cb68d0db15031059ea05054847ae75491569e64`；目录`output/g3-r05-node-diagnosis`。Artifact`10023321291`，880217 bytes，ZIP SHA`b35adc49c11f0192015b0733e7d2ff46bebdb84a3df21aba86495135824d9e1e`，五项清单实际核验。

从原D01相机实际可见表面发射光路检查：近灯覆盖了目标光锥，但六个拼接板采样中五个被`Column_capital.007`遮挡；二十个近侧主拱采样中九个被柱帽、三个被`Load_column.007`遮挡。灯源半径偏移也重现阻挡，其他面仍是掠射入射。未发现目标负变换或Normal输入链接，不能夸大为穷尽全部着色问题。诊断没有保存master；源SHA前后相同。详见`G3-R05-NODE-DIAGNOSIS.md`。

入口：`diagnose_g3_r05_node_paths.py`、`.github/workflows/glasshouse-g3-node-diagnosis.yml`、`g3-node-diagnosis-request.json`。

### R06：真实安装改光路，但原图未过

源码`2ab0070ad8a6ed7ba89cd16d2096724828abd06a`；run`34134897722` / job`101783432648`，success。源checkpoint`310f07c71dcf63db9a6e8e333bebd289717aae0f`；完整证据`719b77ac1678b0ede8edcc9bd86193e1d0db9362`，目录`output/g3-r06`。

master26,467,485 bytes，SHA`65ef58c38685aa6ef26aa0f2d5116e1535e879f4a2b01975100d71be7cb7de26`。Artifact`10024035972`，34,892,106 bytes，ZIP SHA`eb1169341c644f876ea91a85160e9b70f16cfd3c727d62c1cbffd376df7168e2`，19项清单及六张原图实际核验。

在实际`Longitudinal_roof_purlin.001`上夹持两只带支架/灯壳/紧固件的36W紧凑射灯；原R05对象、材质、原灯和镜头不改。灯壳安装后25个上部采样有23个具备直接几何光路，另外两条先命中`Curved_roof_glazing.144`；不宣称25个全通，也不把几何首命中当完整折射输运。六图显示局部改善但仍暗，故R06没有通过。详见`G3-R06-REVIEW.md`。

入口：`relight_g3_upper_nodes.py`、`.github/workflows/glasshouse-g3-upper-node.yml`、`g3-upper-node-request.json`。R06继承的build-report根字段含旧G2/R01血缘；直接父版以upper-node-report和request内R05 SHA为准，不能据旧字段回退。

### R07：两盏既有灯的校准；原运行超时

艺术源码`d7bc41bc02832106da8c6c3c6543e0df8f9a7937`；源checkpoint`de5b700d43afa6e287d7712bd1f2df895226f11d`。只把两只R06檩条灯36→144 native Blender W，数量、位置、光锥、颜色、材质、原柱脚灯、曝光和几何不变。不是实际灯具电气功率标定。

原run`34136755760` / job`101789430599`在14分钟生产截止时，最后一张玻璃近景未完成，故conclusion=failure，不能因后来恢复而改写。已保存主文件及D01节点、完整bay、原42mm三张原图。原部分证据`c68b1d2f746f8349b0ef1932076431f5c9fa12da`，目录`output/g3-r07`；artifact`10024744056`，30,896,618 bytes，ZIP SHA`60492474e475438d17c34d217bda40e79864e16f0680e706eae9b34d1691261e`，18项清单实际核验。早期节点artifact`10024402958`的PNG与结束包节点逐字节一致。

入口：`calibrate_g3_node_wash.py`、`.github/workflows/glasshouse-g3-node-calibration.yml`、`g3-node-calibration-request.json`。本次18分钟job/14分钟生产/4分钟保存的单次请求已经用完，不是自动再校准许可。

### R07只读单图恢复：已完成，不是R08

源码`46f61ca4bb0ff78de6ecedaab79324871f74668f`；run`34138330518` / job`101794374236`，success。只补D01-glass-metal一张，主文件没有save；前三图与master字节保持相同。原失败DELIVERY原字节保存为`R07-PARTIAL-DELIVERY.json`，旧日志仍在。最新证据及artifact见上方优先恢复点。

入口：`recover_g3_r07_glass.py`、`.github/workflows/glasshouse-g3-r07-recovery.yml`、`g3-r07-recovery-request.json`。12分钟job/9分钟生产/3分钟保存、单次观察恢复已完成。该脚本拒绝覆盖已经存在的玻璃图，不能把它当通用重渲入口直接重跑。

## 原图结论与下一项工作

四张R07夜景观察均实际打开：D01节点1280×800、完整bay1440×900、原42mm bay1440×900、玻璃近景1280×800；帧451、曝光0、AgX、64samples，镜头及相机变换逐项与R06一致。R05节点是48samples，不能宣称R05/R07采样数相同。

D01瓶绿截面、拼接板与螺栓恢复可读；中景和原42mm机位未被照平，玻璃近景没有重新出现巨大白斑。原G3-D01-DARK近黑剪影缺陷在这些固定观察中已解决（同上下文自审、仅此缺陷）。完整评审`G3-R07-REVIEW.md`，commit`c3fa6bd444bac313db27ffa1a51fbfad2ff577cc`。

**不再重复加灯或升功率。下一步是G3剩余工艺复核：** 从R07只读确认D02桌面曲边及柜体侧面问题对应的真实对象、UV/纹理坐标和材质链接。对象名、UV情况和实际需要修改的文件范围尚未确认，不得凭模板编造；证据与建议不匹配时先报告，不能强套。之后只做必要局部修正并审查相关当前版本近景/中性图，再判断完整G3门槛。

木作曲边纹理延展与柜侧木纹方向来自本会话重新打开的R04历史D02/D03，不冒称R07专项新图。R06中性bay、D05与R04门运动/反侧等也分别属于历史版本，不能合并冒称本轮完整重渲。四张R07夜景通过这一局部回归，不等于完整样板BEST、全场精修或最终影片。

## 历史恢复与硬约束

R05原始证据`4436b5cb5f870e834ff65639d1a1fbd365b9d4e3` / `output/g3-r05`，master SHA`8ca4ca940a98e80d980fbd895f5ae7c27568b28ee361422bfe4ed267b7b8f02e`，本会话重新下载核验19项和六张原图。R04正确证据`cd3526f4a0f6f8333d75bbd666b4fcfcfa9a529a`，不能混用失败run34125276363。其19图是历史证据，不是R07新图。

G2 BEST：`6520a8b6056cd7582e4bfc09367cd37fdfb193a1` / `output/g2-review/g2-complete-whitebox.blend`，SHA`0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be`。G1素材`0615e137cd53b3e3a150979b1a17d2d9c818eafb`。这里所有output相对路径均位于工作根。更早完整交接在不可变commit`8ae76b3e1b1126ab091b18ae9bd00dab52f63da5`的同名文件中保留；EVIDENCE-INDEX完整保留G1/G2/R01-R05和旧失败/取消记录。

原合同v1.0实际SHA`0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`，本会话从Library完整取回、读取并核验过。视觉精美度优先；复用Blender4.5.13 LTS/Cycles、原素材、scene_common、provision.sh与data-only publish_evidence.sh，不重建全场或另起框架。

main、Leaf、G2 BEST和所有失败图不改；不清认证、不改安全配置、不绕过G1/P1浏览器BLOCKED_BY_ADMINISTRATOR。全场G4、桥拱收口、原生4K30主片、短版、证据片、同源网页、最终验证与人类验收仍未完成。阶段和最终状态均未因CI成功自动通过，`human_acceptance=false`。
