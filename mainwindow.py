import os
import functools
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
import matplotlib
import matplotlib.pyplot as plt
from skimage import io, color, img_as_float, img_as_ubyte

from ui_mainwindow import Ui_MainWindow
from ta_algorithm import *

matplotlib.use('qt5agg')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.img1 = None
        self.img2 = None

        self.canvas1 = FigureCanvasQTAgg(plt.figure())
        self.navToolbar1 = NavigationToolbar2QT(self.canvas1, self)
        self.ui.verticalLayout1.addWidget(self.navToolbar1)
        self.ui.verticalLayout1.addWidget(self.canvas1)
        self.canvas2 = FigureCanvasQTAgg(plt.figure())
        self.navToolbar2 = NavigationToolbar2QT(self.canvas2, self)
        self.ui.verticalLayout2.addWidget(self.navToolbar2)
        self.ui.verticalLayout2.addWidget(self.canvas2)

        self.connect()

    def connect(self):
        self.ui.actionOpen.triggered.connect(self.handleOpen)
        self.ui.actionSave.triggered.connect(self.handleSave)
        self.ui.actionPlane.triggered.connect(self.handlePlane)
        self.ui.actionEqualize.triggered.connect(self.handleEqualize)
        self.ui.actionDenoise.triggered.connect(self.handleDenoise)
        self.ui.actionInterpolate.triggered.connect(self.handleInterpolate)
        self.ui.actionDFT.triggered.connect(self.handleDFT)
        self.ui.actionButterworth.triggered.connect(self.handleButterworth)
        self.ui.actionCanny.triggered.connect(self.handleCanny)
        self.ui.actionMorphology.triggered.connect(self.handleMorphology)
        self.ui.actionHelp.triggered.connect(self.handleHelp)

    def draw(idx):
        assert idx == 1 or idx == 2

        def decorator(func):
            @functools.wraps(func)
            def wrapper(self):
                plt.figure(idx)
                if idx == 2 and self.img1 is None:
                    return
                func(self)
                if idx == 1 and self.img1 is not None:
                    plt.imshow(self.img1, cmap='gray' if self.img1.ndim == 2 else None)
                    self.canvas1.draw()
                elif idx == 2 and self.img2 is not None:
                    plt.imshow(self.img2, cmap='gray' if self.img2.ndim == 2 else None)
                    self.canvas2.draw()

            return wrapper

        return decorator

    def all2gray(self, img):
        return color.rgb2gray(img) if img.ndim == 3 else img

    @draw(1)
    def handleOpen(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, filter='Image Files(*.bmp *.jpg *.png *.tif)')[0]
        if os.path.exists(path):
            self.img1 = io.imread(path)
            if self.img1.ndim == 3 and self.img1.shape[-1] == 4:
                self.img1 = color.rgba2rgb(self.img1)
            self.img1 = img_as_float(self.img1)

    def handleSave(self):
        if self.img2 is None:
            return
        path = QtWidgets.QFileDialog.getSaveFileName(self, filter='Image Files(*.bmp *.jpg *.png *.tif)')[0]
        if os.path.exists(os.path.dirname(path)):
            io.imsave(path, img_as_ubyte(self.img2))

    @draw(2)
    def handlePlane(self):
        self.img2 = plane(img_as_ubyte(self.all2gray(self.img1)))

    @draw(2)
    def handleEqualize(self):
        self.img2 = equalize(self.img1)

    @draw(2)
    def handleDenoise(self):
        self.img2 = denoise(self.img1)

    @draw(2)
    def handleInterpolate(self):
        self.img2 = interpolate(self.img1)

    @draw(2)
    def handleDFT(self):
        self.img2 = dft(self.all2gray(self.img1))

    @draw(2)
    def handleButterworth(self):
        self.img2 = butterworth(self.all2gray(self.img1))

    @draw(2)
    def handleCanny(self):
        self.img2 = canny(self.all2gray(self.img1))

    @draw(2)
    def handleMorphology(self):
        self.img2 = morphology(self.all2gray(self.img1))

    def handleHelp(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/GeeeekExplorer/YAIPT"))
