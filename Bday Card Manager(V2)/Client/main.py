from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import ListProperty
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.animation import Animation
from datetime import datetime, date
# I DONT WANT TO COMMIT TO THIS RELATIONSHIP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from kivy.uix.screenmanager import ScreenManager, Screen
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import TransportError
import google
from PIL import Image, ImageFont, ImageDraw
# from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import socket
import os
import json
import time
import glob  # Amazing library name
import re

SCOPES = ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.metadata']
load_dotenv()
hostname = socket.gethostname()
IP = str(socket.gethostbyname(hostname))
customText = ''
img_reference = list()  # Cant use ids as they are parsed only in .kv file, so need to store references to dynamically added widgets in python.
shake = Animation(x=198, duration=.05) + Animation(x=202, duration=.05) + Animation(x=198, duration=.05) + Animation(
    x=202, duration=.05) + Animation(x=200, duration=.05)
emailRegEx = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Proper email format


class PreviewScreen(BoxLayout, Screen):
    img_src = StringProperty(r'.\CustomImg\Template_1.jpg')
    Font = StringProperty('JandaCelebrationScript')

    R = NumericProperty(0)
    G = NumericProperty(71)
    B = NumericProperty(171)

    CustomImgLoaded = NumericProperty(0)

    customText = StringProperty('')

    def notNull(self, value):
        if value.text == '':
            value.text = '0'

    def valueLimiter(self, value):
        print(f'in valueLimiter {value.text}')
        if value.text == '':
            print('in if')
            value.text = '0'

        elif int(value.text) > 255:
            print('in elif')
            value.text = '255'

    def invokeBDayGen(self, root_manager):
        # Invoked by text widgets in preview screen for every touch through on_text_validate property useful for mobile devices
        print('am in invokebdaygen')
        customBirthdayCard(root_manager)
        return

    def scanimg(self, root_manager):
        if self.CustomImgLoaded == 0:  # Dont want to keep on adding same widgets everytime user clicks "Advanced"
            layout = GridLayout(cols=3)
            filelist = glob.glob(r'.\CustomImg\*.jpg')
            tmpfilelist = glob.glob(r'.\CustomImg\*.jpeg')

            # for i in tmpfilelist:
            #   filelist.append(i)
            for i in range(len(filelist)):
                tmp = ToggleButton(background_color=[1, 1, 1, .5], background_normal=filelist[i],
                                   background_down=filelist[i], group='img')
                tmp.bind(on_press=lambda x: highlight())  # This took an hour to figure out
                img_reference.append(tmp)
                root_manager.get_screen('AdvancedUwU').ids.grid.add_widget(img_reference[i])
            self.CustomImgLoaded = 1

            '''
                Scroll range of Scrollview depends on the height property of child widget, needed to scale GridLayout's 
                height property with the no. of rows present
            '''

            rows = len(filelist) / 3
            if len(filelist) % 3 == 0:
                root_manager.get_screen('AdvancedUwU').ids.grid.height *= rows
            else:
                root_manager.get_screen('AdvancedUwU').ids.grid.height *= (rows + 1)
            print(root_manager.get_screen('AdvancedUwU').ids.grid.height)

            # print(self.img_reference)
            # print(filelist)

            # root_manager.get_screen('AdvancedUwU').ImgFileList = filelist

    def enterData(self, Year, Month, Day, ToEmail):
        global Appendage
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            print('In try')
            s.connect((IP, 9337))
        except socket.timeout:
            print('Cannot connect to server')
            return
        else:
            try:
                UserDate = datetime(int(Year), int(Month), int(Day))  # For validating purposes
            except ValueError:
                print('Invalid Date')
                return
            else:
                UserDateString = UserDate.strftime('%Y-%m-%d')

                DetailsString = f'{UserDateString}${ToEmail}'
                s.send(bytes(DetailsString, 'utf-8'))
                s.close()

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((IP, 9338))  # Cant reopen socket on port 9338 as it was closed earlier
                with open('token.json', 'rb') as f:
                    s.sendall(f.read())
                s.close()

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((IP, 9339))
                with open(f'HappyBirthdayto{Appendage}{ToEmail}.jpg', 'rb') as f:
                    s.sendall(f.read())
                s.close()

    def defaults(self, root_manager):
        global customText
        customText = ''
        self.img_src = r'.\CustomImg\Template_1.jpg'
        self.Font = 'JandaCelebrationScript'

        root_manager.get_screen('previewscreen').ids.R.value = 0
        root_manager.get_screen('previewscreen').ids.G.value = 71
        root_manager.get_screen('previewscreen').ids.B.value = 171

        self.R = 0
        self.G = 71
        self.B = 171

        root_manager.get_screen('previewscreen').ids.FontSize.text = '80'
        root_manager.get_screen('previewscreen').ids.xoffset.text = '300'
        root_manager.get_screen('previewscreen').ids.yoffset.text = '200'
        customBirthdayCard(root_manager)


