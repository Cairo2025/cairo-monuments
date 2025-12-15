# -*- coding: utf-8 -*-
import os

IMAGE_DIR = 'images'

def rename_folders():
    if not os.path.exists(IMAGE_DIR):
        print("找不到 images 文件夹")
        return

    count = 0
    # 获取 images 下的所有文件夹
    for dirname in os.listdir(IMAGE_DIR):
        dir_path = os.path.join(IMAGE_DIR, dirname)
        
        # 只处理文件夹，且名字里带有 # 的
        if os.path.isdir(dir_path) and '#' in dirname:
            # 把 # 替换为 _ (下划线)
            new_dirname = dirname.replace('#', '_')
            new_dir_path = os.path.join(IMAGE_DIR, new_dirname)
            
            try:
                os.rename(dir_path, new_dir_path)
                print(f"✅ 改名: {dirname} -> {new_dirname}")
                count += 1
            except Exception as e:
                print(f"❌ 失败: {dirname} -> {e}")

    print("--------------------------------")
    print(f"🎉 完成！共修改了 {count} 个文件夹名称。")

if __name__ == "__main__":
    rename_folders()
    input("按回车退出...")