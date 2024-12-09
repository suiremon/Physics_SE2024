import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from shiny.express import input, render, ui

ui.input_text("m", label="Введите массу груза (кг):")
ui.input_text("k", label="Введите коэффициент жесткости груза:")
ui.input_text("b", label="Введите коэффициент сопротивления среды:")

def damped_oscillator(t, y, b, m, k):
    x, v = y
    dxdt = v
    dvdt = -(b/m)*v - (k/m)*x
    return [dxdt, dvdt]

with ui.card(full_screen=True):
    @render.plot
    def plot():
        m = input.m()
        k = input.k()
        b = input.b()
        if (m == "" or k == "" or b == ""):
            return
        m = float(m)
        k = float(k)
        b = float(b)
        if (m <= 0 or m > 10000 or abs(k)>10000 or abs(b)>10000):
            return
        x0 = 2.0
        v0 = 0.0
        initial_conditions = [x0, v0]

        t_span = (0, 20)
        t_eval = np.linspace(t_span[0], t_span[1], 1000)

        solution = solve_ivp(damped_oscillator, t_span, initial_conditions, t_eval=t_eval, args=(b,m,k))

        x = solution.y[0]
        v = solution.y[1]
        t = solution.t

        kinetic_energy = 0.5 * m * v**2
        potential_energy = 0.5 * k * x**2
        total_energy = kinetic_energy + potential_energy

        plt.figure(figsize=(10, 6))
        plt.plot(t, kinetic_energy, label='Кинетическая энергия (Ek)', color='r')
        plt.plot(t, potential_energy, label='Потенциальная энергия (Ep)', color='b')
        plt.plot(t, total_energy, label='Общая энергия (Et)', color='g', linestyle='--')
        plt.title('Трансформация энергии при колебании груза на пружине')
        plt.xlabel('Время (с)')
        plt.ylabel('Энергия (Дж)')
        plt.legend()
        plt.grid(True)
        return plt.show()
