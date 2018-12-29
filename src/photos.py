#!/usr/bin/env python3
'''
@File    :   photos.py
@Time    :   2018/12/26 17:04:36
@Author  :   yangshifu
@Version :   1.0
@Contact :   yangshifu@sensetime.com
@Desc    :   None
'''
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class Photos():
    """
        handle imgs, put in frame  of size w_box times h_box
    """
    pil_images = []
    def __init__(self, *imgs, **kwargs):
        """ keyargs: w_box, h_box, out"""
        self.w_box = kwargs.get('w_box', 1920)
        self.h_box = kwargs.get('h_box', 1080)
        self.output_image = kwargs.get('out', None)
        self.imgs = imgs
        # self.pil_image = self.merge_photos(out=self.output_image)

    # def get_merged_photos(self):
    #     return self.merge_photos(out=self.output_image)

    def resize(self, image, w_box, h_box):  
        ''' 
        resize image so it will fit into 
        a box of size w_box times h_box, but retain aspect ratio 
        对一个pil_image对象进行缩放，让它在一个矩形框内，还能保持比例 
        '''  
        pil_image = Image.open(image)
        raw_width, raw_height = pil_image.size
        # 计算待缩放比率
        f1 = 1.0 * w_box / raw_width
        f2 = 1.0 * h_box / raw_height  
        factor = min([f1, f2])  
        # 计算resize的宽高
        width = int(raw_width * factor)  
        height = int(raw_height * factor)  
        pil_image_resized = pil_image.resize((width, height), Image.ANTIALIAS)  # resize
        pil_image_texted = self.add_text(image, pil_image_resized)
        return pil_image_texted

    def merge_photos(self, out=None):
        """ 
        合并图片
        :param out: 输出图片的路径， 如"1.jpg"
        :return : 返回合并后的图片的Image对象
        """
        count = len(self.imgs)
        if count == 0:
            print("没有需要处理的image")
            return
        elif count > 4:
            count = 4
            self.imgs = self.imgs[:4]

        # if count == 3:
        #     self.w_box = self.w_box // 2
        # if count == 4:
        #     self.h_box = self.h_box // 2

        # 先进行resize
        for img in self.imgs:
            self.pil_images.append(self.resize(img, self.w_box, self.h_box))

        # 只有一张图片时，resize后直接返回
        if len(self.pil_images) == 1:
            return self.pil_images[0]

        rows = []

        column = len(self.imgs) if len(self.imgs) < 4 else 2
        for i in range(count):
            if i % column == 0:
                row = np.hstack((np.asarray(i) for i in self.pil_images[i:i+column]))
                rows.append(row) 


        # for a vertical stacking it is simple: use vstack
        photo = np.vstack(rows)
        photo = Image.fromarray(photo)
        if out:
            photo.save(out)    
        return photo

    def add_text(self, image_name, pil_image):
        # 字体
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 24)
        # 文本
        text = os.path.basename(image_name)
        
        image_draw = ImageDraw.Draw(pil_image)
        image_draw.text((30,20), text, font=font, fill='#008844')
        return pil_image

    def destroy(self):
        map(lambda x:x.close, self.pil_images)  # 删除image
        del self.pil_images[:]
        del self.pil_images

if __name__ == "__main__":
    a = Photos('sample/0001.jpg', 'sample/0001.jpg', 'sample/0001.jpg', 'sample/0001.jpg',out='0005.jpg')
    # a.get_merged_photos()
