from shiny.express import input, render, ui
import numpy as np
import matplotlib.pyplot as plt

MAX_VALUE = 10**5
E0 = 8.854e-12
k = 9 * 10**9

ui.input_text("charge_input", "Введите заряды:", value=str([(0, 1, -2), (-1, 2, 3), (4, -1, 7), (0, 0, -1)]), width="100%")
ui.help_text("Заряды вводятся в формате списка кортежей (x, y, заряд), например [(0, 1, -2), (-2, 1, 1)].")
ui.input_numeric("Lx", "Размер области по x (м)", 10)
ui.input_numeric("Ly", "Размер области по y (м)", 10)
ui.input_numeric("dLx", "Шаг сетки по x (м)", 0.1)
ui.input_numeric("dLy", "Шаг сетки по y (м)", 0.1)
ui.input_text("dipole_params", "Параметры диполя (x, y, px, py):", value="(0, 0, 1, 0)", width="100%")
ui.help_text("Введите координаты центра диполя (x, y) и его дипольный момент (px, py). Например: (0, 0, 1, 0).")

with ui.card(full_screen=True):
    @render.plot
    def combined_plot():
        try:
            user_input = input.charge_input()
            Q = eval(user_input)

            if not all(isinstance(q, tuple) and len(q) == 3 for q in Q):
                raise ValueError("Неверный формат заряда. Ожидается список кортежей в формате [(x, y, заряд), ...]")
            if any(abs(val) > MAX_VALUE for q in Q for val in q):
                raise ValueError(f"Значение зарядов или координат превышает допустимый предел {MAX_VALUE}.")

            dipole_input = eval(input.dipole_params())
            if not (isinstance(dipole_input, tuple) and len(dipole_input) == 4):
                raise ValueError("Неверный формат диполя. Ожидается кортеж (x, y, px, py).")
            dipole_x, dipole_y, dipole_px, dipole_py = dipole_input
        except Exception as e:
            raise ValueError(f"Ошибка ввода: {e}")

        Lx, Ly = input.Lx(), input.Ly()
        dLx, dLy = input.dLx(), input.dLy()
        x, y = np.meshgrid(
            np.arange(-Lx, Lx + dLx, dLx),
            np.arange(-Ly, Ly + dLy, dLy)
        )

        Fi = np.zeros_like(x, dtype=np.float64)
        Ex, Ey = np.zeros_like(x), np.zeros_like(y)
        for charge, px, py in Q:
            K = charge / (4 * np.pi * E0)
            distance = np.sqrt((x - px)**2 + (y - py)**2)
            Fi += K / distance

            deltaX, deltaY = x - px, y - py
            Ex += k * charge * deltaX / (distance**3)
            Ey += k * charge * deltaY / (distance**3)

        dipole_distance = np.sqrt((x - dipole_x)**2 + (y - dipole_y)**2)
        dipole_Fi = k * (dipole_px * (x - dipole_x) + dipole_py * (y - dipole_y)) / (dipole_distance**3)
        Fi += dipole_Fi

        dipole_Ex = k * (3 * (dipole_px * (x - dipole_x) + dipole_py * (y - dipole_y)) * (x - dipole_x) / dipole_distance**5 - dipole_px / dipole_distance**3)
        dipole_Ey = k * (3 * (dipole_px * (x - dipole_x) + dipole_py * (y - dipole_y)) * (y - dipole_y) / dipole_distance**5 - dipole_py / dipole_distance**3)

        Ex += dipole_Ex
        Ey += dipole_Ey

        dipole_E = np.array([
            np.interp(dipole_x, x[0], Ex[:, 0]),
            np.interp(dipole_y, y[:, 0], Ey[0, :])
        ])
        force = dipole_px * dipole_E[0] + dipole_py * dipole_E[1]
        torque = dipole_px * dipole_E[1] - dipole_py * dipole_E[0]

        fig, ax = plt.subplots(figsize=(10, 8))

        levels_pos = [10, 20, 40, 60]
        levels_neg = [-60, -40, -20, -10]
        ax.contour(x, y, Fi, levels=levels_pos, colors='red', linewidths=1, linestyles='solid')
        ax.contour(x, y, Fi, levels=levels_neg, colors='blue', linewidths=1, linestyles='dotted')

        ax.streamplot(x, y, Ex, Ey, color='grey', linewidth=0.8, density=1.5)

        ax.scatter([q[1] for q in Q], [q[2] for q in Q], c='green', s=[abs(q[0])*50 for q in Q], zorder=3)
        for q in Q:
            ax.text(q[1] + 0.1, q[2] - 0.3, f'{q[0]}', color='black')

        ax.quiver(dipole_x, dipole_y, dipole_px, dipole_py, angles='xy', scale_units='xy', scale=1, color='red', zorder=4)
        ax.text(dipole_x + 0.2, dipole_y + 0.2, f'F={force:.2e}, T={torque:.2e}', color='red')

        ax.set_title("Эквипотенциальные линии, электрическое поле и диполь")
        ax.set_xlabel("x, м")
        ax.set_ylabel("y, м")
        ax.set_aspect('equal')
        ax.grid(True)

        return fig
