#!/usr/bin/env python3
import argparse
import serial
import time
from time import sleep
import datetime
import random

from controller import Controller, Button, MoveDirection, ManipulateTime

parser = argparse.ArgumentParser()
parser.add_argument('port')
parser.add_argument('--delay', type=int, default=10)
parser.add_argument('--fight-time', type=int, default=150)
parser.add_argument('--use-x-spatk', action='store_true')
parser.add_argument('--use-dynamax', action='store_true')
args = parser.parse_args()

# ダイマックスによる遅延を追加
fight_time = args.fight_time + (20 if args.use_dynamax == True else 0)

dt = datetime.datetime

def send(msg, duration=0):
    now = dt.now()
    print(f'[{now}] {msg}')
    ser.write(f'{msg}\r\n'.encode('utf-8'))
    sleep(duration)
    ser.write(b'RELEASE\r\n')

ser = serial.Serial(args.port, 9600)
controller = Controller(args.port)

# 遅延を入れる
print(f'{args.delay}秒の遅延を入れています…（--delayで指定可能）')
sleep(args.delay)
send('Button B', 0.1)

try:
    start_time = time.time()

    # トーナメント自動化

    for lap in range(0, 999):
        # 話しかける
        #controller.blaze_button(Button.A, ManipulateTime.create_list([(0.2, 1), (0.1, 0.5)]))
        controller.blaze(
            ManipulateTime.create_list([(0.2, 1), (0.1, 0.5)]),
            controller.push_button, Button.A 
        )
        # はい
        #controller.blaze_button(Button.A, ManipulateTime.create_list([(0.1, 1), (0.1, 0.5)]))
        controller.blaze(
            ManipulateTime.create_list([(0.1, 1), (0.1, 0.5)]),
            controller.push_button, Button.A 
        )
        # いる
        #controller.blaze_button(Button.A, ManipulateTime.create_list([(0.1, 0.5), (0.1, 0.5)]))
        controller.blaze(
            ManipulateTime.create_list([(0.1, 1), (0.1, 0.5)]),
            controller.push_button, Button.A 
        )
        # ヤローを選択
        controller.blaze(
            ManipulateTime.create_list([(0.1, 0.1)]*4),
            controller.move, MoveDirection.DOWN
        )
        # セリフを進める
        controller.blaze(
            ManipulateTime.create_list([(0.1, 0.4)]*13),
            controller.push_button, Button.A 
        )

        # 試合
        for i in range(0, 3):
            # 入場
            controller.move(MoveDirection.UP, duration=3, sleep_time=5)

            # 3回セリフ飛ばす
            controller.blaze(
                ManipulateTime.create_list([(0.1, 1)]*2 + [(0.1, 15)]),
                controller.push_button, Button.A
            )

            # 勝負
            print(f'第{i + 1}試合を開始')
            
            # 勝負を　しかけてきた！
            controller.push_button(Button.A, duration=0.1, sleep_time=22)

            # スペシャルアップを使う
            if args.use_x_spatk:
                print('スペシャルアップを使用します')

                controller.blaze(
                    ManipulateTime.create_list([(0.1, 0.1)]*2),
                    controller.move, MoveDirection.DOWN
                )

                controller.push_button(Button.A, duration=0.1, sleep_time=1.5)

                controller.blaze(
                    ManipulateTime.create_list([(0.1, 0.1)]*2),
                    controller.move, MoveDirection.RIGHT
                )

                controller.blaze(
                    ManipulateTime.create_list([(0.1, 0.1)]*2),
                    controller.move, MoveDirection.DOWN
                )

                controller.blaze(
                    ManipulateTime.create_list([(0.1, 0.2), (0.1, 12)]),
                    controller.push_button, Button.A
                )

                controller.blaze(
                    ManipulateTime.create_list([(0.1, 0.5)]*2),
                    controller.move, MoveDirection.UP
                )

            # ダイマックスする
            if args.use_dynamax:
                print('ダイマックスします')

                send('Button A', 0.1)
                sleep(0.5)

                send('LX MIN', 0.1)
                sleep(0.1)

                send('Button A', 0.1)
                sleep(0.2)

                # ダイマックスわざ
                send('Button A', 0.1)
                sleep(0.1)

            fight_start_time = time.time()

            while True:
                if (time.time() - fight_start_time) > fight_time:
                    break

                send('Button A', 0.1)
                sleep(0.1)

                # 残り秒数
                if random.randrange(0, 5) == 0:
                    time_left = round(fight_time - (time.time() - fight_start_time), 2)
                    print(f'[{dt.now()}] 残り{time_left}秒')

            print('勝利')

        # 優勝
        print('優勝')

        # ボールガイ
        for i in range(0, 20):
            send('Button A', 0.1)
            sleep(1)

        send('LY MIN', 1) # 受付に突っ込む

        print(f'[{dt.now()}] {round(time.time() - start_time, 2)}秒経過（{lap}回目）')

except KeyboardInterrupt:
    send('RELEASE')
    ser.close()
