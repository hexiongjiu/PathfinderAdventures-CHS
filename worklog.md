# 2026-06-30 工作记录

## 1. 修复 sharedassets0.assets 白屏崩溃

**问题**：release 里的 sharedassets0.assets 被字体修改损坏（56720 字节 → 原版 74000 字节），导致游戏白屏。

**根因**：dax-bold 是位图字体，字形与纹理图集深度绑定，任何修改都会破坏结构。UnityPy 保存后丢 17KB 数据。

**解决**：从 release 和 git 中移除 sharedassets0.assets，Steam 验证恢复原版。

---

## 2. 分析 all game files 中文内容提取

**方法**：用 UnityPy 解析 `.assets` 文件的 TextAsset（XML）和 level 文件的 TextMesh 组件。

- TextAsset: 从 `<DefaultText>`, `<FemaleText>`, `<Name>`, `<ShortDescription>` 等标签提取
- TextMesh: 读取 `m_Text` 字段
- 用反向引用正则 `\1` 确保开关标签匹配，避免漏抓

**输出**：`chinese_text_v2.csv`（19,113 行）

> 注意：PowerShell 控制台无法显示中文，需用文件输出或 Read 工具查看。

---

## 3. DispositionType 枚举中文修复

**问题**：`EffectExploreRestriction.GetDisplayText` 调用 `UI#1158 "探 索：{0} {1}"`，`{0}` 填 `DispositionType` 枚举。原版 DispositionType 无 `[StrRefAttr]`，显示的 `Banish` 等动词全英文。

**DLL 补丁**：`patch_disposition.py`，为 11 个值加 `[StrRefAttr(id, "HelperText")]`：
- Banish=34, Shuffle=33, Top=153（已有条目）
- Acquire=9995, Bottom=9996, Destroy=9994, SetAside=9993, Box=9992, RemoveFromTheGame=9991, AlwaysBanish=9990, UnderTop=9989（新增）

**resources.assets**：插入 8 个 HelperText 英文条目，CSV 翻译后为中文。
- 9989: Under Top → 压 入 库 底
- 9990: Always Banish → 总 是 放 逐
- 9991-9996: 移出游戏 / 搁置 / 销毁 / 获取 / 底部

---

## 4. EffectCardRestriction 占位符修复

**问题**：UI#1154 `{0}{1}{2} added to check` 被 `EffectCardRestriction` 和 `EffectCardRestrictionPending` 直接返回，不调 `string.Format`，导致显示 `{0}{1}{2}` 字面量。

**分析**：
- UI#1154 是为 `EffectBoostCheck` 设计的（DiceType + DiceBonus + Trait 三个参数）
- `EffectCardRestriction` 没有骰子数据，不需要占位符
- 给 CardRestriction 强加 Format 会显示垃圾数据

**DLL 补丁**：`patch_cardrestriction_v2.py`
- `EffectCardRestriction.GetDisplayText`: `ldc.i4 1154` → `ldc.i4 1353`
- `EffectCardRestrictionPending.GetDisplayText`: 同上

**resources.assets**：新增 UI#1353 `Card Restriction` → `卡 牌 限 制`（无占位符）

---

## 5. apply.py 自定义条目插入修复

**问题**：apply.py 的自定义条目插入代码存在两个 bug：

1. **`data.save()` 后 `obj.read()` 返回原始数据**  
   UnityPy 的 `TextAsset.save()` 不更新内部缓存，后续 `obj.read()` 返回保存前的原始数据。先插入后翻译的流程中，CSV 翻译循环的 `obj.read()` 会把插入内容覆盖掉。

2. **多条插入分多次 `data.save()`**  
   每个插入块独立调用 `data.save()`，只有最后一次保留。

**修复**：将插入逻辑移到 CSV 翻译循环内部，**先插入 → 再翻译 → 最后保存**：
```python
for obj in env.objects:
    data = obj.read()
    s = data.m_Script

    # 1. 插入自定义条目（英文 DefaultText）
    if name == 'HelperText':
        insert 998/999 + 9989-9996
    if name == 'UI':
        insert 9997-9999 + 7000-7009 + 1353

    # 2. CSV 翻译替换（把插入的英文也译成中文）
    s = ID_RE.sub(replacer, s)

    # 3. 保存（翻译+插入一起生效）
    data.m_Script = s
    data.save()
```

**插入条目汇总**：
| 表 | ID 范围 | 用途 |
|-----|---------|------|
| HelperText | 998, 999 | Discard / Bury |
| HelperText | 9989-9996 | DispositionType |
| UI | 9997-9999 | Hand / Discard / Pile |
| UI | 7000-7009 | DeckType |
| UI | 1353 | CardRestriction |

---

## 6. DLL 终极补丁

