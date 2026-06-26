"""导入：从 CSV 应用汉化到游戏目录"""
import csv, shutil, os, re
import UnityPy

BASE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE, 'translations.csv')
GAME_DATA = r'D:\steam\steamapps\common\Pathfinder Adventures\PathfinderAdventures_Data'
BACKUP = os.path.join(BASE, 'backup_new_eng')
RELEASE = os.path.join(BASE, 'release')

def xml_escape(text):
    text = text.replace('&amp;', '\x00AMP\x00')
    text = text.replace('&lt;', '\x00LT\x00')
    text = text.replace('&gt;', '\x00GT\x00')
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('\x00AMP\x00', '&amp;')
    text = text.replace('\x00LT\x00', '&lt;')
    text = text.replace('\x00GT\x00', '&gt;')
    return text

print("读取 CSV...")
updates = {}
with open(CSV, 'r', encoding='utf-8-sig') as f:
    for row in csv.reader(f):
        if len(row) < 4 or row[0] == 'File': continue
        file_name, eid = row[0], row[1]
        
        # 支持两种格式：
        # 5列: File,EntryID,Name,English,Chinese
        # 4列: File,EntryID,English,Chinese
        if len(row) >= 5:
            chs = row[4]
        else:
            chs = row[3]
        
        if not chs.strip(): continue
        chs = chs.replace('\\\\n', '\n').replace('\\n', '\n')
        updates.setdefault(file_name, {})[eid] = chs

total = sum(len(v) for v in updates.values())
print(f"待更新: {total} 条，{len(updates)} 个文件")

print("恢复原版...")
for f in os.listdir(BACKUP):
    src = os.path.join(BACKUP, f)
    dst = os.path.join(GAME_DATA, f)
    if os.path.isfile(src) and f.endswith('.assets'):
        shutil.copy2(src, dst)

print("应用翻译...")
env = UnityPy.load(os.path.join(GAME_DATA, 'resources.assets'))
sf = list(env.files.values())[0]
changed = 0

ID_RE = re.compile(
    r'(<ID>(\d+)</ID>.*?<DefaultText>)(.*?)(</DefaultText>)',
    re.DOTALL
)

for obj in env.objects:
    if obj.type.name != 'TextAsset': continue
    try:
        data = obj.read()
        name = data.m_Name
    except:
        continue
    
    if name not in updates:
        continue
    
    s = data.m_Script
    if isinstance(s, bytes): s = s.decode('utf-8', 'replace')
    if 'StringTableFile' not in s: continue
    
    # 修复：将自闭合的 <DefaultText /> 替换，防止正则跨 Entry 匹配
    s = s.replace('<DefaultText />', '<DefaultText></DefaultText>')
    
    file_updates = updates[name]
    state = [False, 0]
    
    def replacer(m):
        eid = m.group(2)
        if eid in file_updates:
            new_text = xml_escape(file_updates[eid])
            state[0] = True
            state[1] += 1
            return m.group(1) + new_text + m.group(4)
        return m.group(0)
    
    s = ID_RE.sub(replacer, s)
    
    if state[0]:
        changed += state[1]
        data.m_Script = s
        data.save()

result = sf.save()
out_path = os.path.join(GAME_DATA, 'resources.assets')
with open(out_path, 'wb') as f:
    f.write(result)
print(f"已更新 {changed} 条，文件大小 {len(result):,} 字节")

shutil.copy2(out_path, os.path.join(RELEASE, 'resources.assets'))
print("完成！")
