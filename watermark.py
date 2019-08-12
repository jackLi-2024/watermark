#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""

import os
import sys
import json

try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass

import math
import os
import sys
import time

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops


class GenerateWaterMarkImage():
    def __init__(self, mark, fontsize=50, fontttf="zhtjt.ttf", color="red", opacity=0.8, space=None, angle=30):
        """
        生成水印图片
        :param mark: 水印内容
        :param fontsize: 水印的字体大小
        :param fontttf: 水印的字体文件
        :param color: 水印的颜色
        :param opacity: 水印的透明度
        :param space: 水印间的间隔
        :param angle: 水印的倾斜角度
        """
        self.mark = mark
        self.fontsize = fontsize
        self.fontttf = fontttf
        self.color = color
        self.opacity = opacity
        self.space = space
        self.angle = angle

    def generate(self):
        """生成水印图片"""
        width = len(self.mark * self.fontsize)
        mark_img = Image.new(mode="RGBA", size=(width, self.fontsize))

        draw_table = ImageDraw.Draw(im=mark_img)
        draw_table.text(xy=(0, 0), text=self.mark, fill=self.color,
                        font=ImageFont.truetype(self.fontttf, size=self.fontsize))

        del draw_table

        mark_img = self.crop_image(mark_img)
        self.set_opacity(mark_img, self.opacity)

        def func(im, mode="single", single_position_rate_x=0.3, single_position_rate_y=0.3):
            c = int(math.sqrt(im.size[0] * im.size[0] + im.size[1] * im.size[1]))
            mark_img_temp = Image.new(mode="RGBA", size=(c, c))
            y, idx = 0, 0
            if mode == "multi":
                while y < c:
                    x = -int((mark_img.size[0] + self.space) * 0.5 * idx)
                    idx = (idx + 1) % 2
                    while x < c:
                        mark_img_temp.paste(mark_img, (x, y))
                        x = x + mark_img.size[0] + self.space
                    y = y + mark_img.size[1] + self.space
            elif mode == "single":
                x = int(c * single_position_rate_x)
                y = int(c * single_position_rate_y)
                # x = int(c * 0.5)
                mark_img_temp.paste(mark_img, (x, y))

            else:
                raise Exception("Sorry only choose multi/single mode!!")

            mark_img_temp = mark_img_temp.rotate(self.angle)
            if im.mode != 'RGBA':
                im = im.convert('RGBA')
            im.paste(mark_img_temp,  # 大图
                     (int((im.size[0] - c) / 2), int((im.size[1] - c) / 2)),  # 坐标
                     mask=mark_img_temp.split()[3])
            del mark_img_temp
            return im

        return func

    def crop_image(self, im):
        """

        :param im: image图片对象
        :return:
        """
        bg = Image.new(mode='RGBA', size=im.size)
        diff = ImageChops.difference(im, bg)
        del bg
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)
        return im

    def set_opacity(self, im, opacity):
        """
        设置透明度
        :param im: image图片对象
        :param opacity: 透明度
        :return:
        """
        assert opacity >= 0 and opacity <= 1

        alpha = im.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        im.putalpha(alpha)
        return im


class AddMark():
    def __init__(self, mark, fontsize=50, fontttf="zhtjt.ttf", color="red", opacity=0.8, space=None, angle=30,
                 outpath="./output", inpath="./test.png", single_position_rate_x=0.3, single_position_rate_y=0.3,
                 mode="single"):
        """
        开始加水印
        :param mark: 水印内容
        :param fontsize: 字体大小
        :param fontttf: 字体文件
        :param color: 字体颜色
        :param opacity: 透明度
        :param space: 水印间隔空隙
        :param angle: 字体倾斜角度
        :param outpath: 图片输出路径
        :param inpath: 图片输入路径
        :param single_position_rate:  单水印位置百分比
        :param mode: 模式，单水印与多水印模式single, multi
        """
        self.mark = mark
        self.fontsize = fontsize
        self.fontttf = fontttf
        self.color = color
        self.opacity = opacity
        self.space = space
        self.angle = angle
        self.outpath = outpath
        self.inpath = inpath
        self.single_position_rate_x = single_position_rate_x
        self.single_position_rate_y = single_position_rate_y
        self.mode = mode
        self.run_()

    def run_(self):
        """启动加水印"""
        mark_func = GenerateWaterMarkImage(self.mark, fontsize=self.fontsize, fontttf=self.fontttf, color=self.color,
                                           opacity=self.opacity, space=self.space, angle=self.angle).generate()
        if os.path.isdir(self.inpath):
            names = os.listdir(self.inpath)
            for name in names:
                image_file = os.path.join(self.inpath, name)
                self.add_mark(image_file, mark_func)
        else:
            self.add_mark(self.inpath, mark_func)

    def add_mark(self, image_path, mark_func):
        """
        水印
        :param image_path: 图片路径
        :param mark_func: 水印处理函数
        :return:
        """
        im = Image.open(image_path)

        image = mark_func(im, mode=self.mode, single_position_rate_x=self.single_position_rate_x,
                          single_position_rate_y=self.single_position_rate_y)
        name = ''
        if image:
            name = os.path.basename(image_path)
            if not os.path.exists(self.outpath):
                os.mkdir(self.outpath)

            new_name = os.path.join(self.outpath, name)
            if os.path.splitext(new_name)[1] != '.png':
                image = image.convert('RGB')
            image.save(new_name)
            print("Picture {0} add watermark Success.".format(name))
        else:
            print("Picture {0} add watermark Failed.".format(name))


def test():
    mark = "hello world"
    addmark = AddMark(mark, fontsize=50, fontttf="fzhtjt.ttf", color="red", opacity=0.8, space=None, angle=30,
                      outpath="./output", inpath="./IOS.jpg")
    import time
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    addmark = AddMark(str(now), fontsize=30, fontttf="fzhtjt.ttf", color="red", opacity=0.8, space=None, angle=30,
                      outpath="./output", inpath="./output/IOS.jpg", single_position_rate_x=0.4)


if __name__ == '__main__':
    test()
