# G4 用户阶段顺序授权 — 2026-09-07

用户在已收到R07局部节点修复、G3木作仍需复核、未进入G4的说明后，明确指令：**「直接做g04吧」**。

据此从R07进入G4全场扩展。本授权只改变阶段顺序，不回写G3为PASS、不建立虚假的G3 BEST，也不是最终人工验收。G3剩余桌面曲边/柜侧木纹问题转入G4问题清单；最终质量目标、完整区域范围和原合同其余约束不降低。

原合同 SHA-256：0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f。
直接父工件：192eba1352585df211f1aa2447a193eec949f6be / workspaces/glasshouse-terminus/output/g3-r07-recovered/g3-bay-candidate.blend。
实际已重新校验父工件24项清单；master SHA-256：1680bcbcc8f8c0911c3c3486f7fc5da5d849b4a7016e87fad67f4233beb14d5e。

复用优先：R07真实场景、玻璃/金属材质族、已用许可明确的家具植物、原列车/车门/路线及锁定Blender4.5.13 LTS/Cycles、scene_common.py、provision.sh、publish_evidence.sh。仓库当前无G4生产入口，先只读列出现有对象、材质、层级和相机，随后添加最小扩展入口；不得猜对象名称或重建G2。

本轮有限预算：只读续作清点1次，10分钟job；G4第一批全场扩展1次，最多45分钟job、34分钟生产截止、11分钟保存/取回/审查余量。公开标准ubuntu-24.04 runner，渲染单并发、外部新增费用0；每次下载上限1.5GB，工作盘8GB，证据100MB。不是无限重跑授权，也不启用付费GPU/大规格runner。

第一批目标：真实扩展已锁定一跨的建筑/材质/实体照明语言，推进站台、列车内外与背景支承到全场候选；同步处理确认的木作映射问题。只把实际完成且看过的结果写入完成项，不把第一批自动称为完整G4通过。保存源文件在渲染之前，失败时保留可恢复候选和原图。

保护原相机、几何空间链、动画和历史BEST。主工程只写codex/glasshouse-terminus，新证据分支create-only；main和Leaf不改。G1/P1 BLOCKED_BY_ADMINISTRATOR不绕过，影片/同源网页仍留在完整合同。human_acceptance=false。
