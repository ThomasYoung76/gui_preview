#!/usr/bin/env python3
'''
@File    :   tree_dir.py
@Time    :   2018/12/26 13:39:13
@Author  :   yangshifu
@Version :   1.0
@Contact :   yangshifu@sensetime.com
@Desc    :   None
'''
import os
import math
import warnings
import tkinter as tk
from tkinter import *
from tkinter import ttk
from idlelib import tree
from idlelib.config import idleConf

from PIL import Image, ImageTk

from photos import Photos



class SubFileTreeItem(tree.FileTreeItem):
    def GetSubList(self):
        try:
            names = os.listdir(self.path)
            # 过滤掉隐藏文件
            names = list(filter(lambda x: False if x.startswith('.') else True, names))
        except OSError:
            return []
        names.sort(key = os.path.normcase)
        sublist = []
        for name in names:
            item = tree.FileTreeItem(os.path.join(self.path, name))
            sublist.append(item)
        return sublist



class SubTreeNode(tree.TreeNode):
    """ 
    继承父类tree.TreeNode，增加Ctrl+左键及右键的功能， 可多选，当右键时打开jpg文件
    """
    path_list = []
    img_type = 'jpg'    
    photos = Photos()
    def __init__(self, dir_canvas, parent, item):
        tree.TreeNode.__init__(self, dir_canvas, parent, item)

        

    def get_path_list(self, suffix=img_type):
        """ get img_type file list such as get jpg files"""
        img_list = list(filter(lambda x: x.endswith(suffix), self.path_list))
        return img_list

    def select_or_edit(self, event=None):
        self.path_list.clear()
        if self.selected and self.item.IsEditable():
            self.edit(event)
        else:
            self.path_list.append(self.item.path)
            self.select(event)

    def select_more(self, event=None):
        """Control + 左键 触发选择多个文件或目录"""
        self.path_list.append(self.item.path)
        # if self.selected:
        #     return
        # self.deselectall()
        self.selected = True
        # self.canvas.delete(self.image_id)
        self.drawicon()
        self.drawtext()

    def execute_file(self, event=None):
        """ open jpg file or merge several jpg file then open it"""
        file_list = self.get_path_list()
        print(file_list)
        if not file_list:
            return
        # merge image
        # 修复内存泄露的bug，由于没有清除之前打开的图片，第二次打开的图片仍然为之前的图片
        try:
            self.photos.destroy()
        except:
            pass
        self.photos.imgs = file_list  
        merged_photo = self.photos.merge_photos()

        # show image
        try:
            window.destroy()
        except:
            import traceback
            traceback.print_exc()

        window.show_img_in_canvas(merged_photo)
        
        
    def drawtext(self):
        textx = self.x+20-1
        texty = self.y-4
        labeltext = self.item.GetLabelText()
        if labeltext:
            id = self.canvas.create_text(textx, texty, anchor="nw",
                                         text=labeltext)
            self.canvas.tag_bind(id, "<1>", self.select)
            self.canvas.tag_bind(id, "<Double-1>", self.flip)
            x0, y0, x1, y1 = self.canvas.bbox(id)
            textx = max(x1, 200) + 10
        text = self.item.GetText() or "<no text>"
        try:
            self.entry
        except AttributeError:
            pass
        else:
            self.edit_finish()
        try:
            self.label
        except AttributeError:
            # padding carefully selected (on Windows) to match Entry widget:
            self.label = Label(self.canvas, text=text, bd=0, padx=2, pady=2)
        theme = idleConf.CurrentTheme()
        if self.selected:
            self.label.configure(idleConf.GetHighlight(theme, 'hilite'))
        else:
            self.label.configure(idleConf.GetHighlight(theme, 'normal'))
        id = self.canvas.create_window(textx, texty,
                                       anchor="nw", window=self.label)
        self.label.bind("<1>", self.select_or_edit)
        self.label.bind("<Double-1>", self.flip)
        self.label.bind("<Control-1>", self.select_more)
        self.label.bind("<3>", self.execute_file)
        self.text_id = id


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




