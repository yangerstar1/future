# 雨幕终点站 — 当前制作状态

## 2026-09-07：R03雨与材质候选正在原生渲染

用户明确要求「雨呢，还有各个精细的，真实的，顶级的材质呢，我需要看到上限，继续优化」。已只读核查R02真实雨/材质实现，不重新G0/G2。现有雨主要是微弱玻璃凹凸；名称中Train/drain含rain的命中不是实际雨效。优先复用已打包木材/石材/家具/植物贴图和Blender原生节点。

唯一当前制作运行：**34147780955**，job **101823424691**，源码 **6ad3c7c0fbcc66a013ddf42b9ab2a6cec616932d**。构建与源码保存成功，实际原图渲染仍进行中；不得启动重复请求，不得据保存或CI状态宣称美术通过。

已存在源checkpoint：**0e0f56888549e27900070a83b9830f81c3313c4b**，分支`evidence/g4-r03-source-34147780955-1`，目录`workspaces/glasshouse-terminus/output/g4-r03`，文件`g4-full-scene-candidate.blend`。构建日志报告SHA-256 **dfd9a0e28967b8a474bc9688ce0b75d194dba20ce14aab5f18f1d11da7aa32b5**；新文件本会话的下载字节核验与原图自审尚未完成。源日志有Blender退出时18.59MB未释放内存警告，进程已正常退出；不得把日志描述成完全无警告。

新增入口：`finish_g4_rain_materials.py`、`.github/workflows/glasshouse-g4-rain-materials.yml`、`g4-rain-material-request.json`。

本候选建立原生时间驱动雨滴实例，轨迹按停稳帧451真实屋顶/雨棚/地面首命中截断；风迎面玻璃有凸起水珠/依附水流，檐口有滴落，室外石材有浅积水及波纹。调整漆面、金属、木材、织物与干石表面响应，保留原几何、旧相机、灯具参数、曝光0和原运动。原生节点与受控VFX不是流体模拟；移动列车阶段的动态遮雨仍须后续验证。

本次仅一次52分钟job、44分钟生产截止、8分钟保存取回余量；公开标准runner、串行、外部支出0；下载1.5GB、工作盘8GB、证据120MB。七张目标图是否全部取得，以结束包的真实missing和原图为准；没有自动追加下一轮。

## 已核验的父版

R02完整证据`12ae1030686d97823548b2967805d85853d12ab2` / `output/g4-r02/g4-full-scene-candidate.blend`，SHA-256 `173da1291bff8a39da704539c737e21f9b2d739e3d32a106f629601bc2abefdc`。本会话重新核验17项清单、实际master字节并查看大厅/外景原图。R02仍不是完整G4通过。历史完整状态在`819b499bd9c532de7271f22ce1d58364c6f11f2e`同名文件，及G4-R02-REVIEW.md/G4-EVIDENCE-INDEX.json。

本次只读侦察run34146784055已success，证据`d76b129f6808c184faa0f6c725eb35d6e17e8300` / `output/g4-rain-inventory`；artifact10027950844实际227016 bytes，ZIP SHA-256 `02bfa59160a4bef82381c16a27dc19a7dbf52dc15be1f7fc8bff9b2a9697c89a`。完整材质节点、图像、场景对象和原源码快照均已实际取回读取。

## 保留与质量门槛

G4仍未通过；先查看原生雨与材质近景/原厅景/原外景/旧节点回归，而不是计数。车头曲面折痕、海崖大面及海面边界等历史几何问题不因改了材质自动关闭。G2 BEST、R07、R01/R02及所有失败证据、main和Leaf保留。用户G4阶段顺序例外见G4-AUTHORIZATION.md，不追溯改G3为PASS。

原合同SHA-256 `0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`。G1/P1浏览器BLOCKED_BY_ADMINISTRATOR不绕过；最终雨动画/4K30主片/短版/空间证据片/同源网页未完成，human_acceptance=false。
