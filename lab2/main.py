# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


# window class
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_plane = True
        self.is_missile = False

        toolbar = QToolBar("My main toolbar")

        missile_icon = QIcon("img/missile.png")
        missile_button = QToolButton()
        missile_button.setIcon(missile_icon)

        plane_icon = QIcon("img/plane.png")
        plane_button = QToolButton()
        plane_button.setIcon(plane_icon)

        eraser_icon = QIcon("img/eraser.png")
        eraser_button = QToolButton()
        eraser_button.setIcon(eraser_icon)

        start_icon = QIcon("img/start.png")
        start_button = QToolButton()
        start_button.setIcon(start_icon)

        missile_button.clicked.connect(self.missile_draw)
        plane_button.clicked.connect(self.plane_draw)
        eraser_button.clicked.connect(self.clear)

        toolbar.addWidget(missile_button)
        toolbar.addWidget(plane_button)
        toolbar.addWidget(eraser_button)
        toolbar.addWidget(start_button)

        self.addToolBar(toolbar)

        # setting title
        self.setWindowTitle("Paint with PyQt5")

        # setting geometry to main window
        self.setGeometry(100, 100, 800, 600)

        # creating image object
        self.image = QImage(self.size(), QImage.Format_RGB32)

        # making image color to white
        self.image.fill(Qt.white)

        # variables
        # drawing flag
        self.drawing = False
        # default brush size
        self.brushSize = 2
        # default color
        self.brushColor = Qt.black

        # QPoint object to tract the point
        self.lastPoint = QPoint()


    def plane_draw(self):
        self.is_plane = True
        self.is_missile = False

    def missile_draw(self):
        self.is_plane = False
        self.is_missile = True

    # method for checking mouse cicks
    def mousePressEvent(self, event):

        # if left mouse button is pressed
        if event.button() == Qt.LeftButton:

            if self.is_plane:
                if self.drawing:
                    cur_pos = event.pos()
                    print("CUR: ", cur_pos)
                    self.drawLine(cur_pos)
                else:
                    # make drawing flag true
                    self.drawing = True
                    # make last point to the point of cursor
                    self.lastPoint = event.pos()
                    print("LAST: ", self.lastPoint)

            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, 12,
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPoint(event.pos())
            self.update()

    # method for tracking mouse activity
    def mouseMoveEvent(self, event):

        # checking if left button is pressed and drawing flag is true
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            return

    # method for mouse left button release
    def drawLine(self, cur_pos):
        # make drawing flag false
        self.drawing = False

        # creating painter object
        painter = QPainter(self.image)

        # set the pen of the painter
        painter.setPen(QPen(self.brushColor, self.brushSize,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        # draw line from the last point of cursor to the current point
        # this will draw only one step
        painter.drawLine(self.lastPoint, cur_pos)

        self.update()

    # paint event
    def paintEvent(self, event):
        # create a canvas
        canvasPainter = QPainter(self)

        # draw rectangle  on the canvas
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

    # method for saving canvas
    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        if filePath == "":
            return
        self.image.save(filePath)

    # method for clearing every thing on canvas
    def clear(self):
        # make the whole canvas white
        self.image.fill(Qt.white)
        # update
        self.update()


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# showing the window
window.show()

# start the app
sys.exit(App.exec())
