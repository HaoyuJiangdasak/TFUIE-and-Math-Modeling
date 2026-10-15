#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SUIM 彩色 mask -> 单通道类别 PNG（像素值 = 类别 0-7）。

在 AutoDL 实例内运行（CPU 即可，无需 GPU）：

    python tools/mask_convert.py --src <SUIM原始彩色mask目录> --dst <输出目录>

类别顺序（论文 §IV-A）：BW HD PF WR RO RI FV SR -> 0..7
SUIM 官方色值（RGB 口径）：
    BW(0,0,0) HD(0,0,255) PF(0,255,0)  WR(0,255,255)
    RO(255,0,0) RI(255,0,255) FV(255,255,0) SR(255,255,255)

内置自检：单图像素命中率 < 90% 时直接报错（提示颜色顺序反了，
用 --order bgr 重跑）。结束后打印逐类别像素占比，用于人工复核
（例如有潜水员的图，类别 HD 应占一定比例）。
"""
import argparse
import os

import numpy as np
from PIL import Image

RGB2ID = {
    (0, 0, 0): 0,        # BW background waterbody
    (0, 0, 255): 1,      # HD human divers
    (0, 255, 0): 2,      # PF plants/seagrass
    (0, 255, 255): 3,    # WR wrecks/ruins
    (255, 0, 0): 4,      # RO robots/instruments
    (255, 0, 255): 5,    # RI reefs/invertebrates
    (255, 255, 0): 6,    # FV fish/vertebrates
    (255, 255, 255): 7,  # SR sea-floor/rocks
}
BGR2ID = {k[::-1]: v for k, v in RGB2ID.items()}


def build_lut(table):
    """256^3 查表：LUT[r,g,b] -> 类别 id；未命中 = 255。"""
    lut = np.full((256, 256, 256), 255, np.uint8)
    for (r, g, b), i in table.items():
        lut[r, g, b] = i
    return lut


def convert_file(path, lut):
    a = np.array(Image.open(path).convert('RGB'))
    ids = lut[a[:, :, 0], a[:, :, 1], a[:, :, 2]]
    hit = float((ids != 255).mean())
    if hit < 0.90:
        raise RuntimeError(
            f"{path}: 仅 {hit:.1%} 像素命中色值表——颜色顺序很可能反了，"
            f"请加 --order bgr 重跑")
    ids[ids == 255] = 0  # 抗锯齿杂色归入背景 BW
    return ids, hit


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--src', required=True, help='SUIM 原始彩色 mask 目录')
    p.add_argument('--dst', required=True, help='输出类别 PNG 目录')
    p.add_argument('--order', choices=['rgb', 'bgr'], default='rgb',
                   help='色值表口径，自检报错时换 bgr')
    args = p.parse_args()

    table = RGB2ID if args.order == 'rgb' else BGR2ID
    lut = build_lut(table)
    os.makedirs(args.dst, exist_ok=True)

    files = sorted(f for f in os.listdir(args.src) if f.lower().endswith('.png'))
    if not files:
        raise SystemExit(f"{args.src} 下没有 png，检查路径")

    hits, class_pixels = [], np.zeros(8, np.int64)
    for i, f in enumerate(files):
        ids, hit = convert_file(os.path.join(args.src, f), lut)
        Image.fromarray(ids).save(os.path.join(args.dst, f))
        hits.append(hit)
        class_pixels += np.bincount(ids.reshape(-1), minlength=8)[:8]
        if i % 100 == 0:
            print(f'{i}/{len(files)}')

    total = class_pixels.sum()
    names = ["BW", "HD", "PF", "WR", "RO", "RI", "FV", "SR"]
    print(f'\n完成 {len(files)} 张；命中率 min={min(hits):.1%} mean={np.mean(hits):.1%}')
    print('逐类别像素占比（人工复核用，有潜水员的图 HD 应明显非零）：')
    for n, c in zip(names, class_pixels):
        print(f'  {n}: {c / total:.2%}')


if __name__ == '__main__':
    main()
