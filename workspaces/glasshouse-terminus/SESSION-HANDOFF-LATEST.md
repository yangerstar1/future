# 雨幕终点站 — 当前续作入口

仓库yangerstar1/future；制作分支codex/glasshouse-terminus；工作根workspaces/glasshouse-terminus。

## 最新可恢复综合源：COAST-R06_CHECKED，原图审查进行中

绝不能退回G4-R02或孤立雨材质版。最新主文件同时保有海浪、扫描岩体、R04扫描羊毛、R05木纹修正以及R06真实表面雨水。生成图不是工程证据，当前也不是G4艺术通过。

源证据commit **8edab03563070bc62a1a768aaf1f6389d72a68f6**；分支evidence/g4-coast-r06-checked-source-34157793290-1。
目录 **workspaces/glasshouse-terminus/output/g4-coast-r06-checked**；主文件g4-full-scene-candidate.blend。

本会话已实际下载完整源包并校验：master **155045521 bytes**，SHA-256 **590e6793224219c5245f89fd43f7ab2e9daed08b79429b5f8925d6c7c0e36738**。
源artifact10031576609，199142600 bytes，ZIP SHA-2569467ed760e4efd867fa9ad73399394fd365d86b47d0afa196cb3531e4275f326。源包不等于新图已经审查。

## 已存在且正在执行的唯一优先审图任务

run **34157793290**；制作源码 **391b85b38e5c81b124fbd89bf90233387944d44d**。
optical-preflight101853112373已success；native-review **101853380801** 已开始，正在按原机位实渲。先查该run的最新结果，不重复触发。

实际入口：check_g4_water_cap_winding.py（build或render包装器），复用refine_g4_integrated_water_contact.py，workflow .github/workflows/glasshouse-g4-water-contact-checked.yml。
计划本次实际观察：C03厅景、C01海岸、M01附着雨水、M03湿石、M04羊毛、M02木作、D01节点；预算足够时追加8张原生厅景运动帧。未实际出现的文件不计完成。52分钟job、45分钟生产截止、7分钟保存余量，公开标准runner、一个生产renderer、外部支出0、磁盘8GB、证据300MB。

生产并发必须group:glasshouse-production、cancel-in-progress:false、queue:max，不能让新的default-single任务把已排队工件取消。

## 本轮修改与技术修正

只读审计验证516块目标玻璃和原雨粒子图。R06为屋面/侧墙/雨棚增加真实表面米制水膜，增加2752个与求值外表面接触的3D水珠；复用已正确的圆雨滴与稳定生命周期ID，增加7200条室外降雨路径；五个旧水洼保留轮廓并做几何薄边接触；露台顶面复用原石材扫描。室内干地、原海浪/岩体/木作/羊毛、原相机/曝光/实体灯不重建。

构建后检查发现新水珠局部坐标系左手性造成全部2752个闭合水珠面朝内。CHECKED版只反转这些新增水珠的面绕序：顶点坐标和无向拓扑不变，逐水珠规范化有向体积全部转正。旧未检查R06源de436b4f51993ac12b47ec3c9c34b27d672dec34仍保留，不能优先拿它渲染。

首次检查run34157504720在save前失败：Blender自动ngon/非共面quad三角化随反面改了对角线，绝对体积对照不稳定。已实际读失败日志，再改成固定最小顶点ID为原点的同一多边形三角扇，保留更严格的体积/拓扑/位置不变检查；本次重试成功，未伪装旧run成功。

旧run34157160255的源已保存，但其未检查法线的渲染在本次CHECKED源成功保存后被精确取消，保留所有部分图及日志，不再浪费预算渲染已知光学错误。它不是当前证据来源。

## 已取回的父版与历史证据

COAST-R05证据3bb182b7b9b1860b3e410f98fc3a098331455fce，master SHA232a602326d2519d8f3bb5fe125a416c4d36149885173563df1297092e493445。源artifact10030867140已校验。其旧native-paired-review取消于pending，不能称原木纹对照图已完成。

只读审计run34156628127完成，证据8c9af5ae59ebd0283941840c8708487cbb9da26e。audit artifact10031192401，ZIP SHA5c732d16ad246f3bb32541be12deb96100f5436de06b02f067632d370f71cb44。基线artifact10031401049，ZIP SHA825f767affc311d6f22fc4194174ea69070308dfda6cf309bb317b2f6eb9cebf；两张1152×720原生诊断图已实际打开：R05厅景仍偏干、海面仍偏圆滑，未判通过。诊断图不是最终4K图。

COAST-R04动态观察run34154436353现已结束，artifact10031291524实际下载核验31条清单。实际海浪/雨各10张640×400原生帧，source_fps30/step3、显示10fps；各编码为1秒证据片，无生成/插帧。海浪确有运动；雨的动态视觉仍太弱，不因“有帧”判达标。它们明确属于R04，不充作R06运动验收。

从旧R02重新建的孤立天气请求run34156239773使用default-single，导致R04/R05待渲任务被取消。本会话精确确认它仍pending且无jobs后取消，代码/历史保留，不再触发。不要让这一旧入口覆盖综合场景。

## 下一动作和最终边界

先取回现有CHECKED运行的原尺寸图，逐张检查雨水可读性、玻璃通透度、湿地接触、木纹/织物及节点回归。没有新原图不声称顶部材质或G4完成。海水圆滑、泡沫响应、岩体暗部与全事件动态遮雨仍是未关闭项；本轮只声明实际观察支持的改善，不用加噪声、提升曝光或新灯代替工艺。

大型master在Git中为无损分块；恢复该output后运行其中restore_master.py restore .，核验SHA再打开。Actions临时包提供完整.blend；长期取回用确切Git证据commit。数据证据分支不包含最新制作代码，不要整分支替换制作分支。

G4仍PAUSED_UNMET，human_acceptance=false；原合同SHA0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f。G4顺序授权保留，不追溯G3 PASS。main/Leaf/G2 BEST与全部父版失败记录不改；浏览器管理员阻断不绕过。最终4K主片、短版、完整空间证据片、同源网页与最终验收未完成。
