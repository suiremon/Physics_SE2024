import numpy as np
import matplotlib.pyplot as plt
from shiny.express import input, render, ui, output
from scipy.integrate import quad

n_points = 100

ui.input_text("force_expression", label="Введите выражение для силы F(x, y): ")
ui.help_text("x+y - сложение\nx-y - вычитание\nx*y - умножение\nx/y - деление\nx//y - целочисленное деление\nx**y - степень")
ui.input_text("x_min", label="Выберите минимальный x: ")
ui.input_text("y_min", label="Выберите минимальный y: ")
ui.input_text("x_max", label="Введите максимальный x: ")
ui.input_text("y_max", label="Введите максимальный y: ")

def integrate_Fx(x, y, force_expression):
    F = eval(force_expression)
    return F

def integrate_Fy(y, x, force_expression):
    F = eval(force_expression)
    return F

def potential_energy(x, y, force_expression):
    # Интеграл по x и по y
    U_x, _ = quad(integrate_Fx, x, 0, args=(y, force_expression))
    U_y, _ = quad(integrate_Fy, y, 0, args=(x, force_expression))
    return U_x + U_y

with ui.card(full_screen=True):
    @render.plot
    def plot():
        force_expression = input.force_expression()
        x_min = input.x_min()
        y_min = input.y_min()
        x_max = input.x_max()
        y_max = input.y_max()
        
        if (x_min == "" or x_max == "" or y_min == "" or y_max == ""):
            return
        x_min = float(x_min)
        x_max = float(x_max)
        y_min = float(y_min)
        y_max = float(y_max)
        
        if (force_expression == "" or x_max < x_min or y_max < y_min):
            return
        if (abs(x_min) > 100000 or abs(x_max) > 100000 or abs(y_min) > 100000 or abs(y_max) > 100000):
            return
        
        x, y = np.meshgrid(np.linspace(x_min, x_max, n_points), np.linspace(y_min, y_max, n_points))
        
        z = np.zeros_like(x)
        for i in range(len(x)):
            for j in range(len(y)):
                z[i, j] = potential_energy(x[i, j], y[i, j], force_expression)
        
        plt.figure(figsize=(8, 6))
        contour = plt.contourf(x, y, z, 50, cmap='YlOrRd')
        plt.colorbar(contour, label='Потенциальная энергия U(x, y)')
        
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Потенциальное поле')
        plt.grid(True)
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        return plt.show()
