# 雨幕终点站 — 制作状态

权威：用户附件《雨幕终点站》v1.0，文件 SHA-256 `0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f`。原文已在本会话全文读取，本记录不替代合同。不改变主题、完整范围或最终 4K 要求。

## G0 实际证据

- 空仓库 `yangerstar1/future`，公开，有写权限；初始化 README 后建立 `codex/glasshouse-terminus`。Leaf 与其历史保持不变。
- 云环境证据：Actions `33925686525`，分支 `evidence/g0-33925686525`；真实工作根目录 `/home/runner/work/future/future`。4 个逻辑 CPU，16766414848 bytes RAM，首次侦察磁盘空闲 92484087808 bytes。后续 runner 重新检查，不能保证每次相同。
- 工具证据：Actions `33926008263`，分支 `evidence/tools-33926008263`，原始工件可取回并已实际查看。Blender 4.5.13 LTS，构建 `daeeeca98fb0`，内置 Python 3.11.15，Cycles CPU；宿主 Python 3.12.3。官方 Blender 包下载并按官方 SHA-256 校验。
- 技术场景保存、渲染、退出后新进程重开渲染均已执行。两张 320×180 RGBA 图像在取回环境中逐像素完全一致；PNG 文件哈希不等是 Date/RenderTime 元数据所致，不能错误解释成像素不一致。
- Playwright 1.57.0 + Chrome 152.0.7977.64 实际启动、WebGL2 渲染与截图成功。浏览器 SwiftShader、OpenGL llvmpipe，均为软件渲染，不能冒充独显实时性能。
- 第一版 Chrome CLI --dump-dom 阻塞，改为有 timeout 的 Playwright 进程并通过；不是无限重试。
- 执行器：本 ChatGPT 会话协调 + GitHub Actions 运行 bpy/FFmpeg/浏览器。独立评审上下文不可用，记录为同上下文视觉自审 + 用户最终验收。
- 技术工件只有工厂场景诊断，不是艺术作品，不计入最终观察集。

状态：`READY_FOR_EXECUTION`，G0 通过制作入口门槛；G1 尚未通过。

## 输出与有限资源

新建源码范围：`workspaces/glasshouse-terminus/` 及本任务 `.github/workflows/`。工件根目录：`workspaces/glasshouse-terminus/output/`；云端绝对前缀见上。证据以唯一 run-id 分支保存；小型 artifact 只用于回传视觉审查，保留 1 天；持久恢复不能只依赖临时 artifact。

G1 首轮：仅公开标准 ubuntu-24.04 runner，单并发，单 job 不超过 40 分钟；包含安装不超过 1.5 GB 下载、工作磁盘不超过 8 GB；最多 5 张 1280×800 内的代表图、24 帧低分辨率反射序列及一张同源 GLB 浏览器截图。预留该 job 最后 5 分钟保存、校验和回传，外部付费为零，不启用大规格 runner/云付费/付费素材。返工每个失败方法诊断后最多两次同类重试。

G2 后续按 G1 代表帧实测另记录有限预算；840 帧 4K 主片与短版尚未估算。不得用工厂方块 0.73 秒的结果推算成片。

## 已实际查看的参考矩阵（2026-09-05）

| 参考 | 实际读取 | 负责维度 | 边界 |
|---|---|---|---|
| Kew Palm House，RBG Kew / Thom Hudson | 已查看官方整体外景照片 `Palm house in sunlight` | 弯曲玻璃壳、主次拱肋、细分格和屋脊层级 | 只研究结构节奏；不复制整体平面，不分发照片 |
| Belmond L'Observatoire，Ludovic Balay | 已查看官方公开预览 `Marquetry_Design_Details (7)`，穿门看向卧室的木作走廊 | 紧凑内饰的木纹方向、木框收口、皮革/木材区别、门洞形成连续空间与摄影层次 | 不复制独特镶嵌/扇贝图案/品牌，不把照片当纹理，不接受原图下载额外协议 |
| Cartier / Immersive Garden 制作案例 | 已读取制作方正文；封面图片读取失败，未计入已看图包 | Blender→Three.js 的统一美术、发现式交互；仅方法参考 | 不声称已查看全部片段/资产或拥有品牌授权 |
| Poly Haven Slate Floor，Dimitrios Savva | 已查看官方材质预览和许可；具体下载另记 | 暗色石材的片理、低调反射；候选平台材料 | 仅资产文件 CC0；预览图不复制进入工程 |

来源：
- https://www.kew.org/kew-gardens/whats-in-the-gardens/palm-house
- https://www.kew.org/sites/default/files/styles/image_gallery/public/2019-02/Palm%20house%20in%20sunlight.jpg.webp?itok=uHejtT5v
- https://mediahub.belmond.com/venice-simplon-orient-express-a-belmond-train-europe-unveils-the-interiors-of-lobservatoire-a-new-sleeper-carriage-by-artist-jr/?lang=en
- https://mediahub.belmond.com/wp-content/uploads/2024/10/1415bce75c1f25f99fcfa8d154eaf88c-1500x1875.jpg.webp
- https://www.awwwards.com/watches-wonders-immersive-experience-for-cartier.html
- https://polyhaven.com/a/slate_floor
- https://polyhaven.com/license
- https://github.com/Poly-Haven/Public-API/blob/master/ToS.md

已核查 API 条款：唯一 User-Agent、适量请求、清楚标明来源；本任务只请求选定资产的 metadata/files，不爬全站。资产实际下载、作者、URL、字节数与摘要由 fetch_assets.py 记录。未下载的素材不冒称已经使用。

## 当前艺术门槛

G1 风险样板待制作与看图；G2 完整白模待制作；G3 最终质量样板未开始；全场/电影/网页未完成。无艺术 BEST。不能以此状态文档、CI 通过或物体数量代替作品。
