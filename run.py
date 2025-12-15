# -*- coding: utf-8 -*-
import os
import json
import re
import urllib.parse
import sys

# 1. 强制定位工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("========================================")
print(">>> 🚀 脚本已启动！正在更新数据连接...")
print("========================================")

DATA_FILE = 'data.js'           
IMAGE_ROOT = 'images'           
OUTPUT_FILE = 'data_with_paths.js' 

def main():
    if not os.path.exists(DATA_FILE):
        print(f"❌ 错误：找不到 {DATA_FILE}")
        return
    if not os.path.exists(IMAGE_ROOT):
        print(f"❌ 错误：找不到 {IMAGE_ROOT} 文件夹")
        return

    print(f"正在读取 {DATA_FILE}...")
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(r'const\s+FULL_DATABASE\s*=\s*(\[\s*\{.*\}\s*\])\s*;', content, re.DOTALL)
        
        if not match:
            print("❌ 无法识别 data.js 格式")
            return
        
        json_str = match.group(1)
        data_list = json.loads(json_str)
        
        coords_match = re.search(r'const\s+SAVED_COORDINATES\s*=\s*(\{.*\})\s*;', content, re.DOTALL)
        coords_content = coords_match.group(1) if coords_match else "{}"

    except Exception as e:
        print(f"❌ 解析出错: {e}")
        return

    # 4. 建立文件夹映射 (这里是修改过的地方)
    print(f"正在扫描 {IMAGE_ROOT} 文件夹...")
    id_to_folder = {}
    
    for name in os.listdir(IMAGE_ROOT):
        path = os.path.join(IMAGE_ROOT, name)
        if os.path.isdir(path):
            # ★★★ 修改：同时支持 #ID# 和 _ID_ 格式 ★★★
            m = re.match(r'^[#_](\w+)[#_]', name)
            if m:
                id_to_folder[m.group(1)] = name
            else:
                id_to_folder[name] = name

    # 5. 关联图片
    count = 0
    for item in data_list:
        item_id = str(item.get('id', '')).strip()
        item['image_paths'] = [] 

        folder = id_to_folder.get(item_id)
        if folder:
            full_path = os.path.join(IMAGE_ROOT, folder)
            # 使用 os.walk 以防万一有子文件夹，或者直接 listdir
            for fname in sorted(os.listdir(full_path)):
                if fname.lower().endswith(('.jpg', '.png', '.jpeg', '.webp')):
                    # URL 编码，确保特殊字符安全
                    safe_folder = urllib.parse.quote(folder)
                    safe_file = urllib.parse.quote(fname)
                    p = f"{IMAGE_ROOT}/{safe_folder}/{safe_file}"
                    item['image_paths'].append(p)
            
            if item['image_paths']:
                count += 1

    # 6. 写入文件
    print("正在写入新文件...")
    final_js_content = f"""
// ==========================================
// 自动生成的带图片路径数据文件
// ==========================================

const FULL_DATABASE = {json.dumps(data_list, ensure_ascii=False, indent=4)};

const SAVED_COORDINATES = {coords_content};
"""

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_js_content)
    
    print("\n----------------------------------------")
    print(f"🎉 成功！已生成文件: {OUTPUT_FILE}")
    print(f"📊 共为 {count} 个地点关联了图片")
    print("----------------------------------------")

if __name__ == "__main__":
    main()