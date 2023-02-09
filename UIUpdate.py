from PySide2.QtCore import Qt, QObject, Signal
from PySide2.QtWidgets import QTableWidgetItem
from zlgcan import ZCAN_CAN_FRAME
from main import *

class UIUpdate(QObject):

    glb_signal = Signal([ZCAN_CAN_FRAME])
    TableUpdateSignal = Signal(str, str, str, str, str)

    def __init__(self, mainwindow):
        super().__init__()
        self.mw = mainwindow  # type: MainWindow
        self.TableUpdateSignal.connect(self.TableUpdateFunc)
        self.glb_signal.connect(self.PlainTextShow)

    def TableUpdateFunc(self, s0, s1, s2, s3, s4):
        table_row_cnt = self.mw.ui.MsgShow_tblw.rowCount()
        self.mw.ui.MsgShow_tblw.insertRow(table_row_cnt)
        # 序号
        item = QTableWidgetItem(str(table_row_cnt + 1))
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mw.ui.MsgShow_tblw.setItem(table_row_cnt, 0, item)
        # 时间
        item = QTableWidgetItem(s0)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mw.ui.MsgShow_tblw.setItem(table_row_cnt, 1, item)
        # ID
        item = QTableWidgetItem(s1)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mw.ui.MsgShow_tblw.setItem(table_row_cnt, 2, item)
        # 方向
        item = QTableWidgetItem(s2)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mw.ui.MsgShow_tblw.setItem(table_row_cnt, 3, item)
        # 长度
        item = QTableWidgetItem(s3)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mw.ui.MsgShow_tblw.setItem(table_row_cnt, 4, item)

        self.mw.ui.MsgShow_tblw.setItem(table_row_cnt, 5, QTableWidgetItem(s4))
        self.mw.ui.MsgShow_tblw.scrollToBottom()

    def PlainTextShow(self):
        self.mw.ui.plainTextEdit_2.appendPlainText('收到报文')
