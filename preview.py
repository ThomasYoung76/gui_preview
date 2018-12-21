import tkinter as tk

from tkinter.filedialog import askdirectory
from pathlib import Path
from PIL import Image


class UI():
    def __init__(self):
        self.root = tk.Tk()
        self.center_window(600, 600)
        self.set_ui()
    
    def center_window(self, width, height):
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
        self.root.geometry(size)

    def set_ui(self):
        self.path = tk.StringVar()
        self.filter = tk.StringVar()
        tk.Label(self.root, text = "图片路径: ", width=10).grid(row=0, column=0)
        tk.Entry(self.root, textvariable=self.path, width=50).grid(row=0, column=1, columnspan=5)
        tk.Button(self.root, text='浏览', command=self.select_path, width=10, background='gray').grid(row=0, column=6, padx=5)
        tk.Label(self.root, text='filter: ').grid(row=1, column=0, padx=2, )
        tk.Entry(self.root, textvariable=self.filter, width=10).grid(row=1, column=1, padx=2, sticky='s') 
        tk.Button(self.root, text='开始', command=self.scan, width=10).grid(row=1, column=6, padx=2)
        self.root.mainloop()

    def select_path(self):
        path_ = askdirectory()
        self.path.set(path_)

    def scan(self):
        size = (128, 128)
        filter_ = self.filter.get()
        for p in Path(self.path.get()).glob("*{}".format(filter_)):
            img = Image.open(str(p))
            # img.show()
            img.thumbnail(size,Image.ANTIALIAS)
            img.show()




if __name__ == "__main__":
    ui = UI()
