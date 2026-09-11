# CHIRON SAPPHIRE — R02 production candidate

独立、非官方的 Bugatti Chiron Tourbillon Sapphire Crystal — Clear 数字研究。**本版本尚未通过合同九项终验，不是官方产品网站，也不是原厂 CAD。**

## 运行

已实际使用 Node.js 22.16.0。生产依赖锁定 Three.js 0.180.0，构建 esbuild 0.25.10，验证 Playwright 1.55.1。

```sh
npm ci
npm test
npm run build
npm run serve
```

服务默认端口 4173。也可以在构建后直接打开 `dist/Chiron-Sapphire-R02.html`：它含完整网页、渲染器和参数，没有运行时 CDN、字体文件或模型 API。浏览器需要 WebGL2。标准 HTTP 版本在 `dist/index.html`，静态服务器应同时提供 app.js、style.css 和 mechanism.json。

## 真实文件职责

- `index.html` / `style.css`：七章产品叙事、响应式重排、HTML 控件、规格、来源与非官方身份。
- `main.mjs`：单渲染循环、相机控制权、DOM 输入、加载/故障恢复、照明、音频和只读诊断。
- `watch.mjs`：本项目自制可编辑程序化整表、材质、动态零件、装配层级；不是购买或提取的原厂模型。
- `mechanics.mjs`：16 活塞的连续滑块—曲柄解算、八组共享曲轴销数字近似、独立时间域/能量与装配状态。
- `tools/build.mjs` / `tools/serve.mjs`：可重建的两种入口及源/构建哈希。
- `tools/mechanics.test.mjs` / `tools/browser-check.mjs`：数值检查和真实界面回归。
- `references/CONTRACT-V1.md` / `REFERENCES.md`：冻结任务与资料、近似及权利边界。
- `assets/`：成功运行浏览器资产导出检查后，保存当前模型 GLB 和注册表。GLB 是静态编辑快照；动作与拆解的权威来源是上述程序化源码，未声称 GLB 含全部动画。

## 操作

首页可直接 Start W16 或 Explore in 3D。探索中可以旋转、缩放、查看前/后/两侧，移壳，隔离 W16/陀飞轮、设置观察速率、调时与双向上弦。Anatomy 滑块可连续展开/收拢；Reassemble 回到同一模型。演示初态已经上弦，右冠或 START 发起一次 15 个模拟秒动作。慢放改变观看时间，暂停保留当前相位与已消费储能。手动相位观察不是原表按钮。

画布焦点：方向键旋转；+/- 缩放；F/B 正/背面；R 重组；Esc 退出。Motion 控制减少非必要运动；Sound 默认关闭，开启后仅是合成轻响而非原件录音。Light 切换发布/中性检查。

## 验证命令与边界

```sh
npx playwright install --with-deps chromium
xvfb-run -a node tools/browser-check.mjs
```

默认检查通过本地 HTTP 访问。沙箱浏览器政策阻止本地地址时，使用：

```sh
CHIRON_LOCAL_DOCUMENT=1 CHIRON_SMALL=1 xvfb-run -a node tools/browser-check.mjs
```

后者是实际 Chromium 执行完整离线文档，不是 HTTP 冷启动。`CHIRON_SMALL=1` 为 1100×800 诊断视口；去掉后是 1920×1080。`CHIRON_QUICK=1` 会明确标记未执行长回归，不能作为全套通过依据。软件 SwiftShader、手机视口模拟与真实硬件证据严格区分。

`window.__chiron` 仅提供快照、资产/约束读取和导出，不提供伪造用户状态的测试 setter。正常用户路线通过真实按钮、键盘、拖动和选择框验证。

## 已知未通过项

不能以构建成功/单元测试通过来认定合同完成。R02 的整表比例/细部/蓝宝石表现和全页面工艺尚需与冻结参考严格复核；不能授予 CU01/CU06/CU08 的 Q3。当前尚无消费级 GPU 或实机手机性能证据。完整 O01—O32 覆盖、动态慢放、悬挂、故障/冷启动与复验报告以 `PRODUCTION-STATE.md` 和实际 evidence 为准。

未授权公开部署、购买模型、交易或品牌商业宣传。仅提交到已授权分支，不修改 main 或其他工作区。
