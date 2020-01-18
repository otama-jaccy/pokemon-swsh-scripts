from controller import Controller, Button
import argparse

if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('port')
    args = parser.parse_args()

    controller = Controller(args.port)
    
    try:
        while True:
            controller.push_button(Button.A, 0.1, 0.1)
    except KeyboardInterrupt:
        controller.release()