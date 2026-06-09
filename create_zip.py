#!/usr/bin/env python3
"""
创建 NIKKE PVP Tracker release zip。
使用 Python zipfile 确保 Unicode 文件名正确写入。
"""

import zipfile
import os
import sys
from pathlib import Path


def create_release_zip(dist_dir, output_path, zip_name="nikke-pvp-tracker"):
    """创建 release zip，保留 Unicode 文件名"""
    dist_dir = Path(dist_dir).resolve()
    output_path = Path(output_path).resolve()

    # 如果 zip 不存在则创建
    arc_prefix = zip_name  # 顶层文件夹名

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(str(dist_dir)):
            for file in files:
                full_path = os.path.join(root, file)
                # 计算 zip 内的相对路径（带顶层文件夹）
                rel = os.path.relpath(full_path, str(dist_dir))
                arcname = os.path.join(arc_prefix, rel)
                zf.write(full_path, arcname)

        # 确保 start.bat 也在顶层（它在 dist 目录内）
        start_bat = dist_dir / "start.bat"
        if start_bat.exists():
            zf.write(str(start_bat), f"{arc_prefix}/start.bat")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python create_zip.py <dist_dir> <output_zip> [zip_name]")
        sys.exit(1)

    dist_dir = sys.argv[1]
    output_path = sys.argv[2]
    zip_name = sys.argv[3] if len(sys.argv) > 3 else "nikke-pvp-tracker"

    create_release_zip(dist_dir, output_path, zip_name)
    zip_size = os.path.getsize(output_path)
    print(f"✅ zip 创建成功: {output_path}")
    print(f"   大小: {zip_size / 1024 / 1024:.1f} MB")
