import datetime
import threading

import pynput
import telebot

from pynput import mouse
from tkinter import Tk, Label, Button


class MouseListener:

    def __init__(self):
        self.start_position = None
        self.stop_position = None

    def get_position(self):
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        x, y = map(int, (x, y))
        if self.start_position and self.stop_position:
            raise pynput.mouse.Listener.StopException
        if self.start_position is None:
            self.start_position = x, y
            print(self.start_position)
        elif self.stop_position is None and self.start_position != (x, y):
            self.stop_position = x, y
            print(self.stop_position)


class Mouse:

    def __init__(self):
        self.mouse = mouse.Controller()

    def left_click(self):
        self.mouse.click(mouse.Button.left)
        print('Mouse clicked at %s', self.mouse.position)

    def set_position(self, position):
        self.mouse.position = position
        print('Mouse moved at %s', self.mouse.position)


class TimeTracker:

    def __init__(self, start_position, stop_position, mouse):
        self.start_position = start_position
        self.stop_position = stop_position
        self.mouse = mouse

    def start(self):
        self.mouse.set_position(self.start_position)
        self.mouse.left_click()
        print('Time tracking started %s', datetime.datetime.now())

    def stop(self):
        self.mouse.set_position(self.stop_position)
        self.mouse.left_click()
        print('Time tracking stopped %s', datetime.datetime.now())


class TimeTrackingBot:

    TOKEN = 'TOKEN'

    bot = telebot.TeleBot(token=TOKEN)

    def __init__(self, start_position, stop_position):
        self.time_tracker = TimeTracker(
            start_position, stop_position, Mouse(),
        )

        self.greeting = self.bot.message_handler(
            commands=['start', 'help'])(self.greeting)

        self.start_tracking = self.bot.message_handler(
            commands=['track'])(self.start_tracking)

        self.stop_tracking = self.bot.message_handler(
            commands=['stop'])(self.stop_tracking)

    def greeting(self, message):
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.add(telebot.types.KeyboardButton(text='/track'))
        markup.add(telebot.types.KeyboardButton(text='/stop'))
        self.bot.send_message(
            message.chat.id, text='commands', reply_markup=markup,
        )

    def start_tracking(self, message):
        self.time_tracker.start()
        self.bot.send_message(message.chat.id, text='tracking started')

    def stop_tracking(self, message):
        self.time_tracker.stop()
        self.bot.send_message(message.chat.id, text='tracking stopped')

    def run(self):
        self.bot.polling()


class GUI:

    def __init__(self, master):
        self.master = master
        self.listener = None
        self.background = None
        self.label = None
        self.master.title("Time tracking bot")
        self.setup_mouse_button = self.create_button(
            "Setup mouse", self.setup_mouse)
        self.run_bot_button = self.create_button("Run bot", self.run_bot)
        self.notify("Click start button then click stop button")

    def setup_mouse(self):
        self.listener = MouseListener()
        self.listener.get_position()

    def create_button(self, text, command):
        button = Button(self.master, text=text, command=command)
        button.pack()
        return button

    def notify(self, text):
        if self.label is not None:
            self.label.destroy()
        self.label = Label(self.master, text=text)
        self.label.pack()

    def run_bot(self):
        if self.listener is None:
            self.notify('Setup mouse first')
            return
        bot = TimeTrackingBot(
            self.listener.start_position,
            self.listener.stop_position,
        )
        self.background = threading.Thread(target=bot.run)
        self.background.start()
        self.notify('Bot has been started!')


if __name__ == '__main__':
    root = Tk()
    root.geometry('350x200')
    my_gui = GUI(root)
    root.mainloop()
