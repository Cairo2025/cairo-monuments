# -*- coding: utf-8 -*-
import os
import json
import re
import urllib.parse
import sys

# 1. 强制定位工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("========================================")
print(">>> 🚀 脚本已启动！正在处理你的 data.js")
print("========================================")

DATA_FILE = 'data.js'           
IMAGE_ROOT = 'images'           
OUTPUT_FILE = 'data_with_paths.js' 

def main():
    # 2. 基础检查
    if not os.path.exists(DATA_FILE):
        print(f"❌ 错误：找不到 {DATA_FILE}")
        return
    if not os.path.exists(IMAGE_ROOT):
        print(f"❌ 错误：找不到 {IMAGE_ROOT} 文件夹")
        return

    # 3. 读取并“抠出”数据
    print(f"正在读取 {DATA_FILE}...")
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # --- 核心修改：使用正则表达式精确提取数组 ---
        # 你的文件格式是: const FULL_DATABASE = [ ... ];
        # 我们只提取 [ ... ] 中间的部分
        match = re.search(r'const\s+FULL_DATABASE\s*=\s*(\[\s*\{.*\}\s*\])\s*;', content, re.DOTALL)
        
        if not match:
            print("❌ 无法识别 data.js 格式。请确认文件开头是 'const FULL_DATABASE = ['")
            return
        
        # 提取出的纯 JSON 字符串
        json_str = match.group(1)
        
        # 解析数据
        data_list = json.loads(json_str)
        print(f"✅ 成功解析 FULL_DATABASE，共 {len(data_list)} 条数据")

        # 同时我们也尝试保留 SAVED_COORDINATES 部分，以免丢失
        coords_match = re.search(r'const\s+SAVED_COORDINATES\s*=\s*(\{.*\})\s*;', content, re.DOTALL)
        coords_content = ""
        if coords_match:
            coords_content = coords_match.group(1)
            print("✅ 成功识别 SAVED_COORDINATES 数据")
        else:
            print("⚠️ 未找到 SAVED_COORDINATES，新文件将为空坐标（不影响图片功能）")
            coords_content = "{}"

    except Exception as e:
        print(f"❌ 解析出错: {e}")
        return

    # 4. 建立文件夹映射
    print(f"正在扫描 {IMAGE_ROOT} 文件夹...")
    id_to_folder = {}
    
    if len(os.listdir(IMAGE_ROOT)) == 0:
        print("⚠️  注意：images 文件夹是空的！")

    for name in os.listdir(IMAGE_ROOT):
        path = os.path.join(IMAGE_ROOT, name)
        if os.path.isdir(path):
            # 尝试匹配 #ID#
            m = re.match(r'^#(\w+)#', name)
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
            for fname in sorted(os.listdir(full_path)):
                if fname.lower().endswith(('.jpg', '.png', '.jpeg', '.webp')):
                    safe_folder = urllib.parse.quote(folder)
                    safe_file = urllib.parse.quote(fname)
                    p = f"{IMAGE_ROOT}/{safe_folder}/{safe_file}"
                    item['image_paths'].append(p)
            
            if item['image_paths']:
                count += 1

    # 6. 完美还原文件格式
    # 我们不仅要保存数据，还要把原来的格式（const ...）写回去，
    # 并且把 SAVED_COORDINATES 也带上，保证地图功能不丢失。
    
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
    input("\n按回车键退出程序...")