# -*- coding: utf-8 -*-
import os
import json
import re
import urllib.parse
import sys
import traceback

# 强制设置标准输出为utf-8，防止Windows控制台打印Emoji报错
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.6 以下兼容
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def main():
    # 1. 强制定位工作目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("========================================")
    print(">>> 🚀 万能适配版脚本已启动！")
    print(">>> 正在扫描数据与图片连接...")
    print("========================================")

    DATA_FILE = 'data.js'           
    IMAGE_ROOT = 'images'           
    OUTPUT_FILE = 'data_with_paths.js' 

    # --- 基础检查 ---
    if not os.path.exists(DATA_FILE):
        print(f"❌ 错误：找不到 {DATA_FILE}")
        return
    if not os.path.exists(IMAGE_ROOT):
        print(f"❌ 错误：找不到 {IMAGE_ROOT} 文件夹")
        return

    # --- 读取 data.js ---
    print(f"📖 正在读取 {DATA_FILE}...")
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取核心数据数组
    match = re.search(r'const\s+FULL_DATABASE\s*=\s*(\[\s*\{.*\}\s*\])\s*;', content, re.DOTALL)
    if not match:
        print("❌ 无法识别 data.js 格式。请确认文件开头是 'const FULL_DATABASE = ['")
        return
    
    json_str = match.group(1)
    # 尝试处理 JS 对象中的末尾逗号 (常见导致 json.loads 失败的原因)
    json_str = re.sub(r',\s*\}', '}', json_str)
    json_str = re.sub(r',\s*\]', ']', json_str)

    try:
        data_list = json.loads(json_str)
    except json.JSONDecodeError as je:
        print("❌ data.js 内容格式有误，无法解析为 JSON。")
        print(f"   具体错误: {je}")
        print("   提示: 请检查 data.js 里是否有语法错误，例如多余的逗号。")
        return
    
    # 提取坐标数据
    coords_match = re.search(r'const\s+SAVED_COORDINATES\s*=\s*(\{.*\})\s*;', content, re.DOTALL)
    coords_content = coords_match.group(1) if coords_match else "{}"

    # --- 建立文件夹映射 ---
    print(f"🔍 正在扫描 {IMAGE_ROOT} 文件夹...")
    id_to_folder = {}
    
    for name in os.listdir(IMAGE_ROOT):
        path = os.path.join(IMAGE_ROOT, name)
        if os.path.isdir(path):
            m1 = re.match(r'^[#_](\w+)[#_]', name)
            m2 = re.match(r'^(\w+)_', name)
            
            if m1:
                id_to_folder[m1.group(1)] = name
            elif m2:
                id_to_folder[m2.group(1)] = name
            else:
                id_to_folder[name] = name

    # --- 关联图片 ---
    count = 0
    match_count = 0
    
    for item in data_list:
        item_id = str(item.get('id', '')).strip()
        item['image_paths'] = [] 

        folder_name = id_to_folder.get(item_id)
        
        if folder_name:
            match_count += 1
            full_path = os.path.join(IMAGE_ROOT, folder_name)
            
            if os.path.exists(full_path):
                for fname in sorted(os.listdir(full_path)):
                    if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                        safe_folder = urllib.parse.quote(folder_name)
                        safe_file = urllib.parse.quote(fname)
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

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_js_content)
    
    print("\n----------------------------------------")
    print(f"🎉 成功！已生成文件: {OUTPUT_FILE}")
    print(f"📂 成功匹配文件夹: {match_count} 个")
    print(f"📸 包含图片的地点: {count} 个")
    print("----------------------------------------")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("❌ 程序发生严重错误 (Crash):")
        print(traceback.format_exc())
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    finally:
        # 无论成功还是失败，都暂停等待用户按键
        try:
            input("\n按回车键退出程序...")
        except:
            pass