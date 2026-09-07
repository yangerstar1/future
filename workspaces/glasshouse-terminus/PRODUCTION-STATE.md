# 雨幕终点站 — 当前制作状态

## 原生海面/岩体已经完成模型整合，禁止被旧雨材质模型覆盖

用户明确纠正：不是生成图片，而是改真实项目，并追加真实海面和山体。生成图不计证据。

最新已保存的综合候选为 **COAST-R02**：真实JONSWAP海浪几何、OceanFoam与基于实际岩体距离的岸边泡沫、许可清晰的扫描海崖及表面细节、原R03全部材质/玻璃水珠，再合入已检查的R04圆雨滴与快门修正。它不是旧平面海面版。实际native图像仍待已排队运行结束，不宣称艺术通过。

- 综合源码：`2eafacb420814b72c7b7170ea60e6889396eea4e`
- 综合源checkpoint：**`071ba6959335f094209fbc4537d2ce2b1246d2dc`**
- 根目录：`workspaces/glasshouse-terminus/output/g4-coast-r02`
- master：`g4-full-scene-candidate.blend`，构建记录105,907,025 bytes
- 构建记录SHA-256：**`b8cea93e7511088f418afbc843b66ddd4dcd0e82f34860b192150341f258ef64`**
- 现有运行：**34150153500**；integrate-source101830554160已success，native-render101830847684等待前序雨任务。不要重复启动。

Git evidence存放无损分块：恢复该output目录后运行`python3 restore_master.py restore .`，每块与合并字节都有SHA验证；Actions下载包包含完整.blend，无需分块。不能因为超过Git单文件自定98MB上限而删贴图、降质或重建。前一COAST-R01原始完整字节已实际下载核验，SHA1be3507f7c31ed2f8e5431aefaf787ff414a29fdce696b596a2baff68b0789c6；当前COAST-R02的结束包仍待下载复核。

## 必须保住队列和不同修改范围

所有新建的共享生产渲染请求使用GitHub官方支持的`group: glasshouse-production`、`cancel-in-progress: false`、**`queue: max`**。这仍只有一个生产renderer，但允许多个任务按等待顺序排队，避免default-single自动取消旧pending。原coast34149501788的native-review101828652348曾被R04排队替换，尚未开始、没有产图；其源已安全保存。不要再次用default-single请求取消当前综合海景观察。

R04圆雨滴运行34149669782正继承R03进行独立玻璃/运动观察，本会话没有取消或覆盖它。它的源没有新的海浪/扫描岩体。后续织物、木作、湿石修正若从R04生产，应明确记录为材料分支，再把具体已验证的修改合入上述COAST-R02，而不能用R04整场替换综合场景。最终源必须同时包含雨、材料、海和山，不能各有一份互相缺失的版本。

详见COAST-CURRENT-STATE.md与COAST-RAIN-COORDINATION.md。两份记录也区分源保存和实际图像通过。

## R03实际取回情况

R03源码6ad3c7c0fbcc66a013ddf42b9ab2a6cec616932d；运行34147780955，源checkpoint0e0f56888549e27900070a83b9830f81c3313c4b；master SHA dfd9a0e28967b8a474bc9688ce0b75d194dba20ce14aab5f18f1d11da7aa32b5，实际34,013,306 bytes。

已实际取回结束artifact10029248613，43,573,583 bytes，ZIP SHA43ce831c344648704029ff7b39b6be41e2fb7c9483150d62bb970af2ff0ca726。19项清单匹配；实际六张PNG（玻璃雨、厅景、木作、湿石、织物、外景）已查看。缺D01-node-regression.png和detail-reopen-check.json，上传状态PARTIAL_OR_FAILED_NOT_A_PASS，不写成完整七图通过。

R03原尺寸审查：玻璃出现尖锐黑雨杆，因此才做R04光学修正；湿石观察整体过暗、积水边界过硬；织物显得过于均匀、微结构不足以独立读出；木作有可见纹理，但曲边条带及反光层次仍有问题。C01大景降雨也不够显著。不要把“节点已增加”写成顶级材质完成。这些是已见图的问题，并非所有后续修正都已完成。

原R03在运行时的完整状态保存在commit38de05879dec51d8e533676da16a15e13e201756的本文件。其未释放内存警告、缺图与原黑雨杆证据保留，不重写失败历史。

## 历史保护与未完成项

R02完整证据12ae1030686d97823548b2967805d85853d12ab2，master SHA173da1291bff8a39da704539c737e21f9b2d739e3d32a106f629601bc2abefdc。G2 BEST、R07、所有原图/失败/工件、main和Leaf均不改。G4阶段顺序例外仍见G4-AUTHORIZATION.md，G3不追溯PASS。

海浪是原生深水谱与几何接触范围的受控泡沫，不是岸边冲击流体求解；雨的屋顶截断基于停稳451帧，不是完整进站动态碰撞验证。G4仍未通过，最终4K主片/短版/空间证据片/同源网页未完成，human_acceptance=false。浏览器BLOCKED_BY_ADMINISTRATOR不绕过。

综合候选单次源15分钟、渲染50分钟（43分钟生产+7分钟保存余量），标准公开runner、单生产并发、外部费用0、磁盘8GB、证据180MB。待已安排的原生观察返回后再判断具体修改，不自动启动无限轮次。
