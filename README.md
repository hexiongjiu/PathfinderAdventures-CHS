> 随缘更新，如果看到更新日期很久之前了，就是比较稳定版本了
> 虽然是基于游侠网的补丁做，但原来的汉化错误超多，而且哥布林2 DLC也没有翻译。一边玩，一边发现不对的地方去改
> 最后，错误实在太多了，用Agent逐条对照改，基本上现在错误是比较少了。

# Pathfinder Adventures 中文汉化补丁

基于游侠网汉化 v2.7 修改适配最新 Steam 版本，包含哥布林 DLC 汉化。

## 术语对照表

| 原文 | 汉化 | 机制本质 |
|------|------|---------|
| Recharge | 回库 | 结算成功后放回牌库底部，最完美的常规回收机制 |
| Discard | 弃牌 | 进入角色的弃牌堆，容易被治疗法术洗回牌库 |
| Bury | 埋葬 | 压入角色牌底，该局游戏很难再用（但未彻底死亡） |
| Banish | 放逐 | 彻底移出本局游戏，直接放回公共游戏大盒 |
| Bane | 祸害 | 统称所有对玩家不利的卡牌（怪物、屏障、心腹等） |
| Boon | 恩赐 | 统称所有对玩家有利的卡牌（武器、法术、盟友等） |
| Henchman | 心腹 | 区别于普通怪物，击败他能触发关闭地点 |
| Villain | 反派 | 关底Boss，通常需封锁地点来将其彻底围剿 |
| Reveal | 亮出 | 展示给其他玩家看后收回手牌 |
| Trait | 特性 | 卡牌属性标签（如 Book trait = 书籍特性） |
| Character | 角色 | 严禁写成"人物"或"玩家" |
| Elite | 精英 | 高阶卡牌特性，非"经营" |



## 安装方法

1. 在 Steam 库中右键 Pathfinder Adventures → 管理 → 浏览本地文件
2. 进入 PathfinderAdventures_Data 文件夹
3. 将本补丁中的文件复制进去覆盖：
   - resources.assets
   - sharedassets0.assets
   - level1
   - level2
   - level5
   - level8
   - level9
4. 将 Assembly-CSharp.dll 复制到 PathfinderAdventures_Data\Managed\ 覆盖（战斗界面动词中文显示修复）
5. 启动游戏

## 汉化内容

- 188 个文本文件完整汉化（卡牌、地点、场景、UI、教程、规则）
- 2034 张卡牌名称和描述全部翻译
- 新增 DLC 内容翻译（涂鸦脸、长腿人的复仇、深入盐沼、旧沉船等）
- 主菜单按钮汉化（开始/收藏/退出/设置）
- 场景内 UI 标签汉化
- 术语统一修正（恩赐/灾祸/地精/回库等）
- LLM 辅助校对：逐条对比中英文，修正 1600+ 条目
  - 术语统一：人物→角色、灾祸→祸害、经营→精英、装填→回库、显示→亮出
  - 漏译补全：关键信息如 "this woman"、"down"、"I'll do it" 等
  - 错译修正：dumb dog→蠢狗（非装哑巴）、downfall→覆灭（非黄昏）、slaves→奴隶（非努力）
  - 人名地名保持原样不修改
  - 保留全角空格排版格式

## 原始汉化

游侠网汉化 v2.7：https://game.ali213.net/thread-6273163-1-1.html

## 战斗界面动词修复（DLL 补丁）

叠牌数惩罚等界面显示英文 Discard/Bury/Pile 的问题，通过修改 Assembly-CSharp.dll 解决：

- **原理**：`GameStatePenalty`/`GameStateSacrifice`/`GameStatePickHand` 的 `GetHelpText` 方法将 `box ActionType` 替换为 `Extensions.ToText()`，利用枚举上已有的 `[StrRefAttr]` 特性查 UI 表获取中文文本
- **文件**：`patcher/` 目录含 Mono.Cecil 补丁脚本与说明

## 声明

本汉化仅供学习交流使用，请勿用于商业化用途。

