import logging
import random
import sys
import socket
import errno
import struct
import threading
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QLine, QRect
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QLCDNumber, QProgressBar,
                             QFrame, )

logging.basicConfig(format="%(message)s", level=logging.INFO)

gears = {
    0: 'R', 1: '0', 2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9'
}
cars_data = {'unknown': {'RD': 0}, 'UF1': {'RD': 6983}, 'XFG': {'RD': 7979}, 'XRG': {'RD': 6981}, 'LX4': {'RD': 8974}, 'LX6': {'RD': 8975}, 'RB4': {'RD': 7481}, 'FXO': {'RD': 7482}, 'XRT': {'RD': 7481}, 'RAC': {'RD': 6986}, 'FZ5': {'RD': 7971}, 'UFR': {'RD': 8979}, 'XFR': {'RD': 7979}, 'FXR': {'RD': 7492}, 'XRR': {'RD': 7492}, 'FZR': {'RD': 8475}, 'MRT': {'RD': 12922}, 'FBM': {'RD': 9180}, 'FOX': {'RD': 7481}, 'FO8': {'RD': 9477}, 'BF1': {'RD': 19912}, }


# We shouldn't update UI from another thread
# QThread is thread safe for UI widgets
class ReceiverThread(QThread):

    changed_values = pyqtSignal(tuple)

    def run(self):

        # Create UDP socket.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # Bind to LFS.
            sock.bind(("127.0.0.1", 30000))
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                print("Port is already in use")
            else:
                # something else raised the socket.error exception
                print(e)

        logging.info('starting receiving data...')
        while True:
            # Receive data.
            try:
                data = sock.recv(256)
            except:
                data = []
                continue

            if not data:
                print("No data")
                break  # Lost connection

            # Unpack the data.
            og_pack = struct.unpack('I3sxH2B7f2I3f15sx15sx', data)

            self.changed_values.emit(og_pack)

        # Release the socket.
        sock.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.get_data = False
        self.car = False
        self.setWindowTitle("Gauges")
        self.setMinimumSize(1024, 720)
        # a = self.windowTitle()
        self.setGeometry(0, 0, 1024, 720)
        self.setStyleSheet("background-color: #04AA6D;")
        self.initUI()

    def closeEvent(self, a0):
        logging.info("Program terminated...")

    def initUI(self):
        # add UI elements
        logging.info("Init UI")

        # Horizontal line top
        self.line_t = QFrame(self)
        self.line_t.setGeometry(QRect(150, 130, 770, 20))
        self.line_t.setLineWidth(1)
        self.line_t.setMidLineWidth(1)
        self.line_t.setFrameShape(QFrame.HLine)
        self.line_t.setFrameShadow(QFrame.Sunken)
        # Horizontal line bottom
        self.line_b = QFrame(self)
        self.line_b.setGeometry(QRect(150, 600, 770, 20))
        self.line_b.setLineWidth(1)
        self.line_b.setMidLineWidth(1)
        self.line_b.setFrameShape(QFrame.HLine)
        self.line_b.setFrameShadow(QFrame.Sunken)

        self.rpm_bar = QProgressBar(self)
        self.rpm_bar.setGeometry(150, 50, 700, 50)
        self.rpm_bar.setTextVisible(False)
        self.rpm_bar.setStyleSheet("QProgressBar::chunk " "{" "background-color: white;" "}")
        # self.rpm_bar.setOrientation(Qt.Horizontal)

        self.rpm_bar_red = QProgressBar(self)
        self.rpm_bar_red.setGeometry(850, 50, 70, 50)
        self.rpm_bar_red.setTextVisible(False)
        self.rpm_bar_red.setStyleSheet("QProgressBar::chunk " "{" "background-color: red;" "}")
        self.rpm_bar_red.setMaximum(1)
        self.rpm_bar_red.setValue(1)

        self.input_line = QLineEdit(self)
        self.input_line.setGeometry(220, 100, 100, 50)
        self.input_line.hide()

        # Rpm Label
        self.rpm_label = QLabel('0', self)
        self.rpm_label.setGeometry(20,100, 100, 100)
        self.rpm_label.hide()

        # Speed Label
        self.speed_label = QLabel('0', self)
        self.speed_label.setGeometry(20, 150, 100, 100)
        self.speed_label.hide()

        # RPM LCD
        self.rpm_lcd = QLCDNumber(self)
        self.rpm_lcd.setGeometry(QRect(420, 170, 201, 81))
        self.rpm_lcd.setLineWidth(1)
        self.rpm_lcd.setMidLineWidth(1)
        self.rpm_lcd.display('00000')
        # Gear LCD
        self.gear_lcd = QLCDNumber(self)
        self.gear_lcd.setGeometry(QRect(420, 260, 201, 201))
        self.gear_lcd.setFrameShape(QFrame.Box)
        self.gear_lcd.setMidLineWidth(1)
        self.gear_lcd.setSmallDecimalPoint(False)
        self.gear_lcd.setDigitCount(1)
        self.gear_lcd.display('0')
        # Speed LCD
        self.speed_lcd = QLCDNumber(self)
        self.speed_lcd.setGeometry(QRect(420, 470, 201, 81))
        self.speed_lcd.setMidLineWidth(1)
        self.speed_lcd.display('000')

        # Start button
        self.btn_start = QPushButton('Start', self)
        self.btn_start.setGeometry(460, 640, 100, 50)
        self.btn_start.clicked.connect(self.oc_btn_start)

        # Test button
        self.btn_test = QPushButton('Test', self)
        self.btn_test.setGeometry(10, 150, 100, 50)
        self.btn_test.clicked.connect(self.oc_btn_test)
        self.btn_test.hide()

    def oc_btn_test(self):

        print('ON click test')

        # self.rpm_label.setText(f"RPM is :{random.randint(1, 100)}")

        # self.rpm_lcd.display(8)

        # self.rpm_lcd.setSegmentStyle(2)

        self.rpm_bar.setValue(random.randint(0, 6000))


        # print(self.input_line.text())
        # self.rpm_lcd.display(self.input_line.text())

        logging.info('Some log info')

    def oc_btn_start(self):

        self.data_thread = ReceiverThread()
        self.data_thread.changed_values.connect(self.UpdateUI)
        self.data_thread.start()

    def UpdateUI(self, og_pack):
        # print(og_pack)
        time = og_pack[0]
        try:
            car = og_pack[1].decode()
        except:
            car = 'unknown'

        if car != self.car:
            self.car = car
            self.setWindowTitle(car)
            car_info = cars_data.get(car)
            max_rpm = car_info['RD']
            # set max rpm
            self.rpm_bar.setMaximum(max_rpm - 50)

        flags = og_pack[2]
        gear = og_pack[3]
        speed = og_pack[5]  # მეტრი წამში გადაყვანა სჭირდება.
        r_speed = int((speed * 3600 / 1000) + 0.5)
        if r_speed < 10:  # რატომღაც 0 ზე არ ჩერდება.
            r_speed = 0
        rpm = int(og_pack[6] + 0.5)
        turbo = og_pack[7]
        eng_temp = og_pack[8]
        fuel = og_pack[9]
        oil_pressure = og_pack[10]
        oil_temp = og_pack[11]
        dashlights = og_pack[12]
        show_lights = og_pack[13]
        throttle = og_pack[14]
        brake = og_pack[15]
        clutch = og_pack[16]
        display1 = og_pack[17]
        display2 = og_pack[18]

        # SPEED
        self.speed_label.setText(f"Speed is :{r_speed} Km/h")
        self.speed_lcd.display(str(r_speed).rjust(3, '0'))
        # RPM
        self.rpm_label.setText(f"RPM is :{rpm}")
        self.rpm_lcd.display(str(rpm).rjust(5, '0'))
        # whn rpm is bigger than redline
        if rpm >= self.rpm_bar.maximum():
            self.rpm_bar.setValue(self.rpm_bar.maximum())
            if self.rpm_bar_red.value() == 0:
                self.rpm_bar_red.setValue(1)
            else:
                self.rpm_bar_red.setValue(0)
        else:
            self.rpm_bar.setValue(rpm)
            self.rpm_bar_red.setValue(1)

        # GEAR
        self.gear_lcd.display(gears[gear])

    def oc_btn_start_2(self):

        dt_thread = threading.Thread(target=self.receive_data, daemon=True)
        dt_thread.start()

def main():

    app = QApplication(sys.argv)
    window = MainWindow()
    # window.oc_btn_start()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
