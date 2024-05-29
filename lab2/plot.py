import json
import time
from tkinter import *
from tkinter import simpledialog
from tkinter.ttk import Combobox
from PIL import Image, ImageTk

import numpy as np

import trajectorygenerator

prev_x = None
prev_y = None
res_coeff = None
Plane = []
point1 = {}
point2 = {}
ImitationRequest = ''
ImitationResponse = ''
isUsualHit = 'red'
isFuzzyHit = 'red'
window_master = None
is_pop_enter_open = False
is_pop_result_open = False

def requestPointToNPPoint(p):
    return np.array([[p['x']], [p['y']]], np.float64)


class PopupWindow(object):
    def __init__(self, master):
        self.top = Toplevel(master)
        self.top.title("Введите параметры запуска")
        self.top.grid()

        self.fly_time_label = Label(self.top, text="Введите время полета")
        self.fly_time_label.grid(row=0, column=0, sticky=W, padx=10)
        self.fly_time = Entry(self.top)
        self.fly_time.grid(row=1, column=0, sticky=W, padx=10)

        self.velo_label = Label(self.top, text="Введите скорость ракеты")
        self.velo_label.grid(row=0, column=2, sticky=W)
        self.velo = Entry(self.top)
        self.velo.grid(row=1, column=2, sticky=W, padx=10)

        self.b = Button(self.top, text='Start', command=self._start_sim)
        self.b.grid(row=2, column=1, sticky=W, pady=15)

        fuzzy_methods_label = Label(self.top, text="Fuzzy")
        fuzzy_methods_label.grid(column=3, row=0, padx=5, pady=5)
        self.fuzzy_methods = Combobox(self.top, values=["Метод правого максимума", "Метод центра тяжести"],
                                 width=30, state="readonly")
        self.fuzzy_methods.grid(column=3, row=1, padx=5, pady=5)
        self.fuzzy_methods.current(1)

        defuzzy_logic_methods_label = Label(self.top, text="Defuzzy")
        defuzzy_logic_methods_label.grid(column=4, row=0, padx=5, pady=5)
        self.defuzzy_logic_methods = Combobox(self.top, values=["Метод максимума-минимума", "Метод максимума-произведения"],
                                         width=30, state="readonly")
        self.defuzzy_logic_methods.grid(column=4, row=1, padx=5, pady=5)
        self.defuzzy_logic_methods.current(1)

    def _start_sim(self):
        global is_pop_enter_open
        entered_fly_time = int(self.fly_time.get())
        entered_velocity = int(self.velo.get())
        defuzzy = self.defuzzy_logic_methods.get()
        fuzzy = self.fuzzy_methods.get()
        start(entered_fly_time, entered_velocity, defuzzy, fuzzy)
        is_pop_enter_open = False
        self.top.destroy()


def start_com():
    global window_master
    global is_pop_enter_open
    if is_pop_enter_open:
        return
    PopupWindow(window_master)


