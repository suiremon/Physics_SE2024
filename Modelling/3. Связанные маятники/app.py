import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from matplotlib.widgets import Slider, Button, TextBox

params = {
    'm': 1.0,     # pendulum mass
    'L': 1.0,     # pendulum length
    'g': 9.81,    # gravity
    'k': 0.5,     # spring stiffness
    'L1': 0.5,    # spring mount distance
    'beta': 0.05  # damping coefficient
}

def solve_system(m, L, g, k, L1, beta, phi1_0, phi2_0):
    def equations(t, y):
        phi1, omega1, phi2, omega2 = y
        dphi1_dt = omega1
        domega1_dt = (-beta * omega1 - k * L1**2 * (phi1 - phi2) - m * g * L * phi1) / (m * L**2)
        dphi2_dt = omega2
        domega2_dt = (-beta * omega2 - k * L1**2 * (phi2 - phi1) - m * g * L * phi2) / (m * L**2)
        return [dphi1_dt, domega1_dt, dphi2_dt, domega2_dt]

    y0 = [phi1_0, 0.0, phi2_0, 0.0]
    t_span = (0, 1000)
    t_eval = np.linspace(*t_span, 10000)
    sol = solve_ivp(equations, t_span, y0, t_eval=t_eval)
    return sol

def compute_normal_frequencies(m, L, g, k, L1):
    omega1 = np.sqrt(g / L)
    omega2 = np.sqrt(g / L + (2 * k * L1**2) / (m * L**2))
    return np.array([omega1, omega2])

sol = solve_system(params['m'], params['L'], params['g'], params['k'], params['L1'], params['beta'], 0.1, 0.0)

fig, axs = plt.subplots(3, figsize=(10, 8))
plt.subplots_adjust(left=0.1, bottom=0.55)

l1, = axs[0].plot(sol.t, sol.y[0], label='ϕ₁')
l2, = axs[0].plot(sol.t, sol.y[2], label='ϕ₂')
axs[0].set_ylabel('Angle (rad)')
axs[0].legend()
axs[0].grid()

w1, = axs[1].plot(sol.t, sol.y[1], label='ω₁')
w2, = axs[1].plot(sol.t, sol.y[3], label='ω₂')
axs[1].set_ylabel('Angular V (rad/s)')
axs[1].legend()
axs[1].grid()

freq_text = axs[2].text(0.1, 0.5, '', fontsize=12)
axs[2].axis('off')

axcolor = 'lightgoldenrodyellow'
ax_k = plt.axes([0.25, 0.45, 0.65, 0.03], facecolor=axcolor)
ax_beta = plt.axes([0.25, 0.4, 0.65, 0.03], facecolor=axcolor)

s_k = Slider(ax_k, 'k', 0.1, 2.0, valinit=params['k'])
s_beta = Slider(ax_beta, 'beta', 0.0, 0.2, valinit=params['beta'])

ax_m = plt.axes([0.25, 0.35, 0.1, 0.03])
ax_L = plt.axes([0.45, 0.35, 0.1, 0.03])
ax_L1 = plt.axes([0.65, 0.35, 0.1, 0.03])
text_m = TextBox(ax_m, 'm (kg)', initial=str(params['m']))
text_L = TextBox(ax_L, 'L (m)', initial=str(params['L']))
text_L1 = TextBox(ax_L1, 'L1 (m)', initial=str(params['L1']))

ax_phi1 = plt.axes([0.25, 0.3, 0.1, 0.03])
ax_phi2 = plt.axes([0.45, 0.3, 0.1, 0.03])
text_phi1 = TextBox(ax_phi1, 'ϕ₁(0) (rad)', initial="0.1")
text_phi2 = TextBox(ax_phi2, 'ϕ₂(0) (rad)', initial="0.0")

def update(val):
    try:
        m = float(text_m.text)
        L = float(text_L.text)
        L1 = float(text_L1.text)
        k = s_k.val
        beta = s_beta.val
        phi1_0 = float(text_phi1.text)
        phi2_0 = float(text_phi2.text)
        if (abs(phi1_0) > 1 or abs(phi2_0) > 1 or m <= 0 or m >= 10000 or L <= 0 or L >= 10000 or L1 <= 0 or L1 >= 10000):
            return

        new_sol = solve_system(m, L, params['g'], k, L1, beta, phi1_0, phi2_0)
        
        l1.set_xdata(new_sol.t)
        l1.set_ydata(new_sol.y[0])
        l2.set_xdata(new_sol.t)
        l2.set_ydata(new_sol.y[2])
        w1.set_xdata(new_sol.t)
        w1.set_ydata(new_sol.y[1])
        w2.set_xdata(new_sol.t)
        w2.set_ydata(new_sol.y[3])
        
        for ax in axs[:2]:
            ax.relim()
            ax.autoscale_view()

        freqs = compute_normal_frequencies(m, L, params['g'], k, L1)
        freq_text.set_text(f'Normal freq: {freqs[0]:.2f} rad/s, {freqs[1]:.2f} rad/s')

        fig.canvas.draw_idle()
    except ValueError:
        pass


s_k.on_changed(update)
s_beta.on_changed(update)
text_m.on_submit(update)
text_L.on_submit(update)
text_L1.on_submit(update)
text_phi1.on_submit(update)
text_phi2.on_submit(update)

resetax = plt.axes([0.8, 0.05, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')
def reset(event):
    s_k.reset()
    s_beta.reset()
    text_m.set_val(str(params['m']))
    text_L.set_val(str(params['L']))
    text_L1.set_val(str(params['L1']))
    text_phi1.set_val("0.1")
    text_phi2.set_val("0.0")
    update(None)
button.on_clicked(reset)

plt.show()
