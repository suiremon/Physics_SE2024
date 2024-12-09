import numpy as np
import matplotlib.pyplot as plt
import random
from shiny.express import input, render, ui

def getColor():
    return (random.randint(0,255)/255,random.randint(0,255)/255,random.randint(0,255)/255)

dt = 0.01
g = 9.81
def derivatives(t, vx, vy, k):
    dxdt = vx
    dydt = vy
    dvxdt = -k * vx
    dvydt = -g - k * vy
    return dxdt, dydt, dvxdt, dvydt

ui.input_text("V", label="Введите начальную скорость (м/с):")
ui.input_text("a", label="Введите угол между вектором скорости и линией горизонта:")
ui.input_text("h0", label="Введите высоту, с которой брошено тело (м):")
ui.input_text("k", label="Введите коэффициент сопротивления среды:")

with ui.card(full_screen=True):
    @render.plot
    def plot():
        v0 = input.V()
        a = input.a()
        h0 = input.h0()
        k = input.k()
        if (v0 != "" and a != "" and h0 != "" and k != ""):
            v0 = float(v0)
            a = float(a)
            h0 = float(h0)
            k = float(k)
            theta = np.radians(a)
        else:
            return
        if (abs(v0) > 1000000 or abs(a) > 1000000 or abs(h0) > 1000000 or abs(k) > 1000000):
            return

        vx0 = v0 * np.cos(theta)
        vy0 = v0 * np.sin(theta)

        t_values = [0]
        x_values = [0]
        y_values = [h0]
        vx_values = [vx0]
        vy_values = [vy0]

        t = 0
        x = 0
        y = h0
        vx = vx0
        vy = vy0

        while y >= 0:
            dxdt1, dydt1, dvxdt1, dvydt1 = derivatives(t, vx, vy, k)
            dxdt2, dydt2, dvxdt2, dvydt2 = derivatives(t + dt/2, vx + dvxdt1 * dt/2, vy + dvydt1 * dt/2,k)
            dxdt3, dydt3, dvxdt3, dvydt3 = derivatives(t + dt/2, vx + dvxdt2 * dt/2, vy + dvydt2 * dt/2,k)
            dxdt4, dydt4, dvxdt4, dvydt4 = derivatives(t + dt, vx + dvxdt3 * dt, vy + dvydt3 * dt,k)
            
            vx += (dvxdt1 + 2*dvxdt2 + 2*dvxdt3 + dvxdt4) * dt / 6
            vy += (dvydt1 + 2*dvydt2 + 2*dvydt3 + dvydt4) * dt / 6
            x += (dxdt1 + 2*dxdt2 + 2*dxdt3 + dxdt4) * dt / 6
            y += (dydt1 + 2*dydt2 + 2*dydt3 + dydt4) * dt / 6
            
            t += dt
            
            t_values.append(t)
            x_values.append(x)
            y_values.append(y)
            vx_values.append(vx)
            vy_values.append(vy)
            
        t_values = np.array(t_values)
        x_values = np.array(x_values)
        y_values = np.array(y_values)
        vx_values = np.array(vx_values)
        vy_values = np.array(vy_values)

        total_speed = np.sqrt(vx_values**2 + vy_values**2)

        fig, axs = plt.subplots(2, 2, figsize=(12, 18))
        axs[0][0].plot(x_values, y_values, label='S (расстояние)', color=getColor())
        axs[0][0].set_title("Движение тела с учетом сопротивления воздуха")
        axs[0][0].set_xlabel("Горизонтальное расстояние (м)")
        axs[0][0].set_ylabel("Вертикальное расстояние (м)")
        axs[0][0].legend()
        axs[0][0].grid(True)

        axs[0][1].plot(t_values, total_speed, label='V (Скорость)', color=getColor())
        axs[0][1].set_title("График скорости от времени")
        axs[0][1].set_xlabel("Время (с)")
        axs[0][1].set_ylabel("Скорость (м/с)")
        axs[0][1].legend()
        axs[0][1].grid(True)

        axs[1][0].plot(t_values, x_values, label='x (Положение по Ох)', color=getColor())
        axs[1][0].set_title("График положения тела по Ох от времени")
        axs[1][0].set_xlabel("Время (с)")
        axs[1][0].set_ylabel("Положение (м)")
        axs[1][0].legend()
        axs[1][0].grid(True)

        axs[1][1].plot(t_values, y_values, label='y (Положение по Оу)', color=getColor())
        axs[1][1].set_title("График положения тела по Оу от времени")
        axs[1][1].set_xlabel("Время (с)")
        axs[1][1].set_ylabel("Положение (м)")
        axs[1][1].legend()
        axs[1][1].grid(True)
        plt.subplots_adjust(hspace=0.5)
        return plt.show()




