from shiny.express import input, render, ui

import numpy as np

def find_t(h,v,a):
    d = v**2*np.sin(a)**2+4*9.81/2*h
    t1=(-v*np.sin(a)+np.sqrt(d))/(-9.81)
    t2=(-v*np.sin(a)-np.sqrt(d))/(-9.81)
    return [t1,t2]

    
ui.input_text("angle", label="Введите угол:")
ui.input_text("velocity", label="Введите скорость:")
ui.input_text("height", label="Введите высоту:")

with ui.card(full_screen=True):
    g = 9.81
    @render.plot
    def plot():
        import matplotlib.pyplot as plt
        angle = input.angle()
        velocity = input.velocity()
        height = input.height()
        if (angle != "" and velocity != "" and height != "" and int(height) >=0):
            velocity = float(velocity)
            height = float(height)
            angle = np.radians(float(angle))
            time_of_flight = find_t(height, velocity, angle)[1]
        else:
            return plt.plot(0, 0)
        #time_of_flight = 2 * velocity * np.sin(angle) / g
        time = np.linspace(0, time_of_flight, 100)
        x = velocity * np.cos(angle) * time
        y = height + velocity * np.sin(angle) * time - 0.5 * g * time**2

        vx = velocity * np.cos(angle)
        vy = velocity * np.sin(angle) - g * time
        v = np.sqrt(vx**2 + vy**2)

        fig, axis = plt.subplots(2, 2)

        axis[0,0].plot(time,v)
        axis[0,0].set_xlabel("Время (с)")
        axis[0,0].set_ylabel("Скорость (м/с)")
        axis[0,0].set_title("Зависимость скорости от времени")
        axis[0,0].grid(True)
        axis[0,0].plot(time,v)

        axis[0,1].plot(x, y)
        axis[0,1].set_xlabel("Горизонтальное расстояние (м)")
        axis[0,1].set_ylabel("Высота (м)")
        axis[0,1].set_title("Баллистическая кривая")
        axis[0,1].grid(True)

        axis[1, 0].plot(time, x)
        axis[1, 0].set_ylabel("Координата х (м)")
        axis[1, 0].set_xlabel("Время (с)")
        axis[1, 0].set_title("Зависимость координаты х от времени")
        axis[1, 0].grid(True)

        axis[1, 1].plot(time, y)
        axis[1, 1].set_ylabel("Координата y (м)")
        axis[1, 1].set_xlabel("Время (с)")
        axis[1, 1].set_title("Зависимость координаты y от времени")
        axis[1, 1].grid(True)
        return fig

