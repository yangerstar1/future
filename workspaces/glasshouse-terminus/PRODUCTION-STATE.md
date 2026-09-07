# 雨幕终点站 — 当前真实制作状态

本条覆盖此前仍写COAST-R02排队的过期摘要。历史原文保留在900ee566be2f28d307ef970837004180c5b95c24。

## 已经实际保存、下载和核验的父版：COAST-R05

- 证据commit：3bb182b7b9b1860b3e410f98fc3a098331455fce。
- 目录：workspaces/glasshouse-terminus/output/g4-coast-r05。
- master：g4-full-scene-candidate.blend，151,750,411 bytes。
- 实际SHA-256：232a602326d2519d8f3bb5fe125a416c4d36149885173563df1297092e493445。
- artifact10030867140，195,928,303 bytes，ZIP SHA-2563550ef51903213d7473a93bff569e0efc946f68864d3d627bc2ed80982cd8b8d。

本会话已下载上述原字节并核对，不是仅引用构建日志。该源同时包含原生海浪、扫描岩体、圆雨滴/水珠、扫描羊毛、已修正坐标的木作；不能退回旧R02或孤立雨材质场景。R05源构建success，但其旧native-paired-review101846897282被取消且未开始，不能写成美术已通过。

## 当前实际执行，先读结果，不重复建请求

只读审计与原机位基线run34156628127，源码8838deee952af12dcceb18686118ee001dae99a3。审计已完成，证据8c9af5ae59ebd0283941840c8708487cbb9da26e；artifact10031192401 ZIP SHA-2565c732d16ad246f3bb32541be12deb96100f5436de06b02f067632d370f71cb44。本会话已下载并读取真实对象/雨节点/玻璃表面/材质。基线两张1152×720是诊断原生分辨率，不冒称最终4K图。

新的COAST-R06局部雨水接触候选：run34157160255，源码f49f9f67d269ee776c2deccb8b2fcef0b5aaa908；入口refine_g4_integrated_water_contact.py与.github/workflows/glasshouse-g4-water-contact.yml。目前已提交执行，源构建与新图结果须实时查询，尚不宣称完成。15分钟源构建；52分钟单生产渲染（45分钟生产、7分钟保存），公开标准runner、外部费用0、磁盘8GB、证据300MB，不自动无限重跑。

干预范围由实测审计决定：516块屋面/侧墙/雨棚玻璃增加绑定真实表面的米制水膜/水珠；保留旧圆雨滴与stable SetID，补真实室外体积的降雨路径；五个旧水洼保留轮廓、几何边缘贴合石面；室外露台顶面复用原扫描石材作干湿响应。海浪、扫描岩体、木作/羊毛、原相机/灯/曝光/空间不重建。材质节点和水珠数量不是视觉通过证据。后续必须看实际原图，确认没有变成磨砂玻璃、黑雨杆、室内漏雨或整地镜面。

## 本会话核对并处理的队列故障

旧workflow glasshouse-g4-weather-r03.yml从R02重新建孤立分支，且未设置queue:max；最新查询显示它创建后R04/R05原图任务被取消。只读审计中的精确守卫确认run34156239773仍pending且jobs为空后取消了它，没有取消正在渲染的任务，源文件保留。不要再触发该旧R02请求。

COAST-R04综合动态观察run34154436353当时仍在运行，其结果保留并单独取回，不冒称R06证据。新建生产渲染必须使用group:glasshouse-production、cancel-in-progress:false、queue:max，串行执行，不覆盖pending。

COAST-R03原生结束包artifact10030806597本会话已实际下载，113,674,607 bytes，ZIP SHA-2560a997184068b8132296ce4139dd0c0eca2f0f0d00c33cf3be78c16f06ad31df9。42项文件校验全部匹配、四张图与十张海浪序列实际存在。海浪近景仍偏暗/圆滑，不能因运动和文件齐全自动通过；它也不是新R06版本。

## 门槛及恢复

G4仍PAUSED_UNMET，stage_best=null，human_acceptance=false。生成图一律不是项目证据。原合同的雨夜、真实材质、同源海与山要求不降低；G3阶段例外按G4-AUTHORIZATION.md保留，不追溯PASS。最终进站动态碰撞、原生4K主片/短版/证据片/网页尚未验收，浏览器管理员阻断不绕过。

大型master在Git证据中以无损分块保存，先运行同目录restore_master.py恢复并核验；Actions包提供完整.blend。main、Leaf、G2 BEST及全部父版/失败证据均保留。恢复者先核对本条已有run，不根据陈旧SESSION-HANDOFF把当前工程回退R02。
