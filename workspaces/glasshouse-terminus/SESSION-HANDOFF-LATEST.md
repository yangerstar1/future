# 雨幕终点站 — 最新续作交接

## 当前阶段已经是G4

用户在得知G3木作尚需复核后，明确要求「直接做g04吧」。依据`G4-AUTHORIZATION.md`直接进入G4全场扩展。这只改变阶段顺序，不将G3历史状态追溯改成PASS，不代表人类接受或降低原合同美术目标。

当前唯一生产运行：**34141383107**。源码：`8f4b50842f3fd868c2312b3c20e0df53338930e7`。入口：`extend_g4_scene.py`、`.github/workflows/glasshouse-g4-expand.yml`、`g4-expansion-request.json`。

截至本次中途交接，运行已启动并处于构建步骤；尚未取得新G4 master或原图的下载验证。不得凭这份中途记录宣称建模、渲染或艺术验收已经完成。恢复时先查上述已存在运行，不再启动同名请求或并发重做。

详细当前状态见`PRODUCTION-STATE.md`。旧`EVIDENCE-INDEX.json`和G3-R07-REVIEW保留G1—G3历史事实；其中旧G4禁止状态已被用户后续的阶段顺序授权覆盖，但不是把旧未通过项消除。最终G4索引应待实际工件返回后再写，不猜SHA。

## 已完成的只读扩展清点

run34140448762，source`eece9b6c88aa596b64e5bbbba33b4ee9931a9976`，持久证据`00390f1a761b1f263e136395444e8bf7c5b7e74a`。

目录`workspaces/glasshouse-terminus/output/g4-inventory`。Artifact10025692571，实际ZIP SHA-256 `4bb865c5e7f8e6a68a81035d16546a69f049f00be319f547ea47a783021d0000`。真实对象、材质、层级、世界边界、相机与源码快照已下载阅读；原R07文件字节不变。这是续作范围清点，不是重做G0或G2。

## 保护的R07恢复点

证据commit `192eba1352585df211f1aa2447a193eec949f6be`。
根目录`workspaces/glasshouse-terminus/output/g3-r07-recovered`。
master `g3-bay-candidate.blend`，26,463,151 bytes。
SHA-256 `1680bcbcc8f8c0911c3c3486f7fc5da5d849b4a7016e87fad67f4233beb14d5e`。

本轮再次检查24项实际文件清单并打开父版样板图。此恢复点不覆盖。完整G1—G3交接仍在不可变提交`29bdb3ad91af4f4a161fc0b4815b3b1e0fc0270e`的同名文件中，所有父工件/失败证据仍见旧EVIDENCE-INDEX。

## 本轮执行范围及验收边界

基于真实R07扩展建筑双侧/端部/拱架与玻璃密封、全厅石材地面及站台干湿分区；复制原有真实家具和成熟植物；替换已有候车椅与咖啡区白模；推进车厢内外、贴合外壳的内拱顶、木作和小型机械细节、实体灯具、海崖与石砌支承表面。原相机/原几何空间链/列车与车门时间轴需要保护摘要核对。

原图将优先取得C01全景和C03厅景，然后取车厢、原G3样板、D02、反侧、站台、中性厅景和D01回归。模型保存必须在渲染之前；不能因运行success或对象数量宣布G4完成。桥拱V形接头仍属专门结构复核项，表面精修不冒充修复了接头。

有限预算为单次45分钟job、34分钟生产截止、11分钟保存取回余量，公开标准runner、渲染单并发、外部费用0。下载1.5GB、工作盘8GB、证据100MB。不是无限重跑许可。

原合同SHA-256 `0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`。G2 BEST不重做，main/Leaf/历史证据不改。G1/P1浏览器BLOCKED_BY_ADMINISTRATOR不绕过；最终雨动画、4K30影片、短版、证据片和同源网页仍未完成。human_acceptance=false。
