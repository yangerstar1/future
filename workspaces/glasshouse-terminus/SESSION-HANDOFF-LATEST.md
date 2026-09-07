# 雨幕终点站 — 最新续作入口

仓库yangerstar1/future；制作分支codex/glasshouse-terminus；工作根workspaces/glasshouse-terminus。

## 当前已完成状态：COAST-R09源与原生观察均已取回

用户要求继续优化各部分、达到商业顶尖建模真实感。本轮实际从R07综合场景继续，完成R08构造优化和原生对照，再完成R09主顶壳体局部修正。**最新可恢复版本是COAST-R09，三张该版本原图已实际审查。不是只有脚本，不再等待旧R07/R08渲染，不得回退R02或孤立雨材质版。**

G4仍PAUSED_UNMET，stage_best=null、human_acceptance=false。源完整、CI成功和局部改善均不等于商业顶尖或最终验收。

## 唯一优先恢复点

完整证据commit：**3b66a604c65b8c98162450a73640c847f2734474**。
证据分支：evidence/g4-coast-r09-34168580326-1。
目录：**workspaces/glasshouse-terminus/output/g4-coast-r09**。
主文件：g4-full-scene-candidate.blend。
实际主文件大小：**154401842 bytes**。
实际SHA-256：**001a708dda2744a0f9db2994937982d121ce766aab6768746e884a72c4feaeef**。

最终artifact10035316043，202948721 bytes，实际ZIP SHA-2564dc902738a01b21c9f40220c56feaef4d83e249f1cab8c20ff58c0fbfc413ce1。**51项文件清单全部匹配，missing=[]**。三张原图为R09-cab-shell.png、R09-complete-coast.png、R09-carriage-interior.png，均已实际打开。三个新进程渲染退出码0、重开外部图片缺失0、master前后相同。

源checkpoint9aaf262f3db4c78b85dcd314e22a382ee6c9db4b。源artifact10034983310，198604092 bytes，ZIP SHA63e12decaa93c98e5a75c1e0b6a4963c075a652664f6945d3ec1dfe86e6d788f；实际主文件、三块无损运输SHA和十项共享资产/来源记录均核验。

Git证据是以main为基底的data-only分支，不含最新制作代码；不要整分支替换制作分支。大主文件在Git中是53MB无损分块，Actions ZIP含完整.blend。临时artifact只有一天保留，长期恢复用上面的完整证据commit。

在已确认位于真实仓库根、工作树无目标冲突的环境：

```bash
git fetch --depth=1 origin 3b66a604c65b8c98162450a73640c847f2734474
git archive FETCH_HEAD workspaces/glasshouse-terminus/output/g4-coast-r09 | tar -x
python3 workspaces/glasshouse-terminus/output/g4-coast-r09/restore_master.py restore workspaces/glasshouse-terminus/output/g4-coast-r09
echo '001a708dda2744a0f9db2994937982d121ce766aab6768746e884a72c4feaeef  workspaces/glasshouse-terminus/output/g4-coast-r09/g4-full-scene-candidate.blend' | sha256sum --check
```

主文件默认打开相机已经设回原C01_exterior_hero；所有诊断和失败机位仍在，不删除原角度遮丑。

## 本轮运行已经结束，不重复提交触发

R09 run34168580326，制作源码3309dc100fa082926643888c53f03c9f762f1a36；source101884403819和native-review101884649817均已完成success。脚本correct_g4_r09_barrel_shell.py；工作流.github/workflows/glasshouse-g4-r09-roof-shell.yml。本次12分钟source+24分钟review（20分钟生产、4分钟保存）的有限请求已完成。

R08 source run34165514100建模成功，原组合渲染失败已保留；独立原图恢复run34167314803实际八张观察已齐，无缺图/失败视图。脚本refine_g4_r08_craft.py、observe_g4_r08_craft.py；不要重复启动这些请求。

R07 run34163114491也已结束，最后海岸图超时，其三张完成图与十张雨水帧保留。R06缺失木作/节点早已通过run34162646428补齐，不再重跑旧恢复。

## 实际建模与验收结论

本轮两次只读侦察均读取真实当前master，而非编造结构：

R07工艺审计34164882942，证据fabf97ac9fa264a741429c0dc01c75e63f322381，确认两端车头各50顶点/24个未平滑面、32个八顶点倒角软包以及当前海面修改器/材质。R08把车头改为锚定接口的平滑四边面曲面，软包改为有侧围/隆起裁片/缝边针脚的闭合形体，海面保留原光学水体并增加短风浪和11–51厘米细波。原雨、玻璃、扫描山崖、木作、扫描羊毛、世界、灯光和原相机保留。

