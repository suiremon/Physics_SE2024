import numpy as np
import matplotlib.pyplot as plt
from shiny.express import input, render, ui

ui.input_text("epsilon1", "Введите диэлектрическую проницаемость первой среды", value=1)
ui.input_text("epsilon2", "Введите диэлектрическую проницаемость второй среды", value=2)
ui.input_text("E1_magnitude", "Введите модуль напряженности", value=5)
ui.input_text("D1_magnitude", "Введите модуль индукции", value = 7)
ui.input_text("alpha1", "Введите угол падения в градусах", value=30)
with ui.card(full_screen=True):
    @render.plot
    def plot():

        epsilon1 = input.epsilon1()
        epsilon2 =  input.epsilon2()
        E1_magnitude = input.E1_magnitude()
        D1_magnitude = input.D1_magnitude()
        alpha1 = input.alpha1() 
        if (epsilon1 == "" or epsilon2 == "" or E1_magnitude == "" or alpha1 == ""):
            return
        epsilon1 = float(epsilon1)
        epsilon2 = float(epsilon2)
        E1_magnitude = float(E1_magnitude)
        D1_magnitude = float(D1_magnitude)
        alpha1 = float(alpha1)
        if (epsilon1 < 0 or D1_magnitude < 0 or D1_magnitude > 10000 or epsilon2 < 0 or epsilon1 > 10000 or epsilon2 > 10000 or E1_magnitude < 0 or E1_magnitude > 10000 or alpha1 < -360 or alpha1 > 360):
            return
        epsilon1 = float(epsilon1)
        epsilon2 = float(epsilon2)
        E1_magnitude = float(E1_magnitude)
        alpha1 = float(alpha1)
        alpha1_rad = np.radians(alpha1)
        alpha2_rad = np.arcsin((epsilon1 / epsilon2) * np.sin(alpha1_rad))
        alpha2 = np.degrees(alpha2_rad)

        E1_x = E1_magnitude * np.cos(alpha1_rad)
        E1_y = E1_magnitude * np.sin(alpha1_rad)

        E2_magnitude = E1_magnitude * (epsilon1 / epsilon2)
        E2_x = E2_magnitude * np.cos(alpha2_rad)
        E2_y = E2_magnitude * np.sin(alpha2_rad)

        D1_x = D1_magnitude * np.cos(alpha1_rad)
        D1_y = D1_magnitude * np.sin(alpha1_rad)

        D2_magnitude = epsilon2 * E2_magnitude
        D2_x = D2_magnitude * np.cos(alpha2_rad)
        D2_y = D2_magnitude * np.sin(alpha2_rad)

        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        axes[0].quiver(-2, 0, E1_x, E1_y, angles="xy", scale_units="xy", scale=1, color="orange", label="$E_1$")
        axes[0].quiver(0, 0, E1_x, E1_y, angles="xy", scale_units="xy", scale=1, color="orange", label="")
        axes[0].quiver(2, 0, E1_x, E1_y, angles="xy", scale_units="xy", scale=1, color="orange", label="")
        for i in range(5):
            offset = i - 2
            axes[0].quiver(-E2_x + offset, -E2_y, E2_x, E2_y, angles="xy", scale_units="xy", scale=1, color="blue", label="$E_2$" if i == 0 else "")
            axes[0].set_xlim(-5, 5)
        axes[0].set_ylim(-5, 5)
        axes[0].set_xlabel("X")
        axes[0].set_ylabel("Y")
        axes[0].legend()
        axes[0].grid(True)
        axes[0].set_title("Напряженность $E$")

        axes[1].axhline(0, color="black", linewidth=0.8)
        for i in range(5):
            offset = i - 2
            axes[1].quiver(offset, 0, D1_x, D1_y, angles="xy", scale_units="xy", scale=1, color="red", label="$D_1$" if i == 0 else "")
            axes[1].quiver(-D2_x + offset, -D2_y, D2_x, D2_y, angles="xy", scale_units="xy", scale=1, color="blue", label="$D_2$" if i == 0 else "")
        axes[1].set_xlim(-5, 5)
        axes[1].set_ylim(-5, 5)
        axes[1].set_xlabel("X")
        axes[1].set_ylabel("Y")
        axes[1].legend()
        axes[1].grid(True)
        axes[1].set_title("Индукция $D$")

        plt.tight_layout()
        return plt.show()
