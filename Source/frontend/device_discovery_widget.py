from math import ceil

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Source: https://stackoverflow.com/a/48443775/10334793
class Spinner(QWidget):
    mColor = QColor(Qt.gray)
    mRoundness = 100.0
    mMinimumTrailOpacity = 31.4159265358979323846
    mTrailFadePercentage = 50.0
    mRevolutionsPerSecond = 1.57079632679489661923
    mNumberOfLines = 20
    mLineLength = 10
    mLineWidth = 2
    mInnerRadius = 20
    mCurrentCounter = 0
    mIsSpinning = False

    def __init__(self, centerOnParent=True, disableParentWhenSpinning=True, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.mCenterOnParent = centerOnParent
        self.mDisableParentWhenSpinning = disableParentWhenSpinning
        self.initialize()

    def initialize(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.updateSize()
        self.updateTimer()
        self.hide()

    @pyqtSlot()
    def rotate(self):
        self.mCurrentCounter += 1
        if self.mCurrentCounter > self.numberOfLines():
            self.mCurrentCounter = 0
        self.update()

    def updateSize(self):
        size = (self.mInnerRadius + self.mLineLength) * 2
        self.setFixedSize(size, size)

    def updateTimer(self):
        interval = int(1000 / (self.mNumberOfLines * self.mRevolutionsPerSecond))
        self.timer.setInterval(interval)

    def updatePosition(self):
        if self.parentWidget() and self.mCenterOnParent:
            parent_width = self.parentWidget().width()
            parent_height = self.parentWidget().height()
            self.move(int(parent_width / 2 - self.width() / 2),
                    int(parent_height / 2 - self.height() / 2))

    def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
        distance = primary - current
        if distance < 0:
            distance += totalNrOfLines
        return distance

    def currentLineColor(self, countDistance, totalNrOfLines, trailFadePerc, minOpacity, color):
        if countDistance == 0:
            return color

        minAlphaF = minOpacity / 100.0

        distanceThreshold = ceil((totalNrOfLines - 1) * trailFadePerc / 100.0)
        if countDistance > distanceThreshold:
            color.setAlphaF(minAlphaF)

        else:
            alphaDiff = self.mColor.alphaF() - minAlphaF
            gradient = alphaDiff / distanceThreshold + 1.0
            resultAlpha = color.alphaF() - gradient * countDistance
            resultAlpha = min(1.0, max(0.0, resultAlpha))
            color.setAlphaF(resultAlpha)
        return color

    def paintEvent(self, event):
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)
        if self.mCurrentCounter > self.mNumberOfLines:
            self.mCurrentCounter = 0
        painter.setPen(Qt.NoPen)

        for i in range(self.mNumberOfLines):
            painter.save()
            painter.translate(self.mInnerRadius + self.mLineLength,
                              self.mInnerRadius + self.mLineLength)
            rotateAngle = 360.0 * i / self.mNumberOfLines
            painter.rotate(rotateAngle)
            painter.translate(self.mInnerRadius, 0)
            distance = self.lineCountDistanceFromPrimary(i, self.mCurrentCounter,
                                                         self.mNumberOfLines)
            color = self.currentLineColor(distance, self.mNumberOfLines,
                                          self.mTrailFadePercentage, self.mMinimumTrailOpacity, self.mColor)
            painter.setBrush(color)
            painter.drawRoundedRect(QRect(0, -self.mLineWidth // 2, self.mLineLength, self.mLineLength),
                                    self.mRoundness, Qt.RelativeSize)
            painter.restore()

    def start(self):
        self.updatePosition()
        self.mIsSpinning = True
        self.show()

        if self.parentWidget() and self.mDisableParentWhenSpinning:
            self.parentWidget().setEnabled(False)

        if not self.timer.isActive():
            self.timer.start()
            self.mCurrentCounter = 0

    def stop(self):
        self.mIsSpinning = False
        self.hide()

        if self.parentWidget() and self.mDisableParentWhenSpinning:
            self.parentWidget().setEnabled(True)

        if self.timer.isActive():
            self.timer.stop()
            self.mCurrentCounter = 0

    def setNumberOfLines(self, lines):
        self.mNumberOfLines = lines
        self.updateTimer()

    def setLineLength(self, length):
        self.mLineLength = length
        self.updateSize()

    def setLineWidth(self, width):
        self.mLineWidth = width
        self.updateSize()

    def setInnerRadius(self, radius):
        self.mInnerRadius = radius
        self.updateSize()

    def color(self):
        return self.mColor

    def roundness(self):
        return self.mRoundness

    def minimumTrailOpacity(self):
        return self.mMinimumTrailOpacity

    def trailFadePercentage(self):
        return self.mTrailFadePercentage

    def revolutionsPersSecond(self):
        return self.mRevolutionsPerSecond

    def numberOfLines(self):
        return self.mNumberOfLines

    def lineLength(self):
        return self.mLineLength

    def lineWidth(self):
        return self.mLineWidth

    def innerRadius(self):
        return self.mInnerRadius

    def isSpinning(self):
        return self.mIsSpinning

    def setRoundness(self, roundness):
        self.mRoundness = min(0.0, max(100, roundness))

    def setColor(self, color):
        self.mColor = color

    def setRevolutionsPerSecond(self, revolutionsPerSecond):
        self.mRevolutionsPerSecond = revolutionsPerSecond
        self.updateTimer()

    def setTrailFadePercentage(self, trail):
        self.mTrailFadePercentage = trail

    def setMinimumTrailOpacity(self, minimumTrailOpacity):
        self.mMinimumTrailOpacity = minimumTrailOpacity


class DeviceDiscoveryWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__()

        self.layout = QVBoxLayout()

        self.label = QLabel("Ricerca dispositivo in corso")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.spinner = Spinner(self)
        self.spinner.start()
        self.layout.addWidget(self.spinner)

        self.button = QPushButton("Annulla")
        self.button.clicked.connect(self.ask_reject)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def ask_reject(self):
        reply = QMessageBox.question(self, "Conferma chiusura",
                                     "Sei sicuro di voler interrompere la ricerca?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cancel_search()

    def cancel_search(self):
        QMessageBox.information(self, "Ricerca dispositivo annullata", "La ricerca del dispositivo è stata annullata.")
        QApplication.exit()
