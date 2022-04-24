from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
from kivy.uix.screenmanager import ScreenManager, Screen
import socket
IP = 'Enter IPv4 Address of your server'
class PreviewScreen(Screen):
    pass
class WindowManager(ScreenManager):
    pass

def enterData(Year,Month,Day,From,To,ToEmail,Template,Font):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((IP,1337))
    UserDate = datetime(int(Year),int(Month),int(Day))
    UserDateString = UserDate.strftime('%Y-%m-%d')
    DetailsString = f'{UserDateString}${From}${To}${ToEmail}${Template}${Font}'
    s.send(bytes(DetailsString, 'utf-8'))

def customBirthdayCard(From,To,Template,Font):
    myimg = Image.open(f'{Template}.jpg')
    title_font = ImageFont.truetype(f'{Font}.ttf', 80)
    title_text = f'{From} wishes you a \n  very happy birthday.\n Have a very splendid year \n  {To}'

    imgedit = ImageDraw.Draw(myimg)
    imgedit.text((300,200), title_text, (0, 71, 171), font=title_font)
    myimg.save(f'HappyBirthdayto{To}.jpg')
    return f'HappyBirthdayto{To}.jpg'
class DetailInputScreen(BoxLayout,Screen):
    Template = StringProperty('Template_1.jpg')
    Font = StringProperty('')
    def previewimagegen(self):
        print('Meow!')
    def onFontSelect(self,font):
        self.Font = font
        #print(self.Font)
    def on_active_checkbox(self,active,TemplateString,chk2,chk3):
        if active == True:
            chk2.active = False
            chk3.active = False
            self.Template = TemplateString
            print(self.Template)
    def passtext(self, Year, Month, Day, From, To, ToEmail,Template,Font):
        enterData(Year, Month, Day, From, To, ToEmail, Template, Font)
kv = Builder.load_file('birthday.kv')
class BirthdayApp(App):
    def build(self):
        return kv


if __name__ == '__main__':
    BirthdayApp().run()
