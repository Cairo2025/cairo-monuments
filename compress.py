# -*- coding: utf-8 -*-
import os
from PIL import Image
import sys

# =================配置区域=================
IMAGE_DIR = 'images'       # 图片文件夹名字
MAX_WIDTH = 1600           # 图片最大宽度 (像素)
MAX_HEIGHT = 1600          # 图片最大高度 (像素)
QUALITY = 80               # 压缩质量 (1-100)

# ★★★ 新增设置：触发压缩的门槛 ★★★
TRIGGER_SIZE_KB = 800      # 只有大于 800KB 的图片才会被压缩
# =========================================

def get_size_mb(size_in_bytes):
    return size_in_bytes / (1024 * 1024)

def get_size_kb(size_in_bytes):
    return size_in_bytes / 1024

def compress_images():
    if not os.path.exists(IMAGE_DIR):
        print(f"❌ 错误：找不到 '{IMAGE_DIR}' 文件夹！")
        return

    print(f"🚀 开始扫描图片...")
    print(f"🎯 策略：只压缩大于 {TRIGGER_SIZE_KB}KB 的图片")
    print(f"📉 目标：尺寸限制 {MAX_WIDTH}x{MAX_HEIGHT}，质量 {QUALITY}%")
    print("------------------------------------------------------")

    processed_count = 0
    skipped_count = 0
    saved_space = 0
    
    # 遍历所有子文件夹
    for root, dirs, files in os.walk(IMAGE_DIR):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                file_path = os.path.join(root, file)
                
                try:
                    # 获取原始文件大小
                    original_size = os.path.getsize(file_path)
                    
                    # ★★★ 核心修改：先判断文件大小 ★★★
                    # 如果文件小于设定值 (800KB)，直接跳过
                    if original_size <= TRIGGER_SIZE_KB * 1024:
                        skipped_count += 1
                        # 你可以取消下面这行的注释，查看哪些图片被跳过了
                        # print(f"⏩ 跳过 (太小): {file} ({get_size_kb(original_size):.1f}KB)")
                        continue

                    # --- 开始处理大图片 ---
                    with Image.open(file_path) as img:
                        width, height = img.size
                        
                        # 计算调整后的比例 (保持原比例)
                        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
                        
                        new_width, new_height = img.size
                        
                        # 保存逻辑
                        if file.lower().endswith('.png'):
                            img.save(file_path, optimize=True)
                        else:
                            # 转换色彩模式防止报错
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            img.save(file_path, "JPEG", quality=QUALITY, optimize=True)
                        
                        # 计算压缩后的效果
                        new_size = os.path.getsize(file_path)
                        diff = original_size - new_size
                        
                        # 如果压缩后反而变大了（极少情况），或者没省多少空间
                        if diff > 0:
                            saved_space += diff
                            processed_count += 1
                            print(f"✅ 压缩: {file}")
                            print(f"   体积: {get_size_kb(original_size):.0f}KB -> {get_size_kb(new_size):.0f}KB (省了 {get_size_kb(diff):.0f}KB)")
                        else:
                            print(f"⚠️ {file} 压缩后未减小，保持原样")

                except Exception as e:
                    print(f"⚠️ 无法处理 {file}: {e}")

    print("======================================================")
    print(f"🎉 处理完成！")
    print(f"⏭️  跳过的小图: {skipped_count} 张 (小于 {TRIGGER_SIZE_KB}KB)")
    print(f"📉 压缩的大图: {processed_count} 张")
    print(f"💾 共节省空间: {get_size_mb(saved_space):.2f} MB")
    print("======================================================")

if __name__ == "__main__":
    print(f"⚠️  警告：此操作将覆盖 {IMAGE_DIR} 文件夹内大于 {TRIGGER_SIZE_KB}KB 的图片。")
    user_input = input("确认要开始吗？(输入 y 并回车): ")
    
    if user_input.lower() == 'y':
        compress_images()
        input("\n按回车键退出...")
    else:
        print("操作已取消。")