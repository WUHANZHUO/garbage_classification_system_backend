import os
import imagehash
from PIL import Image
from collections import defaultdict

def find_and_remove_duplicate_images(dataset_path, remove_duplicates=True):
    """
    检测数据集中相同分类下的重复图片，并可选择删除重复项
    :param dataset_path: 数据集根目录路径 (e.g., 'dataset/')
    :param remove_duplicates: 是否删除重复图片，默认为True
    """
    duplicates_found = False
    total_removed = 0
    
    # 遍历每个分类目录
    for class_name in os.listdir(dataset_path):
        class_path = os.path.join(dataset_path, class_name)
        
        if not os.path.isdir(class_path):
            continue
            
        print(f"\n检查分类: {class_name}")
        image_hashes = defaultdict(list)
        
        # 遍历分类目录中的图片文件
        for filename in os.listdir(class_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                img_path = os.path.join(class_path, filename)
                
                try:
                    with Image.open(img_path) as img:
                        # 计算感知哈希 (可替换为average_hash, dhash等)
                        img_hash = str(imagehash.phash(img))
                        image_hashes[img_hash].append((filename, img_path))
                except Exception as e:
                    print(f"  跳过损坏图片: {filename} ({str(e)})")
        
        # 检查重复项
        class_removed = 0
        for img_hash, file_info_list in image_hashes.items():
            if len(file_info_list) > 1:
                duplicates_found = True
                print(f"  ⚠️ 发现重复图片 (哈希: {img_hash}):")
                
                # 显示所有重复文件
                for i, (filename, filepath) in enumerate(file_info_list):
                    if i == 0:
                        print(f"    - {filename} (保留)")
                    else:
                        print(f"    - {filename} (待删除)")
                
                # 删除重复项（保留第一个）
                if remove_duplicates:
                    for i, (filename, filepath) in enumerate(file_info_list[1:], 1):
                        try:
                            os.remove(filepath)
                            print(f"    ✅ 已删除: {filename}")
                            class_removed += 1
                            total_removed += 1
                        except Exception as e:
                            print(f"    ❌ 删除失败: {filename} ({str(e)})")
        
        if class_removed > 0:
            print(f"  📊 {class_name} 分类删除了 {class_removed} 张重复图片")
    
    # 显示总结信息
    if duplicates_found:
        if remove_duplicates:
            print(f"\n🎯 清理完成！总共删除了 {total_removed} 张重复图片")
        else:
            print(f"\n📋 检测完成！发现重复图片但未删除（remove_duplicates=False）")
    else:
        print("\n✅ 未发现重复图片")

def backup_dataset(dataset_path):
    """
    创建数据集备份（可选功能）
    :param dataset_path: 数据集路径
    """
    import shutil
    backup_path = f"{dataset_path}_backup"
    
    if os.path.exists(backup_path):
        print(f"⚠️ 备份目录已存在: {backup_path}")
        return False
    
    try:
        shutil.copytree(dataset_path, backup_path)
        print(f"✅ 数据集已备份到: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ 备份失败: {str(e)}")
        return False

if __name__ == "__main__":
    dataset_root = "garbage-dataset"  # 修改为你的数据集路径
    
    print("🚀 开始清理数据集重复图片...")
    find_and_remove_duplicate_images(dataset_root, remove_duplicates=True)