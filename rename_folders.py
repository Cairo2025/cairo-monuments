# -*- coding: utf-8 -*-
import os
import re

IMAGE_DIR = 'images'

def rename_folders():
    if not os.path.exists(IMAGE_DIR):
        print("找不到 images 文件夹")
        return

    count = 0
    for dirname in os.listdir(IMAGE_DIR):
        dir_path = os.path.join(IMAGE_DIR, dirname)
        
        # 匹配以 # 或 _ 开头的文件夹
        # 例如: _187_Complex... 或 #187#Complex...
        if os.path.isdir(dir_path):
            match = re.match(r'^[#_](\w+)[#_](.*)', dirname)
            if match:
                monument_id = match.group(1)
                rest_name = match.group(2)
                
                # 新名字格式：187_Complex (去掉开头的符号)
                new_dirname = f"{monument_id}_{rest_name}"
                new_dir_path = os.path.join(IMAGE_DIR, new_dirname)
                
                try:
                    os.rename(dir_path, new_dir_path)
                    print(f"✅ 改名: {dirname} -> {new_dirname}")
                    count += 1
                except Exception as e:
                    print(f"❌ 失败: {dirname} -> {e}")

    print("--------------------------------")
    print(f"🎉 完成！共修改了 {count} 个文件夹。")

if __name__ == "__main__":
    rename_folders()