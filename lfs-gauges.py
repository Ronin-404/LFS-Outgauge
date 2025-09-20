import logging
import random
import sys
import socket
import errno
import struct
import threading

from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QPushButton, QLabel, QLineEdit

logging.basicConfig(format="%(message)s", level=logging.INFO)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.get_data = False
        self.setWindowTitle("Gauges")
        # a = self.windowTitle()
        self.setGeometry(0, 0, 1024, 720)
        self.initUI()

    def closeEvent(self, a0):
        logging.info("Program terminated...")

    def initUI(self):
        # add UI elements
        logging.info("Init UI")

        self.input = QLineEdit()
        self.input.setGeometry(20, 100, 100, 100)

        # Rpm Label
        self.rpm_label = QLabel('0', self)
        self.rpm_label.setGeometry(20,200, 100, 100)

        # Speed Label
        self.speed_label = QLabel('0', self)
        self.speed_label.setGeometry(20, 250, 100, 100)

        # Start button
        self.btn_start = QPushButton('Start', self)
        self.btn_start.setGeometry(10, 10, 100, 50)
        # self.btn_start.styleSheet("font-size: 30px;")
        self.btn_start.clicked.connect(self.oc_btn_start)

        # Start button
        self.btn_test = QPushButton('Test', self)
        self.btn_test.setGeometry(10, 80, 100, 50)
        self.btn_test.clicked.connect(self.oc_btn_test)

    def oc_btn_test(self):

        print('ON click test')

        self.rpm_label.setText(f"RPM is :{random.randint(1, 100)}")

        logging.info('Some log info')

    def oc_btn_start(self):

        dt_thread = threading.Thread(target=self.receive_data, daemon=True)
        dt_thread.start()

    def receive_data(self):

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
                break # Lost connection

            # Unpack the data.
            og_pack = struct.unpack('I3sxH2B7f2I3f15sx15sx', data)
            time = og_pack[0]
            car = og_pack[1]
            flags = og_pack[2]
            gear = og_pack[3]
            speed = og_pack[5]  # მეტრი წამში გადაყვანა სჭირდება.
            r_speed = int((speed * 3600 / 1000) + 0.5)
            if r_speed < 10:  # რატომღაც 0 ზე არ ჩერდება.
                r_speed = 0
            rpm = int(og_pack[6]+0.5)
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

            print(f"*RPM is {rpm}")

            self.rpm_label.setText(f"RPM is :{rpm}")
            self.speed_label.setText(f"Speed is :{r_speed} Km/h")

        # Release the socket.
        sock.close()

def main():

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
