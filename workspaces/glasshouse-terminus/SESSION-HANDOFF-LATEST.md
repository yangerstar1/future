# 雨幕终点站 — 最新续作入口

仓库yangerstar1/future；制作分支codex/glasshouse-terminus；工作根workspaces/glasshouse-terminus。

## 当前：COAST-R08源已实际保存、下载核验，前后原图正在渲染

用户要求继续优化各部分、达到商业顶尖建模真实感。本轮按原合同优先改模型本体，不再连续只堆灯光与雨滴。**最新恢复候选为COAST-R08，不能退回R02、孤立雨材质版或未检查水珠法线的R06。G4仍未通过。**

源证据commit **caf093e65db1e364e2403e6a7807a3ef5da88b5b**；分支evidence/g4-coast-r08-source-34165514100-1；目录 **workspaces/glasshouse-terminus/output/g4-coast-r08**。

主文件g4-full-scene-candidate.blend，实际 **154411214 bytes**，SHA-256 **c96c202a13c5ecd342a7b614a77b1e24ec9889bdb79cc328a255607467d7e877**。实际源artifact10034038296，198608122 bytes，ZIP SHA-256f1f2e033026c7c9b43643e7b492db1028e3ac451de5646ee06c14b5fb0cdd9a3。本会话已核对完整主文件、三个无损分块对应SHA、九项共享资产/来源文件与父版逐字节一致。源保存不代表艺术通过。

制作源码 **d1db8a6e1ee005db14f145e7a1b402620bab4ae6**；唯一当前制作run **34165514100**。source job101875644193已success；native-craft-review **101875989506**已进入父版同机位原图渲染，尚未收齐本轮图片。先查询这一现有run，不重建或重复触发。

入口：refine_g4_r08_craft.py、render_g4_r08_baseline.py、.github/workflows/glasshouse-g4-r08-craft.yml。额外诊断相机QA_R08_cab_joinery保存在候选中；baseline脚本只将这台确切相机读入未保存的R07会话，以保证前后镜头完全一致，原C01/C09及其他所有旧相机保留。

目标观察：R07 BEFORE-cab/BEFORE-upholstery；R08 AFTER-cab/AFTER-upholstery；R08 C09车厢、C01海岸、E02海面。实际完成与缺项必须读最终DELIVERY；当前不得声称七图已齐或已通过。这些是1280×800/1440×900原生诊断图，不是最终4K影片。

## 本轮实际构造修改

只读审计run34164882942已success，证据 **fabf97ac9fa264a741429c0dc01c75e63f322381**；artifact10033826717、71503 bytes、ZIP SHAa8e2c037aaab421b61b3e9fbaa33ad0eb07fd80f6258e964cc906445af144cf6。已下载并读取真实顶点、面、修改器、材质节点和实际源码。

两端Cab_complete_roof_loft原为50顶点、24个未平滑拼面，正端法线向下。R08改成边界锚定的连续四边面曲面，保持50个原始接口采样点完全不动、70mm壳厚保留，统一外法线并补窄卷边。轮廓/曲面必须以原图判断，不以1536面计分。

十个车厢座垫、十个靠垫、十二个长椅座垫原为倒圆八顶点盒体。R08改成有侧围、隆起裁片、2mm缝边和细针脚的闭合软包，保持原外廓容差1.5mm和移动父对象；继承原扫描羊毛、0.3m纹理米制尺度。旧网格保留为源数据，不是丢掉原场景重建。

海面保留原完整光学水体、主波谱、岸边距离泡沫与207m远景渐变，加入35m短风程波谱和0.11–0.51m方向细波纹。451→466→451求值可复现、远处稀疏网格保持平坦。它是受控谱叠加，不声称撞岸流体模拟。原雨/玻璃/木作/岩体、世界环境、灯光、曝光及旧相机不改。保护摘要前后一致，仍不代替视觉验收。

## R07已完整取回的事实，不再写成仍在运行

父版R07源91b5bcc932c58e5a43b20061299bb6a6f606aaaa，master SHA386ab4bfb0134988962efaa96d03e883ed557b30843aba6c20de0af9d999c396。其run34163114491现已结束：source成功，native-review因最后海岸图未完成为failure。完整保存证据 **37b91cc3bddbfaae64d1f34bf4951e16146be1b1** / output/g4-coast-r07。

实际下载最终artifact10034156270：208017010 bytes，ZIP SHA43ac065b58f54b75146a6c176a4ce5635194d5ba3b2af5b3efd877183b6116a3。58项清单全部匹配。完成三张原尺寸图（厅景、雨玻璃、湿石）和十张640×400实际雨水帧；缺C01-runoff-coast.png、context-reopen.json，最后海岸停于sample36/48。原失败不改写。

本会话实际逐张/逐帧读图：附着水局部流动已存在但分布偏均匀、圆粒化；四盏低位灯仍未让湿石近景达到可读质量；完整暴雨身份仍弱。详见 **G4-COAST-R07-NATIVE-REVIEW.md**，提交bb92531aabd2b62d6925653a9b4189a1b372d8d3。已用十张原帧编码1秒10fps本地证据片并完整解码；不是最终30fps电影，不是R08运动验收。

R06缺失木作/节点已通过run34162646428补齐，证据f0569934f05ec2b94c4b44e3ee00f250ff8e548b；不再重新启动旧恢复请求。R06原失败及其五张原图保留。

## 恢复、资源与门槛

R08一次14分钟源构建、52分钟单生产渲染（45分钟生产截止、7分钟保存余量）；公开标准runner、外部支出0、下载1.5GB、磁盘8GB、证据350MB。无无限自动重试授权。生产队列必须group:glasshouse-production、cancel-in-progress:false、queue:max；禁止旧default-single请求挤掉待渲工件。

大主文件在Git中为无损53MB分块。恢复相应output目录后，用其中restore_master.py restore .合并并核对SHA；Actions ZIP含完整.blend。证据分支不是制作代码分支，不整分支覆盖当前制作分支。

当前实际判断入口为本文件、G4-R08-CURRENT.md及R07原图评审。仍停在R02/R05的旧PRODUCTION-STATE/G4-EVIDENCE-INDEX在本次渲染结束后统一刷新，不能据其旧摘要回退工程。更早完整交接保留在60c3855e0e4f00fbf66ab8ecb87911360a03ee2f的同名文件。

R08原图回来后必须比较曲面/缝边是否真改善，检查车厢、外景、风浪有没有退步。湿石压黑、暴雨识别、崖顶与基础接口、岸边泡沫和完整动态遮雨尚未关闭，本轮不冒称已同时解决。原合同本会话完整读取；G4顺序例外保留，不追溯G3 PASS。main/Leaf/G2 BEST及旧失败证据不改，浏览器管理员阻断不绕过。最终4K主片/短版/空间证据片/同源网页未交付；stage_best=null、human_acceptance=false。
