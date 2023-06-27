from __future__ import print_function
import socket
from datetime import datetime
import threading
import time
import os


import os.path  # All these libraries to access Gmail API :(
import base64
import requests
import json

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Temporary stuff
# load_dotenv()
hostname = socket.gethostname()
IP = str(socket.gethostbyname(hostname))
FromToken = 'token'
TheCard = 'test'
SetTime = '00:00:01'  # For scheduling

SCOPES = ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.metadata']


def timecheck():  # Checks for current time in background
    print('timecheck() started')
    while True:
        if datetime.now().strftime('%H:%M:%S') == SetTime:
            sendmail()


def jsonlistner():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Token Listner ready!\n')
    s.bind((IP, 9338))
    s.listen(50)
    while True:
        (clientsock, address) = s.accept()
        print('Connection Established')
        f = open('recievetoken.json', 'wb')
        while True:
            DataRecieved = clientsock.recv(8)
            f.write(DataRecieved)
            #print(f'{DataRecieved}\n')
            if len(DataRecieved) <= 0:
                break
        f.close()


def img_listner():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Img Listner ready!\n')
    s.bind((IP, 9339))
    s.listen(50)
    while True:
        (clientsock, address) = s.accept()
        print('Connection Established')
        f = open('recieveimg.jpg', 'wb')
        while True:
            DataRecieved = clientsock.recv(100000)
            f.write(DataRecieved)
            #print(f'{DataRecieved}\n')
            if len(DataRecieved) <= 0:
                break
        f.close()


def sendmail():
    # count = 1
    f = open('Details.txt', 'r')
    DetailsList = f.read().split('\n')  # Reads empty string at last as well
    DetailsList.pop()  # Last item is empty string so popping it
    print(DetailsList)
    for i in DetailsList:

        Date, ToEmail = i.split('$')
        CurDT = datetime.now().strftime('%Y-%m-%d')
        if Date == CurDT:
            TheCard = f'HappyBirthdayto{ToEmail}.jpg'
            gmail_send_message(ToEmail, TheCard)
            os.remove(TheCard)  # Deleteing the card once sent
        else:
            print('TODAY IS NOT THE DAY!\n\n')
    time.sleep(1)  # This function executes in less than a second causing Details file to be scanned multiple times


def gmail_send_message(ToEmail, TheCard):
    creds = Credentials.from_authorized_user_file(f'{ToEmail}Token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(f'{ToEmail}Token.json', 'w') as token:
                token.write(creds.to_json())
    f = open(f'{ToEmail}Token.json')  # Dont forget to close
    myjson = json.load(f)
    mytoken = myjson['token']
    useremail = requests.get('https://gmail.googleapis.com/gmail/v1/users/me/profile',
                             headers={'Authorization': f'Bearer {mytoken}'})
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


#sendmail()
#exit()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, 9337))
s.listen(50)
#print(IP)
print('Server established')
DetailsString = ''
threading.Thread(target=timecheck).start()
threading.Thread(target=jsonlistner).start()
threading.Thread(target=img_listner).start()
while True:
    print('Details listner ready!')
    (clientsock, address) = s.accept()
    time.sleep(1)
    while True:
        DataRecieved = clientsock.recv(8)
        #print(f'{DataRecieved}\n')
        if len(DataRecieved) <= 0:
            break
        DetailsString += DataRecieved.decode('utf-8')

    print(DetailsString)
    f = open('Details.txt', 'a')
    f.write(DetailsString + '\n')
    f.close()
    time.sleep(1)  # To make sure token is received before renaming recievetoken.json
    ToEmail = DetailsString.split('$')[1]
    if os.path.isfile(f'./{ToEmail}Token.json') or os.path.isfile(f'HappyBirthdayto{ToEmail}.jpg'):
        # Wasn't renaming received files when client files already existed
        os.remove(f'{ToEmail}Token.json')
        os.remove(f'HappyBirthdayto{ToEmail}.jpg')

    time.sleep(.7)
    print('In permission error')
    os.rename('recievetoken.json', f'{ToEmail}Token.json')
    os.rename('recieveimg.jpg', f'HappyBirthdayto{ToEmail}.jpg')
    DetailsString = ''
    print('Image,Details,Token Recieved :)\n')