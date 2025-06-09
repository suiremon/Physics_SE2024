import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def h(r, R):
    return r**2 / (2 * R)

def intensity_mono(r, lam, R):
    return 0.5 * (1 + np.cos(4 * np.pi * h(r, R) / lam))

def wavelength_to_rgb(wavelength):
    R = G = B = 0.0
    if 380 <= wavelength < 440:
        R = -(wavelength - 440) / (440 - 380)
        G = 0.0
        B = 1.0
    elif 440 <= wavelength < 490:
        R = 0.0
        G = (wavelength - 440) / (490 - 440)
        B = 1.0
    elif 490 <= wavelength < 510:
        R = 0.0
        G = 1.0
        B = -(wavelength - 510) / (510 - 490)
    elif 510 <= wavelength < 580:
        R = (wavelength - 510) / (580 - 510)
        G = 1.0
        B = 0.0
    elif 580 <= wavelength < 645:
        R = 1.0
        G = -(wavelength - 645) / (645 - 580)
        B = 0.0
    elif 645 <= wavelength <= 780:
        R = 1.0
        G = 0.0
        B = 0.0

    R = np.clip(R, 0, 1)
    G = np.clip(G, 0, 1)
    B = np.clip(B, 0, 1)
    return (R, G, B)

def spectral_weight(lam, lam_center, delta_lam):
    sigma = delta_lam / 2.355
    return np.exp(-0.5 * ((lam - lam_center) / sigma)**2)

def simulate_colored_image(R, size, pixel_size, lam_center=550e-9, delta_lam=0, n_lam=200):
    x = np.linspace(-size//2, size//2, size) * pixel_size
    y = np.linspace(-size//2, size//2, size) * pixel_size
    X, Y = np.meshgrid(x, y)
    r = np.sqrt(X**2 + Y**2)

    img = np.zeros((size, size, 3))

    if delta_lam == 0:
        I = intensity_mono(r, lam_center, R)
        color = wavelength_to_rgb(lam_center * 1e9)
        for i in range(3):
            img[:, :, i] = I * color[i]
    else:
        wavelengths = np.linspace(lam_center - delta_lam / 2 * 1e-9,
                                  lam_center + delta_lam / 2 * 1e-9,
                                  n_lam)
        weights = spectral_weight(wavelengths, lam_center, delta_lam * 1e-9)
        weights /= np.sum(weights)

        for lam, w in zip(wavelengths, weights):
            I = intensity_mono(r, lam, R)
            color = wavelength_to_rgb(lam * 1e9)
            for i in range(3):
                img[:, :, i] += w * I * color[i]

    img = np.clip(img, 0, None)
    max_val = np.max(img)
    if max_val > 0:
        img /= max_val

    return img, r[size//2, :], img[size//2, :, :]

class NewtonRingsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Newton's rings modeling")
        self.setMinimumSize(1000, 600)

        self.R = 1.0
        self.size = 400
        self.pixel_size = 5e-6
        self.lam_center = 550
        self.delta_lam = 0

        self.canvas = FigureCanvas(Figure(figsize=(10, 4)))
        self.ax_img = self.canvas.figure.add_subplot(1, 2, 1)
        self.ax_plot = self.canvas.figure.add_subplot(1, 2, 2)

        self.slider_lam = QSlider(Qt.Horizontal)
        self.slider_lam.setMinimum(380)
        self.slider_lam.setMaximum(780)
        self.slider_lam.setValue(self.lam_center)
        self.slider_lam.valueChanged.connect(self.update_plot)
        self.label_lam_val = QLabel(f"{self.lam_center} nm")

        self.slider_dl = QSlider(Qt.Horizontal)
        self.slider_dl.setMinimum(0)
        self.slider_dl.setMaximum(200)
        self.slider_dl.setValue(self.delta_lam)
        self.slider_dl.valueChanged.connect(self.update_plot)
        self.label_dl_val = QLabel(f"{self.delta_lam} nm")

        self.slider_R = QSlider(Qt.Horizontal)
        self.slider_R.setMinimum(1)
        self.slider_R.setMaximum(100)
        self.slider_R.setValue(int(self.R * 10))
        self.slider_R.valueChanged.connect(self.update_plot)
        self.label_R_val = QLabel(f"{self.R:.1f} m")

        self.combo_type = QComboBox()
        self.combo_type.addItems(["Monochromatic", "Quasi-monochromatic"])
        self.combo_type.currentIndexChanged.connect(self.update_plot)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        sliders_layout = QHBoxLayout()
        sliders_layout.addWidget(QLabel("λ₀ (nm):"))
        sliders_layout.addWidget(self.slider_lam)
        sliders_layout.addWidget(self.label_lam_val)

        sliders_layout.addWidget(QLabel("Δλ (nm):"))
        sliders_layout.addWidget(self.slider_dl)
        sliders_layout.addWidget(self.label_dl_val)

        sliders_layout.addWidget(QLabel("R (m):"))
        sliders_layout.addWidget(self.slider_R)
        sliders_layout.addWidget(self.label_R_val)

        sliders_layout.addWidget(QLabel("Light type:"))
        sliders_layout.addWidget(self.combo_type)


        layout.addLayout(sliders_layout)
        self.setLayout(layout)
        self.update_plot()

    def update_plot(self):
        self.lam_center = self.slider_lam.value()
        self.R = self.slider_R.value() / 10.0

        if self.combo_type.currentIndex() == 0:
            self.delta_lam = 0
            self.slider_dl.setValue(0)
        else:
            self.delta_lam = self.slider_dl.value()

        img, r_line, rgb_line = simulate_colored_image(
            self.R, self.size, self.pixel_size,
            lam_center=self.lam_center * 1e-9,
            delta_lam=self.delta_lam
        )

        self.ax_img.clear()
        extent = [-self.size/2 * self.pixel_size * 1e3,
                   self.size/2 * self.pixel_size * 1e3,
                  -self.size/2 * self.pixel_size * 1e3,
                   self.size/2 * self.pixel_size * 1e3]
        self.ax_img.imshow(img, extent=extent)
        self.ax_img.set_title(f"Newtons rings\nλ₀={self.lam_center} nm, Δλ={self.delta_lam} nm, R={self.R:.2f} m")
        self.ax_img.set_xlabel("mm")
        self.ax_img.set_ylabel("mm")

        self.ax_plot.clear()
        self.ax_plot.plot(r_line * 1e3, np.mean(rgb_line, axis=1))
        self.ax_plot.set_title("Intensity along the radius")
        self.ax_plot.set_xlabel("r (mm)")
        self.ax_plot.set_ylabel("Intensity")

        self.label_lam_val.setText(f"{self.lam_center} nm")
        self.label_dl_val.setText(f"{self.delta_lam} nm")
        self.label_R_val.setText(f"{self.R:.1f} m")


        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewtonRingsApp()
    window.show()
    sys.exit(app.exec_())
