import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution
from scipy.integrate import quad
from shiny.express import input, render, ui
from htmltools import HTML, div
g = 1.62 
Vsafe = 0
reactive_values = {'result': None, 't': None, 't_x': None}
g_total = 9 * 9.81
with ui.card(full_screen=True):
    ui.HTML("<h2 style='text-align:center;'>Лунолет</h2>")
    ui.HTML("""
    <div style="display: flex; justify-content: space-between;">
        <div style="flex: 1; margin-right: 10px;">
            <div style="margin-bottom: 10px;">
                {input_M}
            </div>
            <div style="margin-bottom: 10px;">
                {input_m}
            </div>
            <div style="margin-bottom: 10px;">
                {input_Vp}
            </div>
        </div>
        <div style="flex: 1;">
            <div style="margin-bottom: 10px;">
                {input_H0}
            </div>
            <div style="margin-bottom: 10px;">
                {input_V0}
            </div>
            <div style="margin-bottom: 10px;">
                {input_Vm}
            </div>
        </div>
    </div>
    """.format(
        input_M=ui.input_text("M", label="Введите массу аппарата (кг):"),
        input_m=ui.input_text("m", label="Введите массу топлива (кг):"),
        input_Vp=ui.input_text("Vp", label="Введите скорость истечения продуктов (м/с):"),
        input_H0=ui.input_text("H0", label="Введите расстояние до Луны (м):"),
        input_V0=ui.input_text("V0", label="Введите начальную скорость (м/с):"),
        input_Vm=ui.input_text("Vm", label="Введите расход топлива (кг/с):")
    ))
def integrand(y, Vp, M, m, Vm):
    return (Vp) * np.log((M + m) / ((M+m) - Vm*y))
def getV_eng_on(t, M, m, g, Vp, Vm, V0):
    return V0 - g * t + Vp * np.log((M + m) / (M + m - Vm * t))
def getV_eng_off(t, V0):
    return V0 - g * t
def get_a_eng_on(t, M, m, g, Vp, Vm, V0):
    return Vp*Vm/((M+m)-Vm*t)
def get_a_eng_off(t, V0):
    return -g+t-t
def get_H_eng_on(t, M, m, g, Vp, Vm, V0, H0):
    integral_value, _ = quad(integrand, 0, t, args=(Vp, M, m, Vm))
    return H0 + V0*t - (g*t**2)/2 + integral_value
def get_H_eng_off(t, V0, H0):
    return H0+V0*t-g*t**2/2
def calculate():
    M = input.M()
    m = input.m()
    Vp = input.Vp()
    H0 = input.H0()
    V0 = input.V0()
    Vm = input.Vm()
    if (M == "" or m == "" or Vp == "" or H0 == "" or V0 == "" or Vm == ""):
        return 1, None, None, None, None, None, None, None, None, None, None
    M = float(M)
    m = float(m)
    Vp = float(Vp)
    H0 = float(H0)
    V0 = float(V0)
    Vm = float(Vm)

    if (M <= 0 or M > 10000 or m <= 0 or m > 10000 or H0 <= 0 or H0 > 10000 or abs(Vp) > 10000 or abs(V0) > 10000 or Vm <= 0 or Vm > 10000):
        return 1, None, None, None, None, None, None, None, None, None, None

    def equations(vars):
        x, y = vars
        integral_value, _ = quad(integrand, 0, y, args=(Vp, M, m, Vm)) 
        V = (V0-Vsafe) - g*x - g*y + (Vp)*np.log((M+m)/((M+m)-Vm*y))
        H = H0 + V0*x - (g*x**2)/2 + (V0 - g*x)*y - (g*y**2)/2 + integral_value
        return V**2 + H**2

    t_max = (M + m + Vm * Vp / g_total) / Vm
    t_eng = m / Vm
    bounds = [(0, t_max), (0, min(t_eng, t_max))] 

    result = differential_evolution(equations, bounds, tol=1e-6)
    if result.success:
        return 0, result, result.x[0], result.x[1], M, m, g, Vp, Vm, H0, V0
    else:
        return 1, None, None, None, None, None, None, None, None, None, None
        
with ui.card(full_screen=True):
    @render.plot
    def plot():
        code, result, x, y, M, m, g, Vp, Vm, H0, V0 = calculate()
        if code == 1:
            return

        t_eng_off = np.linspace(0, x, 500)
        t_eng_on = np.linspace(0, y, 500)

        plt.figure(figsize=(12, 4))
        V_eng_off = getV_eng_off(t_eng_off, V0)
        V_eng_on = getV_eng_on(t_eng_on, M, m, g, Vp, Vm, V_eng_off[-1])
        plt.subplot(1, 3, 1)
        plt.plot(t_eng_off, V_eng_off, label="двигатель выключен", color='blue')
        plt.plot(np.linspace(x, x+y, 500), V_eng_on, label="двигатель включен", color='red')
        plt.title("Зависимость V_y от времени")
        plt.xlabel("Время (t)")
        plt.ylabel("Скорость по оси Y (V_y)")
        plt.grid(True)
        plt.legend()

        a_eng_off = get_a_eng_off(t_eng_off, V0)
        a_eng_on = get_a_eng_on(t_eng_on, M, m, g, Vp, Vm, a_eng_off[-1])
        plt.subplot(1, 3, 2)
        plt.plot(t_eng_off, a_eng_off, label="двигатель выключен", color='blue')
        plt.plot(np.linspace(x, x+y, 500), a_eng_on, label="двигатель включен", color='red')
        plt.title("Зависимость a от времени")
        plt.xlabel("Время (t)")
        plt.ylabel("Ускорение по оси Y (a_y)")
        plt.grid(True)
        plt.legend()

        H_eng_off = get_H_eng_off(t_eng_off, V0, H0)
        H_eng_on = np.array([])
        for i in t_eng_on:
            H_eng_on = np.append(H_eng_on, get_H_eng_on(i, M, m, g, Vp, Vm, V_eng_off[-1], H_eng_off[-1]))
        plt.subplot(1, 3, 3)
        plt.plot(t_eng_off, H_eng_off, label="двигатель выключен", color='blue')
        plt.plot(np.linspace(x, x+y, 500), H_eng_on, label="двигатель включен", color='red')
        plt.title("Зависимость H от времени")
        plt.xlabel("Время (t)")
        plt.ylabel("Высота по оси Y (H_y)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        return plt.show()
with ui.card():
    @render.ui
    def text():
        code, result, t, t_x, M, m, g, Vp, Vm, H0, V0 = calculate()
        if code == 1:
            return div(HTML("<p>Нет результата.</p>"))
        H = get_H_eng_off(t, V0, H0)
        V_eng_off = getV_eng_off(t, V0)
        V_eng_on = getV_eng_on(t_x, M, m, g, Vp, Vm, V_eng_off)
        return ui.markdown(
        f"**Вертикальная скорость на высоте 0:** -{V_eng_on:.2f} м/с<br>"
        f"**Высота, на которой был включен двигатель:** {H:.2f} м<br>"
        f"**Время полета с выключенным двигателем:** {t:.2f} с<br>"
        f"**Время полета со включенным двигателем:** {t_x:.2f} с"
        )
