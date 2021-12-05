from PIL import Image, ImageFilter
import face_recognition
import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar
import os

# TODO: make these options in main program 
GAP = 5         # padding around the face; bigger = less padding 
MOD = 'hog'     # hog: faster, cnn: more accurate

class person:
    def __init__(self, name, image):
        self.name = name
        self.img = face_recognition.load_image_file(image)
        self.encoding = face_recognition.face_encodings(self.img)[0]

def open_folder():
    global folder
    folder = askdirectory() + '/'
    if not folder: return
    lbl_open["text"] = folder
    if lbl_output["text"] == '':
        lbl_output["text"] = folder
    btn_run["state"] = "normal"

def output_folder():
    output = askdirectory() + '/'
    if not output: return
    lbl_output["text"] = output

def known_folder():
    global known
    known = askdirectory() + '/'
    if not known: return
    lbl_known["text"] = known

def close():
    window.destroy()

def face_check():
    people = []
    try:
        knownList = os.listdir(known)
        for k in knownList:
            name = k.split('.')[0]
            people.append(person(name, f"{known}{k}"))
    except NameError:
        # TODO: Double-check user really wants to run without recognized faces
        pass
    people_encodings = [i.encoding for i in people]

    # Get and create relevant folders
    output_folder = lbl_output["text"]
    if not os.path.exists(output_folder + 'unknown'):
        os.makedirs(output_folder + 'unknown')
    for i in people:
        if not os.path.exists(output_folder + i.name):
            os.makedirs(output_folder + i.name)

    c = 0
    s = ent_size.get()
    if s == '':
        SIZE = 100
    else:
        SIZE = int(s)
    fileList = os.listdir(folder)
    bar_progress["maximum"] = float(len(fileList))
    bar_progress["value"] = 0
    # TODO: include option to rerun failed images
    for f in fileList:
        img = Image.open(folder + f)
        image = face_recognition.load_image_file(folder + f)
        face_locations = face_recognition.face_locations(image, 0, model=MOD)
    
        for i in face_locations:
            # Mathematical hot mess to get SQUARE images
            top, right, bottom, left = i
            w_adjust = (right - left)//GAP
            h_adjust = (bottom - top)//GAP
            top = max(0, top - h_adjust)
            left = max(0, left - w_adjust)
            bottom = min(img.height - 1, bottom + h_adjust)
            right = min(img.width - 1, right + w_adjust)
            square_size = max(bottom - top, right - left)
            if top == 0: bottom = square_size
            if left == 0: right = square_size
            if bottom == img.height - 1: top = bottom - square_size
            if right == img.width - 1: left = right - square_size
            h = bottom - top
            w = right - left
            hw_diff = abs(h - w)//2
            if h < w:
                top = max(0, bottom - square_size, top - hw_diff)
                bottom = top + square_size
            elif w < h:
                left = max(0, right - square_size, left - hw_diff)
                right = left + square_size
            face_image = image[top:bottom, left:right]

            try:
                img_encoding = face_recognition.face_encodings(face_image)[0]
            except IndexError:
                break
            results = face_recognition.compare_faces(people_encodings, img_encoding)
            pil_image = Image.fromarray(face_image)
            # Sort extracted faces against known people
            matched = False
            for i, j in enumerate(results):
                if j == True:
                    name = people[i].name
                    pil_image = pil_image.filter(ImageFilter.SHARPEN).resize((SIZE,SIZE))
                    pil_image.save(f'{output_folder}{name}/{name}{str(c)}.png')
                    matched = True
                    break
            if matched == False:
                pil_image = pil_image.filter(ImageFilter.SHARPEN).resize((SIZE,SIZE))
                pil_image.save(f'{output_folder}unknown/unknown{str(c)}.png')
            c += 1

        img.close()
        bar_progress["value"] += 1
        bar_progress.update_idletasks()
    lbl_close["text"] = "Complete"

window = tk.Tk()
window.title('Iconographer')
window.columnconfigure(1, minsize=100, weight=1)

# TODO: This is a hot mess but probably best to fix after sorting all features/layout
btn_open = tk.Button(text="Open", command=open_folder)
lbl_open = tk.Label()
btn_output = tk.Button(text="Output", command=output_folder)
lbl_output = tk.Label()
btn_known = tk.Button(text="Known Images", command=known_folder)
lbl_known = tk.Label()
lbl_size = tk.Label(text="Icon Size:")
ent_size = tk.Entry()
btn_run = tk.Button(text="Run", command=face_check, state="disabled")
bar_progress = Progressbar(length=200, mode='determinate')
btn_close = tk.Button(text="Close", command=close)
lbl_close = tk.Label()

r = 0
btn_open.grid(row=r, column=0, sticky='ew')
lbl_open.grid(row=r, column=1, sticky='ew')
r += 1
btn_output.grid(row=r, column=0, sticky='ew')
lbl_output.grid(row=r, column=1, sticky='ew')
r += 1
btn_known.grid(row=r, column=0, sticky='ew')
lbl_known.grid(row=r, column=1, sticky='ew')
r += 1
lbl_size.grid(row=r, column=0, sticky='ew')
ent_size.grid(row=r, column=1, sticky='ew')
ent_size.insert(0, '100')
r += 1
btn_run.grid(row=r, column=0, sticky='ew')
bar_progress.grid(row=r, column=1, sticky='ew')
r += 1
btn_close.grid(row=r, column=0, sticky='ew')
lbl_close.grid(row=r, column=1, sticky='ew')

window.mainloop()