class CustomText(Popup):
    def updateText(self, text):
        print(text)
        global customText
        customText = text


class Advanced(Screen):
    # ImgFileList = ListProperty([])
    def togglecheck(self, root_manager):
        # toggle_ref_list = root_manager.get_screen('previewscreen').img_reference

        for i in img_reference:
            if i.state == 'down':
                root_manager.get_screen('previewscreen').img_src = i.background_normal
                customBirthdayCard(root_manager)


def highlight():
    # Couldn't figure out how to pass widget reference to this func by binding on_press to the widget

    for i in img_reference:
        if i.state == 'down':
            i.background_color = [1, 1, 1, 1]
        else:
            i.background_color = [1, 1, 1, .5]


class WindowManager(ScreenManager):
    pass


class NetworkIssue(BoxLayout):
    pass


class DetailInputScreen(BoxLayout, Screen):
    Year = StringProperty('2022')
    Month = StringProperty('10')
    Day = StringProperty('15')
    From = StringProperty('Me')
    To = StringProperty('You')
    ToEmail = StringProperty('a.hmohdlords@gmail.com')
    TextFieldAccessCount = NumericProperty(
        0)  # Dont want to prompt user to enter a valid entry as soon as they try to enter data
    TextFieldAccessCount2 = NumericProperty(0)
    DateValid = BooleanProperty(False)
    EmailValid = BooleanProperty(False)

    def InputCheck(self, Next):
        if self.DateValid and self.EmailValid:
            Next.disabled = False
        else:
            Next.disabled = True

    def emailValidate(self, emailText, emailLabel, Next):
        print('in emailValidate')
        if self.TextFieldAccessCount2 == 0:  # Needed to avoid constanly updating TextFieldAccessCount
            self.TextFieldAccessCount2 += 1
        elif not re.fullmatch(emailRegEx, emailText):
            emailLabel.text = 'Enter a valid email'
            emailLabel.color = 1, 0, 0, 1
            shake.start(emailLabel)
            # Next.disabled = True
            self.EmailValid = False
        else:
            emailLabel.text = "Enter your friend's Email"
            emailLabel.color = 1, 1, 1, 1
            # Next.disabled = False
            self.EmailValid = True

    def dateValidate(self, DD, MM, YYYY, Next, dateLabel, ):
        if self.TextFieldAccessCount <= 4:  # Needed to avoid constanly updating TextFieldAccessCount
            self.TextFieldAccessCount += 1
        else:
            print('In dateValidate')
            print(dateLabel.pos)
            try:
                UserDate = datetime(int(YYYY), int(MM), int(DD))  # For validating purposes

            except ValueError:
                print('Invalid Date')
                # Next.disabled = True
                dateLabel.text = 'Enter a valid date:'
                dateLabel.color = 1, 0, 0, 1
                # moveleft.start(dateLabel)
                # shake.repeat = True
                shake.start(dateLabel)
                self.DateValid = False
                return

            CurrentDate = datetime.now()
            CurrentYear = CurrentDate.year  # Need to compare date only, now() method returns time as well
            CurrentMonth = CurrentDate.month  # Yup, thats right, i couldn't find a better way to do this, another way would be converting them into strings.
            CurrentDay = CurrentDate.day
            CurrentDate = datetime(CurrentYear, CurrentMonth, CurrentDay)

            if UserDate < CurrentDate:
                print('Invalid Date')
                # Next.disabled = True
                dateLabel.text = 'Enter a valid date:'
                dateLabel.color = 1, 0, 0, 1
                shake.start(dateLabel)
                self.DateValid = False
                return

            # self.TextFieldAccessCount = 0
            dateLabel.text = 'Enter date:'
            dateLabel.color = 1, 1, 1, 1
            # Next.disabled = False
            self.DateValid = True

    def on_next(self, YYYY, MM, DD, From, To, ToEmail):
        App.get_running_app().Year = YYYY
        App.get_running_app().Month = MM
        App.get_running_app().Day = DD
        App.get_running_app().From = From
        App.get_running_app().To = To
        App.get_running_app().ToEmail = ToEmail

    def load_font(self, root_manager):
        customBirthdayCard(root_manager)
        fontlist = glob.glob('.\CustomFonts\*.ttf')
        for i in fontlist:
            # root_manager.get_screen('previewscreen').ids.FontList.values.append(i)
            i = re.sub(r'.\\CustomFonts', '', i)
            i = re.sub(r'\\','',i) # A slash was remaining, re.sub() is weird with backslashes
            i = re.sub('.ttf', '', i)
            root_manager.get_screen('previewscreen').ids.FontList.values.append(i)
            print(i)

    def nextscreen(self, root_manager):
        if self.DateValid and self.EmailValid:
            App.get_running_app().root.current = 'previewscreen'


