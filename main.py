'''

I am aware i have repeated some codes (D.R.Y).
I have done so becouse of a well known issue of a missing concept.
This app will be re-written again soon in the recommeded way.

'''


from kivymd.app import MDApp
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivymd.uix.behaviors import CircularRippleBehavior
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget, ThreeLineIconListItem

from kivy.uix.button import Button
from kivymd.uix.button import MDTextButton
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.uix.label import Label

from acc import account_sid, auth_token, twilio_number

from twilio.rest import Client
from twilio.rest import TwilioRestClient
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.voice_response import Hangup, VoiceResponse

import os
import time
# from jnius import autoclass
from datetime import datetime
from time import sleep
from threading import Thread

from kivy.core.window import Window, Keyboard
from kivy.config import Config
Window.size = (270, 550)


class ImageButton(CircularRippleBehavior, ButtonBehavior, Image):
    ripple_scale = 0.5


class Mycall(TwoLineIconListItem, ButtonBehavior):
    pass


class LogButton(ThreeLineIconListItem, ButtonBehavior):
    pass


class Tab(FloatLayout, MDTabsBase):
    pass


class MainWin(BoxLayout):
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '+']

        for key in keys:
            btn = Button(text=key,
                         background_normal="",
                         background_color=(1, 1, 1, 1),
                         color=(0, 0, 0, 1),
                         font_size=25,
                         background_down="imgs/bc1.png",
                         on_release=self.display)
            self.ids.content.add_widget(btn)

        t1 = Thread(target=self.call_logs, daemon=True)
        t1.start()
        t2 = Thread(target=self.show_balance, daemon=True)
        t2.start()
        t3 = Thread(target=self.inbox)
        t3.start()

    def display(self, instance):
        num = self.ids.display_n
        calling = self.ids.call_id
        if len(num.text) <= 12:
            num.text += instance.text
            calling.text += instance.text
        else:
            num.text = num.text
            calling.text = calling.text

    def delete(self):
        num = self.ids.display_n
        calling = self.ids.call_id
        num.text = num.text[:-1]
        calling.text = calling.text[:-1]
        return num, calling

    def delete_status(self):
        sleep(2)
        self.ids.status.text = ""

    def show_keyboard(self):
        keybord = Config.set('kivy', 'keyboard_mode', 'systemandmulti')
        return keybord

    def my_except(self):
        client = Client(account_sid, auth_token)
        if self.ids.display_n.text != "" and len(self.ids.display_n.text) >= 8:
            try:
                call = client.calls.create(
                    url='http://demo.twilio.com/docs/voice.xml',
                    to=f'974{self.ids.display_n.text}',
                    from_=twilio_number,
                )

                print("Calling: ", self.ids.display_n.text)
            except TwilioRestException:
                self.ids.screen_manager.current = 'home'
                self.ids.display_n.text = "Invalid"
                print('Wrong Number')
        else:
            self.ids.screen_manager.current = 'home'
            self.ids.display_n.text = "Invalid"

    def start_call(self):
        client = Client(account_sid, auth_token)

        if self.ids.display_n.text != "" and len(self.ids.display_n.text) >= 8:
            try:
                call = client.calls.create(
                    url='http://demo.twilio.com/docs/voice.xml',
                    to=f'974{self.ids.display_n.text}',
                    from_=twilio_number,
                )

                print("Calling: ", self.ids.display_n.text)
                return call
            except TwilioRestException:
                return self.my_except()

        # elif self.ids.display_n.text == '':
        #     call = client.calls.create(
        #         url='http://demo.twilio.com/docs/voice.xml',
        #         to=f'974{self.ids.log_call.secondary_text}',
        #         from_=twilio_number,
        #     )
        #     self.ids.call_id.text = self.ids.log_call.text
        #     print("Calling: ", self.ids.log_call.text)
        #     return call
        else:
            self.ids.screen_manager.current = 'home'
            self.ids.display_n.text = "Invalid"
            print("Number Required")

    def end_call(self):
        x = Client(account_sid, auth_token)
        pass

    def get_contacts(self):
        from jnius import autoclass
        contacts = autoclass('android.provider.ContactsContract$Contacts')
        self.ids.contacts.text = Label(
            text=str(dir(contacts).replace(' ', '\n')))

    def show_balance(self):
        bal_src = Client(account_sid, auth_token)
        self.ids.balances.text = str(bal_src.balance)

    def call_logs(self):
        client_log = Client(account_sid, auth_token)
        log_src = client_log.calls.list(limit=20)
        for record in log_src:
            rec = self.ids.recents
            widg = LogButton(
                text=str(record.to),
                secondary_text=str(record.duration) + ' sec',
                tertiary_text=str(
                    record.date_created.strftime("%b %d %Y %H:%M:%S")))
            iconi = IconLeftWidget(icon='phone')
            widg.add_widget(iconi)
            rec.add_widget(widg)

        # SMS

    def send_msg(self):
        sms_client = Client(account_sid, auth_token)

        try:
            message = sms_client.messages.create(
                to=f'+974{self.ids.p_no.text}',
                from_=twilio_number,
                body=self.ids.new_msg.text,
                status_callback='https://postb.in/b/1594000410504-2666337494738'
            )
        except TwilioRestException:
            return self.msg_status()
        return message

    def msg_status(self):
        if self.ids.new_msg.text != "" and self.ids.p_no.text != "":
            self.ids.status.text = ("message Sent")
        else:
            self.ids.status.text = "Both fields are required!"

    def clear_fields(self):
        if self.send_msg():
            self.ids.new_msg.text = ''
            self.ids.p_no.text = ''
        else:
            pass

    def inbox(self):
        sms_client = Client(account_sid, auth_token)
        msg_records = sms_client.messages.list(limit=20)

        for record in msg_records:
            logs = ThreeLineIconListItem(
                text=str(record.to),
                secondary_text=record.body,
                tertiary_text=str(
                    record.date_created.strftime("%b %d %Y %H:%M:%S"))
            )
            img = IconLeftWidget(icon='chat-outline')
            lst = self.ids.inbox
            logs.add_widget(img)
            lst.add_widget(logs)


class MainApp(MDApp):
    def build(self):
        return MainWin()


if __name__ == '__main__':
    MainApp().run()
