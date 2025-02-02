import tkinter as tk
from tkinter import messagebox

def calculate_capacitor_parameters(U, d, epsilon_r, connected_to_power_source, S=1.0):
    epsilon_0 = 8.854e-12  # Ф/м
    epsilon = epsilon_r * epsilon_0
    E = U / d
    C = (epsilon * S) / d
    Q = C * U
    
    return E, Q

def on_calculate():
    try:
        U = float(entry_voltage.get())
        d = float(entry_distance.get())
        epsilon_r = float(entry_dielectric.get())
        connected_to_power_source = var_connected.get()
        
        E, Q = calculate_capacitor_parameters(U, d, epsilon_r, connected_to_power_source)
        
        result_text = f"Напряженность электрического поля (E): {E:.2f} В/м\n"
        result_text += f"Заряд на пластинах (Q): {Q:.2e} Кл"
        
        messagebox.showinfo("Результаты", result_text)
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные значения.")

# Создание основного окна
root = tk.Tk()
root.title("Расчет параметров плоского конденсатора")

# Создание виджетов
label_voltage = tk.Label(root, text="Напряжение (В):")
label_voltage.pack()

entry_voltage = tk.Entry(root)
entry_voltage.pack()

label_distance = tk.Label(root, text="Расстояние между пластинами (м):")
label_distance.pack()

entry_distance = tk.Entry(root)
entry_distance.pack()

label_dielectric = tk.Label(root, text="Диэлектрическая проницаемость:")
label_dielectric.pack()

entry_dielectric = tk.Entry(root)
entry_dielectric.pack()

var_connected = tk.BooleanVar()
checkbox_connected = tk.Checkbutton(root, text="Подключен к источнику питания", variable=var_connected)
checkbox_connected.pack()

button_calculate = tk.Button(root, text="Рассчитать", command=on_calculate)
button_calculate.pack()

# Запуск основного цикла
root.mainloop()
