from __future__ import print_function
import socket
from datetime import datetime
import threading
from PIL import Image, ImageFont, ImageDraw
import time
import os
import smtplib
from email.message import EmailMessage

import os.path        #All these libraries to access Gmail API using OAuth2.0 :(
import base64
import google.auth
import requests
import json

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

#Temporary stuff
load_dotenv()
IP = '192.168.120.133'
#ToEmail = 'abdulhaseebmohammed191'
FromToken = 'token'
TheCard = 'test'
SetTime = '00:00:01'#For scheduling
#print(socket.gethostbyname('Alive'))

SCOPES = ['https://www.googleapis.com/auth/gmail.compose','https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/gmail.metadata']
def timecheck():#Checks for current time in background
    print('timecheck() started')
    while True:
        if datetime.now().strftime('%H:%M:%S') == SetTime:
            sendmail()

def jsonlistner():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('Token Listner ready!\n')
    s.bind((IP,1338))
    s.listen(5)
    while True:
        (clientsock,address) = s.accept()
        print('Connection Established')
        f = open('recievetoken.json','wb')
        while True:
            DataRecieved = clientsock.recv(8)
            f.write(DataRecieved)
            print(f'{DataRecieved}\n')
            if len(DataRecieved) <= 0:
                break
        f.close()

def img_listner():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('Img Listner ready!\n')
    s.bind((IP,1339))
    s.listen(5)
    while True:
        (clientsock,address) = s.accept()
        print('Connection Established')
        f = open('recieveimg.jpg','wb')
        while True:
            DataRecieved = clientsock.recv(100000)
            f.write(DataRecieved)
            print(f'{DataRecieved}\n')
            if len(DataRecieved) <= 0:
                break
        f.close()

def sendmail():
    #count = 1
    f = open('Details.txt','r')
    DetailsList = f.read().split('\n')#Reads empty string at last as well
    DetailsList.pop()#Last item is empty string so popping it
    print(DetailsList)
    for i in DetailsList:

        Date,ToEmail = i.split('$')
        #print(f'Scanned item {count}:\nDate:{Date}\nFrom:{From}\nTo:{To}\nToEmail:{ToEmail}\nTemplate:{Template}\n\n')
        #count+=1
        CurDT = datetime.now().strftime('%Y-%m-%d')
        if Date == CurDT:
            TheCard = f'HappyBirthdayto{ToEmail}'
            #print('Card Created')
            gmail_send_message(ToEmail,TheCard)
            os.remove(TheCard)#Deleteing the card once sent
        else:
            print('TODAY IS NOT THE DAY!\n\n')
    time.sleep(1)#This function executes in less than a second causing Details file to be scanned multiple times



def gmail_send_message(ToEmail,TheCard):

    creds = Credentials.from_authorized_user_file(f'{ToEmail}Token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(f'{ToEmail}Token.json', 'w') as token:
                token.write(creds.to_json())
    f = open(f'{ToEmail}Token.json')#Dont forget to close
    myjson = json.load(f)
    mytoken = myjson['token']
    #print(mytoken)
    useremail = requests.get('https://gmail.googleapis.com/gmail/v1/users/me/profile',headers={'Authorization': f'Bearer {mytoken}'})
    #print(useremail.json())
    try:
        service = build('gmail', 'v1', credentials=creds)
        mime_message = MIMEMultipart()
        mime_message['To'] = ToEmail
        mime_message['From'] = useremail.json()['emailAddress']
        mime_message['Subject'] = f'Happy Birthday!!'

        with open(f'{TheCard}', 'rb') as img:
            image_attachment = MIMEImage(img.read(), _subtype='jpeg')


        image_attachment.add_header('Content-Disposition', 'inline', filename=f'Happy Birthday')
        mime_message.attach(image_attachment)
        # encoded message
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

        create_message = {'raw': encoded_message}
        # pylint: disable=E1101

        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
        return send_message


'''def customBirthdayCard(From,To,Template,Font):
    myimg = Image.open(Template)
    FontColor = (0, 71, 171)
    FontSize = 80
    FontAlignment = (300,200)

    if Template == 'Template_3.jpg':
        FontColor = (255,215,0)
        FontAlignment = (40,400)
        FontSize = 75
    title_font = ImageFont.truetype(f'{Font}.ttf', FontSize)
    title_text = f'{From} wishes you a \n  very happy birthday.\n Have a very splendid year \n  {To}'

    imgedit = ImageDraw.Draw(myimg)
    imgedit.text(FontAlignment, title_text, FontColor, font=title_font)
    myimg.save(f'HappyBirthdayto{To}.jpg')
    return f'HappyBirthdayto{To}.jpg' '''

sendmail()
exit()
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((IP,1337))
s.listen(5)
print('Server established')
DetailsString = ''
threading.Thread(target=timecheck).start()
threading.Thread(target=jsonlistner).start()
threading.Thread(target=img_listner).start()
while True:
    print('Details listner ready!')
    (clientsock,address) = s.accept()
    time.sleep(1)
    while True:
        DataRecieved = clientsock.recv(8)
        print(f'{DataRecieved}\n')
        if len(DataRecieved) <= 0:
            break
        DetailsString += DataRecieved.decode('utf-8')

    print(DetailsString)
    f = open('Details.txt','a')
    f.write(DetailsString+'\n')
    f.close()
    time.sleep(1) #To make sure token is recieved before renaming recievetoken.json
    ToEmail = DetailsString.split('$')[1]
    os.rename('recievetoken.json',f'{ToEmail}Token.json')
    os.rename('recieveimg.jpg',f'HappyBirthdayto{ToEmail}')
    DetailsString = ''
    print('Image,Details,Token Recieved :)\n')