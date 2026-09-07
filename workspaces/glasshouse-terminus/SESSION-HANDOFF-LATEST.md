# 雨幕终点站 — 当前续作入口

仓库yangerstar1/future；制作分支codex/glasshouse-terminus；工作根workspaces/glasshouse-terminus。

## 当前：COAST-R07源已实际核验，原生观察待结束

最新综合候选为COAST-R07，不是G4-R02，也不是孤立雨材质版。源证据commit **91b5bcc932c58e5a43b20061299bb6a6f606aaaa**，分支evidence/g4-coast-r07-source-34163114491-1，目录 **workspaces/glasshouse-terminus/output/g4-coast-r07**。

主文件g4-full-scene-candidate.blend，实际 **154130427 bytes**，实际SHA-256：
**386ab4bfb0134988962efaa96d03e883ed557b30843aba6c20de0af9d999c396**。

源artifact10033285921，实际198338464 bytes，ZIP SHA-256 **80388903dcb6a6957f635b44bfe899118e3787a4031401f1535bcf3403f2e5ac**。本会话已下载原字节，并核对master与三个无损分块的对应SHA。源保存不是艺术通过。

制作源码35b17c626513893b54113cabefad9225d4fea297；入口finish_g4_runoff_and_wet_walkway.py和.github/workflows/glasshouse-g4-runoff-walkway.yml。

当前已存在的制作run **34163114491**：source101868792007已构建成功并保存；native-review等待串行槽。应先查这个已有run，不触发第二个相同请求。四张目标原图为湿石1440x900、附着雨1600x1000、原厅景1440x900、原海岸1440x900；优先取得10张640x400实际雨水序列帧（source30fps/step3），不生成或插帧。实际覆盖以结束DELIVERY和原图为准。

## 本轮实际修改及证据依据

从3836个原静态迎风面水珠中取出548个完整水珠，改成原玻璃支承范围内的下滑水滴/窄尾水膜原生实例；保留3288个静态水珠和其他屋面水珠。复用原SceneTime/稳定生命周期ID节点，新的源水滴网格是闭合正有向体积；玻璃支承间隙25微米，原生求值548实例，帧451→466→481→451位置不同且复位摘要一致。模型同时保留原海浪、扫描岩体、扫描羊毛、对齐木作和R06水膜；不是另起天气场景。水滴是受控解析运动，不是流体/汇合求解。

M03湿石近景严重压黑的只读诊断已实际完成：54条原相机样线全部正朝向表面；36条反射中心光路首先打到暗Hall_plinth。现有露台顶面槽和世界XY米制贴图存在，不是缺UV或整体翻面。于是R07在实际基座外侧x=-12,-4,4,12各安装一只遮光低位外廊灯，18 native Blender W/盏；安装面和有效下照光路再次射线核对。原灯/全局曝光/世界环境未改。新增实灯属于公开的艺术变量，不宣称同照明A/B。

保护摘要前后一致5dd7477e361f01bb70294ce21bb9b78ce6904528f60ef44f1968bf34f582873b，范围见代码；不能将摘要当作原图艺术验收。

## R06父版已取回的实际图像与缺项恢复

父版CHECKED源8edab03563070bc62a1a768aaf1f6389d72a68f6 / output/g4-coast-r06-checked，master SHA590e6793224219c5245f89fd43f7ab2e9daed08b79429b5f8925d6c7c0e36738。本会话实际下载原失败结束artifact10032499833，208424234 bytes，ZIP SHAb9946afc1b96ad101c37a2faeb545968bc5a876bfd832eb799c4cf8fb9df556b，43条清单一致。五张原尺寸PNG全部实际打开：厅景、海岸、水珠、湿石、羊毛。缺M02木作、D01节点、details-reopen。原run34157793290仍failure，不能改写成success。

缺项只读恢复run **34162646428**，源码5bc928c98a179fa09db6175124d090bdd449055e，recover-missing-witnesses job101867597489已在原生渲染；只补两张缺图，不重建源或重复五张已完成图。恢复结果尚待实际取回。R07等它完成后再渲染，不能用default-single把它取消。

同run的audit已成功：证据 **fa5eadee301d2fd38f97990c5c22bfd05a51f634** / output/g4-r06-optical-audit。已下载artifact10033114243，279221bytes，ZIP SHA7766ac70140448ed71c53cf5037f724f21fcbf6174921fc7c21ddc0f8aa322e7；原JSON已读。复核见G4-R06-CHECKED-NATIVE-REVIEW.md。

## 门槛、预算与恢复

R07源14分钟；单原生renderer48分钟，42分钟生产截止+6分钟保存余量。R06缺项恢复25分钟，20分钟生产+5分钟保存。公开标准runner、外部费用0、下载1.5GB、工作盘8GB、R07证据300MB；每项单次请求，不是自动无限重试。

共享原生渲染使用group:glasshouse-production、cancel-in-progress:false、queue:max。禁止另从旧R02发起重复天气任务，禁止覆盖主分支/历史BEST。

大型master在Git为无损分块：恢复相应output后运行其中restore_master.py restore .并核验SHA；Actions ZIP含完整.blend。数据证据分支不含最新制作源码，不整分支覆盖制作分支。

接下来必须先收取上面两个已有run的实际图像和序列，审查新增灯是否真正改善湿石且无炫光、贴面流动是否可辨且不穿玻璃/重生拉线，再判断当前候选。海水仍偏圆滑、岩体暗面与撞岸泡沫、全事件列车动态遮雨、车头曲面和最终完整观察集尚未关闭。不要为了说明完成而把静态位置摘要当视频。

G4仍PAUSED_UNMET、stage_best=null、human_acceptance=false。原合同SHA0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f；用户G4顺序授权保留，不追溯G3 PASS。main/Leaf/G2 BEST与所有父版/失败原图保留；浏览器管理员阻断不绕过，最终原生4K主片/短版/完整空间证据片/同源网页尚未交付。

本轮之前的完整R06、R05、R04、原失败与取消链，在不可变制作commit03f80220fe30c7e32d9f32f803d9b88c9096988b的同名交接中保留；本文件是运行中checkpoint，完成后应以实际结果更新。
