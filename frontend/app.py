from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QGridLayout
from PyQt6.QtCore import QPointF, QRectF, QLineF, Qt
from PyQt6.QtGui import QPainter, QColor
from enum import Enum
# Only needed for access to command line arguments
import sys

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    CENTER = 4  # when joystick is not moved

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Abstain Base Station")
        joystick = Joystick()
        hstick = HorizontalJoystick()

        layout = QGridLayout()

        layout.addWidget(joystick, 0, 0)
        layout.addWidget(hstick, 1, 0)

        self.setMinimumSize(400,300)

        widget = QWidget()
        widget.setLayout(layout)



        # Set the central widget of the Window.
        self.setCentralWidget(widget)

class Joystick(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(100, 100)
        self.__maxDistance = 50
        self.knobPos = QPointF(0, 0)
        self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        center = self.center()
        # Draw base
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(QColor(220, 220, 220))
        baseRect = QRectF(-self.__maxDistance, -self.__maxDistance,
                          self.__maxDistance * 2, self.__maxDistance * 2).translated(center)
        painter.drawEllipse(baseRect)
        # Draw knob
        painter.setBrush(Qt.GlobalColor.black)
        knobRect = QRectF(-15, -15, 30, 30).translated(center + self.knobPos)
        painter.drawEllipse(knobRect)

    def center(self):
        return QPointF(self.width() / 2, self.height() / 2)

    def mousePressEvent(self, event):
        center = self.center()
        knobRect = QRectF(-15, -15, 30, 30).translated(center + self.knobPos)
        if knobRect.contains(event.position()):
            self.dragging = True

    def mouseMoveEvent(self, event):
        if self.dragging:
            center = self.center()
            delta = event.position() - center
            # Limit movement to max distance
            line = QLineF(QPointF(0, 0), delta)
            if line.length() > self.__maxDistance:
                line.setLength(self.__maxDistance)
            self.knobPos = line.p2()
            self.update()
            print(self.getDirection())

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.knobPos = QPointF(0, 0)
        self.update()

    def getDirection(self):
        # Returns tuple: (Direction, normalized distance 0-1)
        if self.knobPos == QPointF(0, 0):
            return (Direction.CENTER, 0.0)
        angle = QLineF(QPointF(0, 0), self.knobPos).angle()
        distance = min(QLineF(QPointF(0, 0), self.knobPos).length() / self.__maxDistance, 1.0)
        # Angle in PyQt6: 0 is east, counter-clockwise
        if 45 <= angle < 135:
            return (Direction.UP, distance)
        elif 135 <= angle < 225:
            return (Direction.LEFT, distance)
        elif 225 <= angle < 315:
            return (Direction.DOWN, distance)
        return (Direction.RIGHT, distance)

class HorizontalJoystick(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 60)  # wider than tall
        self.__maxDistance = 80  # horizontal range
        self.knobX = 0.0  # horizontal offset from center
        self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        center = self.center()
        # Draw base line
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(QColor(220, 220, 220))
        baseRect = QRectF(-self.__maxDistance, -10, self.__maxDistance * 2, 20).translated(center)
        painter.drawRoundedRect(baseRect, 10, 10)
        # Draw knob
        painter.setBrush(Qt.GlobalColor.black)
        knobRect = QRectF(-15, -20, 30, 40).translated(center + QPointF(self.knobX, 0))
        painter.drawEllipse(knobRect)

    def center(self):
        return QPointF(self.width() / 2, self.height() / 2)

    def mousePressEvent(self, event):
        center = self.center()
        knobRect = QRectF(-15, -20, 30, 40).translated(center + QPointF(self.knobX, 0))
        if knobRect.contains(event.position()):
            self.dragging = True

    def mouseMoveEvent(self, event):
        if self.dragging:
            centerX = self.center().x()
            x = event.position().x() - centerX
            # Clamp to range
            self.knobX = max(-self.__maxDistance, min(self.__maxDistance, x))
            self.update()
            print("Value:", self.value())  # debug output

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.knobX = 0.0  # snap back to center
        self.update()

    def value(self):
        # Return normalized horizontal value: -1.0 (left) -> 1.0 (right)
        return self.knobX / self.__maxDistance

app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()