def start(_fly_time, _velocity, _defuzzy, _fuzzy):
    global res_coeff
    global Plane
    global point1
    global point2
    global isUsualHit
    global isFuzzyHit

    defuzz_val = "Centroid"
    fuzz_val = "Max-Min"

    if _defuzzy == "Метод центра тяжести":
        defuzz_val = "Centroid"
    if _defuzzy == "Метод правого максимума":
        defuzz_val = "Right-Max"
    if _fuzzy == "Метод максимума-минимума":
        fuzz_val = "Max-Min"
    if _fuzzy == "Метод максимума-произведения":
        fuzz_val = "Max-Prod"

    res_coeff = 3
    res_coeff = int(res_coeff)

    AircraftPoints = {"AircraftPoints": Plane,
                      "Missiles": {"Defuzzification": defuzz_val, "Direction": point2, "Inference": fuzz_val,
                                   "LaunchPoint": point1, "PropCoeff": res_coeff, "VelocityModule": _fly_time},
                      "StepsCount": _velocity}

    ImitationRequest = json.dumps(AircraftPoints, ensure_ascii=False)

    tr = trajectorygenerator.TrajectoryGenerator(ImitationRequest)
    ImitationResponse = tr.response_s
    data = json.loads(ImitationResponse)

    curvesBasicPoints = np.hstack(tuple(map(requestPointToNPPoint, data['AircraftTrajectory'])))
    for i in range(_velocity - 5):
        x = curvesBasicPoints[0][i]
        y = curvesBasicPoints[1][i]
        if i % 3 == 0:
            canvas.create_oval(x - 2.0, y + 2.0, x + 2.0, y - 2.0, outline="BLACK", fill="BLACK")

    settings = data['UsualMissile']
    curvesUsual = np.hstack(tuple(map(requestPointToNPPoint, settings['Trajectory'])))
    UsualP = np.shape(curvesUsual)
    for i in range(UsualP[1] - 1):
        x = curvesUsual[0][i]
        y = curvesUsual[1][i]
        if i % 3 == 0:
            canvas.create_oval(x - 2.0, y + 2.0, x + 2.0, y - 2.0, outline="BLUE", fill="BLUE")
    UsualHit = settings['IsHit']

    settings = data['FuzzyMissile']
    curvesFuzzy = np.hstack(tuple(map(requestPointToNPPoint, settings['Trajectory'])))
    FuzzyP = np.shape(curvesFuzzy)
    for i in range(FuzzyP[1] - 1):
        x = curvesFuzzy[0][i]
        y = curvesFuzzy[1][i]
        if i % 3 == 0:
            canvas.create_oval(x - 2.0, y + 2.0, x + 2.0, y - 2.0, outline="RED", fill="RED")
    FuzzyHit = settings['IsHit']

    print("Usual missile hit?", UsualHit)
    print("Fuzzy missile hit?", FuzzyHit)

    if UsualHit:
        first_hit.config(bg='green')
    else:
        first_hit.config(bg='red')

    if FuzzyHit:
        second_hit.config(bg='green')
    else:
        second_hit.config(bg='red')

    oval1 = canvas.create_oval(0, 0, 0, 0, fill="YELLOW")
    oval2 = canvas.create_oval(0, 0, 0, 0, fill="PINK")
    oval3 = canvas.create_oval(0, 0, 0, 0, fill="ORANGE")
    # oval4 = canvas.create_oval(0, 0, 0, 0, outline= "GREEN", width=5)

    FuzzyFlag = False
    UsualFlag = False

    for i in range(_velocity - 5):
        x1 = curvesBasicPoints[0][i]
        y1 = curvesBasicPoints[1][i]
        canvas.coords(oval1, x1 - 5.0, y1 + 5.0, x1 + 5.0, y1 - 5.0)
        time.sleep(0.02)
        window.update()

        if i < UsualP[1]:
            x2 = curvesUsual[0][i]
            y2 = curvesUsual[1][i]
            canvas.coords(oval2, x2 - 5.0, y2 + 5.0, x2 + 5.0, y2 - 5.0)
            window.update()

        if i < FuzzyP[1]:
            x3 = curvesFuzzy[0][i]
            y3 = curvesFuzzy[1][i]
            canvas.coords(oval3, x3 - 5.0, y3 + 5.0, x3 + 5.0, y3 - 5.0)
            window.update()

        if not FuzzyFlag:
            FuzzyFlag = i == FuzzyP[1]
            if FuzzyFlag:
                canvas.create_oval(x3 - 25.0, y3 + 25.0, x3 + 25.0, y3 - 25.0, outline="ORANGE", width=5)
        if not UsualFlag:
            UsualFlag = i == UsualP[1]
            if UsualFlag:
                canvas.create_oval(x2 - 25.0, y2 + 25.0, x2 + 25.0, y2 - 25.0, outline="ORANGE", width=5)

        if FuzzyFlag and UsualFlag:
            break


def missile_com():
    def b1(event):
        global prev_x, prev_y
        global point1, point2
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        if prev_x:
            canvas.create_line(prev_x, prev_y, x, y, arrow=LAST)
            point1 = {"x": prev_x, "y": prev_y}
            point2 = {"x": x, "y": y}
            x = None
            y = None
        prev_x = x
        prev_y = y

    canvas.bind('<Button-1>', b1)