`patch_all_final.py` 补全 release DLL 缺失的：
- DeckType StrRefAttr (7000-7009)（之前备份链断裂丢失）
- "Skip" → "跳 过"（CharacterPowerExamine.ShowPopUp）

最终 release DLL 包含全部补丁：
- ActionType → ToText
- SkillType StrRefAttr
- DeckType StrRefAttr
- GuiSkillLine 属性名（力量/敏捷/体质/智力/智慧/魅力）
- Skip → 跳 过
- DispositionType StrRefAttr
- EffectCardRestriction → 1353

---

## 7. 关键教训

1. **UnityPy 的 `data.save()` 不持久化**：修改后 `obj.read()` 返回原始数据。必须在同一次迭代中完成所有修改再保存。

2. **Unity 5 字体完全不能动**：`sharedassets0.assets` 的 dax-bold 位图字体，任何属性/纹理修改都崩溃。

3. **level 文件 TextMesh 可以用 UnityPy 修改**：最初认为不行（白屏），实际是 hex 编辑和 sharedassets0.assets 的问题。UnityPy 读写 level 文件 TextMesh 正常工作。

4. **PowerShell 内联 Python 引号问题**：`{}` 和 `"` 冲突严重，大段代码必须写 `.py` 文件。

5. **Mono.Cecil IL 替换**：`processor.Replace` 保持原指令 operand 大小。`ldc.i4`（4 字节 operand）换 `ldc.i4` 安全。**修改指令时不能迭代 collection**，需先收集再替换。

6. **CustomAttribute 参数类型**：pythonnet 中必须用 `System.Int32()` 而非 Python `int`，否则 `Python.Runtime.PyInt` 写入失败。

7. **中文字符间距规范**：ALI213 约定每个 CJK 字符间用 ASCII 空格（0x20），数字/英文后跟 CJK 也要空格。`fix_spaces.py` 去所有空格后统一重加。

8. **DLL 备份链管理**：每个 patcher 脚本从当前 DLL 备份后修改。Steam 验证后需重跑所有补丁。release 文件夹的 DLL 是最终版本。

---

## 8. Level 文件 TextMesh 批量汉化

### 方法
用 UnityPy 读取 level 文件 → 找到 TextMesh 组件 → 修改 `m_Text` → `data.save()` → `sf.save()`。

### 已修改的文件
| 文件 | 修改数 | 典型内容 |
|------|--------|---------|
| level1 | 36 | （ALI213 已有的，只修间距） |
| level2 | 31 | Cancel/Normal/OK |
| level3 | 34 | Create Party/Equipment/Current Role/Add Character 等 |
| level4 | 5 | Collection/Equipment/View Party/VIEW ALL/Unclaimed |
| level5 | 6 | Manage\nRunes/Decks/Party |
| level6 | 3 | Cancel/Skip/Continue |
| level7 | 7 | Equipment/Finish/Continue/Manage Party/Decks |
| level8 | 11 | Card/Deck 相关 |
| level9 | 18 | 选择角色提示等 |
| level10-14 | — | 间距修正 |

### 注意
- "Manage Runes" 在 level5 中是 `"Manage\nRunes"`（换行符），容易搜漏
- "VIEW ALL" 全大写，不是 "View All"
- "Collection" → 收 藏（不是"卡牌"）

---

## 9. DLL 硬编码文本补丁

### Stash 计数器
`GuiWindowSelectCards.UpdateCardCounters` 中的 `ldstr "Stash "` → `"存 放 "`（patch_stash_dll.py）

### 注意
"Stash" 不在 TextMesh/贴图/StringTable 任何地方，只有 DLL ldstr

---

## 10. 文件清单

| 文件 | 用途 |
|------|------|
| `patcher/patch_disposition.py` | DispositionType 加 StrRefAttr |
| `patcher/patch_cardrestriction_v2.py` | CardRestriction 改 UI ID |
| `patcher/patch_all_final.py` | DeckType + Skip 补丁 |
| `patcher/patch_stash_dll.py` | Stash 计数器中文 |
| `apply.py` | 翻译导入，含自定义条目插入 |
| `extract_cn_fixed.py` | 提取所有中文文本到 CSV |
| `fix_spaces.py` | 统一中文字符间距 |
| `patch_all_levels.py` | 批量改 level TextMesh |
| `patch_level3_all.py` | level3 单独补丁 |
| `chinese_text_v2.csv` | 中文文本导出 |
| `check_ui_entries.py` | 验证自定义条目存在 |
| `search_kw.py` | CSV 关键词搜索 |
| `worklog_20260630.md` | 本文件 |

---

## 11. 更新流程

```
1. 修改 translations.csv
2. 关闭 Excel
3. 运行: python D:\CHS_Patch_Backup\apply.py
4. 复制 release 文件夹所有文件到游戏 Data 目录
5. 复制 release\Assembly-CSharp.dll → 游戏 Managed 目录
```
