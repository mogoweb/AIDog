# -*- coding: utf-8 -*-

# 随机抽取一部分图像文件作为测试数据集

import argparse
import os
import shutil

import numpy as np

if __name__ == "__main__":
    src_dir = "Images"
    dst_dir = "TestImages"

    parser = argparse.ArgumentParser()
    parser.add_argument("--src_dir", help="images folder for training")
    parser.add_argument("--dst_dir", help="images folder for test")

    args = parser.parse_args()

    if args.src_dir:
        src_dir = args.src_dir
    if args.dst_dir:
        dst_dir = args.dst_dir

    src_dir = os.path.realpath(src_dir)
    if not os.path.exists(src_dir):
        print("source directory not exists")
        exit(-1)

    dst_dir = os.path.realpath(dst_dir)
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir, 0o755)

    folders = [f for f in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, f))]
    for d in folders:
        d_images_dir = os.path.join(dst_dir, d)
        if not os.path.exists(d_images_dir):
            os.mkdir(d_images_dir)

        files = os.listdir(os.path.join(src_dir, d))
        rand_indexs = np.random.choice(len(files), 15, replace=False)
        print(rand_indexs)
        for i in rand_indexs:
            print(files[i])
            shutil.move(os.path.join(src_dir, d, files[i]), os.path.join(d_images_dir, files[i]))
