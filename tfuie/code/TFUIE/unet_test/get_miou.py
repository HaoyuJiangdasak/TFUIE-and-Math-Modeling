#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mIoU / mPA 评价驱动脚本（调用 utils/utils_metrics.py::compute_mIoU，
其打印口径与论文一致：mIoU + mPA，逐类别 IoU/Recall/Precision）。

在 unet_test/ 目录内运行：

  Raw 版权重:
    python get_miou.py --voc VOCdevkit_test --weights logs/<Raw版时间戳>/ep100.pth
  TFUIE 版权重:
    python get_miou.py --voc VOCdevkit_test --weights logs/<TFUIE版时间戳>/ep100.pth

- 权重经 Unet(model_path=...) 传入，其余参数沿用 unet.py 默认值（8 类 / vgg / 256）
- 名单默认读 <voc>/VOC2007/ImageSets/Segmentation/val.txt（test 版 = 110 张官方测试集）
- 每次运行先清空预测目录，防止混入上一版结果
"""
import argparse
import os

from PIL import Image
from unet import Unet
from utils.utils_metrics import compute_mIoU

CLASS_NAMES = ["BW", "HD", "PF", "WR", "RO", "RI", "FV", "SR"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--voc', default='VOCdevkit_test',
                   help='VOCdevkit 目录（评价一般用 VOCdevkit_test）')
    p.add_argument('--weights', required=True,
                   help='logs/<时间戳>/ep100.pth（两版各评一次）')
    p.add_argument('--names-file', default=None,
                   help='默认 <voc>/VOC2007/ImageSets/Segmentation/val.txt')
    p.add_argument('--num-classes', type=int, default=8)
    p.add_argument('--pred-dir', default='miou_pred')
    args = p.parse_args()

    names_file = args.names_file or os.path.join(
        args.voc, 'VOC2007', 'ImageSets', 'Segmentation', 'val.txt')
    with open(names_file) as f:
        names = [l.strip() for l in f if l.strip()]
    print(f'评价名单：{len(names)} 张（来自 {names_file}）')

    gt_dir = os.path.join(args.voc, 'VOC2007', 'SegmentationClass')
    os.makedirs(args.pred_dir, exist_ok=True)
    for f in os.listdir(args.pred_dir):          # 清空上一版预测
        if f.endswith('.png'):
            os.remove(os.path.join(args.pred_dir, f))

    unet = Unet(model_path=args.weights)
    for i, n in enumerate(names):
        img = Image.open(os.path.join(args.voc, 'VOC2007',
                                      'JPEGImages', n + '.bmp'))
        seg = unet.get_miou_png(img)
        seg.save(os.path.join(args.pred_dir, n + '.png'))
        if i % 20 == 0:
            print(f'{i}/{len(names)}')

    compute_mIoU(gt_dir, args.pred_dir, names, args.num_classes, CLASS_NAMES)


if __name__ == '__main__':
    main()