def plane_com():
    global Plane

    def b1(event):
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        canvas.create_oval(x - 5.0, y + 5.0, x + 5.0, y - 5.0, fill="BLACK")

        point = {"x": x, "y": y}
        Plane.append(point)

    canvas.bind('<Button-1>', b1)


def clear_com():
    canvas.delete("all")
    first_hit.config(bg='red')
    second_hit.config(bg='red')
    Plane.clear()


scale = 1


def zoom_c(event):
    global scale
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)

    if event.num == 5 or event.delta == -120:
        canvas.scale('all', x, y, 0.9, 0.9)
    if event.num == 4 or event.delta == 120:
        canvas.scale('all', x, y, 1.1, 1.1)


if __name__ == "__main__":
    window = Tk()
    window.title("Имитатор наведения")
    sw = 1600  # window.winfo_screenwidth()
    sh = 900  # window.winfo_screenheight()
    window.geometry('%dx%d' % (sw - 300, sh - 300))

    window_frame = Frame(window)
    window_master = window_frame.master

    # TOOLBAR
    toolbar = Frame(window_frame.master, bd=1, relief=RAISED)

    # PLANE BUTTON
    window_frame.img = Image.open("img/plane.png")
    plane_img = ImageTk.PhotoImage(window_frame.img)

    plane_button = Button(toolbar, image=plane_img, relief=FLAT, command=plane_com)
    plane_button.image = plane_img
    plane_button.pack(side=LEFT, padx=5, pady=5)

    # MISSILE BUTTON
    window_frame.img = Image.open("img/missile.png")
    missile_img = ImageTk.PhotoImage(window_frame.img)

    missile_button = Button(toolbar, image=missile_img, relief=FLAT, command=missile_com)
    missile_button.image = missile_img
    missile_button.pack(side=LEFT, padx=5, pady=5)

    # ERASER BUTTON
    window_frame.img = Image.open("img/eraser.png")
    eraser_img = ImageTk.PhotoImage(window_frame.img)

    eraser_button = Button(toolbar, image=eraser_img, relief=FLAT, command=clear_com)
    eraser_button.image = eraser_img
    eraser_button.pack(side=LEFT, padx=5, pady=5)

    # START BUTTON
    window_frame.img = Image.open("img/start.png")
    start_img = ImageTk.PhotoImage(window_frame.img)

    start_button = Button(toolbar, image=start_img, relief=FLAT, command=start_com)
    start_button.image = start_img
    start_button.pack(side=LEFT, padx=5, pady=5)

    toolbar.pack(side=TOP, fill=X)
    window_frame.pack()

    # STATUSBAR
    statusbar = Frame(window_frame.master, bd=1, relief=RAISED)

    # нечеткая модификация пропорционального метода наведения
    first_hit_label = Label(statusbar, text="Попадание ПМН")
    first_hit_label.grid(column=0, row=6, padx=5, pady=5)
    first_hit = Entry(statusbar, width=5, bg='red', state="readonly")
    first_hit.grid(column=1, row=6, padx=5, pady=5)

    second_hit_label = Label(statusbar, text="Попадание НМН")
    second_hit_label.grid(column=0, row=7, padx=5, pady=5)
    second_hit = Entry(statusbar, width=5, bg='red', state="readonly")
    second_hit.grid(column=1, row=7, padx=5, pady=5)

    statusbar.pack(side=BOTTOM, fill=X)
    window_frame.pack()

    canvas = Canvas(window, relief=RAISED, borderwidth=1, bg='WHITE')
    canvas.pack(side=RIGHT, padx=5)
    canvas.pack(fill=BOTH, expand=1)

    canvas.bind("<MouseWheel>", zoom_c)
    canvas.bind('<ButtonPress-3>', lambda event: canvas.scan_mark(event.x, event.y))
    canvas.bind("<B3-Motion>", lambda event: canvas.scan_dragto(event.x, event.y, gain=1))

    st = Label(canvas, bg='WHITE')
    st.pack(side=TOP, expand=1)

    window.mainloop()
