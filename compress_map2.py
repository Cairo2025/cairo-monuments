# -*- coding: utf-8 -*-
import os
import sys
import shutil
from PIL import Image

# 解除大图限制
Image.MAX_IMAGE_PIXELS = None

def get_size_mb(filename):
    if os.path.exists(filename):
        return os.path.getsize(filename) / 1024 / 1024
    return 0

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 这里的逻辑是：优先找备份文件(原图)来压缩，保证画质
    # 如果没有备份，就用当前的 map.jpg
    source_file = 'map_backup.jpg'
    if not os.path.exists(source_file):
        if os.path.exists('map.jpg'):
            print("⚠️ 未找到备份文件 map_backup.jpg，将使用当前的 map.jpg 进行压缩...")
            source_file = 'map.jpg'
        else:
            print("❌ 找不到 map.jpg")
            return

    print(f"📄 源文件: {source_file} ({get_size_mb(source_file):.2f} MB)")
    print("----------------------------------------")

    # === 方案 A: 激进优化的 JPEG ===
    # 质量设为 60 (地图纹理复杂，60通常是画质/体积的最佳平衡点)
    # 依然保持 subsampling=0 以防止红色文字/细线模糊
    target_jpg = 'map_optimized.jpg'
    print(f"⏳ 正在生成 {target_jpg} (Quality=60)...")
    with Image.open(source_file) as img:
        img.save(
            target_jpg, 
            "JPEG", 
            quality=60,      # 从 75 降到 60
            optimize=True, 
            progressive=True,
            subsampling=0    # 关键：保持文字清晰
        )
    print(f"✅ JPEG 生成完毕: {get_size_mb(target_jpg):.2f} MB")

    # === 方案 B: WebP 格式 (推荐) ===
    # WebP 在处理大面积色块（地图常见）时效率极高
    target_webp = 'map.webp'
    print(f"⏳ 正在生成 {target_webp} (WebP Quality=75)...")
    with Image.open(source_file) as img:
        img.save(
            target_webp,
            "WEBP",
            quality=75,      # WebP 的 75 相当于 JPEG 的 85-90
            method=6         # 最慢的压缩算法，但体积最小
        )
    print(f"✅ WebP 生成完毕: {get_size_mb(target_webp):.2f} MB")

    print("----------------------------------------")
    print("📊 结果对比：")
    print(f"1. 原始大小: {get_size_mb(source_file):.2f} MB")
    print(f"2. 新版 JPEG: {get_size_mb(target_jpg):.2f} MB (如果不换代码，请把这个重命名为 map.jpg)")
    print(f"3. WebP 格式: {get_size_mb(target_webp):.2f} MB (🔥 强烈推荐，需修改一行代码)")

if __name__ == "__main__":
    main()
    input("\n按回车退出...")