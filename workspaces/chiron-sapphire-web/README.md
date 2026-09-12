# CHIRON SAPPHIRE — R07

独立、非官方的 Clear 蓝宝石腕表数字研究。状态：**DELIVERED_UNQUALIFIED**。可运行候选，不是原厂 CAD，也未通过商业级合同终验。优先阅读 R07-REVIEW.md；原 R04/R05/R06 审查保留作历史记录。

应用提交：201e894ca9f987e3eecb157bbb6b9be4052e0713。
交付测试提交：5db41587eeb7503a68e29cad341f2a86d9fef5f6。
构建哈希：69363d8e2c92cca91bec0ce9539818e13998c355072e95f1bb4420152b7eb92a。

4× 内层 HDR 抗锯齿改善边缘，但 SwiftShader 整表中位帧率从约 0.58 降到 0.28 FPS。它不是性能优化；真实 GPU/手机和精品微距工艺仍未验收。全部九门槛不能由功能测试通过来替代。

## 运行

仓库分支 codex/chiron-sapphire-web，工作目录 workspaces/chiron-sapphire-web。
Node.js 22.16.0；Three.js 0.180.0、esbuild 0.25.10、Playwright 1.55.1；package-lock.json 未改。

```sh
npm ci
npm test
npm run build
npm run serve
```

服务端口 4173。dist/Chiron-Sapphire-R07.html 是自包含单文件，需要 WebGL2，已在 CI 直接 file:// 打开验证，外部 HTTP 请求为 0。静态站点为 dist/index.html、app.js、style.css、mechanism.json。旧 R02/R04/R05/R06 输出名是相同 R07 构建的兼容别名；CI 的 r05 artifact/evidence 命名也属历史兼容，以内部 revision/buildHash 为准。

## 模块

version.mjs 统一版本；main.mjs/index.html/style.css 负责页面、输入、相机与恢复；watch.mjs 负责整表和活动节点；craft.mjs 负责框架、桥板、轴承、悬挂及微距几何；mechanics.mjs 负责 16 活塞约束和独立能量/时间；sapphire.mjs 接入主壳 CAD；nested-sapphire.mjs 负责实时内层 HDR 与外层屏幕空间透射；export-asset.mjs 在副本上导出静态可编辑米制 GLB。实时运动和特殊光学不等同于 GLB 烘焙动画。

## CAD 与光源再生成

```sh
python -m pip install -r cad/requirements.txt
python cad/engine_blocks.py
python cad/main_case.py
python cad/prepare_studio.py
npm run build
node tools/geometry-audit.mjs
```

CadQuery 2.8.0；STEP 输出为毫米。生成两个八孔缸体和带三冠通孔/双镜片台阶的连续主壳。prepare_studio.py 下载并核验已登记的 CC0 原件；可传入既有 EXR 本地路径。本轮保留原 CAD/灯光资产，复核哈希与实际网页网格，没有冒称重新运行 CAD 生成器。

## 浏览器验证

在有浏览器执行许可的 Linux 环境：

```sh
npx playwright install --with-deps chromium
xvfb-run -a node tools/craft-observe.mjs
CHIRON_SMALL=1 xvfb-run -a node tools/browser-check.mjs
xvfb-run -a node tools/health-runner.mjs
xvfb-run -a node tools/route-check.mjs
xvfb-run -a node tools/performance.mjs
```

route-check 完成 HTTP 全路线后运行 standalone-check，直接打开交付 HTML。optics.test 的两项数值测试不替代实际像素证明。health-runner 在一次性测试依赖中关闭 Playwright 的强制焦点模拟并记录哈希，随后恢复；它不伪造 document.hidden 或可见性事件。

[full-check] 运行完整构建/观察/回归/健康/性能；[route-check] 增加路线；[route-only] 仅复跑构建与路线。SKIPPED 不算通过。本轮图形证据来自已授权 Actions；本地宿主拒绝导航时不得换浏览器绕过策略。

## 操作及边界

Explore in 3D 后可旋转、缩放、切换各面、移壳、连续拆解、隔离机构、慢放、暂停、分别上弦及重组。画布聚焦：方向键旋转，+/- 缩放，F/B 正反面，R 重组，Esc 返回。声音默认关闭；减少动态仍允许手动机械观察。15 秒是模拟动作时间，慢放延长观看时间。

没有运行时 CDN、用户数据收集、模型 API 或分发字体。模型、参数与光学近似见 REFERENCES.md；来源/许可不等于品牌商业授权。本轮没有公开部署，也不修改 main 或其他项目。完整验收以 references/CONTRACT-V1.md 为准。
