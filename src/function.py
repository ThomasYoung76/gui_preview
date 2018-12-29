#!/usr/bin/env python3
'''
@File    :   function.py
@Time    :   2018/12/29 16:57:00
@Author  :   yangshifu
@Version :   1.0
@Contact :   yangshifu@sensetime.com
@Desc    :   None
'''
import tkinter as tk
import numpy as np
from tkinter import ttk
from tkinter import Menu
from tkinter import Menubutton
import pyscreenshot as ImageGrab
""" 界面添加其他功能 """

class Function():
    lastx, lasty = 0, 0
    start_coord = (70, 80)
    def __init__(self, master, obj_window=None):
        self.master = master   
        self.obj_window = obj_window
        self.config_menu()
        
        
    def config_menu(self):
        menu_bar = Menu()
        self.master.config(menu=menu_bar)
        file_menu = Menu(menu_bar)
        file_menu.add_command(label='shot', command=lambda : self.shot(
            list(np.array(self.obj_window.box_img_int) + 
            np.array([self.obj_window.tree_width + self.start_coord[0], 0 + self.start_coord[1], self.obj_window.tree_width + self.start_coord[0], 0 + self.start_coord[1]] + 
            np.array(self.obj_window.move_gap + self.obj_window.move_gap)))))
        file_menu.add_command(label='line', command=self.draw_line)
        file_menu.add_command(label='rectangle', command=self.draw_rectangle)
        menu_bar.add_cascade(label='Function', menu=file_menu)

    
    def shot(self, coord):
        """ 
        :param coord: 截图区域，如(x1, y1, x2, y2)
        """
        print(coord)
        im = ImageGrab.grab(bbox=coord)
        print("grab")
        # print(__class__.__dict__.get('start_coord'))
        im.show()        

    def draw_line(self):
        self.canvas = self.obj_window.canvas_image
        self.canvas.bind("<Button-1>", self.xy)
        self.canvas.bind("<B1-ButtonRelease>", self.add_line)
        self.canvas.bind("<3>", self.donw_stroke)
        self.canvas.bind("<Double-1>", self.add_text)

    def draw_rectangle(self):
        self.canvas = self.obj_window.canvas_image
        self.canvas.bind("<Button-1>", self.xy)
        self.canvas.bind("<B1-ButtonRelease>", self.add_rectangle)
        self.canvas.bind("<3>", self.donw_stroke)
        self.canvas.bind("<Double-1>", self.add_text)

    def xy(self, event):
        self.lastx, self.lasty = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

    def setColor(self, newcolor):
        self.color = newcolor
        self.canvas.dtag('all', 'paletteSelected')
        self.canvas.itemconfigure('palette', outline='white')
        self.canvas.addtag('paletteSelected', 'withtag', 'palette%s' % self.color)
        self.canvas.itemconfigure('paletteSelected', outline='#999999')

    def add_line(self, event):
        print(self.lastx, self.lasty)
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        print("x,y: {},{}".format(x,y))
        self.tag_id = self.canvas.create_line((self.lastx, self.lasty, x, y), fill='red', width=5, tags='currentline', arrow=tk.LAST, arrowshape='20 30 10' )
        self.lastx, self.lasty = x, y

    def add_rectangle(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.tag_id = self.canvas.create_rectangle((self.lastx, self.lasty, x, y), width=4)
        self.lastx, self.lasty = x, y

    def add_text(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.create_text(x, y, fill="darkblue", font="Times 20 italic bold",
                        text="Click the bubbles that are multiples of two.")

    def donw_stroke(self, event):
        self.canvas.itemconfigure('currentline', width=5) # What happens if you set this to another number? 
        self.canvas.delete(self.tag_id)     # 右击回滚前一次画图操作  
            

    # id1 = self.canvas.create_rectangle((10, 10, 30, 30), fill="red", tags=('palette', 'palettered'))
    # self.canvas.tag_bind(id1, "<Button-1>", lambda x: self.setColor("red"))
    # id2 = self.canvas.create_rectangle((10, 35, 30, 55), fill="blue", tags=('palette', 'paletteblue'))
    # self.canvas.tag_bind(id2, "<Button-1>", lambda x: setColor("blue"))
    # id3 = self.canvas.create_rectangle((10, 60, 30, 80), fill="black", tags=('palette', 'paletteblack', 'paletteSelected'))
    # self.canvas.tag_bind(id3, "<Button-1>", lambda x: setColor("black"))




if __name__ == '__main__':
    root = tk.Tk()
    func = Function(root)
    a = [0, 0, 50, 50]
    func.shot(a)
    root.mainloop()
