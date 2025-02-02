import numpy as np
import matplotlib.pyplot as plt
import math
from shiny.express import input, render, ui
from htmltools import HTML, div

electron_charge = -1.6e-19
electron_mass = 9.1e-31

with ui.card(full_screen=True):
    ui.HTML("<h2 style='text-align:center;'>Частица в конденсаторе</h2>")
    ui.HTML("""
    <div style="display: flex; justify-content: space-between;">
        <div style="flex: 1; margin-right: 10px;">
            <div style="margin-bottom: 10px;">
                {input_V}
            </div>
            <div style="margin-bottom: 10px;">
                {input_L}
            </div>
        </div>
        <div style="flex: 1;">
            <div style="margin-bottom: 10px;">
                {input_r}
            </div>
            <div style="margin-bottom: 10px;">
                {input_R}
            </div>
        </div>
    </div>
    """.format(
    input_V=ui.input_text("V", label="Введите начальную скорость V (м/с):", value = "800000"),
    input_L=ui.input_text("L", label="Введите длину конденсатора L (см):", value = "30"),
    input_r=ui.input_text("r", label="Введите внутренний радиус r (см):", value = "10.5"),
    input_R=ui.input_text("R", label="Введите внешний радиус R (см):",value = "22")
))
def update_a(volt, dist, r, R):
    return (electron_charge * volt) / (electron_mass * dist * math.log(R/r))

def update_pos(pos, V, a, dt):
    return pos + V * dt + (a * dt ** 2) / 2

def update_V(pos, V, a, dt):
    return V + a * dt

def calculate_t(Vx, l):
    return l / Vx

def binsearch(R, r, t, dt):
    r_U = 1000
    l_U = 0
    U = (r_U + l_U)/2
    while r_U - l_U > 1e-9:

        tmp_U = (r_U + l_U) / 2
        y_pos = (R + r) / 2
        Vy = 0
        a = update_a(tmp_U, y_pos, r, R)
        curr_t = 0

        while r <= y_pos <= R and curr_t < t:
            y_pos = update_pos(y_pos, Vy, a, dt)
            Vy = update_V(y_pos, Vy, a, dt)
            a = update_a(tmp_U, y_pos, r, R)
            curr_t += dt

        if y_pos < r or y_pos > R:
            r_U = tmp_U
        else:
            l_U = tmp_U
            U = tmp_U
    return U, Vy

def calculate():
    V = input.V()
    L = input.L()
    r = input.r()
    R = input.R()
    if V == "" or L == "" or r == "" or R == "":
        return
        
    V = float(V)
    L = float(L)/100
    r = float(r)/100
    R = float(R)/100
        
    if L <= 0 or L > 100000 or r <= 0 or r > 100000 or R <= 0 or R > 100000:
        return 
    t = calculate_t(V, L)
    dt = t / 1000

    U, Vy = binsearch(R, r, t, dt)

    final_speed = math.sqrt(V ** 2 + Vy ** 2)
    return V, U, L, r, R, final_speed, t, dt

with ui.card(full_screen=True):
    @render.plot
    def plot():
        V, U, L, r, R, final_velocity, t, dt = calculate()  
        y_pos, tmp_V = (R + r) / 2, 0
        a = update_a(U, y_pos, r, R)
        pos_data, V_arr, a_arr, t_arr = [y_pos], [tmp_V], [a], [0]

        curr_t = 0
        while r <= y_pos <= R and curr_t <= t:
            y_pos = update_pos(y_pos, tmp_V, a, dt)
            tmp_V = update_V(y_pos, tmp_V, a, dt)
            a = update_a(U, y_pos, r, R)

            curr_t += dt
            pos_data.append(y_pos)
            V_arr.append(tmp_V)
            a_arr.append(a)
            t_arr.append(curr_t)
        
        plt.figure(figsize=(30, 30))

        plt.subplot(2, 2, 1)
        plt.plot(np.linspace(0, L, len(pos_data)), pos_data)
        plt.title(r"$График \: зависимости \: y(x)$")
        plt.xlabel(r"$x \: (м)$")
        plt.ylabel(r"$y \: (м)$")

        plt.subplot(2, 2, 2)
        plt.plot(t_arr, np.array(V_arr))
        plt.title(r"$График \: зависимости \: V_y(t)$")
        plt.xlabel(r"$t \: (с)$")
        plt.ylabel(r"$V_y \: (м/с)$")

        plt.subplot(2, 2, 3)
        plt.plot(t_arr, a_arr)
        plt.title(r"$График \: зависимости \: a_y(t)$")
        plt.xlabel(r"$t \: (с)$")
        plt.ylabel(r"$a_y \: (м/с^2)$")

        plt.subplot(2, 2, 4)
        plt.plot(t_arr, pos_data)
        plt.title(r"$График \: зависимости \: y(t)$")
        plt.xlabel(r"$t \: (с)$")
        plt.ylabel(r"$y \: (м)$")

        plt.tight_layout()
        return plt.show()


with ui.card():
    @render.ui
    def text():
        V, U, L, r, R, final_velocity, final_time, dt = calculate()
        tmp = final_time
        c = 0
        while tmp < 1:
            tmp *= 10
            c+=1
        if final_time > 1:
            return ui.markdown(
            f"**Время полета:** {final_time} с<br>"
            f"**Конечная скорость электрона:** {final_velocity:.5f} м/с<br>"
            f"**Разность потенциалов:** {U:.5f} В"
            )
        else:
            return ui.markdown(
            f"**Время полета:** {tmp}⋅10^(-{c}) с<br>"
            f"**Конечная скорость электрона:** {final_velocity:.5f} м/с<br>"
            f"**Разность потенциалов:** {U:.5f} В"
            )
