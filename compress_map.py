# -*- coding: utf-8 -*-
import os
import sys
import shutil
import time

# 尝试导入 Pillow 库
try:
    from PIL import Image
    # 解除大图限制：防止因为图片像素过大而报错 (DecompressionBombError)
    Image.MAX_IMAGE_PIXELS = None
except ImportError:
    print("❌ 错误：未安装 Pillow 库。")
    print("👉 请先在 CMD 中运行: pip install Pillow")
    input("按回车退出...")
    sys.exit()

def main():
    # 强制定位到脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    map_filename = 'map.jpg'
    backup_filename = 'map_backup.jpg'

    print("========================================")
    print("🗺️  地图无损压缩工具 (尺寸不变版)")
    print("========================================")

    # 1. 检查文件是否存在
    if not os.path.exists(map_filename):
        print(f"❌ 找不到 {map_filename}，请确认文件名正确。")
        return

    # 2. 获取原始大小
    original_size = os.path.getsize(map_filename)
    print(f"📄 原始文件大小: {original_size / 1024 / 1024:.2f} MB")

    # 3. 备份原文件 (如果还没备份过)
    if not os.path.exists(backup_filename):
        print(f"📦 正在备份原图为 {backup_filename} ...")
        shutil.copy2(map_filename, backup_filename)
    else:
        print(f"ℹ️  发现已有备份 {backup_filename}，将基于此备份进行压缩...")
        # 为了保证质量，我们始终用备份（原图）作为源来压缩，避免重复压缩导致画质下降
        shutil.copy2(backup_filename, map_filename)

    # 4. 开始压缩
    print("⏳ 正在处理，请稍候（大图可能需要几秒钟）...")
    
    try:
        # 打开图片 (使用备份文件作为源，确保是最高画质)
        with Image.open(backup_filename) as img:
            print(f"📏 图片尺寸: {img.width} x {img.height} (保持不变)")
            
            # 保存参数说明：
            # quality=75: 视觉无损的甜点位，能大幅减小体积
            # optimize=True: 优化霍夫曼编码表
            # progressive=True: 渐进式加载（网页加载时先模糊后清晰，体验更好）
            # subsampling=0: 保持色彩采样 (4:4:4)，防止地图上的细红线变模糊
            img.save(
                map_filename, 
                "JPEG", 
                quality=75, 
                optimize=True, 
                progressive=True,
                subsampling=0 
            )

        # 5. 结果对比
        new_size = os.path.getsize(map_filename)
        saved = original_size - new_size
        percent = (saved / original_size) * 100

        print("\n✅ 压缩完成！")
        print(f"📉 新文件大小: {new_size / 1024 / 1024:.2f} MB")
        print(f"💰 节省空间: {saved / 1024 / 1024:.2f} MB (瘦身 {percent:.1f}%)")
        print("----------------------------------------")
        print("⚠️ 注意：原图已备份为 map_backup.jpg")
        print("如果觉得画质不满意，删掉 map.jpg，把备份改回名字即可。")

    except Exception as e:
        print(f"\n❌ 处理出错: {e}")
        # 如果出错，尝试恢复备份
        if os.path.exists(backup_filename):
            shutil.copy2(backup_filename, map_filename)
            print("已恢复原文件。")

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")