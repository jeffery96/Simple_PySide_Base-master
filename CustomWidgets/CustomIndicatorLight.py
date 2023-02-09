from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from math import *
import sys

class GaugePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("GaugePanel")
        self.setMinimumWidth(150)
        self.setMinimumHeight(150)

        self.testTimer = QTimer()
        self.testTimer.timeout.connect(self.testTimer_timeout_handle)

        self._sampleTime = 10
        self._startAngle = 135  # 以QPainter坐标方向为准,建议画个草图看看
        self._endAngle = 45  # 以以QPainter坐标方向为准
        self._scaleMainNum = 5  # 主刻度数
        self._scaleSubNum = 14  # 主刻度被分割份数
        self._minValue = 0
        self._maxValue = 14000
        self._title = '×1000rpm'
        self._value = 0
        self._valueSubTitle = 'rpm'
        self._minRadio = 100  # 缩小比例,用于计算刻度数字
        self._decimals = 0  # 小数位数

        self.timer = QTimer()  # 窗口重绘定时器
        self.timer.timeout.connect(self.update)
        self.timer.start(self._sampleTime)

    def testTimer_timeout_handle(self):
        self._value = self._value + 1
        if self._value > self._maxValue:
            self._value = self._minValue

    def setScaleMainNum(self, scale):
        # 设置主刻度分割份数
        self._scaleMainNum = scale

    def setScaleSubNum(self, scale):
        # 设置子刻度分割份数
        self._scaleSubNum = scale

    def setTestTimer(self, flag):
        if flag is True:
            self.testTimer.start(10)
        else:
            self.testTimer.stop()

    def setSampleTime(self, sampleTime):
        # 设置控件UI刷新时间
        self._sampleTime = sampleTime

    def setMinMaxValue(self, min, max):
        # 设置仪表盘上下限值
        self._minValue = min
        self._maxValue = max

    def setTitle(self, title):
        # 设置表盘上方标题
        self._title = title

    def setValue(self, value):
        # 设置当前值
        self._value = value

    def setValueSubTitle(self, title):
        # 设置数显下方标题
        self._valueSubTitle = title

    def setMinRadio(self, minRadio):
        # 设置数值缩小比例
        self._minRadio = minRadio

    def setDecimals(self, decimals):
        # 设置小数位数
        self._decimals = decimals

    def paintEvent(self, event):
        side = min(self.width(), self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)    # 抗锯齿
        painter.translate(
            self.width() /
            2,
            self.height() /
            2)  # painter坐标系原点移至widget中央
        # 缩放painterwidget坐标系，使绘制的时钟位于widge中央,即钟表支持缩放
        painter.scale(side / 200, side / 200)
        self.drawPanel(painter)  # 画外框表盘
        self.drawScaleNum(painter)  # 画刻度数字
        self.drawScaleLine(painter)  # 画刻度线
        self.drawTitle(painter)  # 画标题备注
        self.drawValue(painter)  # 画数显
        self.drawIndicator(painter)  # 画指针

    def drawPanel(self, p):
        p.save()
        radius = 100
        # lg = QLinearGradient(-radius, -radius, radius, radius)
        lg = QLinearGradient(0, radius, 0, -radius)
        lg.setColorAt(0, Qt.white)
        lg.setColorAt(1, QColor(255, 240, 200))
        p.setBrush(lg)
        p.setPen(Qt.NoPen)

        cg = QConicalGradient(0, 0, -90)
        cg.setColorAt(0.125, QColor(125, 255, 115))
        cg.setColorAt(0.875, QColor(0, 185, 255))
        p.setBrush(cg)

        path1 = QPainterPath()
        path2 = QPainterPath()
        path3 = QPainterPath()

        rect1 = QRectF(-radius, -radius, radius * 2, radius * 2)

        radius = 100 + 0.001
        rect2 = QRectF(-radius, -radius, radius * 2, radius * 2)
        radius = 100 * 0.85
        rect3 = QRectF(-radius, -radius, radius * 2, radius * 2)

        path1.arcMoveTo(rect1, -45)
        path1.arcTo(rect1, -45, 270)
        path1.closeSubpath()
        # path2.arcMoveTo(rect1, -45)
        path2.arcTo(rect2, -45, -90)
        path2.closeSubpath()
        path3.arcMoveTo(rect3, 0)
        path3.arcTo(rect3, 0, 360)
        path1 = path1.subtracted(path2).subtracted(path3)

        p.drawPath(path1)

        p.restore()

    def drawScaleNum(self, p):
        p.save()
        p.setPen(Qt.white)
        startRad = self._startAngle * (3.14 / 180)
        stepRad = (360 - (self._startAngle - self._endAngle)) * \
            (3.14 / 180) / self._scaleMainNum

        p.setFont(QFont("Berlin Sans FB", 8))
        fm = QFontMetricsF(p.font())
        for i in range(0, self._scaleMainNum + 1):
            sina = sin(startRad + i * stepRad)
            cosa = cos(startRad + i * stepRad)

            tmpVal = i * ((self._maxValue - self._minValue) /
                          self._scaleMainNum) + self._minValue
            tmpVal = tmpVal / self._minRadio
            s = '{:.0f}'.format(tmpVal)
            w = fm.size(Qt.TextSingleLine, s).width()
            h = fm.size(Qt.TextSingleLine, s).height()
            x = 65 * cosa - w / 2
            y = 65 * sina - h / 2
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

            if i % self._scaleSubNum == 0:
                pen.setWidth(2)
                p.setPen(pen)
                p.drawLine(74, 0, 82, 0)
            else:
                pen.setWidth(1)
                p.setPen(pen)
                p.drawLine(77, 0, 82, 0)
            p.rotate(angleStep)

        p.restore()

    def drawTitle(self, p):
        p.save()
        p.setPen(Qt.white)
        p.setFont(QFont("Berlin Sans FB", 6))
        fm = QFontMetrics(p.font())
        w = fm.size(Qt.TextSingleLine, self._title).width()
        p.drawText(-w / 2, -40, self._title)
        p.restore()

    def drawValue(self, p):
        p.save()
        if self._value > (0.8 * (self._maxValue - self._minValue)):
            p.setPen(Qt.red)
        else:
            p.setPen(Qt.white)

        p.setFont(QFont("Bahnschrift Light Condensed", 16))
        fm = QFontMetricsF(p.font())
        s = str(self._value)
        w = fm.size(Qt.TextSingleLine, s).width()
        h = fm.size(Qt.TextSingleLine, s).height()
        p.drawText(QRectF(-w / 2, 25, w, h), s)

        p.setPen(Qt.white)
        p.drawLine(QPoint(-w / 2, 25 + h), QPoint(w / 2, 25 + h))

        p.setFont(QFont("Bahnschrift Light Condensed", 10))
        fm = QFontMetricsF(p.font())
        s = self._valueSubTitle
        w = fm.size(Qt.TextSingleLine, s).width()
        h = fm.size(Qt.TextSingleLine, s).height()
        p.drawText(QRectF(-w / 2, 55, w, h), s)

    def drawIndicator(self, p):
        p.save()

        polygon = QPolygon([QPoint(0, -5), QPoint(0, 5),
                           QPoint(60, 2), QPoint(60, -2)])
        degRotate = self._startAngle + (360 - (self._startAngle - self._endAngle)) / (
            self._maxValue - self._minValue) * (self._value - self._minValue)
        # 画指针
        p.rotate(degRotate)
        halogd = QRadialGradient(0, 0, 60, 0, 0)
        if degRotate > (135 + 270 * 0.8):
            halogd.setColorAt(0, QColor(255, 0, 0, 0))
            halogd.setColorAt(1, QColor(255, 0, 0, 255))
        else:
            halogd.setColorAt(0, QColor(255, 255, 255, 0))
            halogd.setColorAt(1, QColor(255, 255, 255, 255))
        p.setPen(Qt.NoPen)
        p.setBrush(halogd)
        p.drawConvexPolygon(polygon)
        p.restore()
