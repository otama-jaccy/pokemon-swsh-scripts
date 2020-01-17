import serial
from time import sleep
import datetime
from enum import Enum

class Button(Enum):
    A = 'A'
    B = 'B'
    Y = 'Y'
    X = 'X'
    L = 'L'
    R = 'R'
    ZL = 'ZL'
    ZR = 'ZR'
    SELECT = 'SELECT'
    START = 'START'
    LCLICK = 'LCLICK'
    RCLICK = 'RCLICK'
    HOME = 'HOME'
    CAPTURE = 'CAPTURE'
    RELEASE = 'RELEASE'

class MoveDirection(Enum):
    RIGHT = 'LX MAX'
    LEFT = 'LX MIN'
    UP = 'LY MIN'
    DOWN = 'LY MAX'

class HatDirection(Enum):
    TOP = 'TOP'
    RIGHT = 'RIGHT'
    BOTTOM = 'BOTTOM'
    LEFT = 'LEFT'

class ManipulateTime:
    def __init__(self, duration_time=0, sleep_time=0):
        self.duration_time = duration_time
        self.sleep_time = sleep_time

    # [(duration_time, sleep_time), .....]を渡す
    @classmethod
    def create_list(cls, time_list):
        manipulate_time_list = []
        for t in time_list:
            manipulate_time_list.append(ManipulateTime(t[0], t[1]))
        return manipulate_time_list

class Controller:
    def __init__(self, port):
        self.serial = serial.Serial(port, 9600)

    def __del__(self):
        self.serial.close()

    def send(self, msg, duration=0, is_release=True):
        now = datetime.datetime.now()
        print(f'[{now}] {msg}')
        self.serial.write(f'{msg}\r\n'.encode('utf-8'))
        sleep(duration)
        if is_release:
            print("release")
            self.serial.write(b'RELEASE\r\n')

    def release(self):
        self.send("RELEASE")

    def push_button(self, button, duration=0, sleep_time=0):
        message = 'Button %s' % (button.value)
        self.send(message, duration)
        sleep(sleep_time)

    def blaze_button(self, button, manipulate_time_list):
        for manipulate_time in manipulate_time_list:
            self.push_button(button, manipulate_time.duration_time)
            sleep(manipulate_time.sleep_time)

    def move(self, move_direction, duration=0, sleep_time=0, is_release=True):
        self.send(move_direction.value, duration=duration, is_release=is_release)
        sleep(sleep_time)

    def push_hat(self, hat_direction, duration=0, sleep_time=0):
        message = 'HAT %s' % (hat_direction)
        self.send(message, duration=duration)
        sleep(sleep_time)

    def blaze(self, manipulate_time_list, manipulate_func, *args):
        for manipulate_time in manipulate_time_list:
            manipulate_func(*args, manipulate_time.duration_time)
            sleep(manipulate_time.sleep_time)


if __name__ == '__main__':
    import argparse
    import fcntl
    import termios
    import sys
    import os

    #参考
    def getkey():
        fno = sys.stdin.fileno()

        #stdinの端末属性を取得
        attr_old = termios.tcgetattr(fno)

        # stdinのエコー無効、カノニカルモード無効
        attr = termios.tcgetattr(fno)
        attr[3] = attr[3] & ~termios.ECHO & ~termios.ICANON # & ~termios.ISIG
        termios.tcsetattr(fno, termios.TCSADRAIN, attr)

        # stdinをNONBLOCKに設定
        fcntl_old = fcntl.fcntl(fno, fcntl.F_GETFL)
        fcntl.fcntl(fno, fcntl.F_SETFL, fcntl_old | os.O_NONBLOCK)

        ch = 0

        try:
            # キーを取得
            c = sys.stdin.read(1)
            if len(c):
                while len(c):
                    ch = ord(c)
                    c = sys.stdin.read(1)
        finally:
            # stdinを元に戻す
            fcntl.fcntl(fno, fcntl.F_SETFL, fcntl_old)
            termios.tcsetattr(fno, termios.TCSANOW, attr_old)

        return ch

    parser = argparse.ArgumentParser()
    parser.add_argument('port')
    args = parser.parse_args()

    controller = Controller(args.port)

    while True:
        sleep(0.1)
        code = getkey()
        key = chr(code)
        print("=============")
        print(key)
        print("=============")

        if key == 'b':
            break
        if key == 'a':
            controller.move(MoveDirection.LEFT, 0.2, 0, False)
        elif key == 'd':
            controller.move(MoveDirection.RIGHT, 0.2, 0, False)
        elif key == 's':
            controller.move(MoveDirection.DOWN, 0.2, 0, False)
        elif key == 'w':
            controller.move(MoveDirection.UP, 0.2, 0, False)
        elif key == 'i':
            controller.push_button(Button.X, 0.1, 0)
        elif key == 'k':
            controller.push_button(Button.B, 0.1, 0)
        elif key == 'j':
            controller.push_button(Button.Y, 0.1, 0)
        elif key == 'l':
            controller.push_button(Button.A, 0.1, 0)
        elif code==0:
            controller.release()
    print("end")