#!/usr/bin/env python3
'''
@File    :   show_img.py
@Time    :   2019/01/03 10:32:47
@Author  :   yangshifu
@Version :   1.0
@Contact :   yangshifu@sensetime.com
@Desc    :   None
'''
import os
import math
import warnings
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import ttk
from idlelib import tree
from idlelib.config import idleConf

from PIL import Image, ImageTk, ImageDraw, ImageFont

from photos import Photos


class AutoScrollbar(ttk.Scrollbar):
    """ A scrollbar that hides itself if it's not needed. Works only for grid geometry manager """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        raise tk.TclError('Cannot use place with the widget ' + self.__class__.__name__)


class ShowImgWin(tk.Toplevel):
    menu_height = 100
    canvas_row = 1
    canvas_column=0
    def __init__(self, count=2):
        super().__init__()
        self.count = count
        self.title('Image')
        self.screen_width, self.screen_height = self.get_screen_size(self.master)
        self.geometry("{}x{}".format(self.screen_width, self.screen_height))
        self.create_menu()
        self.create_img_frame()
        # self.create_canvas_by_count(self.count)

    def create_menu(self):
        self.menu_frame = tk.Frame(self, width=self.screen_width, height=self.menu_height, background='gray')
        self.menu_frame.grid(row=0, column=0)

    def create_img_frame(self):
        self.frame_height = self.screen_height - self.menu_height
        self.img_frame = tk.Frame(self, width=self.screen_width, height=self.frame_height, background='red')
        self.img_frame.grid(row=1, column=0)

    def create_canvas(self):
        """ create several canvas """
        self.canvas_width = self.screen_width // self.count if self.count < 4 else self.screen_width // 2
        self.canvas_height = self.frame_height if self.count < 4 else self.frame_height // 2
        # self.img_frame = tk.Frame(self, width=self.canvas_width, height=self.canvas_height, background='red')
        # self.img_frame.grid(row=1, column=0)
        self.canvas_image = tk.Canvas(self.img_frame, highlightthickness=0, width=self.canvas_width, height=self.canvas_height, background='blue')
        self.canvas_image.grid(row=self.canvas_row, column=self.canvas_column, padx=2, pady=1)
        
    def canvas_bind(self):
        # Bind events to the Canvas
        # self.canvas_image.bind('<Configure>', lambda event: self.__show_image())  # canvas is resized
        self.canvas_image.bind('<Control-ButtonPress-1>', self.__move_from)  # remember canvas position
        self.canvas_image.bind('<Control-B1-Motion>',     self.__move_to)  # move canvas to the new position
        self.canvas_image.bind('<Control-B1-ButtonRelease>', self.get_move_gap)
        self.canvas_image.bind('<MouseWheel>', self.__wheel)  # zoom for Windows and MacOS, but not Linux
        self.canvas_image.bind('<Button-5>',   self.__wheel)  # zoom for Linux, wheel scroll down
        self.canvas_image.bind('<Button-4>',   self.__wheel)  # zoom for Linux, wheel scroll up
         # Handle keystrokes in idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time
        # self.canvas_image.bind('<Key>', lambda event: self.canvas_image.after_idle(self.__keystroke, event))   

    def get_screen_size(self, window):
        return window.winfo_screenwidth(),window.winfo_screenheight()
    
    def get_window_size(self, window):
        return window.winfo_reqwidth(),window.winfo_reqheight()


    def show_img_in_canvas(self, image):
        self.imscale = 1.0  # scale for the canvas image zoom, public for outer classes
        self.__delta = 1.3  # zoom magnitude
        self.__filter = Image.ANTIALIAS  # could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        self.__previous_state = 0  # previous state of the keyboard
        self.__img = image
        self.pil_image = self.resize(self.__img, self.canvas_width, self.canvas_height)
            
        self.imwidth, self.imheight = self.pil_image.size  # public for outer classes

        self.__min_side = min(self.imwidth, self.imheight)  # get the smaller image side
        # Create image pyramid
        self.__pyramid = [self.pil_image]
        # Set ratio coefficient for image pyramid
        self.__ratio = 1.0
        self.__curr_img = 0  # current image from the pyramid
        self.__scale = self.imscale * self.__ratio  # image pyramide scale
        self.__reduction = 2  # reduction degree of image pyramid

        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas_image.create_rectangle((0, 0, self.imwidth, self.imheight), width=4, fill='pink')

        imagetk = ImageTk.PhotoImage(self.pil_image)
        self.imageid = self.canvas_image.create_image(0, 0, anchor='nw', image=imagetk)
        self.canvas_image.imagetk = imagetk
        # self.__show_image()  # show image on the canvas
        # self.canvas_image.focus_set()  # set focus on the canvas

    def __scroll_x(self, *args, **kwargs):
        """ Scroll canvas horizontally and redraw the image """
        self.canvas_image.xview(*args)  # scroll horizontally
        self.__show_image()  # redraw the image

    def __scroll_y(self, *args, **kwargs):
        """ Scroll canvas vertically and redraw the image """
        self.canvas_image.yview(*args)  # scroll vertically
        self.__show_image()  # redraw the image

    def __move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse """
        self.canvas_image.scan_mark(event.x, event.y)
        self.from_coord = (event.x, event.y)

    def __move_to(self, event):
        """ Drag (move) canvas to the new position """
        self.canvas_image.scan_dragto(event.x, event.y, gain=1)
        self.to_coord = (event.x, event.y)
        self.__show_image()  # zoom tile and show it on the canvas

    def get_move_gap(self, event):
        """ B1 release时获取移动的距离 """
        try:
            self.move_gap = list(np.array(self.to_coord) - np.array(self.from_coord) + np.array(self.move_gap))
        except:
            self.move_gap = [0, 0]


    def outside(self, x, y):
        """ Checks if the point (x,y) is outside the image area """
        bbox = self.canvas_image.coords(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False  # point (x,y) is inside the image area
        else:
            return True  # point (x,y) is outside the image area

    def __wheel(self, event):
        """ Zoom with mouse wheel """
        x = self.canvas_image.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvas_image.canvasy(event.y)
        if self.outside(x, y): return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down, smaller
            if round(self.__min_side * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.__delta
            scale        /= self.__delta
        if event.num == 4 or event.delta == 120:  # scroll up, bigger
            i = min(self.canvas_image.winfo_width(), self.canvas_image.winfo_height()) >> 1
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.__delta
            scale        *= self.__delta
        # Take appropriate image from the pyramid
        k = self.imscale * self.__ratio  # temporary coefficient
        self.__curr_img = min((-1) * int(math.log(k, self.__reduction)), len(self.__pyramid) - 1)
        self.__scale = k * math.pow(self.__reduction, max(0, self.__curr_img))
        #
        self.canvas_image.scale('all', x, y, scale, scale)  # rescale all objects
        # Redraw some figures before showing image on the screen
        self.redraw_figures()  # method for child classes
        self.__show_image()


    def __keystroke(self, event):
        """ Scrolling with the keyboard.
            Independent from the language of the keyboard, CapsLock, <Ctrl>+<key>, etc. """
        if event.state - self.__previous_state == 4:  # means that the Control key is pressed
            pass  # do nothing if Control key is pressed
        else:
            self.__previous_state = event.state  # remember the last keystroke state
            # Up, Down, Left, Right keystrokes
            if event.keycode in [68, 39, 102]:  # scroll right, keys 'd' or 'Right'
                self.__scroll_x('scroll',  1, 'unit', event=event)
            elif event.keycode in [65, 37, 100]:  # scroll left, keys 'a' or 'Left'
                self.__scroll_x('scroll', -1, 'unit', event=event)
            elif event.keycode in [87, 38, 104]:  # scroll up, keys 'w' or 'Up'
                self.__scroll_y('scroll', -1, 'unit', event=event)
            elif event.keycode in [83, 40, 98]:  # scroll down, keys 's' or 'Down'
                self.__scroll_y('scroll',  1, 'unit', event=event)

    def redraw_figures(self):
        """ Dummy function to redraw figures in the children classes """
        pass

    def crop(self, bbox):
        """ Crop rectangle from the image and return it """
        return self.__pyramid[0].crop(bbox)

    # def destroy(self):
    #     """ ImageFrame destructor """
    #     pass
    #     # del self.move_gap
    #     # del self.canvas_image.imagetk
    #     # # # print(self.imageid)
    #     # self.pil_image.close()
    #     # del self.pil_image
    #     # self.canvas_image.delete(self.imageid)  # 清除画布上的图片
    #     # map(lambda i: i.close, self.__pyramid)  # close all pyramid images
    #     # del self.__pyramid[:]  # delete pyramid list
    #     # del self.__pyramid  # delete pyramid variable
    #     # self.canvas_image.delete(tk.ALL)
    #     # self.canvas_image.destroy()
    #     # self.img_frame.destroy()
    
    def __show_image(self):
        """ Show image on the Canvas. Implements correct image zoom almost like in Google Maps """
        box_image = self.canvas_image.coords(self.container)  # get image area
        # print(box_image)
        box_canvas = (self.canvas_image.canvasx(0),  # get visible area of the canvas
                      self.canvas_image.canvasy(0),
                      self.canvas_image.canvasx(self.canvas_image.winfo_width()),
                      self.canvas_image.canvasy(self.canvas_image.winfo_height()))
        self.box_img_int = tuple(map(int, box_image))  # convert to integer or it will not work properly
        print(box_canvas)
        # Get scroll region box
        box_scroll = [min(self.box_img_int[0], box_canvas[0]), min(self.box_img_int[1], box_canvas[1]),
                      max(self.box_img_int[2], box_canvas[2]), max(self.box_img_int[3], box_canvas[3])]
        # Horizontal part of the image is in the visible area
        if  box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0]  = self.box_img_int[0]
            box_scroll[2]  = self.box_img_int[2]
        # Vertical part of the image is in the visible area
        if  box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1]  = self.box_img_int[1]
            box_scroll[3]  = self.box_img_int[3]
        # Convert scroll region to tuple and to integer
        self.canvas_image.configure(scrollregion=tuple(map(int, box_scroll)))  # set scroll region
        x1 = max(box_canvas[0] - box_image[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            image = self.__pyramid[max(0, self.__curr_img)].crop(  # crop current img from pyramid
                                                                    (int(x1 / self.__scale), int(y1 / self.__scale),
                                    int(x2 / self.__scale), int(y2 / self.__scale)))
            #
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1)), self.__filter))
            self.imageid = self.canvas_image.create_image(max(box_canvas[0], self.box_img_int[0]),
                                               max(box_canvas[1], self.box_img_int[1]),
                                               anchor='nw', image=imagetk)
            print(self.imageid)
            self.canvas_image.lower(self.container)  # set image into background
            self.canvas_image.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
    
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

    def add_text(self, image_name, pil_image):
        # 字体
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 24)
        # 文本
        text = os.path.basename(image_name)
        
        image_draw = ImageDraw.Draw(pil_image)
        image_draw.text((30,20), text, font=font, fill='#008844')
        return pil_image


if __name__ == "__main__":
    top = tk.Tk(className='Test')
    
    var_1 = tk.StringVar()
    entry = tk.Entry(top, textvariable=var_1)
    entry.grid()
    text = tk.Text(top)
    text.grid()

    def show(*img_file):
        count=len(img_file)
        show_img_win = ShowImgWin(count=count)
        for i, img in enumerate(img_file):
            if count < 4:
                show_img_win.canvas_row = 1
                show_img_win.canvas_column = i
            else:
                if i < 2:
                    show_img_win.canvas_row = 1
                    show_img_win.canvas_column = i
                else:
                    show_img_win.canvas_row = 2
                    show_img_win.canvas_column = i - 2
            
            show_img_win.create_canvas()
            show_img_win.canvas_bind()
            show_img_win.show_img_in_canvas(img)
            
        # top.wait_window(show_img_win)

    b = tk.Button(top, text='图片比对', command=lambda: show("sample/0001_release.jpg", "sample/0001.jpg"))
    b.grid()
    top.mainloop()
