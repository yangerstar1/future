# CHIRON SAPPHIRE — R05

独立、非官方的 Bugatti Chiron Tourbillon Sapphire Crystal — Clear 数字研究。
本版本正在按用户反馈进行结构返工，**不是已通过合同终验的成品，也不是原厂 CAD**。

## 运行已准备的源码包

Node.js 22.16.0；Three.js 0.180.0、esbuild 0.25.10、Playwright 1.55.1。

```sh
npm ci
npm test
npm run build
npm run serve
```

服务端口 4173。`dist/Chiron-Sapphire-R05.html` 是自包含离线网页，需要 WebGL2。
正式静态 HTTP 入口为 `dist/index.html`，同时保留 app.js、style.css、mechanism.json。
没有运行时 CDN、字体文件、模型 API 或用户数据收集。

## 从干净仓库重新生成 CAD / CC0 灯光

```sh
python -m pip install -r cad/requirements.txt
python cad/engine_blocks.py
python cad/prepare_studio.py
npm ci
npm test
npm run build
node tools/geometry-audit.mjs
```

CAD 脚本生成两个有实体厚度、各八个径向缸孔的蓝宝石缸体；STEP 输出为毫米。
灯光脚本下载公开 CC0 原件，验证源 SHA256，面积缩放到 1024x512 并验证 RGBE 哈希。
已有原件时可传入其本地路径：`python cad/prepare_studio.py /path/to/studio_small_03_4k.exr`。
不要以另一份 HDR 代替却继续沿用旧画面证据。

## 源码职责

- `watch.mjs`：整表、所有活动节点、实例化活塞/连杆、装配层级。
- `craft.mjs`：承载框架、桥板、轴承、发条盒、悬挂、涡轮固定座、微距工艺。
- `sapphire.mjs`：连续弧面透明表壳与双面表镜。
- `nested-sapphire.mjs`：同一场景的实时内层 HDR 捕获与外层物理透射；屏幕空间近似，不是光线追踪。
- `mechanics.mjs`：16 活塞约束、时钟、能量、装配状态；具体内部数值属数字近似。
- `main.mjs`、`index.html`、`style.css`：真实网页、普通输入、相机、资源/图形恢复。
- `cad/`、`generated/`：可再生成的连续实体、STEP、灯光和来源校验。
- `tools/geometry-audit.mjs`：实际几何间隙、721 相位、四点世界坐标连接；不是视觉评审。
- `export-asset.mjs`：在独立副本中导出带表面贴图的可编辑 GLB；不改动实时模型。
- `tools/craft-observe.mjs`：真实 HTTP、普通 UI、多面/微距/手机视口截图。
- `tools/verify-asset.mjs`：GLB 导出后重新载入，验证 16 组独立活塞/连杆及米制尺度。
- `tools/observed-frame.mjs`：等待画面完成并核对 UI 状态、相机与视口，避免旧帧证据。
- `R04-STRUCTURAL-REVIEW.md`、`R05-REVIEW.md`：历史缺陷、实际修复、证据边界和未完成项。

## 操作及事实边界

Start W16 / Explore in 3D；旋转、缩放、正反侧面、移壳、Anatomy 连续拆解、隔离机构、
慢放、暂停、调时、分别上弦与重组。画布聚焦后方向键旋转、+/- 缩放、F/B 正反面、
R 重组、Esc 返回。声音默认关闭；减动态仍能手动启动和观察机械。

初始数字演示已上弦。15 秒是模拟动作时长，慢放延长观看时间。
GLB 是静态可编辑快照（米），实时运动的权威来源是源码，不宣称导出包含烘焙动画。
三冠的数字控制不代表获得了原厂内部制造结构。

## 浏览器验证

```sh
npx playwright install --with-deps chromium
xvfb-run -a node tools/craft-observe.mjs
xvfb-run -a node tools/browser-check.mjs
xvfb-run -a node tools/health-check.mjs
```

当前生产验证使用真实 HTTP。现有 Actions 在固定提交上分别运行构建、视觉与完整回归，
不再执行旧恢复脚本或自动改写源码。浏览器策略拒绝本地导航的宿主不应绕过该限制；
本轮浏览器证据来自用户已授权的 GitHub Actions 执行环境。
软件 SwiftShader / 手机视口模拟，不可作为真实 GPU / 手机性能证明。

完整验收标准见 `references/CONTRACT-V1.md`。构建成功、接口间隙通过、零件数量和
单张图片都不能代替 CU01/CU06/CU08 的 Q3 或全部九个独立门槛。
