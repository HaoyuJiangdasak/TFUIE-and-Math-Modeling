#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""构造 unet_test 需要的 VOCdevkit 目录。

在 AutoDL 实例内运行（CPU 即可，仓库根目录下执行）：

  Raw 训练版:
    python tools/make_voc.py --img-dir datasets/suim_raw_train \
        --mask-dir datasets/suim_mask_train --out unet_test/VOCdevkit \
        --seed 2024 --mode train
  TFUIE 增强图训练版:
    python tools/make_voc.py --img-dir results/tfuie_train/test_latest/images \
        --mask-dir datasets/suim_mask_train --out unet_test/VOCdevkit_tf \
        --seed 2024 --mode train
  官方 test 评价版:
    python tools/make_voc.py --img-dir datasets/suim_raw_test \
        --mask-dir datasets/suim_mask_test --out unet_test/VOCdevkit_test \
        --mode test

要点：
- dataloader 写死读取 JPEGImages/<stem>.bmp（utils/dataloader.py 第 31 行），
  所以图像一律转 bmp；mask 直接复制为 SegmentationClass/<stem>.png。
- 增强图输出名是 <stem>_fake_B.png，本脚本自动去掉 _fake_B 后缀与 mask 对应。
- --mode train 按种子切 train.txt / val.txt（默认 1400/125）；
  --mode test 全部进 val.txt（供 get_miou.py 评价 110 张官方测试集）。
- Raw 版与 TFUIE 版必须用同一个 --seed，保证两版划分逐张一致（协议可比）。
"""
import argparse
import os
import random
import shutil

from PIL import Image

IMG_EXT = ('.png', '.jpg', '.jpeg', '.bmp')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--img-dir', required=True, help='图像目录（原图或增强图输出均可）')
    p.add_argument('--mask-dir', required=True, help='mask_convert.py 产出的类别 PNG 目录')
    p.add_argument('--out', required=True, help='输出的 VOCdevkit 目录名')
    p.add_argument('--seed', type=int, default=2024)
    p.add_argument('--mode', choices=['train', 'test'], default='train')
    p.add_argument('--train-n', type=int, default=1400)
    p.add_argument('--val-n', type=int, default=125)
    args = p.parse_args()

    ji = os.path.join(args.out, 'VOC2007', 'JPEGImages')
    sc = os.path.join(args.out, 'VOC2007', 'SegmentationClass')
    iset = os.path.join(args.out, 'VOC2007', 'ImageSets', 'Segmentation')
    for d in (ji, sc, iset):
        os.makedirs(d, exist_ok=True)

    names, missing = [], []
    for f in sorted(os.listdir(args.img_dir)):
        if not f.lower().endswith(IMG_EXT):
            continue
        stem = os.path.splitext(f)[0]
        if stem.endswith('_fake_B'):  # test.py 增强输出的命名约定
            stem = stem[:-len('_fake_B')]
        mask_path = os.path.join(args.mask_dir, stem + '.png')
        if not os.path.exists(mask_path):
            missing.append(stem)
            continue
        Image.open(os.path.join(args.img_dir, f)).convert('RGB').save(
            os.path.join(ji, stem + '.bmp'))
        shutil.copy(mask_path, os.path.join(sc, stem + '.png'))
        names.append(stem)

    if missing:
        raise SystemExit(
            f'缺 mask 的图像 stem（先解决对齐问题再重跑）：{missing[:10]} ...'
            f'共 {len(missing)} 个')

    if args.mode == 'train':
        expected = args.train_n + args.val_n
        if len(names) != expected:
            print(f'警告：图像数 {len(names)} != 期望 {expected}，'
                  f'请核对 SUIM 数量后再继续')
        random.seed(args.seed)
        random.shuffle(names)
        with open(os.path.join(iset, 'train.txt'), 'w') as f:
            f.write('\n'.join(names[:args.train_n]))
        with open(os.path.join(iset, 'val.txt'), 'w') as f:
            f.write('\n'.join(names[args.train_n:args.train_n + args.val_n]))
        print(f'{args.out}: train {min(args.train_n, len(names))} / '
              f'val {max(len(names) - args.train_n, 0)}（seed={args.seed}）')
    else:
        with open(os.path.join(iset, 'val.txt'), 'w') as f:
            f.write('\n'.join(names))
        print(f'{args.out}: test {len(names)} 张全部写入 val.txt（评价用）')

    print('JPEGImages:', len(os.listdir(ji)),
          '| SegmentationClass:', len(os.listdir(sc)))


if __name__ == '__main__':
    main()