R08原图对照确认车头折面改善，但暴露主顶高台阶。追加只读界面审计34168368119，证据3171758a15f1aacba0c5fa14807f23bfba5b2637，实测Car_complete_barrel_roof法线朝内，使65mm Solidify厚度长到外面。源网格接口采样吻合曾遗漏求值实体外皮错位，不能再只用基网格误差判几何通过。

R09只反转主顶48面并平滑，98个顶点坐标和无向连接保持不变、65mm厚度不变，主顶求值高度4.135→4.070m，与未再改动的车头相齐。原图确认宽台阶消除、放射折面未恢复；C01/C09原机位回归保持。少量收口高光与细部仍粗，不能声称完整制造级公差通过。

R08八张原生观察包含三组R07/R08同机位前后对照及R08 C01/C09。完整观察证据49d4c68a788a0fc8bff0bcbf7eeed49fae69bdd6 / output/g4-r08-observations，artifact10035011283，12758534 bytes，ZIP SHAaf1443b9ffc25dbacfea23636c4c83428ede024c0f2582ccc3b5ef55ba524e29。49项清单全匹配，三组镜头/位置/焦距/帧/samples/尺寸/曝光/快门逐项一致；两份master均未save。它们是父版观察，不冒称R09新渲。

当前三张R09也分别对照了相同机位和设置。所有图为原生1280×800或1440×900诊断图，不调色、不增强、不超分，不冒称最终4K。评审详见 **G4-COAST-R09-REVIEW.md**（提交9cdd3791ad2aa41f4c1b8baea7c69e6afbd646a5）及G4-COAST-R08-REVIEW.md。最新G4-EVIDENCE-INDEX.json已同步，不再以其中旧R02标签回退。

## 必须继续的真实弱项

雨：贴面水流及雨滴已有源和原生帧，但大景暴雨身份仍弱、部分水珠分布偏均匀。原雨轨迹终点来自更早的停稳场景，本轮车顶实体外皮改变后，须重新检查当前停稳/进站动态的遮雨、落点及浮空间距，不能把保留雨数据当成已通过当前碰撞。

海与山：细波层次增加，但排列仍规则；远海尺度、地平线和岸边泡沫/冲击关系不足。扫描崖壁上方的大轮廓、基座接口和桥拱接头仍不够自然。不要再用盲目加光或噪声代替实际构造。

材质与软包：实际缝边/织物保留，但软包受压、裁片收束、使用痕迹及一些小五金/收口仍需深化。R07湿石原图仍太暗，四只基座灯没有解决；不能因它们存在就关闭该问题。室内保持干燥，不靠全地面镜面化制造高级感。

下一次先从R09只读定位以上待改对象及实际节点/遮挡，挑真正影响全景和近景的高优先问题，做新的有限局部任务并返回当前源原图。不要恢复R02、重复G0/G2、无限加雨、重建已经有的谱海面或重复本轮已完成任务。

## 保留失败与历史恢复

R08初始失败观察证据134985500b8ad25499fde9f7409e1c31203e11bb：新车头仪器被湿雨棚挡住，16分钟组合基线随后在第二张图超时。原artifact10034470859清单38项中37项匹配，baseline-render.log在终止后多138bytes；master与PNG正确，未重写失败包。后续独立观察把内部超时设得短于步骤时限，确保进程退出后再算清单，现49项正确。原失败PNG/相机保留，新无遮挡机位只增加仪器，不删除几何。

R07完整失败保存37b91cc3bddbfaae64d1f34bf4951e16146be1b1，58项清单匹配，三图+十帧，缺最后C01及context-reopen。R07动态由十张640×400原帧直接编码1秒10fps，无插帧；明确属于R07，不冒称R09或最终30fps。

R08父源caf093e65db1e364e2403e6a7807a3ef5da88b5b，masterc96c202a13c5ecd342a7b614a77b1e24ec9889bdb79cc328a255607467d7e877。
R07父源91b5bcc932c58e5a43b20061299bb6a6f606aaaa，master386ab4bfb0134988962efaa96d03e883ed557b30843aba6c20de0af9d999c396。
更早COAST-R04/R05/R06和完整G4-R01/R02索引通过G4-EVIDENCE-INDEX.json的不可变历史链接保留；完整上一轮交接在bb15afcca8f2794b7c983a8ab3a94e02973e49da的同名文件。原G1–G3 EVIDENCE-INDEX.json没有改写。

## 硬边界

生产必须glasshouse-production / cancel-in-progress:false / queue:max，一个生产renderer，保留所有历史候选和失败。官方固定Blender4.5.13 LTS、现有scene_common/provision/publish_evidence/无损运输脚本继续复用，不另起框架。有限请求不是无限重跑授权。

原合同SHA0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f已完整阅读；视觉目标不降低。用户G4阶段顺序例外保留，不追溯G3 PASS。main/Leaf/G2 BEST不改，浏览器管理员阻断不绕过。原生4K30主片、短版、完整空间证据片、同源网页及最终验收仍未交付。
