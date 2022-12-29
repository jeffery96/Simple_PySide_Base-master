################################################################################
##
## BY: WANDERSON M.PIMENTA
## PROJECT MADE WITH: Qt Designer and PySide2
## V: 1.0.0
##
## This project can be used freely for all uses, as long as they maintain the
## respective credits only in the Python scripts, any information in the visual
## interface (GUI) can be modified without any implication.
##
## There are limitations on Qt licenses if you want to use your products
## commercially, I recommend reading them on the official website:
## https://doc.qt.io/qtforpython/licenses.html
##
################################################################################
## ==> GUI FILE
import time

from main import *
from zlgcan import *
import json
import threading
from PySide2.QtCore import Signal, QObject

MAX_DISPLAY     = 1000
MAX_RCV_NUM     = 10

USBCANFD_TYPE    = (41, 42, 43)
USBCAN_XE_U_TYPE = (20, 21, 31)
USBCAN_I_II_TYPE = (3, 4)


class MySignal(QObject):
    TableUpdate = Signal(str, str, str, str)

class CAN_Device(ZCAN):
    signaltest = Signal()

    def __init__(self, mainwindow):
        super().__init__()
        self.mw = mainwindow    # type: MainWindow
        self._dev_info = None

        with open("./dev_info.json", "r") as fd:
            self._dev_info = json.load(fd)
        if self._dev_info is None:
            print("device info no exist!")
            return

        self.DeviceInit()

        self.ms = MySignal()
        self.ms.TableUpdate.connect(self.TableUpdateFunc)


    def DeviceInit(self):
        self._zcan       = ZCAN()
        self._dev_handle = INVALID_DEVICE_HANDLE
        self._can_handle = INVALID_CHANNEL_HANDLE
        self._can_handle_dict = {}

        self._isOpen = False
        self._isChnOpen = False

        #current device info
        self._is_canfd = False
        self._res_support = False

        #Transmit and receive count display
        self._tx_cnt = 0
        self._rx_cnt = 0
        self._view_cnt = 0

        #read can/canfd message thread
        self._read_thread = None
        self._terminated = False
        # self._lock = threading.RLock()

        #period send var
        self._is_sending   = False
        self._id_increase  = False
        self._send_num     = 1
        self._send_cnt     = 1
        self._is_canfd_msg = False
        self._send_msgs    = None
        self._send_thread  = None

    def BtnOpenDev_Click(self):
        if self._isOpen:
            # 如果设备已打开则关闭设备
            for can_channel in self._can_handle_dict.keys():
                self._zcan.ResetCAN(can_channel)
                print(f'通道{can_channel}关闭')
                # self.btnCANCtrl.invoke()

            # Close Device，关闭设备
            self._zcan.CloseDevice(self._dev_handle)

            # self.strvDevCtrl.set("打开")
            self.mw.ui.OpenDevice_Btn.setText('打开设备')
            self.mw.ui.DeviceType_cbb.setEnabled(True)
            self.mw.ui.DeviceIndex_cbb.setEnabled(True)
            self.mw.ui.Baud_cbb.setEnabled(True)
            self.mw.ui.CanChannel_cbb.setEnabled(True)
            # self.cmbDevType["state"] = "readonly"
            # self.cmbDevIdx["state"] = "readonly"
            self._isOpen = False
        else:

            self._cur_dev_info = self._dev_info[self.mw.ui.DeviceType_cbb.currentText()]

            # Open Device
            self._dev_handle = self._zcan.OpenDevice(self._cur_dev_info["dev_type"],
                                                     self.mw.ui.DeviceIndex_cbb.currentIndex(), 0)
            if self._dev_handle == INVALID_DEVICE_HANDLE:
                # Open failed
                # messagebox.showerror(title="打开设备", message="打开设备失败！")
                # QMessageBox.information(parent=self.mw, title='aaa', text="打开设备失败！", button0=QMessageBox.Ok)
                QMessageBox.information(self.mw, '打开设备失败', '1、请检查CAN卡索引或CAN通道是否正确\n2、检查是否其他软件占用CAN卡\n3、请检查CAN卡是否接上', QMessageBox.Ok)
                return

            # Initial channel
            chn_cfg = ZCAN_CHANNEL_INIT_CONFIG()
            chn_cfg.can_type = ZCAN_TYPE_CAN
            # 0表示正常模式，能收能发
            chn_cfg.config.can.mode = 0

            brt = self._cur_dev_info["chn_info"]["baudrate"][self.mw.ui.Baud_cbb.currentText()]
            chn_cfg.config.can.timing0 = brt["timing0"]
            chn_cfg.config.can.timing1 = brt["timing1"]
            chn_cfg.config.can.acc_code = 0
            chn_cfg.config.can.acc_mask = 0xFFFFFFFF

            can_index = self.mw.ui.CanChannel_cbb.currentIndex()
            if can_index == 0 or can_index == 1:
                self._can_handle = self._zcan.InitCAN(self._dev_handle, can_index, chn_cfg)
                self._can_handle_dict[can_index] = self._can_handle
                print('通道0或1初始化成功')
            else:
                self._can_handle = self._zcan.InitCAN(self._dev_handle, 0, chn_cfg)
                self._can_handle_dict[0] = self._can_handle
                self._can_handle = self._zcan.InitCAN(self._dev_handle, 1, chn_cfg)
                self._can_handle_dict[1] = self._can_handle
                print('通道0和1初始化成功')

            for can_handle in self._can_handle_dict.values():
                if self._can_handle == INVALID_CHANNEL_HANDLE:
                    # messagebox.showerror(title="打开通道", message="初始化通道失败!")
                    QMessageBox.information(self.mw, f'CAN{can_handle}通道初始化失败',
                                            f'CAN{can_handle}通道初始化失败，请重试！',
                                            QMessageBox.Ok)
                    return

                ret = self._zcan.StartCAN(can_handle)
                if ret != ZCAN_STATUS_OK:
                    # messagebox.showerror(title="打开通道", message="打开通道失败!")
                    QMessageBox.information(self.mw, f'CAN{can_handle}通道打开失败',
                                            f'CAN{can_handle}通道打开失败，请重试！',
                                            QMessageBox.Ok)
                    return

            # self.strvDevCtrl.set("关闭")
            self.mw.ui.OpenDevice_Btn.setText('关闭设备')
            self.mw.ui.DeviceType_cbb.setEnabled(False)
            self.mw.ui.DeviceIndex_cbb.setEnabled(False)
            self.mw.ui.Baud_cbb.setEnabled(False)
            self.mw.ui.CanChannel_cbb.setEnabled(False)

            # 报文接收线程
            self._read_thread = threading.Thread(None, target=self.CanRecvThreadFunc)
            self._read_thread.start()

            self._isOpen = True

    def BtnCanTrans_Click(self):
        print('点击发送')
        msg = ZCAN_Transmit_Data()
        msg.transmit_type = 2
        msg.frame.can_id = 0x18ffe6a5
        msg.frame.rtr = 0
        msg.frame.eff = 1
        msg.frame.can_dlc = 8
        msg.frame.data = (
            0x01,
            0x02,
            0x03,
            0x04,
            0x05,
            0x06,
            0x07,
            0x08,
        )
        ret = self._zcan.Transmit(self._can_handle_dict[0], msg, 1)
        # print(f'发送成功报文数:{ret}')
        pass

    def CanRecvThreadFunc(self):
        while True:
            if self._isOpen:
                can_num = self._zcan.GetReceiveNum(self._can_handle, ZCAN_TYPE_CAN)
                if not can_num:
                    time.sleep(0.005) #wait 5ms
                    continue

                read_cnt = MAX_RCV_NUM if can_num >= MAX_RCV_NUM else can_num
                can_msgs, act_num = self._zcan.Receive(self._can_handle, read_cnt, MAX_RCV_NUM)
                # print(f'接收成功报文数:{act_num}')
                print('收到报文内容:')
                msg = can_msgs[0].frame.data
                for d in msg:
                    print(d)

                self.CanDisplay(can_msgs[0].frame)
        pass

    def CanDisplay(self, frame):
        # id_col = 0
        # dir_col = 1
        # len_col = 2
        # data_col = 3
        id = hex(frame.can_id)
        dir = 'rx'
        dlc = str(frame.can_dlc)
        data = ""
        for i in frame.data:
            data = data + str(i) + ' '

        # self.mw.ui.tableWidget.setItem(1, 0, QTableWidgetItem(hex(frame.can_id)))
        # self.mw.ui.tableWidget.setItem(1, 1, QTableWidgetItem('rx'))
        # self.mw.ui.tableWidget.setItem(1, 2, QTableWidgetItem(str(frame.can_dlc)))
        # data = ""
        # for i in frame.data:
        #     data = data + str(i) + ' '
        # self.mw.ui.tableWidget.setItem(1, 3, QTableWidgetItem(data))
        self.ms.TableUpdate.emit(id, dir, dlc, data)

    def TableUpdateFunc(self, s0, s1, s2, s3):
        table_row_cnt = self.mw.ui.tableWidget.rowCount()
        self.mw.ui.tableWidget.insertRow(table_row_cnt)
        self.mw.ui.tableWidget.setItem(table_row_cnt, 0, QTableWidgetItem(s0))
        self.mw.ui.tableWidget.setItem(table_row_cnt, 1, QTableWidgetItem(s1))
        self.mw.ui.tableWidget.setItem(table_row_cnt, 2, QTableWidgetItem(s2))
        self.mw.ui.tableWidget.setItem(table_row_cnt, 3, QTableWidgetItem(s3))


class Functions(MainWindow):

    @staticmethod
    def print_some():
        print("设备打开")
    pass
