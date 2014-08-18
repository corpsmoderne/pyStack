#!/usr/bin/env python
import scipy, scipy.misc
import sys
import numpy as np
import threading
import Tkinter, ImageTk, tkFileDialog
import ttk

lst = None
total = 0

# get the list of files from the command line arguments if provided
if (len(sys.argv) > 1):
    lst = sys.argv[1:]
    total = len(lst)

root = Tkinter.Tk()

# if no command line arguments, open a file dialog to get the files...
if total == 0:
    lst = tkFileDialog.askopenfilename(parent=root, multiple=True)
    total = len(lst)

# gamma scale widget
var = Tkinter.DoubleVar()
entry = Tkinter.Scale( root, variable=var, resolution=0.1,
                       orient=Tkinter.HORIZONTAL,
                       from_=1, to=10)
entry.grid(row=0, column=0)

factor = 1.0
running = True

imgRes = None

# reprocess the image
def apply_cb():
    global factor, running
    factor = float(entry.get())
    if running == False:
        makeImg(total)

# open a dialog to save the processed image
def save_cb():
    global imgRes
    filename = tkFileDialog.asksaveasfilename(parent=root)
    print "saving as", filename
    scipy.misc.imsave(filename, imgRes);

# "apply" button
apply = Tkinter.Button(root, text="apply", command=apply_cb)
apply.grid(row=0, column=1)

# "save" button
save = Tkinter.Button(root, text="save", command=save_cb)
save.grid(row=0, column=2)

# "progess bar for loading"
progress = ttk.Progressbar(orient=Tkinter.HORIZONTAL, length=200,
                           mode='determinate', maximum=total)
progress.grid(row=1, column=0, columnspan=2)

res = None
label_image = None

# apply the gamma factor to the image a update the display
def makeImg(i):
    global res, lst, label_image, total, factor, imgRes

    res2 = res.copy()

    res2[...,0] /= res2.max()
    res2[...,1] /= res2.max()
    res2[...,2] /= res2.max()

    res2 **= 1/factor

    pim = scipy.misc.toimage(res2)
    
    W = root.winfo_width()
    H = root.winfo_height()
    
    pim.thumbnail((W, H))
    tkpi = ImageTk.PhotoImage(pim)
    
    if label_image != None:
        label_image.destroy()
    label_image = Tkinter.Label(root, image=tkpi)
    label_image.grid(row=1,column=0, columnspan=3)
    
    label_image.image = tkpi

    imgRes = res2

# load the files and stack them in a float64 array
def stack():
    global res, lst, label_image, total, running, progress
    for i,f in enumerate(lst):
        im = scipy.misc.imread(f)
        if res == None:
            res = np.zeros(im.shape, dtype=np.float64)
        res += im
        progress.step(1)
    running = False

    ratio = float(im.shape[1]) / float(im.shape[0])
    root.geometry('%dx%d' % (900, 900/ratio))
    progress.destroy()
    makeImg(i)

# run the stacking thread
t = threading.Thread(target=stack)
t.daemon = True
t.start()

# start it all...
root.title(lst[0]+" | "+str(total))
root.mainloop()
