# -*- coding: utf-8 -*-
import os
import json
import re
import urllib.parse
import sys

# 1. 强制定位工作目录到脚本所在位置，防止路径错误
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("========================================")
print(">>> 🚀 万能适配版脚本已启动！")
print(">>> 正在扫描数据与图片连接...")
print("========================================")

DATA_FILE = 'data.js'           
IMAGE_ROOT = 'images'           
OUTPUT_FILE = 'data_with_paths.js' 

def main():
    # --- 基础检查 ---
    if not os.path.exists(DATA_FILE):
        print(f"❌ 错误：找不到 {DATA_FILE}")
        input("按回车键退出...")
        return
    if not os.path.exists(IMAGE_ROOT):
        print(f"❌ 错误：找不到 {IMAGE_ROOT} 文件夹")
        input("按回车键退出...")
        return

    # --- 读取 data.js ---
    print(f"📖 正在读取 {DATA_FILE}...")
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取核心数据数组
        match = re.search(r'const\s+FULL_DATABASE\s*=\s*(\[\s*\{.*\}\s*\])\s*;', content, re.DOTALL)
        if not match:
            print("❌ 无法识别 data.js 格式。请确认文件开头是 'const FULL_DATABASE = ['")
            input("按回车键退出...")
            return
        
        json_str = match.group(1)
        data_list = json.loads(json_str)
        
        # 提取坐标数据 (保留原有的地图点位)
        coords_match = re.search(r'const\s+SAVED_COORDINATES\s*=\s*(\{.*\})\s*;', content, re.DOTALL)
        coords_content = coords_match.group(1) if coords_match else "{}"

    except Exception as e:
        print(f"❌ 解析出错: {e}")
        input("按回车键退出...")
        return

    # --- 建立文件夹映射 (核心逻辑) ---
    print(f"🔍 正在扫描 {IMAGE_ROOT} 文件夹...")
    id_to_folder = {}
    
    for name in os.listdir(IMAGE_ROOT):
        path = os.path.join(IMAGE_ROOT, name)
        if os.path.isdir(path):
            # 兼容模式：尝试提取开头的 ID
            # 逻辑：匹配开头可能有的 # 或 _，然后是 ID (数字或字母)，然后必须紧跟一个分隔符 (# 或 _ 或 空格)
            
            # 尝试1: 匹配 _187_ 或 #187# 这种包围结构
            m1 = re.match(r'^[#_](\w+)[#_]', name)
            
            # 尝试2: 匹配 187_Name 这种下划线开头结构 (最推荐的格式)
            m2 = re.match(r'^(\w+)_', name)
            
            if m1:
                monument_id = m1.group(1)
                id_to_folder[monument_id] = name
            elif m2:
                monument_id = m2.group(1)
                id_to_folder[monument_id] = name
            else:
                # 如果没有特殊符号，尝试直接用文件夹名作为 ID
                id_to_folder[name] = name

    # --- 关联图片 ---
    count = 0
    match_count = 0
    
    for item in data_list:
        item_id = str(item.get('id', '')).strip()
        item['image_paths'] = [] # 清空旧路径，防止重复

        # 在映射表中查找这个 ID 对应的文件夹名
        folder_name = id_to_folder.get(item_id)
        
        if folder_name:
            match_count += 1
            full_path = os.path.join(IMAGE_ROOT, folder_name)
            
            # 扫描该文件夹下的所有图片
            if os.path.exists(full_path):
                # 获取文件列表并排序，保证顺序一致
                for fname in sorted(os.listdir(full_path)):
                    # 检查是否是图片格式 (不区分大小写)
                    if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                        # URL 编码，把空格、# 等特殊字符转义，保证网页能读取
                        safe_folder = urllib.parse.quote(folder_name)
                        safe_file = urllib.parse.quote(fname)
                        
                        # 拼接成网页路径
                        p = f"{IMAGE_ROOT}/{safe_folder}/{safe_file}"
                        item['image_paths'].append(p)
                
                if item['image_paths']:
                    count += 1

    # --- 写入新文件 ---
    print("💾 正在写入新文件...")
    
    final_js_content = f"""
// ==========================================
// 自动生成的带图片路径数据文件
// ==========================================

const FULL_DATABASE = {json.dumps(data_list, ensure_ascii=False, indent=4)};

const SAVED_COORDINATES = {coords_content};
"""

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_js_content)
        
        print("\n----------------------------------------")
        print(f"🎉 成功！已生成文件: {OUTPUT_FILE}")
        print(f"📂 成功匹配文件夹: {match_count} 个")
        print(f"📸 包含图片的地点: {count} 个")
        print("----------------------------------------")
        
    except Exception as e:
        print(f"❌ 写入文件失败: {e}")

if __name__ == "__main__":
    main()
    # 这一行是为了防止双击闪退，让你能看到结果
    input("\n按回车键退出程序...")