class WholeWindow():
    def __init__(self, master):
        self.master = master    # 父窗口root 

        self.screen_width, self.screen_height = self.get_screen_size(self.master)
        self.center_window(self.screen_width, self.screen_height)
        self.build_tree_canvas()
        self.build_tree()
        self.build_img_canvas()

    def build_tree_canvas(self):
        # create frame
        self.tree_width = self.screen_width // 7
        self.tree_height = self.screen_height
        frame = tk.Frame(self.master, width=self.tree_width, height=self.tree_height)
        frame.grid(row=0, column=0)
        # canvas
        self.tree_canvas=tk.Canvas(frame, bg='#FFFFFF', scrollregion=(0,0,500,500))
        # vbar & hbar
        hbar=tk.Scrollbar(frame,orient=tk.HORIZONTAL)
        hbar.pack(side=tk.BOTTOM,fill=tk.X)
        hbar.config(command=self.tree_canvas.xview)
        vbar=tk.Scrollbar(frame,orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT,fill=tk.Y)
        vbar.config(command=self.tree_canvas.yview)
        self.tree_canvas.config(width=self.tree_width,height=self.tree_height)
        self.tree_canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.tree_canvas.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)


    def build_tree(self):
        home = os.environ.get('HOME')
        item = SubFileTreeItem(home)
        node = SubTreeNode(self.tree_canvas, None, item)
        node.update()

    def build_img_canvas(self):
        self.box_width = self.screen_width - self.tree_width
        self.img_frame = tk.Frame(self.master, width=self.box_width, height=self.screen_height, background='red')
        self.img_frame.grid(row=0, column=1)
        hbar = AutoScrollbar(self.img_frame, orient=tk.HORIZONTAL)
        vbar = AutoScrollbar(self.img_frame, orient=tk.VERTICAL)
        hbar.grid(row=1, column=1, sticky='we')
        vbar.grid(row=0, column=2, sticky='ns')
        # Create canvas and bind it with scrollbars
        self.canvas_image = tk.Canvas(self.img_frame, highlightthickness=0, width=self.box_width, height=self.screen_height, 
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set, background='blue')
        self.canvas_image.grid(row=0, column=1, sticky='nswe')
        self.canvas_image.update()  # wait till canvas is created
        hbar.configure(command=self.__scroll_x)  # bind scrollbars to the canvas
        vbar.configure(command=self.__scroll_y)
        # Bind events to the Canvas
        self.canvas_image.bind('<Configure>', lambda event: self.__show_image())  # canvas is resized
        self.canvas_image.bind('<ButtonPress-1>', self.__move_from)  # remember canvas position
        self.canvas_image.bind('<B1-Motion>',     self.__move_to)  # move canvas to the new position
        self.canvas_image.bind('<MouseWheel>', self.__wheel)  # zoom for Windows and MacOS, but not Linux
        self.canvas_image.bind('<Button-5>',   self.__wheel)  # zoom for Linux, wheel scroll down
        self.canvas_image.bind('<Button-4>',   self.__wheel)  # zoom for Linux, wheel scroll up
         # Handle keystrokes in idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time
        self.canvas_image.bind('<Key>', lambda event: self.canvas_image.after_idle(self.__keystroke, event))

    def get_screen_size(self, window):
        return window.winfo_screenwidth(),window.winfo_screenheight()
    
    def get_window_size(self, window):
        return window.winfo_reqwidth(),window.winfo_reqheight()

    def center_window(self, width, height):
        screenwidth = self.master.winfo_screenwidth()
        screenheight = self.master.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
        self.master.geometry(size)


    def show_img_in_canvas(self, pil_image):
        self.imscale = 1.0  # scale for the canvas image zoom, public for outer classes
        self.__delta = 1.3  # zoom magnitude
        self.__filter = Image.ANTIALIAS  # could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        self.__previous_state = 0  # previous state of the keyboard
        self.pil_image = pil_image
        
    
        with warnings.catch_warnings():  # suppress DecompressionBombWarning
            warnings.simplefilter('ignore')
            self.__image = self.pil_image  # open image, but down't load it
        self.imwidth, self.imheight = self.__image.size  # public for outer classes

        self.__min_side = min(self.imwidth, self.imheight)  # get the smaller image side
        # Create image pyramid
        self.__pyramid = [self.pil_image]
        # Set ratio coefficient for image pyramid
        self.__ratio = 1.0
        self.__curr_img = 0  # current image from the pyramid
        self.__scale = self.imscale * self.__ratio  # image pyramide scale
        self.__reduction = 2  # reduction degree of image pyramid
        w, h = self.__pyramid[-1].size
        while w > 512 and h > 512:  # top pyramid image is around 512 pixels in size
            w /= self.__reduction  # divide on reduction degree
            h /= self.__reduction  # divide on reduction degree
            self.__pyramid.append(self.__pyramid[-1].resize((int(w), int(h)), self.__filter))
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas_image.create_rectangle((0, 0, self.imwidth, self.imheight), width=0)
        self.__show_image()  # show image on the canvas
        self.canvas_image.focus_set()  # set focus on the canvas

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

    def __move_to(self, event):
        """ Drag (move) canvas to the new position """
        self.canvas_image.scan_dragto(event.x, event.y, gain=1)
        self.__show_image()  # zoom tile and show it on the canvas

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

    def destroy(self):
        """ ImageFrame destructor """
        del self.canvas_image.imagetk
        # # print(self.imageid)
        self.canvas_image.delete(self.imageid)  # 清除画布上的图片
        map(lambda i: i.close, self.__pyramid)  # close all pyramid images
        del self.__pyramid[:]  # delete pyramid list
        del self.__pyramid  # delete pyramid variable
        
        # self.canvas_image.destroy()
        # self.img_frame.destroy()
    
    def __show_image(self):
        """ Show image on the Canvas. Implements correct image zoom almost like in Google Maps """
        box_image = self.canvas_image.coords(self.container)  # get image area
        box_canvas = (self.canvas_image.canvasx(0),  # get visible area of the canvas
                      self.canvas_image.canvasy(0),
                      self.canvas_image.canvasx(self.canvas_image.winfo_width()),
                      self.canvas_image.canvasy(self.canvas_image.winfo_height()))
        box_img_int = tuple(map(int, box_image))  # convert to integer or it will not work properly
        # Get scroll region box
        box_scroll = [min(box_img_int[0], box_canvas[0]), min(box_img_int[1], box_canvas[1]),
                      max(box_img_int[2], box_canvas[2]), max(box_img_int[3], box_canvas[3])]
        # Horizontal part of the image is in the visible area
        if  box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0]  = box_img_int[0]
            box_scroll[2]  = box_img_int[2]
        # Vertical part of the image is in the visible area
        if  box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1]  = box_img_int[1]
            box_scroll[3]  = box_img_int[3]
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
            self.imageid = self.canvas_image.create_image(max(box_canvas[0], box_img_int[0]),
                                               max(box_canvas[1], box_img_int[1]),
                                               anchor='nw', image=imagetk)
            self.canvas_image.lower(self.imageid)  # set image into background
            self.canvas_image.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
            


if __name__ == "__main__":
    root = tk.Tk()
    window = WholeWindow(root)
    
    # window.build_tree()
    # photo = Photos("sample/0001.jpg")
    # window.show_img_in_canvas(photo.pil_image)
    root.mainloop()

