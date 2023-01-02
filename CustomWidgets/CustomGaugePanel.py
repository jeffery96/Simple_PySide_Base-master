from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from math import *
import sys


class GaugePanel(QWidget):
    def __init__(self, parent=None):
        # super(GaugePanel, self).__init__()
        super().__init__(parent=parent)
        # self.setWindowTitle("测试")
        # self.resize(500, 500)

        self.setWindowTitle("GaugePanel")
        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        self.timer = QTimer()  # 窗口重绘定时器
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

        self.testTimer = QTimer()
        self.testTimer.timeout.connect(self.testTimer_timeout_handle)

        self.lcdDisplay = QLCDNumber(self)
        self.lcdDisplay.setDigitCount(4)
        self.lcdDisplay.setMode(QLCDNumber.Dec)
        self.lcdDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.lcdDisplay.setStyleSheet('border:2px solid green;color:green;background:silver')

        self._startAngle = 120  # 以QPainter坐标方向为准,建议画个草图看看
        self._endAngle = 60  # 以以QPainter坐标方向为准
        self._scaleMainNum = 10  # 主刻度数
        self._scaleSubNum = 10  # 主刻度被分割份数
        self._minValue = 0
        self._maxValue = 2000
        self._title = '×100rpm'
        self._value = 0
        self._minRadio = 100  # 缩小比例,用于计算刻度数字
        self._decimals = 0  # 小数位数


    def testTimer_timeout_handle(self):
        self._value = self._value + 1
        if self._value > self._maxValue:
            self._value = self._minValue


    def setTestTimer(self, flag):
        if flag is True:
            self.testTimer.start(10)
        else:
            self.testTimer.stop()


    def setMinMaxValue(self, min, max):
        self._minValue = min
        self._maxValue = max


    def setTitle(self, title):
        self._title = title


    def setValue(self, value):
        self._value = value


    def setMinRadio(self, minRadio):
        self._minRadio = minRadio


    def setDecimals(self, decimals):
        self._decimals = decimals


    def paintEvent(self, event):
        side = min(self.width(), self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)  # painter坐标系原点移至widget中央
        painter.scale(side / 200, side / 200)  # 缩放painterwidget坐标系，使绘制的时钟位于widge中央,即钟表支持缩放

        self.drawPanel(painter)  # 画外框表盘
        self.drawScaleNum(painter)  # 画刻度数字
        self.drawScaleLine(painter)  # 画刻度线
        self.drawTitle(painter)  # 画标题备注
        self.drawValue(painter)  # 画数显
        self.drawIndicator(painter)  # 画指针


    def drawPanel(self, p):
        p.save()
        radius = 100
        lg = QLinearGradient(-radius, -radius, radius, radius)
        lg.setColorAt(0, Qt.white)
        lg.setColorAt(1, Qt.black)
        p.setBrush(lg)
        p.setPen(Qt.NoPen)
        p.drawEllipse(-radius, -radius, radius * 2, radius * 2)

        p.setBrush(Qt.black)
        p.drawEllipse(-92, -92, 92 * 2, 92 * 2)
        p.restore()


    def drawScaleNum(self, p):
        p.save()
        p.setPen(Qt.white)
        startRad = self._startAngle * (3.14 / 180)
        stepRad = (360 - (self._startAngle - self._endAngle)) * (3.14 / 180) / self._scaleMainNum

        fm = QFontMetricsF(p.font())
        for i in range(0, self._scaleMainNum + 1):
            sina = sin(startRad + i * stepRad)
            cosa = cos(startRad + i * stepRad)

            tmpVal = i * ((self._maxValue - self._minValue) / self._scaleMainNum) + self._minValue
            tmpVal = tmpVal / self._minRadio
            s = '{:.0f}'.format(tmpVal)
            w = fm.size(Qt.TextSingleLine, s).width()
            h = fm.size(Qt.TextSingleLine, s).height()
            x = 80 * cosa - w / 2
            y = 80 * sina - h / 2
            p.drawText(QRectF(x, y, w, h), s)

        p.restore()


    def drawScaleLine(self, p):
        p.save()
        p.rotate(self._startAngle)
        scaleNums = self._scaleMainNum * self._scaleSubNum
        angleStep = (360 - (self._startAngle - self._endAngle)) / scaleNums
        p.setPen(Qt.white)

        pen = QPen(Qt.white)
        for i in range(0, scaleNums + 1):
            if i >= 0.8 * scaleNums:
                pen.setColor(Qt.red)

            if i % self._scaleMainNum == 0:
                pen.setWidth(2)
                p.setPen(pen)
                p.drawLine(64, 0, 72, 0)
            else:
                pen.setWidth(1)
                p.setPen(pen)
                p.drawLine(67, 0, 72, 0)
            p.rotate(angleStep)

        p.restore()


    def drawTitle(self, p):
        p.save()
        p.setPen(Qt.white)
        fm = QFontMetrics(p.font())
        w = fm.size(Qt.TextSingleLine, self._title).width()
        p.drawText(-w / 2, -45, self._title)
        p.restore()


    def drawValue(self, p):
        side = min(self.width(), self.height())
        w, h = side / 2 * 0.4, side / 2 * 0.2
        x, y = self.width() / 2 - w / 2, self.height() / 2 + side / 2 * 0.55
        self.lcdDisplay.setGeometry(x, y, w, h)

        ss = '{:.' + str(self._decimals) + 'f}'
        self.lcdDisplay.display(ss.format(self._value))


    def drawIndicator(self, p):
        p.save()
        polygon = QPolygon([QPoint(0, -2), QPoint(0, 2), QPoint(60, 0)])
        degRotate = self._startAngle + (360 - (self._startAngle - self._endAngle)) / (self._maxValue - self._minValue) * (
                    self._value - self._minValue)
        # 画指针
        p.rotate(degRotate)
        halogd = QRadialGradient(0, 0, 60, 0, 0)
        halogd.setColorAt(0, QColor(60, 60, 60))
        halogd.setColorAt(1, QColor(160, 160, 160))
        p.setPen(Qt.white)
        p.setBrush(halogd)
        p.drawConvexPolygon(polygon)
        p.restore()

        # 画中心点
        p.save()
        radGradient = QRadialGradient(0, 0, 10)
        radGradient = QConicalGradient(0, 0, -90)
        radGradient.setColorAt(0.0, Qt.darkGray)
        radGradient.setColorAt(0.5, Qt.white)
        radGradient.setColorAt(1.0, Qt.darkGray)
        p.setPen(Qt.NoPen)
        p.setBrush(radGradient)
        p.drawEllipse(-5, -5, 10, 10)
        p.restore()