class DetailInputScreen2(BoxLayout, Screen):
    Template = StringProperty('Template_1.jpg')
    Font = StringProperty('JandaCelebrationScript')

    # def previewimagegen(self):
    #   print('Meow!')
    def onFontSelect(self, font):
        self.Font = font
        print(self.Font)

    def on_active_checkbox(self, active, TemplateString, chk2, chk3):
        if active == True:
            chk2.active = False
            chk3.active = False
            self.Template = TemplateString
            print(self.Template)

    def passtext(self, root_manager):  # def passtext(self, Year, Month, Day, From, To, ToEmail,Template,Font):
        # enterData(Year, Month, Day, From, To, ToEmail, Template, Font)
        customBirthdayCard(root_manager)


def TokenGen():  # For Client
    global kv
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except TransportError:
                kv = Builder.load_file('exceptions.kv')
                print('Network issue')
                return kv

        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=1337)
        # Save the credentials for the next run0
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


Appendage = 0  # Refer to attached document to understand why this exists


def customBirthdayCard(root_manager):
    print('In card gen')
    global Appendage
    global customText
    ToEmail = root_manager.get_screen('DIS').ids.ToEmail.text
    Appendage += 1
    if os.path.isfile(
            f'.\HappyBirthdayto{Appendage - 1}{ToEmail}.jpg'):
        os.remove(f'HappyBirthdayto{Appendage - 1}{ToEmail}.jpg')  # To remove previous iteration to save space

    Font = root_manager.get_screen('previewscreen').ids.FontList.text
    From = root_manager.get_screen('DIS').ids.From.text
    To = root_manager.get_screen('DIS').ids.To.text
    Template = root_manager.get_screen('previewscreen').img_src
    FontSize = root_manager.get_screen('previewscreen').ids.FontSize.text
    x_offset = root_manager.get_screen('previewscreen').ids.xoffset.text
    y_offset = root_manager.get_screen('previewscreen').ids.yoffset.text
    R = root_manager.get_screen('previewscreen').R
    G = root_manager.get_screen('previewscreen').G
    B = root_manager.get_screen('previewscreen').B
    CustomText = customText

    if CustomText == '':
        CustomText = f'{From} wishes you a \n  very happy birthday.\n Have a very splendid year \n  {To}'

    if int(FontSize) > 999:  # To fix decompression bomb error
        root_manager.get_screen('previewscreen').ids.FontSize.text = '999'
        FontSize = 999
    myimg = Image.open(Template)
    title_font = ImageFont.truetype(fr'.\CustomFonts\{Font}.ttf',
                                    int(FontSize))
    title_text = CustomText

    imgedit = ImageDraw.Draw(myimg)
    imgedit.text((int(x_offset), int(y_offset)), title_text, (R, G, B), font=title_font)

    myimg.save(f'HappyBirthdayto{Appendage}{ToEmail}.jpg')
    root_manager.get_screen('previewscreen').ids.preview.source = f'HappyBirthdayto{Appendage}{ToEmail}.jpg'

    """ 
        For some reason kivy was loading the previous state of the image with the same name after user makes any changes 
        ,probably cuz it was using some cache that uses the file name to load the image in the app, so I changed the 
        name each time the current rendition ss overwritten with a another one by appending it with an unrelated item 
        like an integer and to keep it unique for a user, I attached their email too, I called it an appendage here :P
    """


kvbg = Builder.load_file('bg.kv')
kv = Builder.load_file('birthday.kv')


class bruhBirthdayApp(App):
    def build(self):
        # App.get_running_app().img_src = 'Template_1.jpg'
        TokenGen()
        return kv


if __name__ == '__main__':
    bruhBirthdayApp().run()
