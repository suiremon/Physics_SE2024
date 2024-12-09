import numpy as np
from pathlib import Path
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from shiny.express import input, render, ui
import numpy as np
here = Path(__file__).parent

def circle(a, b, r):
    T = 200
    x, y = [0]*T, [0]*T
    for i,theta in enumerate(np.linspace(0,2*np.pi,T)):
        x[i] = a + r*np.cos(theta)
        y[i] = b + r*np.sin(theta)
    return x, y
def colors():
    return [random.randint(0, 100)/100,random.randint(0, 100)/100,random.randint(0, 100)/100]


    
ui.input_text("R", label="Введите радиус:")
ui.input_text("V", label="Введите скорость:")

with ui.card(full_screen=True):
    gig = [colors(),colors(),colors(),colors()]
    @render.plot
    def plot():
        V = input.V()
        R = input.R()
        if (V != "" and R != ""):
            V = int(V)
            R = float(R)
        else:
            return
        steps = int(np.ceil(5*V / (2*np.pi*R)))
        thetas = np.linspace(0, steps*2*np.pi, 100)
        
        cycloid_x = R*(thetas-np.sin(thetas))
        cycloid_y = R*(1-np.cos(thetas))
        cycloid_c = R*thetas
        fig = plt.figure()

        lns = []
        trans = plt.axes().transAxes
        for i in range(0, 100):
            x,y = circle(cycloid_c[i], R, R)
            ln1, = plt.plot(x, y, color=gig[0])
            ln2, = plt.plot(cycloid_x[:i+1] ,cycloid_y[:i+1], color=gig[1], lw=2)
            ln3, = plt.plot(cycloid_x[i], cycloid_y[i], color=gig[2])
            ln4, = plt.plot([cycloid_c[i], cycloid_x[i]], [R,cycloid_y[i]], color=gig[3], lw=1)
            lns.append([ln1,ln2,ln3,ln4])
        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid()
        plt.gca().set_aspect(aspect="equal", adjustable="datalim")
        ani = animation.ArtistAnimation(fig, lns, interval=50, blit=True)
        #ani.save(f'anim{V}_{R}.gif', fps=80)
        return plt.show()
    
