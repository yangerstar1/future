# 回天港恢复交接 — 前飞跟拍批次已启动，尚未交付新完整影片

先读 PRODUCTION-STATE.json、R07B-FLIGHT-REVIEW.md 和 R06-INTERVENTION.md。原始主合同仍为 1.0.0。用户最新要求是改进差的渲染、舰船独立向前飞、镜头跟随；不再是舰船与巨环共同旋转。

## 当前应继续的唯一渲染批次

Run `34559500985`，工作流 `.github/workflows/skyfold-tracking-delivery.yml`，渲染源提交 `599793ea843b2ebf1d9089b5dd35d1d333cd1d06`。

该批已通过预算检查，四段真实帧范围为 1–48、49–96、97–144、145–192，原生 1920x1080、24 fps，目标合成 8 秒 H.264。另有 2560x1440 主图和无合成控制图。矩阵最多两个 CPU 作业并行，随后复用已存在 assemble_tracking_preview.py 完成帧数、时间戳、来源、变换和拼接验证。

**下一步先查询本 run 的 jobs/artifacts，不重复触发整批。** 完整新影片未取回前不写已完成。单个失败作业只重试该失败部分；修脚本后记录真实新来源。保持旧成功工件，不删除失败证据。

## 精确可恢复源

已实际取回并核验的 Finish 场景：`output/r07b-finish/skyfold-r07b.blend` 与相邻 `BUILD-MANIFEST.json`。
证据 commit `3c7b65226dec6fe43261ad1d247cb4ccb9a845e5`，branch `evidence/skyfold-r07b-finish-34559187757-1`。
Scene SHA256 `e9ffbb9051f27fe6c19d6ff7069cd5f419b9517e3b4ee2b0d0f889845e8086c6`；场景生成源 `6a46b9905188967f618d86fdea6faaf7900afc36`。Probe run `34559187757`，artifact `10183723530`，ZIP SHA256 `4495cbb7408b3ad27a6f2d4d668c7e71ed015037e31c0f6cfda7414e3b67db71`。

此场景含舰船根节点 `R06_SHIP_FORWARD_FLIGHT`、跟拍机位 `R07B_FLIGHT_TRACK`。根节点由 (-20900,-40000,8100) 前进到 (-20900,-40640,8120)，艏向 -Y，镜头追踪真实目标。巨环静止，灯光是明确的影视照明设置。起镜已经释放，不是完整离泊机构或轨道动力学模拟。

R07B 几何及跟拍来自上一证据 commit `823e6d8bb663f0ae7c788bcad773fd2920f16502`，scene SHA256 `870c8f7706fbfc42666eb94301d9c8dced5487b2bfcf9e49100f2380a8349b6b`。Finish 只改变材质/灯光/背景，不再次换镜头。原 R06–R07 的失败试样和旧镜头都留在对应证据分支与版本历史。

## 真实观察与未通过项

Finish probe 15 个清单文件哈希匹配，三张 PNG 解码通过，首末帧已经打开。深色背景让主体轮廓更清楚，但舰船仍有基础体块拼装感，远处城市还像纹理，巨环顶端余量不足；不能称专业渲染已解决，更不能称达到 Rui Huang 作品水平。中性图解码不代替目视结构终验。

G1 校准仍不完整、G2 未冻结，G3–G6 未通过；best=null，AUTO_QUALIFIED=false。20km 环径修订的旧船坞/运输接口没有重新完成终验。当前视频是用户后来要求的真实跟拍候选，不替代原合同的三种职责呈现图、近景工艺和冷恢复。

## 完成后应保存

取回最后 `skyfold-tracking-delivery-34559500985` artifact；它应包含 .blend、所有 192 帧的视频与源哈希/矩阵、选定原始 PNG、解码样本、2560 静帧、脚本和日志。并不是全部未压缩 PNG 都永久保存。核对镜头始终跟住舰船、背景静止、拼接边界连续以及源样本与解码帧一致，再更新真实视觉评审、RUN-LEDGER、EVIDENCE-INDEX、README 和本文。完成后将选定工件并入生产分支，生成聊天恢复包；临时 artifact 不是唯一介质。

## 预算和保护

预算预检已核对 27 个完成作业（包含 R06 首次失败），累计 12968 作业秒、3.602222 runner-hours。当前批次尚未结算，不能用预估当实际。按实测 1080p 首帧 41.879204 秒乘 192*1.5，再加一小时静帧/工具/QA及重试余量，计划 15661.210752 秒。总上限48小时，收尾预留9.6小时，并发最多2；未启用付费 runner/模型API。账户总存储费用未知。

保护旧 R05B `.blend`：SHA256 `890c7d7d166371fb59627d1ab43bacae36a031c81f3a3eebc5de418e7cb363f2`；旧 R04C 720p 视频 SHA256 `15848f4d744c53cc6f1175fd1ab79a3c6ed212b82ad2d8b522704c64e8fa87a0`。二者已交付，不要重跑或混称成新的前飞影片。完整旧交接在 commit `5e210a41dc35829a82ccc39ab5213160d51f76d7`。不改其他项目分支，不发布 Release/Pages，不复制私有 Leaf 历史。
